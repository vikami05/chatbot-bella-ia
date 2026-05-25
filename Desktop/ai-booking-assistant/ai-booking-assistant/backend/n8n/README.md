# n8n Integration (Booking + Gmail)

Esta carpeta incluye un workflow inicial para enviar confirmaciones por email cuando se crea un turno.

## Archivo incluido

- `booking_confirmation_gmail.workflow.json`
- `booking_confirmation_smtp.workflow.json` (recomendado para empezar)

## Que hace este workflow

1. Recibe un webhook POST con evento `booking_created`
2. Valida que el evento sea correcto
3. Valida que exista `booking.client_email`
4. Envia email de confirmacion por Gmail
5. Responde al webhook con un JSON de resultado

## Importar en n8n

1. Ir a `Workflows` -> `Import from file`
2. Seleccionar `backend/n8n/booking_confirmation_gmail.workflow.json`
3. Abrir nodo `Gmail Send Confirmation`
4. Configurar credencial `gmailOAuth2`
5. Guardar y activar workflow

## Opcion recomendada: SMTP Gmail (mas simple)

1. Importar `booking_confirmation_smtp.workflow.json`
2. Abrir nodo `Email Send SMTP`
3. Crear credencial SMTP con:
   - Host: `smtp.gmail.com`
   - Port: `587`
   - Secure: `false`
   - User: tu Gmail completo
   - Password: App Password de Google (16 caracteres)
4. Guardar y activar workflow

Nota: App Password requiere 2FA activado en tu cuenta Google.

## Configurar backend

En `backend/.env` agregar:

```env
N8N_WEBHOOK_URL=https://TU-N8N/webhook/booking-created
```

Luego reiniciar backend para tomar cambios.

## Payload esperado

El backend envia un payload similar a este:

```json
{
  "event": "booking_created",
  "booking": {
    "id": 1,
    "client_name": "Maria",
    "client_email": "maria@email.com",
    "service": "corte",
    "booking_date": "2026-05-10",
    "booking_time": "15:00",
    "status": "confirmed"
  },
  "timestamp": "2026-05-10T12:00:00"
}
```

## Probar rapido

1. Activar workflow en n8n
2. Poner la URL en `N8N_WEBHOOK_URL`
3. Crear una reserva desde el chat con `client_email`
4. Verificar ejecucion en n8n y recepcion del email

Tip: durante la conversación, pasá explícitamente el email del cliente (ej: `mi email es laura@mail.com`).

## Notas

- Si no hay `client_email`, el workflow responde `ok: true` con `reason: missing_client_email`.
- Para seguridad, siguiente paso recomendado: agregar header secreto (`X-Webhook-Secret`) y validarlo en n8n.
