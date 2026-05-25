# AI Booking Assistant

Asistente conversacional para gestionar turnos de un salon de estetica con IA local, backend en Flask y automatizaciones con n8n.

## Que resuelve

- Permite reservar, consultar y cancelar turnos desde un chat.
- Detecta intencion del usuario y extrae datos clave (servicio, fecha, hora, email).
- Valida disponibilidad y guarda los turnos en MySQL.
- Dispara un webhook para enviar confirmaciones por email con n8n.

## Tecnologias usadas

### Backend
- Python 3.9+
- Flask
- SQLAlchemy
- MySQL
- Requests (llamadas HTTP a servicios externos)

### IA
- Ollama (modelo local)
- Prompting para clasificacion de intencion y extraccion de entidades

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)

### Automatizacion
- n8n
- SMTP Gmail o nodo Gmail OAuth para envio de emails

## Arquitectura (alto nivel)

1. El usuario escribe en el chat del frontend.
2. Frontend envia el mensaje a `POST /api/chat`.
3. Flask consulta el modulo de IA para entender la intencion (`book`, `check`, `cancel`, etc.).
4. El servicio de turnos valida datos y opera sobre MySQL.
5. Si se crea una reserva, Flask envia un webhook a n8n.
6. n8n procesa el payload y envia email de confirmacion.

## Flujo del bot

### 1) Entendimiento
- El bot interpreta lenguaje natural del cliente.
- Detecta la accion pedida y los campos relevantes.

### 2) Gestion de contexto
- Si faltan datos (por ejemplo hora o email), el bot los solicita.
- Mantiene una conversacion guiada hasta completar la reserva.

### 3) Reglas de negocio
- Verifica horarios disponibles.
- Evita superposiciones de turnos.
- Normaliza formato de fecha/hora.

### 4) Confirmacion
- Crea el turno en base de datos.
- Responde al usuario con confirmacion.
- (Opcional) dispara email automatico via n8n.

## Estructura del proyecto

```text
ai-booking-assistant/
|- backend/
|  |- app.py
|  |- config/
|  |- models/
|  |- routes/
|  |- services/
|  |- integrations/
|  |- prompts/
|  `- n8n/
|- frontend/
|  |- index.html
|  |- css/
|  `- js/
`- database/
```

## Setup rapido

### 1. Base de datos
```bash
mysql -u root -p
CREATE DATABASE booking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Backend
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 3. Variables de entorno (`backend/.env`)
```env
MYSQL_PASSWORD=tu_password_mysql
MYSQL_DATABASE=booking_db

OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3

# Opcional: webhook de n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/booking-created
```

### 4. Levantar servicios
```bash
# backend
cd backend
python app.py

# frontend (otra terminal)
cd frontend
python -m http.server 8000
```

Abrir: `http://localhost:8000`

## n8n (email de confirmacion)

Workflows incluidos:
- `backend/n8n/booking_confirmation_smtp.workflow.json` (recomendado)
- `backend/n8n/booking_confirmation_gmail.workflow.json`

Pasos:
1. Abrir n8n en `http://localhost:5678`.
2. Importar uno de los workflows.
3. Configurar credencial SMTP/Gmail.
4. Activar workflow.
5. Verificar `N8N_WEBHOOK_URL` en `backend/.env`.

## Endpoints principales

- `POST /api/chat` - procesa mensajes del asistente
- `GET /api/bookings?date=YYYY-MM-DD` - lista turnos por fecha
- `GET /health` - health check

## Ejemplo de payload hacia n8n

Actualmente pueden existir dos formatos segun version del backend:

```json
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
```

o

```json
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
```

## Estado del proyecto

MVP funcional para demo y validacion de flujo completo:
chat -> IA -> reserva -> webhook -> email.

## Licencia

MIT
