---
marp: true
---

# Guide Sora-2 avec OpenWebUI + LiteLLM Tracking

## 🎯 Solution finale

Vous pouvez maintenant utiliser Sora-2 dans OpenWebUI **avec tracking complet des dépenses** dans le dashboard LiteLLM !

## 🏗️ Architecture

```
OpenWebUI → Adaptateur (port 8001) → LiteLLM (port 4000) → OpenAI Sora-2
                ↓                            ↓
         Conversion                    📊 Tracking & Logs
    chat → videos                      💰 Dashboard dépenses
```

## 🚀 Démarrage

### 1. Services en cours d'exécution

- ✅ **LiteLLM Proxy** : `http://localhost:4000`
- ✅ **Adaptateur Sora-2** : `http://localhost:8001`

### 2. Configuration OpenWebUI

1. Ouvrez **OpenWebUI** dans votre navigateur
2. Allez dans **Paramètres** → **Connexions**
3. Ajoutez une nouvelle connexion :
   - **Type :** OpenAI API
   - **URL :** `http://localhost:8001/v1`
   - **API Key :** `sk-anything` (n'importe quoi)
   - **Nom :** Sora-2 (LiteLLM)

4. Sélectionnez le modèle **sora-2**

### 3. Utilisation

Dans OpenWebUI, tapez simplement :
```
un chien qui court dans un parc
```

Vous recevrez un message avec :
- 🆔 Video ID
- 📊 Status de génération
- 💾 Commande pour télécharger

## 📊 Dashboard & Tracking

### Accéder au dashboard LiteLLM

Ouvrez dans votre navigateur : **http://localhost:4000/ui**

Vous y verrez :
- ✅ Toutes les requêtes Sora-2
- 💰 Coûts par requête ($0.10/seconde pour 720x1280)
- 📈 Graphiques d'usage
- 📝 Logs détaillés

## 💾 Télécharger les vidéos

Une fois la vidéo générée, téléchargez-la :

```bash
python download_video.py video_<ID>
```

Exemple :
```bash
python download_video.py video_690e148dbfb08190930a1e369ce6fc18033e3925afefb3b3
```

## ⚙️ Configuration

### Durées supportées
- "4" secondes (défaut)
- "8" secondes
- "12" secondes

### Tailles supportées
- `720x1280` (portrait) - défaut
- `1280x720` (landscape)

### Modifier les paramètres par défaut

Éditez `litellm-config.yaml` :
```yaml
- model_name: sora-2
  litellm_params:
    model: openai/sora-2
    api_key: os.environ/OPENAI_API_KEY
    seconds: "4"  # Changez ici
    size: "720x1280"  # Ou changez ici
```

Puis redémarrez :
```bash
docker restart litellm
python sora_litellm_adapter.py
```

## 🧪 Tests

### Test direct de l'adaptateur
```bash
python test_adapter.py
```

### Test LiteLLM endpoint videos
```bash
python test_litellm_videos.py
```

### Test API OpenAI directe
```bash
python test_sora_direct.py
```

## 📁 Fichiers créés

- `sora_litellm_adapter.py` - Adaptateur principal (EN COURS)
- `download_video.py` - Script de téléchargement
- `litellm-config.yaml` - Configuration LiteLLM
- `test_adapter.py` - Test de l'adaptateur
- `test_litellm_videos.py` - Test endpoint LiteLLM
- `test_sora_direct.py` - Test API OpenAI

## 💡 Avantages de cette solution

✅ **Tracking complet** - Toutes les requêtes sont trackées dans LiteLLM
✅ **Dashboard visuel** - Interface web pour voir les dépenses
✅ **Compatible OpenWebUI** - Fonctionne comme n'importe quel autre modèle
✅ **Logs centralisés** - Tous les logs au même endroit
✅ **Rate limiting** - Contrôle des limites via LiteLLM
✅ **Gestion multi-clés** - Possibilité d'ajouter plusieurs clés OpenAI

## 🔧 Dépannage

### L'adaptateur ne démarre pas
```bash
# Vérifier que le port 8001 est libre
netstat -ano | findstr :8001

# Redémarrer l'adaptateur
python sora_litellm_adapter.py
```

### LiteLLM ne répond pas
```bash
# Vérifier le statut Docker
docker ps | findstr litellm

# Redémarrer LiteLLM
docker restart litellm
```

### Pas d'accès au dashboard
Vérifiez que vous utilisez l'URL correcte : **http://localhost:4000/ui**

## 💰 Coûts

**Sora-2 Standard :** $0.10 par seconde
- 4 secondes = $0.40
- 8 secondes = $0.80
- 12 secondes = $1.20

**Sora-2 Pro :** $0.30 par seconde (meilleure qualité)

Tous les coûts sont trackés automatiquement dans le dashboard LiteLLM !

## 🎬 Exemples de prompts

```
un chat qui joue avec une pelote de laine
un coucher de soleil sur la mer
une voiture qui roule sur une route de montagne
des feuilles d'automne qui tombent au ralenti
```

## 📞 Support

- **Documentation LiteLLM :** https://docs.litellm.ai
- **Documentation Sora :** https://openai.com/sora
- **OpenWebUI :** https://github.com/open-webui/open-webui

---

✨ Profitez de Sora-2 avec un suivi complet de vos dépenses !
