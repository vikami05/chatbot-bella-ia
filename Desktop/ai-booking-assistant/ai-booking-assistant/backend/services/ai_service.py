import json
import requests
from prompts.system_prompt import SYSTEM_PROMPT, EXTRACTION_PROMPT

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


class AIService:

    def __init__(self):
        pass

    def call_ollama(self, prompt: str) -> str:
        """Hace llamada a Ollama local"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        result = response.json()

        return result.get("response", "").strip()

    def clean_json_response(self, text: str) -> str:
        """Limpia respuestas rotas típicas de LLM"""

        if not text:
            return "{}"

        # remover markdown
        if "```" in text:

            parts = text.split("```")

            for part in parts:

                part = part.strip()

                if part.startswith("{"):
                    text = part
                    break

        # encontrar primer y último {}
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            text = text[start:end]

        # limpiezas comunes
        text = text.replace("(no disponible)", "")
        text = text.replace("'", '"')

        return text.strip()

    def build_conversation_history(self, context: dict = None) -> str:
        """Construye historial conversacional"""

        if not context:
            return ""

        history = context.get("history", [])

        if not history:
            return ""

        conversation = ""

        for msg in history:

            role = msg.get("role", "")
            content = msg.get("content", "")

            if not content:
                continue

            if role == "user":
                conversation += f"Usuario: {content}\n"

            elif role == "assistant":
                conversation += f"Asistente: {content}\n"

        return conversation

    def process_message(self, user_message: str, context: dict = None) -> dict:

        try:

            # =========================
            # HISTORIAL
            # =========================

            conversation_history = self.build_conversation_history(context)

            # =========================
            # CONTEXTO ESTRUCTURADO
            # =========================

            structured_context = ""

            if context:

                structured_data = {
                    key: value
                    for key, value in context.items()
                    if key != "history"
                }

                if structured_data:
                    structured_context = json.dumps(
                        structured_data,
                        ensure_ascii=False,
                        indent=2
                    )

            # =========================
            # RESPUESTA DEL ASISTENTE
            # =========================

            prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO ACTUAL:
{structured_context}

HISTORIAL DE CONVERSACIÓN:
{conversation_history}

ÚLTIMO MENSAJE DEL USUARIO:
Usuario: {user_message}

INSTRUCCIONES IMPORTANTES:
- Recordá información previa
- No reinicies la conversación
- Si el usuario ya eligió servicio, recordalo
- Si ya dio fecha u horario, recordalo
- Si solo falta el nombre, pedilo
- Si ya tenés todos los datos, confirmá la reserva
- Respondé de forma natural y breve

Asistente:
"""

            assistant_response = self.call_ollama(prompt)

            # fallback simple
            if not assistant_response:

                assistant_response = (
                    "Disculpá, no pude responder correctamente 😅"
                )

            # =========================
            # EXTRACCIÓN ESTRUCTURADA
            # =========================

            extraction_prompt = f"""
{EXTRACTION_PROMPT}

CONTEXTO ACTUAL:
{structured_context}

HISTORIAL:
{conversation_history}

MENSAJE ACTUAL:
{user_message}

RESPUESTA DEL ASISTENTE:
{assistant_response}

IMPORTANTE:
- Respondé SOLO JSON válido
- No expliques nada
- No uses markdown
- No agregues comentarios
- No uses texto como "(no disponible)"
- Si falta un dato, no lo incluyas
- Nunca inventes servicios
- Usá el historial para entender contexto
- Si el usuario ya mencionó un servicio antes, conservá ese servicio
- Si el usuario ya mencionó fecha/hora antes, conservá esos datos
"""

            extracted_text = self.call_ollama(extraction_prompt)

            print("\n========== RAW JSON RESPONSE ==========")
            print(extracted_text)
            print("=======================================\n")

            # =========================
            # LIMPIAR JSON
            # =========================

            cleaned_json = self.clean_json_response(extracted_text)

            print("\n========== CLEANED JSON ==========")
            print(cleaned_json)
            print("==================================\n")

            # =========================
            # PARSEAR JSON
            # =========================

            try:

                extracted_data = json.loads(cleaned_json)

            except json.JSONDecodeError as json_error:

                print("\n========== JSON ERROR ==========")
                print(json_error)
                print("================================\n")

                extracted_data = {
                    "intent": "unknown",
                    "data": {}
                }

            # =========================
            # RESPUESTA FINAL
            # =========================

            return {
                "response": assistant_response,
                "intent": extracted_data.get("intent", "unknown"),
                "extracted_data": extracted_data.get("data", {})
            }

        except Exception as e:

            print("\n========== ERROR OLLAMA ==========")
            print(e)
            print("==================================\n")

            return {
                "response": "Disculpá, no pude procesar tu mensaje 😅",
                "intent": "unknown",
                "extracted_data": {}
            }
