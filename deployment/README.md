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
## Configuration de production

### Variables d'environnement

L'application utilise un fichier `docker-compose.prod.yml` optimisé pour la production avec les paramètres suivants :

- **DEBUG=False** : Désactive le mode debug Django pour afficher les pages d'erreur personnalisées
- **DJANGO_SETTINGS_MODULE=router_supervisor.prod_settings** : Utilise les paramètres de production
- Conteneurs avec restart policy `unless-stopped`
- Volumes persistants
- Health checks

Pour vérifier que l'application est en mode production :

```bash
# Vérifier que DEBUG=False
ssh supervision-server "docker exec router_django_prod env | grep DEBUG"

# Tester les pages d'erreur personnalisées
curl -I http://SERVER_IP:8080/nonexistentpage
# Doit retourner une page d'erreur personnalisée, pas la page de debug Django
```

### Utilisation du fichier de production

Le script `deploy_simple.sh` utilise automatiquement le fichier `deployment/docker-compose.prod.yml` :

```bash
# Sur le serveur distant
cd /opt/supervision-routeur-cisco
docker compose -f deployment/docker-compose.prod.yml up -d
```

## Configuration des fichiers statiques

L'application utilise **whitenoise** pour servir les fichiers statiques (CSS, JS, images) en production. Cette configuration :

- Sert les fichiers statiques directement via Django/gunicorn
- Ajoute des hashes aux noms de fichiers pour le cache-busting
- Applique une compression gzip automatique
- Gère les en-têtes de cache optimaux

Les fichiers statiques sont automatiquement collectés et traités lors du déploiement.

#### Vérifier que les fichiers statiques fonctionnent

```bash
# Tester l'accès aux fichiers CSS
curl -I http://SERVER_IP:8080/static/dashboard_app/style.css

# Doit retourner HTTP/1.1 200 OK
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

### Résolution de problèmes

#### Problèmes avec les fichiers statiques

Si les styles CSS ne s'affichent pas correctement :

```bash
# 1. Vérifier que whitenoise est installé
ssh supervision-server "docker exec router_django_prod pip show whitenoise"

# 2. Vérifier l'accès aux fichiers statiques
curl -I http://SERVER_IP:8080/static/dashboard_app/style.css

# 3. Recollect les fichiers statiques
ssh supervision-server "docker exec router_django_prod bash -c 'cd router_supervisor && python3 manage.py collectstatic --noinput'"

# 4. Redémarrer le conteneur Django
ssh supervision-server "cd supervision-routeur-cisco && docker compose -f deployment/docker-compose.prod.yml restart router_django_prod"
```

#### Vérifier les logs

```bash
# Logs de l'application Django
ssh supervision-server "cd supervision-routeur-cisco && docker compose -f deployment/docker-compose.prod.yml logs router_django_prod"

# Logs de tous les services
ssh supervision-server "cd supervision-routeur-cisco && docker compose -f deployment/docker-compose.prod.yml logs"
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
