"""
Script pour télécharger les vidéos Sora-2 générées
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
    """Vérifie le statut d'une vidéo"""
    response = requests.get(
        f"{OPENAI_BASE_URL}/videos/{video_id}",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erreur lors de la vérification: {response.text}")
        return None

def download_video(video_id, output_path=None):
    """Télécharge une vidéo Sora-2"""

    if not OPENAI_API_KEY:
        print("❌ ERREUR: OPENAI_API_KEY non définie")
        return False

    print("=" * 60)
    print("📥 TÉLÉCHARGEMENT VIDÉO SORA-2")
    print("=" * 60)
    print()
    print(f"Video ID: {video_id}")
    print()

    # Vérifier le statut
    print("🔍 Vérification du statut...")
    status_data = check_video_status(video_id)

    if not status_data:
        return False

    status = status_data.get('status')
    print(f"   Status: {status}")

    # Si pas encore prêt, attendre
    max_wait = 300  # 5 minutes max
    start_time = time.time()

    while status in ['queued', 'processing'] and (time.time() - start_time) < max_wait:
        print(f"   ⏳ En cours... ({status})")
        time.sleep(10)
        status_data = check_video_status(video_id)
        if status_data:
            status = status_data.get('status')
            progress = status_data.get('progress', 0)
            print(f"      Progression: {progress}%")
        else:
            break

    if status != 'completed':
        print(f"❌ La vidéo n'est pas prête. Status: {status}")
        if status == 'failed':
            error = status_data.get('error', 'Unknown error')
            print(f"   Erreur: {error}")
        return False

    print("✅ Vidéo prête!")
    print()

    # Télécharger la vidéo
    print("📥 Téléchargement...")

    # L'URL de téléchargement devrait être dans la réponse
    # Selon la doc OpenAI, il peut y avoir un champ 'url' ou il faut faire une requête GET
    video_url = status_data.get('url')

    if video_url:
        # Télécharger depuis l'URL fournie
        video_response = requests.get(video_url, stream=True)
    else:
        # Essayer de télécharger directement depuis l'endpoint
        video_response = requests.get(
            f"{OPENAI_BASE_URL}/videos/{video_id}/content",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            stream=True
        )

    if video_response.status_code != 200:
        print(f"❌ Erreur de téléchargement: {video_response.status_code}")
        print(f"   {video_response.text}")
        return False

    # Sauvegarder
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
                    print(f"\r   Téléchargement: {percent:.1f}%", end='', flush=True)

    print()
    print()
    print(f"✅ Vidéo sauvegardée: {output_path}")
    print()

    # Afficher les métadonnées
    print("📊 Métadonnées:")
    print(f"   Prompt: {status_data.get('prompt')}")
    print(f"   Durée: {status_data.get('seconds')}s")
    print(f"   Taille: {status_data.get('size')}")
    print(f"   Modèle: {status_data.get('model')}")

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_video.py <video_id> [output_path]")
        print()
        print("Exemple:")
        print("  python download_video.py video_690e0c4ab8a481909e70d21d2a555dea081e3ac30545498f")
        print("  python download_video.py video_690e0c4ab8a481909e70d21d2a555dea081e3ac30545498f ma_video.mp4")
        sys.exit(1)

    video_id = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = download_video(video_id, output_path)

    print()
    print("=" * 60)

    sys.exit(0 if success else 1)
