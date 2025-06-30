#!/bin/bash

# Script pour configurer une clé de déploiement SSH
# Ce script génère une clé SSH dédiée au déploiement

set -e

echo "🔑 Configuration de la clé de déploiement..."

# Variables
DEPLOY_KEY_NAME="supervision_routeur_deploy"
DEPLOY_KEY_PATH="$HOME/.ssh/${DEPLOY_KEY_NAME}"
DEPLOY_KEY_PUB_PATH="${DEPLOY_KEY_PATH}.pub"

# Créer le répertoire .ssh s'il n'existe pas
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

# Générer la clé SSH si elle n'existe pas déjà
if [[ ! -f "$DEPLOY_KEY_PATH" ]]; then
    echo "📝 Génération de la clé SSH de déploiement..."
    ssh-keygen -t ed25519 -f "$DEPLOY_KEY_PATH" -N "" -C "deploy-key-supervision-routeur-$(date +%Y%m%d)"
    chmod 600 "$DEPLOY_KEY_PATH"
    chmod 644 "$DEPLOY_KEY_PUB_PATH"
    echo "✅ Clé SSH générée: $DEPLOY_KEY_PATH"
else
    echo "ℹ️ Clé SSH de déploiement existe déjà: $DEPLOY_KEY_PATH"
fi

# Afficher la clé publique
echo ""
echo "🔓 Clé publique à ajouter au serveur distant:"
echo "================================================"
cat "$DEPLOY_KEY_PUB_PATH"
echo "================================================"
echo ""

# Créer/mettre à jour le fichier de configuration SSH
SSH_CONFIG="$HOME/.ssh/config"
CONFIG_ENTRY="
# Configuration pour le déploiement supervision-routeur
Host supervision-server
    HostName 172.16.10.40
    User user
    IdentityFile $DEPLOY_KEY_PATH
    IdentitiesOnly yes
    StrictHostKeyChecking no
"

# Vérifier si la configuration existe déjà
if ! grep -q "Host supervision-server" "$SSH_CONFIG" 2>/dev/null; then
    echo "📝 Ajout de la configuration SSH..."
    echo "$CONFIG_ENTRY" >> "$SSH_CONFIG"
    chmod 600 "$SSH_CONFIG"
    echo "✅ Configuration SSH ajoutée"
else
    echo "ℹ️ Configuration SSH existe déjà"
fi

echo ""
echo "📋 Prochaines étapes:"
echo "1. Copiez la clé publique ci-dessus"
echo "2. Ajoutez-la au fichier ~/.ssh/authorized_keys sur votre serveur"
echo "3. Modifiez la configuration SSH dans $SSH_CONFIG"
echo "   - Remplacez YOUR_SERVER_IP par l'IP de votre serveur"
echo "   - Remplacez YOUR_USERNAME par votre nom d'utilisateur"
echo "4. Testez la connexion: ssh supervision-server"
echo "5. Exécutez le script de déploiement: ./deployment/deploy.sh"
