"""
Sora-2 Adapter for OpenWebUI + LiteLLM
Converts chat/completion requests to video generation requests
while maintaining LiteLLM tracking!
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

# LiteLLM Configuration - Load from environment
LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY")

if not LITELLM_MASTER_KEY:
    print("WARNING: LITELLM_MASTER_KEY environment variable not set!")
    print("Please set it before running the adapter.")

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    Intercepts chat/completion requests for sora-2
    Converts them to /v1/videos requests to LiteLLM
    """
    try:
        data = request.json
        model = data.get('model', '')

        # If it's not sora-2, pass directly to LiteLLM
        if 'sora' not in model.lower():
            # Transparent proxy for other models
            response = requests.post(
                f"{LITELLM_BASE_URL}/v1/chat/completions",
                json=data,
                headers={
                    "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                    "Content-Type": "application/json"
                }
            )
            return jsonify(response.json()), response.status_code

        # For sora-2, convert to video request
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        # Extract the prompt
        prompt = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                prompt = msg.get('content')
                break

        if not prompt:
            return jsonify({"error": "No user message found"}), 400

        # Video parameters
        seconds = data.get('seconds', '4')
        size = data.get('size', '720x1280')

        print(f"🎬 Sora-2 video generation via LiteLLM")
        print(f"   Prompt: {prompt[:50]}...")
        print(f"   Duration: {seconds}s")

        # Call LiteLLM /v1/videos (with tracking!)
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
            print(f"❌ LiteLLM Error: {error_detail}")
            return jsonify(error_detail), video_response.status_code

        video_data = video_response.json()
        video_id = video_data.get('id')
        status = video_data.get('status')

        print(f"✅ Video created: {video_id}")
        print(f"📊 Tracked in LiteLLM: {LITELLM_BASE_URL}/ui")

        # Return response in chat/completion format
        response_text = f"""🎬 Sora-2 Video Generation Started

**Video ID:** `{video_id}`
**Status:** {status}
**Prompt:** {prompt}
**Duration:** {seconds}s
**Size:** {size}

⏳ Video is being processed...

To download the video once ready:
```bash
python download_video.py {video_id}
```

📊 **Cost Tracking:** {LITELLM_BASE_URL}/ui
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
        print(f"❌ LiteLLM connection error: {e}")
        return jsonify({
            "error": {
                "message": f"LiteLLM connection error: {str(e)}",
                "type": "connection_error"
            }
        }), 503

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
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
    """Transparent proxy for all other routes"""
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
    print(f"✓ Adapter running on: http://localhost:8001")
    print()
    print("📊 LiteLLM Tracking & Dashboard:")
    print(f"   👉 {LITELLM_BASE_URL}/ui")
    print()
    print("📝 OpenWebUI Configuration:")
    print("   1. Add an OpenAI connection")
    print("   2. URL: http://localhost:8001/v1")
    print("   3. API Key: anything (not validated)")
    print("   4. Model: sora-2")
    print()
    print("✨ Features:")
    print("   ✓ Complete tracking in LiteLLM")
    print("   ✓ Cost dashboard")
    print("   ✓ Centralized logs")
    print("   ✓ OpenWebUI compatible")
    print()
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=8001, debug=False)
