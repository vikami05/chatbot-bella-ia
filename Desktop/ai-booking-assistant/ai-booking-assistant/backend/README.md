# 🤖 AI Booking Assistant - Backend

Sistema de gestión de turnos con IA para salón de estética.

## 🚀 Instalación Rápida

### 1. Requisitos Previos
- Python 3.9+
- MySQL 8.0+
- Ollama instalado y corriendo localmente

### 2. Configurar Base de Datos

```bash
# Crear la base de datos
mysql -u root -p
CREATE DATABASE booking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

### 3. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Ejecutar la Aplicación

```bash
python app.py
```

La API estará disponible en: `http://localhost:5000`

## 📡 Endpoints

### `POST /api/chat`
Procesar mensajes del chat

**Request:**
```json
{
  "message": "Quiero un turno para corte mañana a las 15hs",
  "context": {
    "client_name": "María"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "¡Perfecto! Tu turno está confirmado...",
  "intent": "book",
  "data": {...}
}
```

### `GET /api/bookings?date=2026-05-10`
Listar turnos de una fecha

### `GET /health`
Health check

## 🗂️ Estructura

```
backend/
├── app.py              # Aplicación principal
├── config/             # Configuración
├── models/             # Modelos SQLAlchemy
├── routes/             # Endpoints
├── services/           # Lógica de negocio
├── integrations/       # Webhooks externos
└── prompts/            # Prompts de IA
```

## 🔧 Configuración de n8n

1. En n8n, crear un webhook node
2. Copiar la URL del webhook
3. Agregar la URL en `.env` como `N8N_WEBHOOK_URL`

El sistema enviará notificaciones automáticas cuando se cree un turno.

### Flujo sugerido: confirmación por Gmail

1. `Webhook` (POST): recibe `booking_created`
2. `IF`: validar que `event` sea `booking_created`
3. `IF`: validar que `booking.client_email` exista
4. `Gmail` (Send Email): enviar confirmación al cliente
5. (Opcional) `Gmail` adicional: notificación interna del salón

### Workflow listo para importar

Este repositorio ya incluye un workflow base:

- `backend/n8n/booking_confirmation_gmail.workflow.json`
- `backend/n8n/booking_confirmation_smtp.workflow.json` (recomendado para setup rapido)

Guía rápida de importación y prueba:

- `backend/n8n/README.md`

## 🐛 Troubleshooting

**Error de conexión a MySQL:**
- Verificar que MySQL esté corriendo
- Revisar credenciales en `.env`
- Probar conexión: `mysql -u root -p`

**Error de conexión con Ollama:**
- Verificar que Ollama esté corriendo localmente
- Probar: `ollama list`
- Confirmar acceso a `http://localhost:11434`
- Verificar que el modelo `llama3` esté disponible

## 📝 Licencia

MIT
