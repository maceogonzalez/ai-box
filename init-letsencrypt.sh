#!/bin/bash

# Configuration - MODIFIEZ CES VALEURS
domains=(monollama.duckdns.org)  # Votre domaine DuckDNS (sans www)
email="maceogonzalez2001@gmail.com"  # Email pour Let's Encrypt
staging=0  # Mettez à 1 pour tester avec l'environnement de staging

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Initialisation des certificats Let's Encrypt ===${NC}\n"

# Vérifications
if [ -d "./certbot/conf/live/${domains[0]}" ]; then
  echo -e "${YELLOW}Les certificats existent déjà pour ${domains[0]}${NC}"
  read -p "Voulez-vous les remplacer ? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

# Créer les dossiers nécessaires
echo -e "${GREEN}Création des dossiers...${NC}"
mkdir -p "./certbot/conf"
mkdir -p "./certbot/www"

# Télécharger les paramètres SSL recommandés
echo -e "${GREEN}Téléchargement des paramètres SSL recommandés...${NC}"
if [ ! -f "./certbot/conf/options-ssl-nginx.conf" ] || [ ! -f "./certbot/conf/ssl-dhparams.pem" ]; then
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "./certbot/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "./certbot/conf/ssl-dhparams.pem"
fi

# Créer un certificat dummy temporaire
echo -e "${GREEN}Création d'un certificat temporaire pour ${domains[0]}...${NC}"
path="/etc/letsencrypt/live/${domains[0]}"
mkdir -p "./certbot/conf/live/${domains[0]}"

docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:4096 -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" certbot

# Démarrer Nginx
echo -e "${GREEN}Démarrage de Nginx...${NC}"
docker-compose up --force-recreate -d nginx

# Supprimer le certificat dummy
echo -e "${GREEN}Suppression du certificat temporaire...${NC}"
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/${domains[0]} && \
  rm -Rf /etc/letsencrypt/archive/${domains[0]} && \
  rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot

# Demander le vrai certificat
echo -e "${GREEN}Demande du certificat SSL pour ${domains[*]}...${NC}"

# Construire la commande avec tous les domaines
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Choisir l'environnement (staging ou production)
if [ $staging != "0" ]; then
  staging_arg="--staging"
  echo -e "${YELLOW}Mode STAGING activé (certificats de test)${NC}"
else
  staging_arg=""
fi

# Obtenir le certificat
docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $domain_args \
    --email $email \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal \
    --non-interactive" certbot

# Recharger Nginx
echo -e "${GREEN}Rechargement de Nginx...${NC}"
docker-compose exec nginx nginx -s reload

echo -e "\n${GREEN}=== Configuration terminée ! ===${NC}"
echo -e "${GREEN}Votre site est maintenant accessible en HTTPS${NC}"
echo -e "URL: ${GREEN}https://${domains[0]}${NC}\n"