# 🚀 Installation et Démarrage - Supervision Routeur Cisco

## ⚡ **SOLUTION RAPIDE pour l'erreur "address already in use"**

Si vous avez cette erreur :
```
failed to bind host port for 0.0.0.0:80:172.23.0.8:80/tcp: address already in use
```

**Créez un fichier `.env` dans le dossier du projet avec :**
```env
CADDY_PORT=8001
```

**Puis relancez :**
```bash
docker compose down
docker compose up -d
```

**L'application sera alors accessible sur http://localhost:8080** ✅

---

## 📋 Prérequis

- Docker et Docker Compose installés
- Au moins 4GB de RAM disponible
- Ports disponibles (voir configuration ci-dessous)

## 🔧 Configuration des Ports

Le projet utilise plusieurs ports. Si vous avez des conflits, modifiez le fichier `.env` :

```env
CADDY_PORT=8000      # Port principal pour accéder à l'application
DJANGO_PORT=8080     # Port direct Django (optionnel)
PGADMIN_PORT=5050    # Interface PostgreSQL
INFLUXDB_PORT=8086   # Base de données métriques
TELEGRAF_PORT=57500  # Collecteur de métriques
```

### 🚨 **Si vous avez l'erreur "port already in use" :**

1. **Ouvrez le fichier `.env`**
2. **Changez le port problématique**. Par exemple :
   ```env
   CADDY_PORT=8001  # Au lieu de 8000
   ```
3. **Redémarrez les conteneurs** : `docker compose down && docker compose up -d`

## 🚀 Démarrage Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/TerminatordeTSP/supervision-routeur-cisco.git
cd supervision-routeur-cisco

# 2. Démarrer tous les services
docker compose up -d

# 3. Attendre que tout démarre (environ 1-2 minutes)
docker compose ps

# 4. Accéder à l'application à http://localhost:8000
```

## 🌐 Accès aux Services

Une fois démarré, vous pouvez accéder à :

- **� Application principale** : http://localhost:8000 (ou votre CADDY_PORT)
- **🔧 Django Admin** : http://localhost:8080/admin (ou votre DJANGO_PORT)
- **�️ pgAdmin** : http://localhost:5050 (ou votre PGADMIN_PORT)
- **📊 InfluxDB** : http://localhost:8086 (ou votre INFLUXDB_PORT)

### 🔑 Identifiants par défaut

- **pgAdmin** : 
  - Email : `admin@telecom-sudparis.eu`
  - Mot de passe : `admin`

- **InfluxDB** : 
  - Username : `admin`
  - Mot de passe : `admin123456`

## �️ Commandes Utiles

```bash
# Voir le statut des conteneurs
docker compose ps

# Voir les logs d'un service
docker compose logs router_django

# Arrêter tous les services
docker compose down

# Redémarrer un service spécifique
docker compose restart router_django

# Reconstruire et redémarrer (après modification du code)
docker compose up -d --build
```

## 🔍 Dépannage

### ❌ Erreur "port already in use"
- Modifiez le fichier `.env` pour changer le port problématique
- Ou trouvez quel processus utilise le port : `netstat -ano | findstr :80`

### ❌ Conteneur qui ne démarre pas
- Vérifiez les logs : `docker compose logs [nom-du-service]`
- Vérifiez l'espace disque disponible
- Redémarrez Docker Desktop

### ❌ Page blanche ou erreur 500
- Les migrations sont automatiques maintenant
- Attendez 1-2 minutes que tous les services démarrent
- Vérifiez : `docker compose logs router_django`

## 📁 Structure du Projet

```
supervision-routeur-cisco/
├── .env                    # Configuration des ports et variables
├── docker-compose.yml     # Configuration des services
├── Caddyfile              # Configuration du proxy web
├── router_supervisor/     # Code Django
├── telegraf/              # Configuration collecteur métriques
└── scripts/               # Scripts d'aide
```

## 🆘 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs avec `docker compose logs`
2. Vérifiez que tous les ports sont libres
3. Redémarrez Docker Desktop si nécessaire
- **Proxy :** Caddy (conteneur `caddy`)
- **Application :** Django (conteneur `router_django`)

## 🆘 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs : `docker compose logs`
2. Vérifiez les conteneurs : `docker compose ps`
3. Contactez l'équipe de développement

---

## ⚡ TL;DR (Démarrage rapide)

```bash
git clone https://github.com/TerminatordeTSP/supervision-routeur-cisco.git
cd supervision-routeur-cisco
docker compose up -d
```

➡️ Ouvrir http://localhost:8000
