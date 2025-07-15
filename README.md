# Router Cisco Supervision - Guide d'installation et d'utilisation

Ce projet permet de surveiller et d'afficher les métriques d'un routeur Cisco. Il collecte les données via Telegraf, les stocke dans InfluxDB et PostgreSQL, et les affiche sur un tableau de bord Django avec interface d'administration.

## 🚀 Installation automatique (Recommandé)

### Pour Windows :
```batch
# Cloner le projet
git clone https://github.com/TerminatordeTSP/supervision-routeur-cisco.git
cd supervision-routeur-cisco

# Lancer l'installation automatique
install.bat
```

### Pour Linux/macOS :
```bash
# Cloner le projet
git clone https://github.com/TerminatordeTSP/supervision-routeur-cisco.git
cd supervision-routeur-cisco

# Rendre le script exécutable
chmod +x install.sh

# Lancer l'installation automatique
./install.sh
```

### Installation manuelle rapide :
```bash
# Alternative simple
docker-compose up --build
```

## ✨ Qu'est-ce que l'installation automatique fait ?

1. **Vérification des prérequis** : Docker et Docker Compose
2. **Nettoyage automatique** : Suppression des anciens conteneurs
3. **Configuration automatique** : Création du fichier `.env` avec les valeurs par défaut
4. **Migrations automatiques** : Initialisation de la base de données
5. **Création du superutilisateur** : admin/admin123
6. **Démarrage des services** : Tous les conteneurs sont lancés
7. **Vérification de santé** : Statut des services

## 🎯 Accès immédiat après installation

- **Dashboard principal** : http://localhost:8080/
- **Page Settings** : http://localhost:8080/settings/
- **Page Alertes** : http://localhost:8080/alertes/
- **Page Thresholds** : http://localhost:8080/thresholds/
- **InfluxDB** : http://localhost:8086/
- **pgAdmin** : http://localhost:5050/

**Compte administrateur** : `admin` / `admin123`

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django App    │───▶│   PostgreSQL    │◀───│    pgAdmin      │
│   Port: 8080    │    │   Port: 5432    │    │   Port: 5050    │
│  (Gunicorn)     │    │  (Base données) │    │ (Administration)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │
        ▼                       │
┌─────────────────┐              │
│    InfluxDB     │              │
│   Port: 8086    │              │
│   (Métriques)   │              │
└─────────────────┘              │
        ▲                       │
        │                       │
┌─────────────────┐              │
│    Telegraf     │              │
│   Port: 57500   │              │
│  (Collecteur)   │              │
└─────────────────┘              │
                                │
┌─────────────────┐              │
│     Caddy       │              │
│   Ports: 80/443 │              │
│ (Reverse Proxy) │              │
└─────────────────┘──────────────┘
```

## 🚀 Modes de déploiement

### 1. **Mode Développement** (Recommandé pour tests)
- Docker Compose avec hot-reload
- Base de données SQLite locale ou PostgreSQL
- Debug activé

### 2. **Mode Production** 
- Docker Compose optimisé
- PostgreSQL obligatoire
- Reverse proxy Caddy
- Logs structurés
- Health checks

## 📋 Prérequis

- **Docker & Docker Compose** (obligatoire)
- **Python 3.9+** (pour développement local uniquement)
- **Accès réseau** au routeur Cisco à superviser

## 🔧 Installation et Déploiement

### **Option A : Déploiement Development (Docker Compose)**

1. **Cloner le projet :**
   ```bash
   git clone https://github.com/votre-utilisateur/supervision-routeur-cisco.git
   cd supervision-routeur-cisco
   ```

2. **Démarrer tous les services :**
   ```bash
   docker-compose up -d --build
   ```

3. **Vérifier que tous les conteneurs fonctionnent :**
   ```bash
   docker-compose ps
   ```

4. **Créer un superutilisateur Django :**
   ```bash
   docker-compose exec router_django python3 router_supervisor/manage.py createsuperuser
   ```

### **Option B : Déploiement Production**

1. **Utiliser la configuration production :**
   ```bash
   cd deployment/
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **Services et ports en production :**
   - **Application Django** : http://localhost:8080
   - **pgAdmin** : http://localhost:5050
   - **InfluxDB** : http://localhost:8086
   - **Caddy (HTTP)** : http://localhost:80
   - **Caddy (HTTPS)** : https://localhost:443

## 🗃️ Base de Données PostgreSQL

### **Configuration automatique**
L'application détecte automatiquement l'environnement :
- **Docker/Production** : PostgreSQL (si variable `SQL_HOST` présente)
- **Développement local** : SQLite (par défaut)

### **Paramètres de connexion PostgreSQL :**
| Paramètre | Valeur | Description |
|-----------|---------|-------------|
| **Host** | `db` | Nom du service Docker |
| **Port** | `5432` | Port PostgreSQL standard |
| **Database** | `routerdb` | Base de données principale |
| **Username** | `user` | Utilisateur PostgreSQL |
| **Password** | `password` | Mot de passe (⚠️ À changer en production) |

### **Migrations Django :**
```bash
# Appliquer les migrations
docker-compose exec router_django python3 router_supervisor/manage.py migrate

# Créer de nouvelles migrations (si modification des modèles)
docker-compose exec router_django python3 router_supervisor/manage.py makemigrations

# Vérifier l'état des migrations
docker-compose exec router_django python3 router_supervisor/manage.py showmigrations
```

## 🔧 Administration avec pgAdmin

### **Accès à pgAdmin :**
- **URL** : http://localhost:5050
- **Email** : `admin@telecom-sudparis.eu`
- **Mot de passe** : `admin`

### **Configurer la connexion PostgreSQL dans pgAdmin :**

1. **Clic droit sur "Servers" → "Register" → "Server"**

2. **Onglet "General" :**
   - **Name** : `Router Database`
   - **Description** : `PostgreSQL supervision routeur`

3. **Onglet "Connection" :**
   - **Host name/address** : `db`
   - **Port** : `5432`
   - **Maintenance database** : `routerdb`
   - **Username** : `user`
   - **Password** : `password`
   - ✅ **Save password** : Coché

## 📊 Monitoring et Métriques

### **InfluxDB (Métriques temporelles) :**
- **URL** : http://localhost:8086
- **Organisation** : `telecom-sudparis`
- **Bucket** : `router-metrics`
- **Token** : `my-super-secret-auth-token`

### **Telegraf (Collecteur de données) :**
- **Port d'écoute** : `57500`
- **Configuration** : `telegraf/telegraf.conf`
- **Processeurs** : `telegraf/processors.conf`
## 🧪 Tests et Validation

### **Vérifier la santé des services :**
```bash
# Status de tous les conteneurs
docker-compose ps

# Logs d'un service spécifique
docker-compose logs router_django
docker-compose logs postgres
docker-compose logs pgadmin

# Test de connexion PostgreSQL
docker-compose exec router_django python3 router_supervisor/manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ PostgreSQL OK')"

# Test de l'application Django
curl http://localhost:8080/health/
```

### **Commandes de maintenance :**
```bash
# Redémarrer un service
docker-compose restart router_django

# Reconstruire et redémarrer
docker-compose up -d --build router_django

# Accéder au shell du conteneur
docker-compose exec router_django bash
docker-compose exec postgres psql -U user -d routerdb

# Sauvegarder PostgreSQL
docker-compose exec postgres pg_dump -U user routerdb > backup_$(date +%Y%m%d).sql
```

## 📁 Structure du Projet

```
supervision-routeur-cisco/
├── 📄 docker-compose.yml           # Configuration développement
├── 📄 Dockerfile                   # Image Django/Python
├── 📄 requirements.txt             # Dépendances Python
├── 📄 Caddyfile                   # Configuration reverse proxy
├── 
├── 📁 router_supervisor/           # Application Django
│   ├── 📄 manage.py
│   ├── 📄 prod_settings.py        # Settings production
│   ├── 📁 src/                    # Configuration Django
│   ├── 📁 api_app/                # API REST
│   ├── 📁 dashboard_app/          # Interface utilisateur
│   ├── 📁 settings_app/           # Paramètres système
│   └── 📁 thresholds_app/         # Gestion des seuils
│
├── 📁 telegraf/                    # Collecteur de données
│   ├── 📄 telegraf.conf           # Configuration principale
│   ├── 📄 processors.conf         # Traitement des données
│   └── 📁 sample_metrics/         # Données de test
│
├── 📁 deployment/                  # Configuration production
│   └── 📄 docker-compose.prod.yml # Docker Compose production
│
└── 📁 logs/                       # Logs applicatifs
```

## 🔧 Variables d'Environnement

### **Django (router_django) :**
| Variable | Valeur | Description |
|----------|---------|-------------|
| `DATABASE` | `postgres` | Type de base de données |
| `SQL_HOST` | `db` | Host PostgreSQL |
| `SQL_PORT` | `5432` | Port PostgreSQL |
| `SQL_USER` | `user` | Utilisateur BD |
| `SQL_PASSWORD` | `password` | Mot de passe BD |
| `SQL_DATABASE` | `routerdb` | Nom de la base |
| `DJANGO_SETTINGS_MODULE` | `router_supervisor.prod_settings` | Configuration Django |
| `DEBUG` | `False` | Mode debug (production) |
| `GUNICORN_WORKERS` | `4` | Nombre de workers |

### **PostgreSQL (db) :**
| Variable | Valeur | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `user` | Utilisateur administrateur |
| `POSTGRES_PASSWORD` | `password` | Mot de passe |
| `POSTGRES_DB` | `routerdb` | Base de données par défaut |

### **pgAdmin :**
| Variable | Valeur | Description |
|----------|---------|-------------|
| `PGADMIN_DEFAULT_EMAIL` | `admin@telecom-sudparis.eu` | Email de connexion |
| `PGADMIN_DEFAULT_PASSWORD` | `admin` | Mot de passe |

### **InfluxDB :**
| Variable | Valeur | Description |
|----------|---------|-------------|
| `DOCKER_INFLUXDB_INIT_USERNAME` | `admin` | Utilisateur admin |
| `DOCKER_INFLUXDB_INIT_PASSWORD` | `admin123456` | Mot de passe |
| `DOCKER_INFLUXDB_INIT_ORG` | `telecom-sudparis` | Organisation |
| `DOCKER_INFLUXDB_INIT_BUCKET` | `router-metrics` | Bucket de données |
| `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` | `my-super-secret-auth-token` | Token d'API |

## 🛠️ Dépannage

### **Problèmes courants**

#### **Conteneur PostgreSQL ne démarre pas :**
```bash
# Vérifier les logs
docker-compose logs db

# Supprimer le volume si corruption
docker-compose down -v
docker volume rm supervision-routeur-cisco_pgdata
docker-compose up -d db
```

#### **Erreur de connexion pgAdmin → PostgreSQL :**
- ✅ Utiliser `db` comme host (pas `localhost`)
- ✅ Port `5432` (pas `5050`)
- ✅ Vérifier que les conteneurs sont sur le même réseau

#### **Django ne se connecte pas à PostgreSQL :**
```bash
# Vérifier les variables d'environnement
docker-compose exec router_django env | grep SQL

# Tester la connexion manuellement
docker-compose exec router_django python3 -c "
import psycopg2
conn = psycopg2.connect(host='db', port=5432, user='user', password='password', dbname='routerdb')
print('✅ Connexion PostgreSQL réussie')
"
```

#### **Problème de permissions sur les volumes :**
```bash
# Linux/Mac - Ajuster les permissions
sudo chown -R $USER:$USER ./logs
sudo chown -R $USER:$USER ./telegraf/sample_metrics

# Windows - Redémarrer Docker Desktop
```

#### **Erreurs de migration Django :**
```bash
# Reset complet des migrations (⚠️ Perte de données)
docker-compose exec router_django python3 router_supervisor/manage.py migrate --fake-initial
docker-compose exec router_django python3 router_supervisor/manage.py migrate
```

### **Commandes de diagnostic :**
```bash
# Santé générale du système
docker system df
docker system prune

# Réseaux Docker
docker network ls
docker network inspect supervision-routeur-cisco_default

# Volumes persistants
docker volume ls
docker volume inspect supervision-routeur-cisco_pgdata
```

## 🔒 Sécurité en Production

### **⚠️ À MODIFIER AVANT LA PRODUCTION :**

1. **Mots de passe par défaut :**
   ```bash
   # PostgreSQL
   POSTGRES_PASSWORD: VotreMotDePasseSecurise123!
   
   # pgAdmin
   PGADMIN_DEFAULT_PASSWORD: AdminSecurise456!
   
   # InfluxDB
   DOCKER_INFLUXDB_INIT_PASSWORD: InfluxSecurise789!
   ```

2. **Certificats SSL/TLS :**
   - Configurer Caddy avec des certificats valides
   - Désactiver HTTP en production (HTTPS uniquement)

3. **Firewall et accès réseau :**
   ```bash
   # Limiter l'accès aux ports sensibles
   # pgAdmin (5050) : Accès interne uniquement
   # PostgreSQL (5432) : Pas d'exposition publique
   ```

## 📚 Ressources Supplémentaires

### **Documentation technique :**
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Manual](https://www.postgresql.org/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Telegraf Documentation](https://docs.influxdata.com/telegraf/)

### **Monitoring et logs :**
```bash
# Surveiller les ressources
docker stats

# Logs en temps réel
docker-compose logs -f router_django

# Analyser l'utilisation disque
docker system df -v
```

## 📝 Changelog PostgreSQL

### **Version 2.0 - Migration PostgreSQL** ✅
- ✅ Migration SQLite → PostgreSQL
- ✅ Configuration Docker Compose automatisée  
- ✅ Interface pgAdmin intégrée
- ✅ Détection automatique d'environnement
- ✅ Volumes persistants pour les données
- ✅ Health checks et logging structuré
- ✅ Configuration production séparée

### **Avantages obtenus :**
- 🚀 **Performance** : PostgreSQL plus rapide que SQLite
- 🔄 **Concurrence** : Support multi-utilisateurs
- 📈 **Scalabilité** : Gestion de grandes quantités de données
- 🛡️ **Fiabilité** : Transactions ACID, backup/restore
- 🔧 **Administration** : Interface pgAdmin intégrée

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Développé par l'équipe Telecom SudParis** 🎓  
**Version:** 2.0 - PostgreSQL Edition  
**Dernière mise à jour:** Juillet 2025
