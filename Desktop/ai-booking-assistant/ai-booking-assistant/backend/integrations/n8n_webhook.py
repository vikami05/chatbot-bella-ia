import requests
from config.settings import Config

def send_booking_notification(booking_data: dict) -> bool:
    """
    Enviar notificación de nueva reserva a n8n
    """
    if not Config.N8N_WEBHOOK_URL:
        print("N8N webhook URL no configurada")
        return False
    
    try:
        payload = {
            'event': 'booking_created',
            'booking': booking_data,
            'timestamp': booking_data.get('created_at')
        }
        
        response = requests.post(
            Config.N8N_WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        
        if 200 <= response.status_code < 300:
            print(f"Notificación enviada a n8n para booking {booking_data.get('id')}")
            return True
        else:
            print(
                f"Error enviando a n8n: {response.status_code} "
                f"- URL: {Config.N8N_WEBHOOK_URL}"
            )
            return False
    
    except Exception as e:
        print(f"Error en webhook n8n: {str(e)}")
        return False
