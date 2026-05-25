
from flask import Blueprint, request, jsonify
from datetime import datetime
import re

from services.ai_service import AIService
from services.booking_service import BookingService

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

ai_service = AIService()
booking_service = BookingService()

# =========================
# SERVICIOS
# =========================

SERVICES = {
    "corte": {
        "name": "Corte de cabello",
        "price": "$5.000",
        "duration": "30 min"
    },
    "tintura": {
        "name": "Tintura",
        "price": "$15.000",
        "duration": "90 min"
    },
    "manicura": {
        "name": "Manicura",
        "price": "$8.000",
        "duration": "45 min"
    },
    "pedicura": {
        "name": "Pedicura",
        "price": "$10.000",
        "duration": "60 min"
    },
    "depilacion": {
        "name": "Depilación",
        "price": "$7.000",
        "duration": "30 min"
    },
    "tratamiento_facial": {
        "name": "Tratamiento facial",
        "price": "$12.000",
        "duration": "60 min"
    }
}

# =========================
# HELPERS
# =========================

def normalize_service_name(service):

    if not service:
        return None

    service = service.lower().strip()

    mapping = {
        "tratamiento facial": "tratamiento_facial",
        "facial": "tratamiento_facial",
        "manicura": "manicura",
        "pedicura": "pedicura",
        "depilacion": "depilacion",
        "depilación": "depilacion",
        "corte": "corte",
        "corte de cabello": "corte",
        "tintura": "tintura"
    }

    return mapping.get(service, service)


def is_valid_date(date_str):

    if not date_str:
        return False

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True

    except:
        return False


def is_valid_time(time_str):

    if not time_str:
        return False

    try:
        datetime.strptime(time_str, "%H:%M")
        return True

    except:
        return False


def is_valid_email(email_str):

    if not email_str or not isinstance(email_str, str):
        return False

    email = email_str.strip().lower()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return re.match(pattern, email) is not None


def clean_llm_value(value):

    if not value:
        return None

    if not isinstance(value, str):
        return value

    value = value.strip()

    invalid_values = [
        "unknown",
        "null",
        "none",
        "undefined",
        "",
        "n/a"
    ]

    if value.lower() in invalid_values:
        return None

    return value


def is_goodbye_message(message):

    goodbye_words = [
        "gracias",
        "muchas gracias",
        "chau",
        "adiós",
        "adios",
        "nos vemos",
        "hasta luego",
        "bye",
        "ok gracias"
    ]

    message = message.lower().strip()

    for word in goodbye_words:

        if word in message:
            return True

    return False


def get_missing_fields(context):

    required = [
        "client_name",
        "client_email",
        "service",
        "date",
        "time"
    ]

    missing = []

    for field in required:

        value = context.get(field)

        if not value:
            missing.append(field)

    return missing


def generate_missing_field_message(missing_fields):
    if "service" in missing_fields:
        return "Perfecto 😊 ¿Qué servicio querés reservar?"

    if "client_name" in missing_fields:
        return "Perfecto 😊 ¿Cuál es tu nombre?"

    if "client_email" in missing_fields:
        return "Perfecto 😊 ¿Me compartís tu email para enviarte la confirmación?"

    if "date" in missing_fields and "time" in missing_fields:
        return "Perfecto 😊 ¿Para qué día y horario querés reservar?"

    if "date" in missing_fields:
        return "Perfecto 😊 ¿Para qué día querés reservar?"

    if "time" in missing_fields:
        return "Perfecto 😊 ¿Qué horario preferís?"

    return "Necesito algunos datos más 😊"


# =========================
# ROUTE
# =========================

@chat_bp.route('/chat', methods=['POST'])
def chat():

    try:

        data = request.get_json()

        if not data or 'message' not in data:

            return jsonify({
                'error': 'Se requiere un mensaje'
            }), 400

        user_message = data['message']
        lower_msg = user_message.lower()

        # =========================
        # CONTEXTO
        # =========================

        context = data.get('context', {})

        if not context:
            context = {}

        history = context.get("history", [])

        history.append({
            "role": "user",
            "content": user_message
        })

        context["history"] = history

        # =========================
        # DESPEDIDA / AGRADECIMIENTO
        # =========================

        if is_goodbye_message(user_message):

            response_message = (
                "¡Gracias a vos! 😊 "
                "Te esperamos en tu turno. "
                "Que tengas un hermoso día 💖"
            )

            # limpiar contexto completo
            context["client_name"] = None
            context["client_email"] = None
            context["service"] = None
            context["date"] = None
            context["time"] = None

            context["history"].append({
                "role": "assistant",
                "content": response_message
            })

            return jsonify({
                'success': True,
                'message': response_message,
                'intent': 'goodbye',
                'data': context
            }), 200

        # =========================
        # IA
        # =========================

        ai_response = ai_service.process_message(
            user_message,
            context
        )

        extracted_data = ai_response.get(
            "extracted_data",
            {}
        )

        print("\n========== EXTRACTED DATA ==========")
        print(extracted_data)
        print("====================================\n")

        # =========================
        # FUSIONAR DATOS
        # =========================

        for key, value in extracted_data.items():

            value = clean_llm_value(value)

            if not value:
                continue

            if key == "service":
                value = normalize_service_name(value)

            context[key] = value

        # =========================
        # VALIDACIONES
        # =========================

        if context.get("date"):

            if not is_valid_date(context["date"]):
                context["date"] = None

        if context.get("time"):

            if not is_valid_time(context["time"]):
                context["time"] = None

        if context.get("client_email"):

            context["client_email"] = str(
                context["client_email"]
            ).strip().lower()

            if not is_valid_email(context["client_email"]):
                context["client_email"] = None

        # =========================
        # INTENT
        # =========================

        intent = ai_response.get(
            "intent",
            "unknown"
        )

        response_message = ai_response.get(
            "response",
            ""
        )

        # ==================================================
        # BOOKING FLOW (PRIORIDAD MÁXIMA)
        # ==================================================

        if (
            intent == "book"
            or context.get("service")
            or context.get("client_name")
            or context.get("date")
            or context.get("time")
        ):

            missing_fields = get_missing_fields(context)

            # =========================
            # FALTAN DATOS
            # =========================

            if missing_fields:

                response_message = (
                    generate_missing_field_message(
                        missing_fields
                    )
                )

            # =========================
            # CREAR BOOKING
            # =========================

            else:

                booking_result = (
                    booking_service.create_booking(
                        context
                    )
                )

                if booking_result.get("success"):

                    service_name = SERVICES[
                        context.get("service")
                    ]["name"]

                    response_message = (
                        f"Perfecto {context.get('client_name')} 😊\n\n"
                        f"Te reservé un turno para:\n"
                        f"• Servicio: {service_name}\n"
                        f"• Fecha: {context.get('date')}\n"
                        f"• Hora: {context.get('time')}\n"
                        f"• Confirmación: {context.get('client_email')}"
                    )

                    # limpiar flujo COMPLETO
                    context["client_name"] = None
                    context["client_email"] = None
                    context["service"] = None
                    context["date"] = None
                    context["time"] = None

                else:

                    response_message = booking_result.get(
                        "message",
                        "No se pudo crear la reserva."
                    )

        # =========================
        # TODOS LOS SERVICIOS
        # =========================

        elif (
            "servicios" in lower_msg
            or "qué ofrecen" in lower_msg
            or "que ofrecen" in lower_msg
            or "todos los precios" in lower_msg
        ):

            response_message = (
                "Estos son nuestros servicios 😊\n\n"
            )

            for service in SERVICES.values():

                response_message += (
                    f"• {service['name']} "
                    f"({service['duration']}) - "
                    f"{service['price']}\n"
                )

        # =========================
        # PRECIOS
        # =========================

        elif (
            "precio" in lower_msg
            or "cuesta" in lower_msg
            or "vale" in lower_msg
        ):

            service = context.get("service")

            if service and service in SERVICES:

                service_data = SERVICES[service]

                response_message = (
                    f"{service_data['name']} cuesta "
                    f"{service_data['price']} "
                    f"y dura {service_data['duration']} 😊"
                )

            else:

                response_message = (
                    "¿Sobre qué servicio querés "
                    "saber el precio? 😊"
                )

        # =========================
        # HORARIOS
        # =========================

        elif (
            "horario" in lower_msg
            or "horarios" in lower_msg
        ):

            response_message = (
                "Nuestros horarios son:\n\n"
                "🕘 Lunes a sábado: 9:00 AM a 7:00 PM\n"
                "❌ Domingos: cerrado"
            )

        # =========================
        # INFO
        # =========================

        elif intent == "info":

            service = context.get("service")

            if service and service in SERVICES:

                service_data = SERVICES[service]

                response_message = (
                    f"{service_data['name']} dura "
                    f"{service_data['duration']} "
                    f"y cuesta {service_data['price']} 😊"
                )

        # =========================
        # GREETING
        # =========================

        elif intent == "greeting":

            response_message = (
                "¡Hola! 😊 ¿En qué puedo ayudarte hoy?"
            )

        # =========================
        # FALLBACK
        # =========================

        elif not response_message:

            response_message = (
                "Disculpá 😊 ¿Podrías explicarme "
                "un poco más?"
            )

        # =========================
        # GUARDAR HISTORIAL
        # =========================

        context["history"].append({
            "role": "assistant",
            "content": response_message
        })

        context["history"] = context["history"][-20:]

        # =========================
        # RESPONSE
        # =========================

        return jsonify({
            'success': True,
            'message': response_message,
            'intent': intent,
            'data': context
        }), 200

    except Exception as e:

        print("\n========== CHAT ERROR ==========")
        print(e)
        print("================================\n")

        return jsonify({
            'success': False,
            'error': str(e),
            'message': (
                'Disculpá, hubo un error '
                'procesando tu mensaje.'
            )
        }), 500
