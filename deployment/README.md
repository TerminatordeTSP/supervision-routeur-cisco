# Guide de déploiement - Supervision Routeur Cisco

Ce guide vous explique comment déployer l'application de supervision de routeur Cisco sur un serveur distant.

## Prérequis

- Serveur Linux (Ubuntu/Debian recommandé)
- Accès SSH au serveur
- Docker et Docker Compose installés (ou script les installera)
- Git installé localement

## Configuration initiale

### 1. Configurer la clé de déploiement

Exécutez le script de configuration :

```bash
chmod +x deployment/setup_deploy_key.sh
./deployment/setup_deploy_key.sh
```

Ce script va :
- Générer une clé SSH dédiée au déploiement
- Afficher la clé publique à copier
- Créer la configuration SSH

### 2. Configurer le serveur distant

1. Copiez la clé publique affichée par le script
2. Connectez-vous à votre serveur
3. Ajoutez la clé à `~/.ssh/authorized_keys` :

```bash
# Sur le serveur distant
echo "VOTRE_CLE_PUBLIQUE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Modifier la configuration SSH

Éditez le fichier `~/.ssh/config` et remplacez :
- `YOUR_SERVER_IP` par l'IP de votre serveur
- `YOUR_USERNAME` par votre nom d'utilisateur

```
Host supervision-server
    HostName YOUR_SERVER_IP
    User YOUR_USERNAME
    IdentityFile /home/paul/.ssh/supervision_routeur_deploy
    IdentitiesOnly yes
    StrictHostKeyChecking no
```

### 4. Tester la connexion

```bash
ssh supervision-server
```

## Déploiement

### Déploiement complet

```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### Options de déploiement

```bash
# Préparer seulement le serveur (installer Docker, etc.)
./deployment/deploy.sh --prepare-only

# Synchroniser les fichiers seulement
./deployment/deploy.sh --sync-only

# Déployer seulement (sans sync)
./deployment/deploy.sh --deploy-only
```

## Configuration de production

### Variables d'environnement

Copiez et modifiez le fichier de configuration :

```bash
cp deployment/deploy.conf.example deployment/deploy.conf
```

Éditez `deployment/deploy.conf` avec vos valeurs.

### Docker Compose de production

Le fichier `deployment/docker-compose.prod.yml` contient une configuration optimisée pour la production avec :
- Restart automatique des conteneurs
- Logs limités
- Volumes persistants
- Health checks

Pour l'utiliser :

```bash
# Sur le serveur distant
cd /opt/supervision-routeur-cisco
docker compose -f deployment/docker-compose.prod.yml up -d
```

## Sauvegarde

### Script de sauvegarde

```bash
# Exécuter une sauvegarde
./deployment/backup.sh
```

### Sauvegarde automatique

Ajoutez une tâche cron pour la sauvegarde automatique :

```bash
# Sur le serveur distant
crontab -e

# Ajouter cette ligne pour une sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/supervision-routeur-cisco/deployment/backup.sh
```

## Services déployés

Après le déploiement, les services suivants seront disponibles :

- **Application web** : `http://SERVER_IP/`
- **InfluxDB** : `http://SERVER_IP:8086/`
- **PgAdmin** : `http://SERVER_IP:5050/`

## Résolution de problèmes

### Vérifier le statut des conteneurs

```bash
ssh supervision-server "cd /opt/supervision-routeur-cisco && docker compose ps"
```

### Voir les logs

```bash
ssh supervision-server "cd /opt/supervision-routeur-cisco && docker compose logs -f [SERVICE_NAME]"
```

### Redémarrer un service

```bash
ssh supervision-server "cd /opt/supervision-routeur-cisco && docker compose restart [SERVICE_NAME]"
```

### Mise à jour

Pour mettre à jour l'application :

```bash
# Faire vos modifications localement
git add .
git commit -m "Vos modifications"

# Redéployer
./deployment/deploy.sh
```

## Sécurité

### Recommandations

1. **Changez les mots de passe par défaut** dans le fichier de configuration
2. **Configurez un firewall** pour limiter l'accès aux ports
3. **Utilisez HTTPS** en production (configurez Caddy avec un certificat SSL)
4. **Surveillez les logs** régulièrement
5. **Mettez à jour** Docker et les images régulièrement

### Ports utilisés

- `80` : Interface web (HTTP)
- `443` : Interface web (HTTPS)
- `5050` : PgAdmin
- `8086` : InfluxDB
- `57500` : Telegraf

## Support

En cas de problème :

1. Vérifiez les logs des conteneurs
2. Vérifiez la configuration réseau
3. Testez la connectivité SSH
4. Consultez la documentation Docker Compose
