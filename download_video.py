"""
Script to download generated Sora-2 videos
"""
import os
import sys
import requests
import time
import json

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"

def check_video_status(video_id):
    """Check the status of a video"""
    response = requests.get(
        f"{OPENAI_BASE_URL}/videos/{video_id}",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error checking status: {response.text}")
        return None

def download_video(video_id, output_path=None):
    """Download a Sora-2 video"""

    if not OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not set")
        return False

    print("=" * 60)
    print("📥 SORA-2 VIDEO DOWNLOAD")
    print("=" * 60)
    print()
    print(f"Video ID: {video_id}")
    print()

    # Check status
    print("🔍 Checking status...")
    status_data = check_video_status(video_id)

    if not status_data:
        return False

    status = status_data.get('status')
    print(f"   Status: {status}")

    # If not ready yet, wait
    max_wait = 300  # 5 minutes max
    start_time = time.time()

    while status in ['queued', 'processing'] and (time.time() - start_time) < max_wait:
        print(f"   ⏳ In progress... ({status})")
        time.sleep(10)
        status_data = check_video_status(video_id)
        if status_data:
            status = status_data.get('status')
            progress = status_data.get('progress', 0)
            print(f"      Progress: {progress}%")
        else:
            break

    if status != 'completed':
        print(f"❌ Video is not ready. Status: {status}")
        if status == 'failed':
            error = status_data.get('error', 'Unknown error')
            print(f"   Error: {error}")
        return False

    print("✅ Video ready!")
    print()

    # Download the video
    print("📥 Downloading...")

    # The download URL should be in the response
    # According to OpenAI docs, there may be a 'url' field or a GET request is needed
    video_url = status_data.get('url')

    if video_url:
        # Download from provided URL
        video_response = requests.get(video_url, stream=True)
    else:
        # Try to download directly from endpoint
        video_response = requests.get(
            f"{OPENAI_BASE_URL}/videos/{video_id}/content",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            stream=True
        )

    if video_response.status_code != 200:
        print(f"❌ Download error: {video_response.status_code}")
        print(f"   {video_response.text}")
        return False

    # Save file
    if not output_path:
        output_path = f"video_{video_id}.mp4"

    total_size = int(video_response.headers.get('content-length', 0))
    downloaded = 0

    with open(output_path, 'wb') as f:
        for chunk in video_response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r   Download: {percent:.1f}%", end='', flush=True)

    print()
    print()
    print(f"✅ Video saved: {output_path}")
    print()

    # Display metadata
    print("📊 Metadata:")
    print(f"   Prompt: {status_data.get('prompt')}")
    print(f"   Duration: {status_data.get('seconds')}s")
    print(f"   Size: {status_data.get('size')}")
    print(f"   Model: {status_data.get('model')}")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_video.py <video_id> [output_path]")
        print()
        print("Example:")
        print("  python download_video.py video_690e0c4ab8a481909e70d21d2a555dea081e3ac30545498f")
        print("  python download_video.py video_690e0c4ab8a481909e70d21d2a555dea081e3ac30545498f my_video.mp4")
        sys.exit(1)

    video_id = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = download_video(video_id, output_path)

    print()
    print("=" * 60)

    sys.exit(0 if success else 1)
