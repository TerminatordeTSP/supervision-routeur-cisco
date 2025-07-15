# Router Cisco Supervision - Guide d'installation et d'utilisation

Ce projet permet de surveiller et d'afficher les métriques d'un routeur Cisco. Il collecte les données via Telegraf, les stocke dans InfluxDB et PostgreSQL, et les affiche sur un tableau de bord Django avec interface d'administration.

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

## Modes de déploiement

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

## Prérequis

- **Docker & Docker Compose** (obligatoire)
- **Python 3.9+** (pour développement local uniquement)
- **Accès réseau** au routeur Cisco à superviser

## Installation locale rapide

### **Prérequis :**
- Docker & Docker Compose installés
- Git pour cloner le repository
- Accès réseau au routeur Cisco (optionnel pour les tests)

### **Installation en 4 étapes :**

1. **Cloner le projet :**
   ```bash
   git clone https://github.com/TerminatordeTSP/supervision-routeur-cisco.git
   cd supervision-routeur-cisco
   ```

2. **Démarrer tous les services :**
   ```bash
   docker-compose up -d --build
   ```

3. **Attendre que tous les conteneurs soient prêts (30-60 secondes) :**
   ```bash
   docker-compose ps
   ```

4. **[Optionnel] Créer un utilisateur administrateur Django :**
   ```bash
   docker-compose exec router_django python3 router_supervisor/manage.py createsuperuser
   ```

### **Accès aux services :**
- **Application Django** : http://localhost:8080
- **pgAdmin** : http://localhost:5050 
- **InfluxDB** : http://localhost:8086

### **Logins par défaut :**

| Service | URL | Login | Mot de passe |
|---------|-----|-------|--------------|
| **Django Admin** | http://localhost:8080/admin/ | admin | projetinfo1A |
| **pgAdmin** | http://localhost:5050 | admin@telecom-sudparis.eu | admin |
| **InfluxDB** | http://localhost:8086 | admin | admin123456 |

> **Note :** Le login Django `admin/projetinfo1A` est configuré par défaut pour toute nouvelle base de données.

## Roadmap - État du Projet

### **Ce qui fonctionne déjà :**

#### **Infrastructure & Déploiement**
- Architecture complète Docker Compose 
- Base de données PostgreSQL avec pgAdmin
- Base de données InfluxDB pour métriques temporelles
- Reverse proxy Caddy avec SSL automatique
- Health checks et monitoring des conteneurs
- Configuration automatique des services

#### **Collecte et Stockage de Données**
- Collecteur Telegraf SNMP fonctionnel
- Intégration InfluxDB pour métriques temporelles
- Pipeline de traitement des données
- Générateur de données de test pour développement
- API REST complète pour accès aux métriques

#### **Interface Utilisateur**
- Dashboard Django avec authentification
- Visualisation temps réel des métriques routeur
- Interface d'administration complète
- Gestion des utilisateurs et permissions
- API REST documentée

#### **Métriques Supportées**
CPU utilization, Mémoire RAM (ratio utilisée/libre), Uptime du routeur, Statistiques interfaces réseau (trafic, erreurs, statut), tests de connectivité ping sur la VM.

#### **🔧 Administration**
- Interface d'administration Django avec gestion des seuils d'alerte par utilisateur, configuration des routeurs supervisés, logs structurés et rotation automatique

### **Ce qu'il reste à faire :**

#### **Système d'Alertes Avancé**
- Intégration de solutions de communication (basées sur Matrix pour rester sur un projet opensource)
- Escalade des alertes selon la criticité
- Webhook personnalisables

#### **Visualisations Avancées**
- Graphiques historiques interactifs
- Dashboard personnalisable par utilisateur
- Export de rapports PDF/Excel
- Cartes de chaleur des performances
- Prédictions basées sur l'IA

#### **Fonctionnalités Métier**
- Multi-tenancy (gestion de plusieurs clients)
- SLA monitoring et reporting
- Analyse de tendances automatique
- Corrélation d'événements
- Maintenance planifiée

#### **Sécurité et Conformité**
- Authentification LDAP/Active Directory
- Audit trail complet
- Chiffrement des données au repos
- Politique de rétention avancée
- Conformité RGPD complète

#### **Performance et Scalabilité**
- Clustering InfluxDB
- Load balancing Django avec Redis
- Optimisation des requêtes base de données
- Cache Redis pour métriques fréquentes
- Support Kubernetes

#### **Intégrations**
- API GraphQL en plus de REST
- Intégration Grafana native
- Support Prometheus metrics
- Webhook entrants pour événements externes
- Intégration ITSM (ServiceNow, Jira)

#### **Mobile et Accessibilité**
- Application mobile native
- Progressive Web App (PWA)
- Interface accessible (WCAG 2.1)
- Mode hors-ligne partiel


## Installation et Déploiement

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

## Base de Données PostgreSQL

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
| **Password** | `password` | Mot de passe (**À changer en production**) |

### **Migrations Django :**
```bash
# Appliquer les migrations
docker-compose exec router_django python3 router_supervisor/manage.py migrate

# Créer de nouvelles migrations (si modification des modèles)
docker-compose exec router_django python3 router_supervisor/manage.py makemigrations

# Vérifier l'état des migrations
docker-compose exec router_django python3 router_supervisor/manage.py showmigrations
```

## Administration avec pgAdmin

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
   - **Save password** : Coché

## Monitoring et Métriques

### **InfluxDB (Métriques temporelles) :**
- **URL** : http://localhost:8086
- **Organisation** : `telecom-sudparis`
- **Bucket** : `router-metrics`
- **Token** : `my-super-secret-auth-token`

### **Telegraf (Collecteur de données) :**
- **Port d'écoute** : `57500`
- **Configuration** : `telegraf/telegraf.conf`
- **Processeurs** : `telegraf/processors.conf`
## Tests et Validation

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

## Structure du Projet

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

## Variables d'Environnement

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

## Dépannage

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
- Utiliser `db` comme host (pas `localhost`)
- Port `5432` (pas `5050`)
- Vérifier que les conteneurs sont sur le même réseau

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

## Sécurité en Production

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

## Ressources Supplémentaires

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

Ce projet est sous licence [MIT](https://mit-license.org/).

---

**Développé par le groupe 4 des FISA LIMA Telecom SudParis** 🎓  
**Version:** 2.0 - PostgreSQL Edition  
**Dernière mise à jour:** Juillet 2025
