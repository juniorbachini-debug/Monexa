"""
Servidor Python/Flask de IA para o Monexa.
Roda na porta 5001 ao lado do Express.
Endpoints:
  POST /transcribe  — transcreve áudio (ogg/webm/mp4) → texto
  POST /analyze-image — analisa comprovante/recibo via Claude Vision → texto
  GET  /health
"""
import asyncio
import base64
import sys
import os
from flask import Flask, request, jsonify
from transcribe_audio import transcribe_audio
from anthropic import Anthropic

app = Flask(__name__)
anthropic_client = Anthropic()  # Uses ANTHROPIC_API_KEY injected by llm-api:website

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()
    media_type = audio_file.content_type or "audio/webm"

    # Normaliza para tipos suportados
    supported = ["audio/mpeg", "audio/wav", "audio/mp4", "audio/webm", "audio/ogg", "audio/flac"]
    if media_type not in supported:
        # WebM com codec opus é o padrão do MediaRecorder
        if "webm" in media_type:
            media_type = "audio/webm"
        elif "ogg" in media_type:
            media_type = "audio/ogg"
        elif "mp4" in media_type or "m4a" in media_type:
            media_type = "audio/mp4"
        else:
            media_type = "audio/webm"

    try:
        result = asyncio.run(transcribe_audio(
            audio_bytes,
            media_type=media_type,
            language="pt",  # Prioriza português
        ))
        text = result.get("text", "").strip()
        if not text:
            return jsonify({"error": "Não consegui entender o áudio"}), 422
        return jsonify({"text": text, "language": result.get("language_code", "pt")})
    except Exception as e:
        print(f"Transcription error: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    """
    Recebe uma imagem de comprovante (multipart: campo 'image') e retorna
    uma descrição textual da transação detectada.
    """
    if "image" not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    img_file = request.files["image"]
    img_bytes = img_file.read()
    mime_type = img_file.content_type or "image/jpeg"

    # Normaliza tipos comuns
    if mime_type not in ["image/jpeg", "image/png", "image/webp", "image/gif"]:
        mime_type = "image/jpeg"

    img_b64 = base64.standard_b64encode(img_bytes).decode("utf-8")

    try:
        message = anthropic_client.messages.create(
            model="claude_sonnet_4_6",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": img_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "Você é um assistente financeiro brasileiro. "
                                "Analise este comprovante ou recibo e extraia: "
                                "valor total em reais, tipo (Despesa ou Recebimento), "
                                "estabelecimento/descrição e data se visível. "
                                "Responda em UMA ÚNICA LINHA descritiva, por exemplo: "
                                "\"Despesa de R$ 89,90 no iFood em 04/04/2026\". "
                                "Se não for possível identificar um valor financeiro, "
                                "responda apenas: NAO_LEGIVEL"
                            ),
                        },
                    ],
                }
            ],
        )
        text = message.content[0].text.strip()
        if text == "NAO_LEGIVEL" or not text:
            return jsonify({"error": "Comprovante não legível"}), 422
        return jsonify({"text": text})
    except Exception as e:
        print(f"Vision error: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("TRANSCRIPTION_PORT", 5001))
    print(f"Transcription server running on port {port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
