# 🤖 Chatbot SAT Lima - Sistema Conversacional con RASA

Sistema de chatbot inteligente para el Servicio de Administración Tributaria (SAT) de Lima, desarrollado con RASA 3.6.21.

---

## 📋 Contenido

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación Rápida](#instalación-rápida)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Entrenamiento](#entrenamiento)
- [Despliegue](#despliegue)
- [Desarrollo](#desarrollo)
- [Mantenimiento](#mantenimiento)

---

## ✨ Características

- 🚗 Consulta de papeletas
- 💰 Consulta de impuestos y deuda tributaria
- 📋 Información de trámites administrativos
- 🏢 Servicios e información del SAT
- 🤝 Escalación a asesor humano


---

## 💻 Requisitos

- Ubuntu 20.04+
- Docker 20.10+
- Docker Compose 1.29+
- 4GB RAM mínimo

---

## 🚀 Instalación Rápida

### 1. Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
sudo apt install -y docker-compose
```

### 2. Clonar Proyecto

```bash
cd ~
git clone https://github.com/{URL_REPO} rasa
cd rasa
```

### 3. Configurar Variables

```bash
nano .env
```

Contenido del archivo `.env`:

```env
USER_ID=1000
GROUP_ID=1000

# Backend Configuration
BACKEND_BASE_URL=http://[IP_BACKEND]:3000
BACKEND_API_VERSION=v1

# Backend Authentication
BACKEND_AUTH_EMAIL=rasa-bot@mail.com
BACKEND_AUTH_PASSWORD=QiMAL5JDP8sfzfom

# Authentication Endpoint
BACKEND_AUTH_LOGIN_ENDPOINT=/v1/auth/login

# Citizen Endpoints
CITIZEN_GET_INFO_ENDPOINT=/v1/channel-citizen/{phone}/basic-information
CITIZEN_REQUEST_ADVISOR_ENDPOINT=/v1/channel-citizen/{phone}/request-advisor
ASSISTANCE_CLOSE_ENDPOINT=/v1/channel-room/assistances/assistance/close
```

### 4. Entrenar Modelo

```bash
docker run --rm -u $(id -u):$(id -g) -v $(pwd):/app rasa/rasa:3.6.21-full train
```

### 5. Iniciar Servicios

```bash
docker-compose up -d
```

### 6. Verificar

```bash
curl http://localhost:5005/status
```

Respuesta esperada: `{"version": "3.6.21", "is_ready": true}`

---

## 📂 Estructura del Proyecto

```
rasa/
├── actions/
│   ├── api/                     # APIs externas (SAT, Backend)
│   ├── utils/                   # Validadores
│   ├── handlers/                # Actions del bot
│   │   ├── shared/              # Sesión, asesor, fallback, router
│   │   ├── papeletas/           # Consultas de multas
│   │   ├── impuestos/           # Consultas tributarias
│   │   ├── retencion/           # Órdenes de captura
│   │   ├── lugares_pagos/       # Info oficinas
│   │   ├── servicios_virtuales/ # Info servicios virtuales
│   │   └── tramites/            # Requisitos TUPA
│   └── actions.py               # Registro central
│
├── data/
│   ├── nlu.yml                  # Intents y ejemplos
│   ├── rules.yml                # Reglas deterministas
│   └── stories.yml              # Historias conversacionales
│
├── models/                      # Modelos entrenados
├── config.yml                   # Pipeline NLU y políticas
├── domain.yml                   # Intents, entities, responses
├── .env                         # Variables de entorno
└── docker-compose.yml           # Orquestación servicios
```

---

## 🎓 Entrenamiento

### Cuándo Reentrenar

✅ Cambios en `data/` (nlu, rules, stories)  
✅ Cambios en `domain.yml`  
✅ Cambios en `config.yml`  

❌ NO reentrenar si solo cambias `actions/` (código Python)

### Comando

```bash
docker run --rm -u $(id -u):$(id -g) -v $(pwd):/app rasa/rasa:3.6.21-full train
```

---

## 🐳 Despliegue

### Iniciar

```bash
docker-compose up -d
```

### Detener

```bash
docker-compose down
```

### Ver Logs

```bash
docker-compose logs -f
```

### Reiniciar

```bash
docker-compose restart
```

### Servicio Systemd (inicio automático)

Crear archivo:

```bash
sudo nano /etc/systemd/system/sat-chatbot.service
```

Contenido:

```ini
[Unit]
Description=SAT Chatbot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/usuario/rasa
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Habilitar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sat-chatbot
sudo systemctl start sat-chatbot
```

---

## 🛠️ Desarrollo

### Agregar Nuevo Intent

**1. En `data/nlu.yml`:**

```yaml
- intent: mi_nuevo_intent
  examples: |
    - ejemplo 1
    - ejemplo 2
```

**2. En `domain.yml`:**

```yaml
intents:
  - mi_nuevo_intent
```

**3. Crear Action (si necesitas lógica):**

```python
# actions/handlers/[modulo]/mi_action.py
from rasa_sdk import Action

class ActionMiAccion(Action):
    def name(self):
        return "action_mi_accion"
    
    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Respuesta")
        return []
```

**4. Registrar en `actions/actions.py`**

**5. Agregar Rule/Story en `data/rules.yml`:**

```yaml
- rule: Mi regla
  steps:
  - intent: mi_nuevo_intent
  - action: action_mi_accion
```

**6. Aplicar cambios:**

```bash
# Reentrenar
docker run --rm -u $(id -u):$(id -g) -v $(pwd):/app rasa/rasa:3.6.21-full train

# Si cambios en actions/
docker-compose build rasa-actions

# Reiniciar
docker-compose restart
```

### Modificar Respuestas

**Estáticas (en `domain.yml`):**

```yaml
responses:
  utter_greet:
  - text: "Nueva respuesta"
```

```bash
docker-compose restart
```

**Dinámicas (en código Python):**

Editar archivo en `actions/handlers/`

```bash
docker-compose build rasa-actions
docker-compose restart
```

---

## 🔧 Mantenimiento

### Comandos Útiles

```bash
# Estado
docker-compose ps

# Logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Reconstruir (cambios en código)
docker-compose build rasa-actions
docker-compose up -d
```

### Actualizar Modelo

```bash
docker-compose down
docker-compose build rasa-actions  # Si hay cambios en actions/
docker run --rm -u $(id -u):$(id -g) -v $(pwd):/app rasa/rasa:3.6.21-full train
docker-compose up -d
```

### Troubleshooting

**Bot no responde:**

```bash
docker-compose ps        # Ver estado
docker-compose logs -f   # Ver errores
docker-compose restart   # Reiniciar
```

**Puerto ocupado:**

```bash
sudo lsof -i :5005
sudo kill -9 [PID]
```

**Permisos:**

```bash
sudo chown -R $USER:$USER .
```

---

## 📊 API Endpoints

| Endpoint | Puerto | Descripción |
|----------|--------|-------------|
| `/webhooks/rest/webhook` | 5005 | Enviar mensajes |
| `/status` | 5005 | Health check Core |
| `/health` | 5055 | Health check Actions |

### Ejemplo

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook 
  -H "Content-Type: application/json" 
  -d '{
    "sender": "test",
    "message": "hola"
  }'
```

---

**Versión**: 1.0  
**Última actualización**: 2025