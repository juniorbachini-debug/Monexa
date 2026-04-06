"""
Servidor Python/Flask de IA para o Monexa.
"""
import base64, sys, os, tempfile
from flask import Flask, request, jsonify
from openai import OpenAI
from anthropic import Anthropic

app = Flask(__name__)
openai_client = None
anthropic_client = None

def get_openai():
    global openai_client
    if openai_client is None:
        key = os.environ.get("OPENAI_API_KEY")
        if key: openai_client = OpenAI(api_key=key)
    return openai_client

def get_anthropic():
    global anthropic_client
    if anthropic_client is None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if key: anthropic_client = Anthropic(api_key=key)
    return anthropic_client

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "Nenhum audio enviado"}), 400
    client = get_openai()
    if not client:
        return jsonify({"error": "OPENAI_API_KEY nao configurada"}), 500
    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()
    if len(audio_bytes) < 1000:
        return jsonify({"text": ""})
    suffix = ".ogg"
    if audio_file.content_type:
        if "webm" in audio_file.content_type: suffix = ".webm"
        elif "mp4" in audio_file.content_type: suffix = ".mp4"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(model="whisper-1", file=f, language="pt")
        os.unlink(tmp_path)
        return jsonify({"text": result.text.strip() if result.text else ""})
    except Exception as e:
        print(f"Transcription error: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400
    client = get_anthropic()
    if not client:
        return jsonify({"error": "ANTHROPIC_API_KEY nao configurada"}), 500
    img_file = request.files["image"]
    img_bytes = img_file.read()
    mime_type = img_file.content_type or "image/jpeg"
    if mime_type not in ["image/jpeg","image/png","image/webp","image/gif"]:
        mime_type = "image/jpeg"
    img_b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=300,
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":mime_type,"data":img_b64}},
                {"type":"text","text":"Voce e um assistente financeiro brasileiro. Analise este comprovante e extraia: valor em reais, tipo (Despesa ou Recebimento), descricao e data. Responda em UMA linha: \"Despesa de R$ 89,90 no iFood em 04/04/2026\". Se nao for possivel ler, responda: NAO_LEGIVEL"}
            ]}]
        )
        text = message.content[0].text.strip()
        if text == "NAO_LEGIVEL": return jsonify({"error": "nao legivel"}), 422
        return jsonify({"text": text})
    except Exception as e:
        print(f"Vision error: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("SIDECAR_PORT", 5001))
    print(f"Transcription server running on port {port}")
    app.run(host="0.0.0.0", port=port)
