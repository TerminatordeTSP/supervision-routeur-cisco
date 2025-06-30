#!/bin/bash

# Script pour préparer le serveur distant
# Ce script vous guide pour installer Docker et configurer l'utilisateur

set -e

SERVER_HOST="supervision-server"

echo "🛠️ Préparation du serveur distant"
echo "=================================="

echo ""
echo "📋 Instructions pour préparer votre serveur:"
echo ""

echo "1️⃣ Connectez-vous à votre serveur:"
echo "   ssh user@172.16.10.40"
echo ""

echo "2️⃣ Installez Docker (si pas déjà installé):"
echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
echo "   sudo sh get-docker.sh"
echo "   rm get-docker.sh"
echo ""

echo "3️⃣ Ajoutez votre utilisateur au groupe docker:"
echo "   sudo usermod -aG docker \$USER"
echo "   newgrp docker"
echo ""

echo "4️⃣ Testez Docker:"
echo "   docker --version"
echo "   docker compose version"
echo "   docker ps"
echo ""

echo "5️⃣ Créez le répertoire de déploiement (optionnel):"
echo "   mkdir -p \$HOME/supervision-routeur-cisco"
echo ""

echo "🔧 Ou exécutez ce script automatiquement:"
echo ""

read -p "Voulez-vous exécuter ces commandes automatiquement sur le serveur ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Exécution automatique..."
    
    # Tester la connexion
    if ! ssh -o ConnectTimeout=10 "$SERVER_HOST" "echo 'Connexion OK'" > /dev/null 2>&1; then
        echo "❌ Impossible de se connecter à $SERVER_HOST"
        echo "Vérifiez votre configuration SSH"
        exit 1
    fi
    
    echo "✅ Connexion SSH établie"
    
    # Exécuter les commandes sur le serveur distant
    ssh -t "$SERVER_HOST" '
        echo "🔍 Vérification de Docker..."
        if command -v docker &> /dev/null; then
            echo "✅ Docker déjà installé"
        else
            echo "📦 Installation de Docker..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            rm get-docker.sh
            echo "✅ Docker installé"
        fi
        
        echo "👤 Configuration de l'\''utilisateur..."
        sudo usermod -aG docker $USER
        
        echo "📁 Création du répertoire de déploiement..."
        mkdir -p $HOME/supervision-routeur-cisco
        
        echo "✅ Serveur préparé!"
        echo ""
        echo "⚠️  IMPORTANT: Vous devez vous déconnecter et vous reconnecter"
        echo "   pour que les changements de groupe prennent effet:"
        echo "   exit"
        echo "   ssh supervision-server"
        echo ""
        echo "🧪 Puis testez Docker:"
        echo "   docker --version"
        echo "   docker ps"
    '
    
    echo ""
    echo "✅ Configuration terminée!"
    echo ""
    echo "🔄 Prochaines étapes:"
    echo "1. Déconnectez-vous et reconnectez-vous au serveur"
    echo "2. Testez Docker: ssh supervision-server 'docker ps'"
    echo "3. Lancez le déploiement: ./deployment/deploy_simple.sh"
    
else
    echo ""
    echo "📋 Suivez les instructions manuelles ci-dessus"
    echo "Une fois terminé, lancez: ./deployment/deploy_simple.sh"
fi
