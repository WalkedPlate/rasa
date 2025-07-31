# timeout_scheduler.py - Scheduler externo completo para manejar timeouts
import requests
import time
import json
import threading
import signal
import sys
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, Set, Optional
import sqlite3
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ConversationDatabase:
    """Manejo de base de datos para persistir conversaciones"""
    
    def __init__(self, db_path="conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    sender_id TEXT PRIMARY KEY,
                    started_at TIMESTAMP,
                    last_activity TIMESTAMP,
                    warning_sent BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES conversations (sender_id)
                )
            """)
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones de BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def register_conversation(self, sender_id: str):
        """Registra nueva conversación"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO conversations 
                (sender_id, started_at, last_activity, warning_sent, status)
                VALUES (?, ?, ?, FALSE, 'active')
            """, (sender_id, datetime.now(), datetime.now()))
            conn.commit()
    
    def update_activity(self, sender_id: str):
        """Actualiza última actividad"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE conversations 
                SET last_activity = ?, warning_sent = FALSE
                WHERE sender_id = ?
            """, (datetime.now(), sender_id))
            conn.commit()
    
    def set_warning_sent(self, sender_id: str):
        """Marca warning como enviado"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE conversations 
                SET warning_sent = TRUE
                WHERE sender_id = ?
            """, (sender_id,))
            conn.commit()
    
    def close_conversation(self, sender_id: str):
        """Cierra conversación"""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE conversations 
                SET status = 'closed'
                WHERE sender_id = ?
            """, (sender_id,))
            conn.commit()
    
    def get_active_conversations(self) -> list:
        """Obtiene todas las conversaciones activas"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM conversations 
                WHERE status = 'active'
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def log_event(self, sender_id: str, event_type: str, event_data: dict = None):
        """Registra evento en el log"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO conversation_events 
                (sender_id, event_type, event_data)
                VALUES (?, ?, ?)
            """, (sender_id, event_type, json.dumps(event_data or {})))
            conn.commit()

class TimeoutScheduler:
    """Scheduler que monitorea conversaciones y maneja timeouts automáticamente"""
    
    def __init__(self, rasa_url="http://localhost:5005", check_interval=30):
        self.rasa_url = rasa_url.rstrip('/')
        self.check_interval = check_interval
        self.running = False
        self.scheduler_thread = None
        
        # Timeouts en segundos
        self.WARNING_TIMEOUT = 240  # 4 minutos
        self.FINAL_TIMEOUT = 300    # 5 minutos
        
        # Base de datos
        self.db = ConversationDatabase()
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 TimeoutScheduler inicializado")
        logger.info(f"📊 Configuración: Warning={self.WARNING_TIMEOUT}s, Final={self.FINAL_TIMEOUT}s")
    
    def start(self):
        """Inicia el scheduler en un hilo separado"""
        if self.running:
            logger.warning("⚠️ Scheduler ya está ejecutándose")
            return
        
        logger.info("🚀 Iniciando Timeout Scheduler...")
        self.running = True
        
        # Iniciar en hilo separado
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info(f"⏰ Scheduler activo - Verificando cada {self.check_interval} segundos")
    
    def stop(self):
        """Detiene el scheduler"""
        logger.info("🛑 Deteniendo Timeout Scheduler...")
        self.running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("✅ Scheduler detenido correctamente")
    
    def _signal_handler(self, signum, frame):
        """Maneja señales del sistema"""
        logger.info(f"📡 Señal recibida: {signum}")
        self.stop()
        sys.exit(0)
    
    def _run_scheduler(self):
        """Loop principal del scheduler"""
        logger.info("🔄 Scheduler iniciado - Loop principal activo")
        
        while self.running:
            try:
                self._check_all_conversations()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error en scheduler loop: {e}")
                time.sleep(5)  # Pausa breve antes de reintentar
    
    def _check_all_conversations(self):
        """Verifica todas las conversaciones activas"""
        try:
            active_conversations = self.db.get_active_conversations()
            
            if not active_conversations:
                logger.debug("💤 No hay conversaciones activas")
                return
            
            logger.debug(f"🔍 Verificando {len(active_conversations)} conversaciones activas")
            
            for conv in active_conversations:
                self._check_conversation_timeout(conv)
                
        except Exception as e:
            logger.error(f"❌ Error verificando conversaciones: {e}")
    
    def _check_conversation_timeout(self, conversation: dict):
        """Verifica timeout para una conversación específica"""
        sender_id = conversation['sender_id']
        
        try:
            # Obtener tracker de Rasa
            tracker_data = self._get_tracker(sender_id)
            if not tracker_data:
                logger.warning(f"⚠️ No se pudo obtener tracker para {sender_id}")
                return
            
            # Calcular tiempo de inactividad
            inactivity_time = self._calculate_inactivity(tracker_data)
            
            logger.debug(f"👤 {sender_id}: {inactivity_time:.0f}s de inactividad")
            
            # Verificar timeouts
            if (inactivity_time >= self.WARNING_TIMEOUT and 
                inactivity_time < self.FINAL_TIMEOUT and 
                not conversation['warning_sent']):
                
                self._send_timeout_warning(sender_id)
                self.db.set_warning_sent(sender_id)
                self.db.log_event(sender_id, "warning_sent", {"inactivity_seconds": inactivity_time})
                logger.info(f"⏰ Warning enviado a {sender_id}")
                
            elif inactivity_time >= self.FINAL_TIMEOUT:
                self._send_timeout_final(sender_id)
                self._cleanup_conversation(sender_id)
                self.db.log_event(sender_id, "timeout_final", {"inactivity_seconds": inactivity_time})
                logger.info(f"⏰ Timeout final para {sender_id}")
                
        except Exception as e:
            logger.error(f"❌ Error verificando timeout para {sender_id}: {e}")
    
    def _get_tracker(self, sender_id: str) -> Optional[dict]:
        """Obtiene tracker de conversación desde Rasa"""
        try:
            tracker_url = f"{self.rasa_url}/conversations/{sender_id}/tracker"
            response = requests.get(tracker_url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Error obteniendo tracker para {sender_id}: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Error de conexión obteniendo tracker para {sender_id}: {e}")
            return None
    
    def _calculate_inactivity(self, tracker_data: dict) -> float:
        """Calcula tiempo de inactividad basado en último mensaje de usuario"""
        events = tracker_data.get('events', [])
        
        # Buscar último evento de usuario
        last_user_timestamp = None
        for event in reversed(events):
            if event.get('event') == 'user':
                last_user_timestamp = event.get('timestamp')
                break
        
        if last_user_timestamp is None:
            return 0
        
        return time.time() - last_user_timestamp
    
    def _send_timeout_warning(self, sender_id: str):
        """Envía warning de timeout al usuario"""
        try:
            message_data = {
                "sender": sender_id,
                "message": "/timeout_warning"
            }
            
            webhook_url = f"{self.rasa_url}/webhooks/rest/webhook"
            response = requests.post(webhook_url, json=message_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Warning enviado correctamente a {sender_id}")
            else:
                logger.error(f"❌ Error enviando warning a {sender_id}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando warning a {sender_id}: {e}")
    
    def _send_timeout_final(self, sender_id: str):
        """Envía mensaje final y cierra conversación"""
        try:
            message_data = {
                "sender": sender_id,
                "message": "/timeout_final"
            }
            
            webhook_url = f"{self.rasa_url}/webhooks/rest/webhook"
            response = requests.post(webhook_url, json=message_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Timeout final enviado correctamente a {sender_id}")
            else:
                logger.error(f"❌ Error enviando timeout final a {sender_id}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando timeout final a {sender_id}: {e}")
    
    def _cleanup_conversation(self, sender_id: str):
        """Limpia datos de conversación después del timeout"""
        self.db.close_conversation(sender_id)
        logger.debug(f"🧹 Limpieza completada para {sender_id}")
    
    def register_conversation(self, sender_id: str):
        """Registra una nueva conversación activa"""
        self.db.register_conversation(sender_id)
        self.db.log_event(sender_id, "conversation_started")
        logger.info(f"📝 Conversación registrada para {sender_id}")
    
    def update_activity(self, sender_id: str, message: str = ""):
        """Actualiza la última actividad de una conversación"""
        self.db.update_activity(sender_id)
        self.db.log_event(sender_id, "user_message", {"message": message[:100]})  # Truncar mensaje largo
        logger.debug(f"🔄 Actividad actualizada para {sender_id}")
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del scheduler"""
        active_conversations = self.db.get_active_conversations()
        warnings_sent = sum(1 for conv in active_conversations if conv['warning_sent'])
        
        return {
            'active_conversations': len(active_conversations),
            'warnings_sent': warnings_sent,
            'running': self.running,
            'check_interval': self.check_interval,
            'warning_timeout': self.WARNING_TIMEOUT,
            'final_timeout': self.FINAL_TIMEOUT,
            'rasa_url': self.rasa_url
        }
    
    def get_conversation_history(self, sender_id: str) -> dict:
        """Obtiene historial de conversación"""
        with self.db.get_connection() as conn:
            # Obtener datos de conversación
            conv_cursor = conn.execute("""
                SELECT * FROM conversations WHERE sender_id = ?
            """, (sender_id,))
            conversation = conv_cursor.fetchone()
            
            # Obtener eventos
            events_cursor = conn.execute("""
                SELECT * FROM conversation_events 
                WHERE sender_id = ? 
                ORDER BY timestamp
            """, (sender_id,))
            events = [dict(row) for row in events_cursor.fetchall()]
            
            return {
                'conversation': dict(conversation) if conversation else None,
                'events': events
            }

class TimeoutWebhook:
    """Webhook que permite a Rasa comunicarse con el scheduler"""
    
    def __init__(self, scheduler: TimeoutScheduler):
        self.scheduler = scheduler
    
    def handle_user_message(self, sender_id: str, message: str):
        """Maneja mensajes de usuario y actualiza actividad"""
        # Verificar si es nueva conversación
        active_conversations = self.scheduler.db.get_active_conversations()
        existing_conv = next((c for c in active_conversations if c['sender_id'] == sender_id), None)
        
        if not existing_conv:
            self.scheduler.register_conversation(sender_id)
        else:
            self.scheduler.update_activity(sender_id, message)
    
    def handle_conversation_end(self, sender_id: str):
        """Maneja finalización manual de conversación"""
        self.scheduler.db.close_conversation(sender_id)
        self.scheduler.db.log_event(sender_id, "conversation_ended_manually")
        logger.info(f"👋 Conversación finalizada manualmente para {sender_id}")

# ========== API WEB PARA MONITOREO ==========
def create_monitoring_api(scheduler: TimeoutScheduler):
    """Crea API web simple para monitoreo (opcional)"""
    try:
        from flask import Flask, jsonify, request
        
        app = Flask(__name__)
        webhook = TimeoutWebhook(scheduler)
        
        @app.route('/stats')
        def get_stats():
            return jsonify(scheduler.get_stats())
        
        @app.route('/conversations')
        def get_conversations():
            return jsonify(scheduler.db.get_active_conversations())
        
        @app.route('/conversation/<sender_id>')
        def get_conversation(sender_id):
            return jsonify(scheduler.get_conversation_history(sender_id))
        
        @app.route('/webhook/user_message', methods=['POST'])
        def handle_user_message():
            data = request.json
            sender_id = data.get('sender')
            message = data.get('message', '')
            
            webhook.handle_user_message(sender_id, message)
            return jsonify({"status": "ok"})
        
        @app.route('/webhook/conversation_end', methods=['POST'])
        def handle_conversation_end():
            data = request.json
            sender_id = data.get('sender')
            
            webhook.handle_conversation_end(sender_id)
            return jsonify({"status": "ok"})
        
        return app
    
    except ImportError:
        logger.warning("⚠️ Flask no disponible - API web deshabilitada")
        return None

# ========== FUNCIÓN PRINCIPAL ==========
def main():
    """Función principal para ejecutar el scheduler"""
    
    # Configuración desde variables de entorno o valores por defecto
    RASA_URL = os.getenv('RASA_URL', 'http://localhost:5005')
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))
    ENABLE_API = os.getenv('ENABLE_API', 'false').lower() == 'true'
    API_PORT = int(os.getenv('API_PORT', '8080'))
    
    logger.info("🚀 INICIANDO TIMEOUT SCHEDULER PARA CHATBOT SAT")
    logger.info("=" * 50)
    logger.info(f"📊 Configuración:")
    logger.info(f"   • Rasa URL: {RASA_URL}")
    logger.info(f"   • Check Interval: {CHECK_INTERVAL}s")
    logger.info(f"   • API Web: {'Habilitada' if ENABLE_API else 'Deshabilitada'}")
    
    # Crear e iniciar scheduler
    scheduler = TimeoutScheduler(rasa_url=RASA_URL, check_interval=CHECK_INTERVAL)
    
    try:
        # Iniciar scheduler
        scheduler.start()
        
        # Iniciar API web si está habilitada
        if ENABLE_API:
            app = create_monitoring_api(scheduler)
            if app:
                logger.info(f"🌐 API web disponible en http://localhost:{API_PORT}")
                # Ejecutar Flask en hilo separado
                import threading
                api_thread = threading.Thread(
                    target=lambda: app.run(host='0.0.0.0', port=API_PORT, debug=False),
                    daemon=True
                )
                api_thread.start()
        
        logger.info("✅ Timeout Scheduler iniciado correctamente")
        logger.info("📊 Comandos disponibles:")
        logger.info("   • Ctrl+C: Detener scheduler")
        logger.info("   • Ver stats: curl http://localhost:8080/stats")
        logger.info("   • Ver conversaciones: curl http://localhost:8080/conversations")
        
        # Mostrar estadísticas cada 5 minutos
        last_stats_time = 0
        
        # Mantener el programa corriendo
        while scheduler.running:
            time.sleep(1)
            
            # Mostrar estadísticas periódicamente
            current_time = time.time()
            if current_time - last_stats_time >= 300:  # 5 minutos
                stats = scheduler.get_stats()
                logger.info(f"📊 Stats: {stats['active_conversations']} conversaciones activas, "
                          f"{stats['warnings_sent']} warnings enviados")
                last_stats_time = current_time
    
    except KeyboardInterrupt:
        logger.info("🛑 Deteniendo scheduler por solicitud del usuario...")
    
    except Exception as e:
        logger.error(f"❌ Error fatal en scheduler: {e}")
    
    finally:
        scheduler.stop()
        logger.info("✅ Scheduler detenido correctamente")

# ========== SCRIPT DE UTILIDADES ==========
def cli_commands():
    """Comandos de línea de comandos para el scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Timeout Scheduler para Chatbot SAT')
    parser.add_argument('command', choices=['start', 'stats', 'conversations', 'history'], 
                       help='Comando a ejecutar')
    parser.add_argument('--sender-id', help='ID del sender para comandos específicos')
    parser.add_argument('--rasa-url', default='http://localhost:5005', help='URL de Rasa')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        main()
    
    elif args.command == 'stats':
        scheduler = TimeoutScheduler(rasa_url=args.rasa_url)
        stats = scheduler.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'conversations':
        scheduler = TimeoutScheduler(rasa_url=args.rasa_url)
        conversations = scheduler.db.get_active_conversations()
        print(json.dumps(conversations, indent=2, default=str))
    
    elif args.command == 'history':
        if not args.sender_id:
            print("Error: --sender-id requerido para comando 'history'")
            sys.exit(1)
        
        scheduler = TimeoutScheduler(rasa_url=args.rasa_url)
        history = scheduler.get_conversation_history(args.sender_id)
        print(json.dumps(history, indent=2, default=str))

# ========== PUNTO DE ENTRADA ==========
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_commands()
    else:
        main()
