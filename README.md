🤖 AI Booking Assistant

✨ Asistente conversacional inteligente para gestionar turnos de un salón de estética utilizando IA local, backend en Flask y automatizaciones con n8n.

📌 ¿Qué resuelve?

Este proyecto permite que los clientes puedan:

✅ Reservar turnos
✅ Consultar disponibilidad
✅ Cancelar reservas
✅ Recibir confirmaciones automáticas por email

Todo desde un chat conversacional 💬

El sistema detecta la intención del usuario y extrae automáticamente datos clave como:

🧴 Servicio
📅 Fecha
⏰ Hora
📧 Email

Luego:

valida disponibilidad,
evita superposición de turnos,
guarda la información en MySQL,
y dispara un webhook hacia n8n para enviar emails automáticos 

🛠️ Tecnologías utilizadas

⚙️ Backend
🐍 Python 3.9+
🌶️ Flask
🗄️ SQLAlchemy
🐬 MySQL
🌐 Requests (HTTP requests)

🧠 Inteligencia Artificial

🤖 Ollama (modelo local)
📝 Prompt Engineering

🔍 Clasificación de intención

🧩 Extracción de entidades
🎨 Frontend
🌐 HTML5
🎨 CSS3
⚡ JavaScript Vanilla

🔄 Automatización

🔗 n8n
✉️ SMTP Gmail / Gmail OAuth

🏗️ Arquitectura (High Level)

👤 Usuario
   ↓
💬 Frontend Chat
   ↓
📡 POST /api/chat
   ↓
🧠 Módulo IA (Ollama)
   ↓
📋 Detección de intención
   ↓
🗄️ Servicio de reservas
   ↓
🐬 MySQL
   ↓
🔗 Webhook n8n
   ↓
✉️ Email de confirmación
🤖 Flujo del Bot
🧠 Entendimiento

El bot interpreta lenguaje natural y detecta:

intención del usuario (book, check, cancel)
servicio solicitado
fecha
hora
email

💬 Gestión de contexto

Si faltan datos importantes, el asistente los solicita automáticamente y mantiene una conversación guiada hasta completar la reserva.

📋 Reglas de negocio

El sistema:

✅ Verifica horarios disponibles
✅ Evita superposición de turnos
✅ Normaliza fecha y hora

✅ Confirmación

Una vez validada la reserva:

se guarda en MySQL,
se responde al usuario,
y opcionalmente se envía un email automático vía n8n.
📂 Estructura del proyecto
ai-booking-assistant/
│
├── backend/
│   ├── app.py
│   ├── config/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── integrations/
│   └── prompts/
│
├── n8n/
│
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
│
└── database/

⚡ Setup rápido
1️⃣ Crear base de datos
mysql -u root -p

CREATE DATABASE booking_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
2️⃣ Configurar backend
cd backend

python -m venv venv
▶️ Windows
venv\Scripts\activate
📦 Instalar dependencias
pip install -r requirements.txt
📄 Variables de entorno
copy .env.example .env
3️⃣ Configurar .env
MYSQL_PASSWORD=tu_password_mysql
MYSQL_DATABASE=booking_db

OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3

# Opcional - webhook n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/booking-created
🚀 Levantar servicios
▶️ Backend
cd backend
python app.py
🌐 Frontend
cd frontend
python -m http.server 8000

Abrir en navegador:

http://localhost:8000
🔄 n8n - Confirmación de emails
📂 Workflows incluidos
backend/n8n/booking_confirmation_smtp.workflow.json
(recomendado)

backend/n8n/booking_confirmation_gmail.workflow.json

⚙️ Pasos
Abrir n8n en:
http://localhost:5678
Importar uno de los workflows
Configurar credencial SMTP/Gmail

Activar workflow ✅
Verificar:
N8N_WEBHOOK_URL=http://localhost:5678/webhook/booking-created

🔌 Endpoints principales

💬 Procesar mensajes
POST /api/chat

📅 Obtener turnos por fecha
GET /api/bookings?date=YYYY-MM-DD

❤️ Health Check
GET /health

📨 Ejemplo de payload hacia n8n
Formato 1
{
  "event": "booking_created",
  "booking": {
    "client_name": "Kamila",
    "client_email": "kamila@mail.com",
    "service": "manicura",
    "booking_date": "2026-06-19",
    "booking_time": "10:40"
  }
}
Formato 2
{
  "intent": "book",
  "data": {
    "client_name": "Andrea Mariana",
    "client_email": "andrea@mail.com",
    "service": "tratamiento_facial",
    "date": "2026-06-18",
    "time": "10:30"
  }
}
📌 Estado del proyecto

🚧 MVP funcional para demo y validación de flujo completo:

Chat → IA → Reserva → Webhook → Email
