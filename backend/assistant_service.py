import os, time, logging, base64
from typing import Optional, List, Dict, Any
from flask import Flask, request, jsonify
from openai import OpenAI, APIStatusError, RateLimitError, AuthenticationError, APIConnectionError, OpenAIError

# ================== CONFIG BÁSICA ==================
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")          # asst_VWAsSMQML3yPqXnNDlK1frH1
if not ASSISTANT_ID:
    raise RuntimeError("Falta OPENAI_ASSISTANT_ID")
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Falta OPENAI_API_KEY")

POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "0.6"))
MAX_WAIT_MESSAGES = float(os.getenv("MAX_WAIT_MESSAGES", "2.0"))
RETRY_ON_FORMAT = os.getenv("RETRY_ON_FORMAT", "true").lower() == "true"
MAX_IMAGE_BYTES = 1_500_000

# Si quieres validar formato (ej. dos líneas) ponlo aquí:
VALIDATE_FORMAT = False  # pon True si luego deseas validar

client = OpenAI()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ================== HELPERS ==================

def decode_image_if_present(image_b64: Optional[str]):
    if not image_b64:
        return
    try:
        raw = base64.b64decode(image_b64, validate=True)
    except Exception:
        raise ValueError("BAD_IMAGE_BASE64")
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValueError("IMAGE_TOO_LARGE")

def build_parts(text: str, image_b64: Optional[str], mode: str) -> List[Dict[str, Any]]:
    """
    mode = 'legacy'  -> input_text / input_image
    mode = 'modern'  -> text / image_url (data URL)
    """
    parts: List[Dict[str, Any]] = []
    if text:
        if mode == "legacy":
            parts.append({"type": "input_text", "text": text})
        else:
            parts.append({"type": "text", "text": text})
    if image_b64:
        if mode == "legacy":
            parts.append({"type": "input_image", "image_base64": image_b64})
        else:
            parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
    return parts

def create_user_message_with_fallback(thread_id: str, text: str, image_b64: Optional[str]):
    """
    Intenta primero con modo 'legacy'. Si la API responde 400 indicando que
    los tipos válidos son 'text'/'image_url', reintenta en modo 'modern'.
    """
    # 1er intento legacy
    mode = "legacy"
    try:
        parts = build_parts(text, image_b64, mode)
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=parts
        )
        return mode
    except APIStatusError as e:
        emsg = str(e)
        if "Supported values are: 'text'" in emsg or "Supported values are: 'text'," in emsg:
            # reintentar moderno
            mode = "modern"
            parts2 = build_parts(text, image_b64, mode)
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=parts2
            )
            return mode
        raise

def poll_run(thread_id: str, run_id: str):
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ("queued", "in_progress", "cancelling"):
            time.sleep(POLL_INTERVAL)
            continue
        return run

def fetch_assistant_text(thread_id: str, wait_seconds: float = MAX_WAIT_MESSAGES) -> Optional[str]:
    """
    Poll corto para esperar a que el mensaje aparezca en el thread
    (algunas veces llega una fracción después del estado 'completed').
    Acepta partes 'output_text' o 'text'.
    """
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        msgs = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in msgs.data:
            if m.role == "assistant":
                collected = []
                for part in m.content:
                    # Nuevos (output_text) o antiguos (text)
                    if part.type == "output_text" and hasattr(part, "text"):
                        collected.append(part.text.value)
                    elif part.type == "text" and hasattr(part, "text"):
                        collected.append(part.text.value)
                if collected:
                    return "\n".join(collected).strip()
        time.sleep(0.25)
    return None

def format_invalid(raw: str) -> bool:
    if not VALIDATE_FORMAT:
        return False
    # EJEMPLO de validación real si la activas:
    # return not re.match(r"^Incidente:\s?.+\nDescripción:\s?.+", raw, re.S)
    return False  # por ahora desactivado

def maybe_retry_format(thread_id: str, assistant_id: str, previous_output: str):
    """
    Si quieres reforzar el formato SIN cambiar tu Assistant base.
    Solo se ejecuta si VALIDATE_FORMAT está True y RETRY_ON_FORMAT True.
    """
    if not (VALIDATE_FORMAT and RETRY_ON_FORMAT and format_invalid(previous_output)):
        return previous_output, False

    run2 = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        additional_instructions="Corrige el formato. Devuelve exactamente las dos líneas requeridas sin texto adicional."
    )
    run2 = poll_run(thread_id, run2.id)
    if run2.status != "completed":
        return previous_output, False
    fixed = fetch_assistant_text(thread_id)
    if fixed and not format_invalid(fixed):
        return fixed, True
    return previous_output, False

# ================== ENDPOINT ==================

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True) or {}
    user_text = (data.get("input") or "").strip()
    image_b64 = data.get("image")
    user_id = data.get("user_id")

    if not user_text and not image_b64:
        return jsonify({"error": "EMPTY_INPUT", "message": "Falta 'input' o 'image'"}), 400

    # Validar imagen si se manda
    if image_b64:
        try:
            decode_image_if_present(image_b64)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

    try:
        # 1. Thread
        thread = client.beta.threads.create()

        # 2. Mensaje usuario (con fallback tipos)
        mode_used = create_user_message_with_fallback(
            thread_id=thread.id,
            text=user_text or "[Imagen sin texto]",
            image_b64=image_b64
        )

        # 3. Run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
            # puedes agregar: additional_instructions="(algo muy corto puntual)"
        )
        run = poll_run(thread.id, run.id)

        # Manejo básico de estados especiales
        if run.status == "requires_action":
            return jsonify({"error": "REQUIRES_ACTION", "details": run.required_action}), 501
        if run.status != "completed":
            return jsonify({
                "error": "RUN_NOT_COMPLETED",
                "status": run.status,
                "last_error": getattr(run, "last_error", None)
            }), 500

        # 4. Obtener salida
        raw = fetch_assistant_text(thread.id)
        if raw is None:
            return jsonify({"error": "NO_OUTPUT"}), 500

        # 5. (Opcional) Retry formato
        fixed_output, retried = maybe_retry_format(thread.id, ASSISTANT_ID, raw)

        app.logger.info({
            "event": "assistant_reply",
            "thread_id": thread.id,
            "run_id": run.id,
            "mode_used": mode_used,
            "retried_format": retried,
            "output_len": len(fixed_output),
            "user_id": user_id
        })

        return jsonify({
            "assistant_id": ASSISTANT_ID,
            "thread_id": thread.id,
            "run_id": run.id,
            "mode_used": mode_used,
            "retried_format": retried,
            "output": fixed_output,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    except RateLimitError as e:
        return jsonify({"error": "RATE_LIMIT", "message": str(e)}), 429
    except AuthenticationError as e:
        return jsonify({"error": "AUTH_ERROR", "message": str(e)}), 401
    except APIConnectionError as e:
        return jsonify({"error": "UPSTREAM_CONNECTION", "message": str(e)}), 502
    except APIStatusError as e:
        status = e.status_code or 500
        return jsonify({
            "error": "OPENAI_API_STATUS",
            "status_code": status,
            "message": str(e)
        }), (400 if status == 400 else 502)
    except OpenAIError as e:
        return jsonify({"error": "OPENAI_GENERIC", "message": str(e)}), 502
    except Exception as e:
        app.logger.exception("INTERNAL_ERROR")
        return jsonify({"error": "INTERNAL_ERROR", "message": str(e)}), 500

@app.route("/healthz")
def healthz():
    return {"status": "ok"}

@app.route("/meta")
def meta():
    return {
        "assistant_id": ASSISTANT_ID,
        "validate_format": VALIDATE_FORMAT,
        "retry_on_format": RETRY_ON_FORMAT,
        "poll_interval": POLL_INTERVAL
    }

if __name__ == "__main__":
    print(">>> Usando Assistant puro:", ASSISTANT_ID)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
