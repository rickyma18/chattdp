import os
import time
import logging
import base64
from typing import Optional, List, Dict, Any

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from openai import (
    OpenAI,
    APIStatusError,
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
    OpenAIError,
)

# ================== CONFIG BÁSICA ==================
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
if not ASSISTANT_ID:
    raise RuntimeError("Falta OPENAI_ASSISTANT_ID")
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("Falta OPENAI_API_KEY")

POLL_INTERVAL     = float(os.getenv("POLL_INTERVAL",     "0.6"))
MAX_WAIT_MESSAGES = float(os.getenv("MAX_WAIT_MESSAGES", "2.0"))
MAX_IMAGE_BYTES   = 1_500_000
VALIDATE_FORMAT   = False
RETRY_ON_FORMAT   = os.getenv("RETRY_ON_FORMAT","true").lower() == "true"

# ================== APP & CORS ==================
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
client = OpenAI()

# Para depuración abrimos CORS a todo el mundo. 
# Luego en producción vuelve a poner tu dominio en lugar de "*".
CORS(
    app,
    resources={r"/generate": {"origins": "*"}},
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# Garantiza que todas las respuestas devuelvan los headers CORS
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "POST,OPTIONS"
    return response

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

def build_parts(text: str, image_b64: Optional[str], mode: str) -> List[Dict[str,Any]]:
    parts: List[Dict[str,Any]] = []
    if text:
        parts.append({
            "type": "input_text" if mode=="legacy" else "text",
            "text": text
        })
    if image_b64:
        if mode=="legacy":
            parts.append({
                "type":"input_image",
                "image_base64": image_b64
            })
        else:
            parts.append({
                "type":"image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
            })
    return parts

def create_user_message_with_fallback(thread_id: str, text: str, image_b64: Optional[str]):
    mode = "legacy"
    try:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=build_parts(text, image_b64, mode)
        )
        return mode
    except APIStatusError as e:
        if "Supported values are: 'text'" in str(e):
            mode = "modern"
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=build_parts(text, image_b64, mode)
            )
            return mode
        raise

def poll_run(thread_id: str, run_id: str):
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ("queued","in_progress","cancelling"):
            time.sleep(POLL_INTERVAL)
            continue
        return run

def fetch_assistant_text(thread_id: str, wait_seconds: float = MAX_WAIT_MESSAGES) -> Optional[str]:
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        msgs = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in msgs.data:
            if m.role=="assistant":
                collected = []
                for part in m.content:
                    if part.type in ("output_text","text") and hasattr(part,"text"):
                        collected.append(part.text.value)
                if collected:
                    return "\n".join(collected).strip()
        time.sleep(0.25)
    return None

def maybe_retry_format(thread_id: str, assistant_id: str, prev: str):
    return prev, False

# ================== ENDPOINT ==================
@app.route("/generate", methods=["POST", "OPTIONS"])
def generate():
    # Responde tú mismo al preflight
    if request.method == "OPTIONS":
        return make_response("", 200)

    # → aquí va tu lógica habitual de POST
    data      = request.get_json(force=True) or {}
    user_text = (data.get("input") or "").strip()
    image_b64 = data.get("image")
    user_id   = data.get("user_id")

    if not user_text and not image_b64:
        return jsonify({"error":"EMPTY_INPUT","message":"Falta 'input' o 'image'"}), 400

    if image_b64:
        try: decode_image_if_present(image_b64)
        except ValueError as ve:
            return jsonify({"error":str(ve)}), 400

    try:
        thread    = client.beta.threads.create()
        mode_used = create_user_message_with_fallback(thread.id, user_text or "[Imagen sin texto]", image_b64)
        run       = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
        run       = poll_run(thread.id, run.id)

        if run.status != "completed":
            return jsonify({"error":"RUN_NOT_COMPLETED","status":run.status}), 500

        raw = fetch_assistant_text(thread.id)
        if raw is None:
            return jsonify({"error":"NO_OUTPUT"}), 500

        output, retried = maybe_retry_format(thread.id, ASSISTANT_ID, raw)

        logging.info({
            "event":"assistant_reply",
            "thread_id":thread.id,
            "run_id":run.id,
            "mode_used":mode_used,
            "output_len":len(output),
            "user_id":user_id
        })

        return jsonify({
            "assistant_id": ASSISTANT_ID,
            "thread_id": thread.id,
            "run_id": run.id,
            "mode_used": mode_used,
            "retried_format": retried,
            "output": output,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    except RateLimitError as e:
        return jsonify({"error":"RATE_LIMIT","message":str(e)}), 429
    except AuthenticationError as e:
        return jsonify({"error":"AUTH_ERROR","message":str(e)}), 401
    except APIConnectionError as e:
        return jsonify({"error":"UPSTREAM_CONNECTION","message":str(e)}), 502
    except APIStatusError as e:
        code = 400 if (e.status_code or 500)==400 else 502
        return jsonify({"error":"OPENAI_API_STATUS","message":str(e)}), code
    except OpenAIError as e:
        return jsonify({"error":"OPENAI_GENERIC","message":str(e)}), 502
    except Exception as e:
        logging.exception("INTERNAL_ERROR")
        return jsonify({"error":"INTERNAL_ERROR","message":str(e)}), 500

@app.route("/healthz")
def healthz():
    return {"status":"ok"}

@app.route("/meta")
def meta():
    return {
        "assistant_id": ASSISTANT_ID,
        "validate_format": VALIDATE_FORMAT,
        "retry_on_format": RETRY_ON_FORMAT,
        "poll_interval": POLL_INTERVAL
    }

if __name__ == "__main__":
    print(">>> Usando Assistant:", ASSISTANT_ID)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","8080")))
