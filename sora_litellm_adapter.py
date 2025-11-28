"""
Adaptateur Sora-2 pour OpenWebUI + LiteLLM
Convertit les requêtes chat/completions en requêtes videos
Tout en gardant le tracking LiteLLM !
"""
import os
import sys
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
CORS(app)

# Configuration LiteLLM
LITELLM_BASE_URL = "http://localhost:4000"
LITELLM_MASTER_KEY = "sk-tabRFR7RrNGxz0kGtFoTZaHtWK5g9BgbY1z1wV1zveNq13nN0BDxNP2THax1V86h"

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    Intercepte les requêtes chat/completions pour sora-2
    Les convertit en requêtes /v1/videos vers LiteLLM
    """
    try:
        data = request.json
        model = data.get('model', '')

        # Si ce n'est pas sora-2, passer à LiteLLM directement
        if 'sora' not in model.lower():
            # Proxy transparent pour les autres modèles
            response = requests.post(
                f"{LITELLM_BASE_URL}/v1/chat/completions",
                json=data,
                headers={
                    "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                    "Content-Type": "application/json"
                }
            )
            return jsonify(response.json()), response.status_code

        # Pour sora-2, convertir en requête videos
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        # Extraire le prompt
        prompt = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                prompt = msg.get('content')
                break

        if not prompt:
            return jsonify({"error": "No user message found"}), 400

        # Paramètres vidéo
        seconds = data.get('seconds', '4')
        size = data.get('size', '720x1280')

        print(f"🎬 Génération vidéo Sora-2 via LiteLLM")
        print(f"   Prompt: {prompt[:50]}...")
        print(f"   Durée: {seconds}s")

        # Appeler LiteLLM /v1/videos (avec tracking!)
        video_response = requests.post(
            f"{LITELLM_BASE_URL}/v1/videos",
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "prompt": prompt,
                "seconds": seconds,
                "size": size
            },
            timeout=30
        )

        if video_response.status_code != 200:
            error_detail = video_response.json() if video_response.text else {"error": "Unknown error"}
            print(f"❌ Erreur LiteLLM: {error_detail}")
            return jsonify(error_detail), video_response.status_code

        video_data = video_response.json()
        video_id = video_data.get('id')
        status = video_data.get('status')

        print(f"✅ Vidéo créée: {video_id}")
        print(f"📊 Trackée dans LiteLLM: {LITELLM_BASE_URL}/ui")

        # Retourner une réponse au format chat/completions
        response_text = f"""🎬 Vidéo Sora-2 en génération

**Video ID:** `{video_id}`
**Status:** {status}
**Prompt:** {prompt}
**Durée:** {seconds}s
**Taille:** {size}

⏳ La vidéo est en cours de traitement...

Pour télécharger la vidéo une fois prête :
```bash
python download_video.py {video_id}
```

📊 **Suivi des dépenses:** {LITELLM_BASE_URL}/ui
"""

        return jsonify({
            "id": f"chatcmpl-{video_id}",
            "object": "chat.completion",
            "created": video_data.get('created_at'),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(prompt.split()) + len(response_text.split())
            },
            "video_data": video_data
        })

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à LiteLLM: {e}")
        return jsonify({
            "error": {
                "message": f"LiteLLM connection error: {str(e)}",
                "type": "connection_error"
            }
        }), 503

    except Exception as e:
        print(f"❌ Erreur: {type(e).__name__}: {e}")
        return jsonify({
            "error": {
                "message": str(e),
                "type": "internal_error"
            }
        }), 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    """Proxy transparent vers LiteLLM"""
    try:
        response = requests.get(
            f"{LITELLM_BASE_URL}/v1/models",
            headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"}
        )
        return jsonify(response.json()), response.status_code
    except:
        return jsonify({
            "object": "list",
            "data": [{"id": "sora-2", "object": "model", "owned_by": "openai"}]
        })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "adapter": "sora-litellm",
        "litellm_url": LITELLM_BASE_URL
    })

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_all(path):
    """Proxy transparent pour toutes les autres routes"""
    try:
        url = f"{LITELLM_BASE_URL}/{path}"
        response = requests.request(
            method=request.method,
            url=url,
            headers={
                "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                "Content-Type": "application/json"
            },
            json=request.json if request.is_json else None,
            params=request.args
        )
        return jsonify(response.json() if response.text else {}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SORA-2 LITELLM ADAPTER")
    print("=" * 60)
    print()
    print(f"✓ LiteLLM Backend: {LITELLM_BASE_URL}")
    print(f"✓ Adaptateur sur: http://localhost:8001")
    print()
    print("📊 Tracking & Dashboard LiteLLM:")
    print(f"   👉 {LITELLM_BASE_URL}/ui")
    print()
    print("📝 Configuration OpenWebUI:")
    print("   1. Ajoutez une connexion OpenAI")
    print("   2. URL: http://localhost:8001/v1")
    print("   3. API Key: n'importe quoi (non vérifiée)")
    print("   4. Modèle: sora-2")
    print()
    print("✨ Avantages:")
    print("   ✓ Tracking complet dans LiteLLM")
    print("   ✓ Dashboard de dépenses")
    print("   ✓ Logs centralisés")
    print("   ✓ Compatible OpenWebUI")
    print()
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=8001, debug=False)
