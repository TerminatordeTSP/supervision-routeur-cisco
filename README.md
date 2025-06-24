# Router Cisco Supervision - Guide d'installation et d'utilisation

Ce projet permet de surveiller et d'afficher les métriques d'un routeur Cisco. Il collecte les données via Telegraf, les stocke dans InfluxDB (et optionnellement PostgreSQL), et les affiche sur un tableau de bord Django.

## Configuration système

Deux modes de fonctionnement sont disponibles:
1. **Mode complet** - Utilise Django + InfluxDB + PostgreSQL
2. **Mode minimal** - Utilise uniquement InfluxDB (plus léger, sans nécessiter Django/PostgreSQL)

## Prérequis

- Python 3.7 ou supérieur (compatible avec Python 3.13)
- Docker (pour exécuter Telegraf)
- InfluxDB (installé localement ou via Docker)
- PostgreSQL (optionnel, pour le mode complet)

## Installation

1. Cloner le dépôt:
   ```bash
   git clone https://github.com/votre-utilisateur/supervision-routeur-cisco.git
   cd supervision-routeur-cisco
   ```

2. Créer un environnement virtuel:
   ```bash
   python -m venv .env
   source .env/bin/activate
   ```

3. Installer les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

## Choix du mode de fonctionnement

### Mode minimal (InfluxDB uniquement)

Utilisez ce mode si vous souhaitez uniquement collecter et stocker les métriques dans InfluxDB, sans PostgreSQL ni Django:

```bash
./start_collector_minimal.sh
```

Ce mode est particulièrement utile:
- Lors d'incompatibilités de version avec PostgreSQL/Django
- Pour des machines avec des ressources limitées
- Pour la collecte de données sans interface web

### Mode complet (avec PostgreSQL et interface Django)

Pour utiliser toutes les fonctionnalités (historique PostgreSQL, alertes, tableau de bord Django):

1. Configurez PostgreSQL en suivant les instructions dans `DATABASE_SETUP_COMPLETE.md`
2. Démarrez le collecteur complet:
   ```bash
   ./start_collector.sh
   ```
3. Dans un autre terminal, démarrez l'application Django:
   ```bash
   cd router_supervisor
   python manage.py runserver
   ```
4. Accédez au tableau de bord à l'adresse http://localhost:8000

## Configuration

- **InfluxDB**: Modifiez les paramètres de connexion dans `collect_metrics.py`
- **PostgreSQL**: Modifiez la connexion dans `router_supervisor/src/settings.py`
- **Telegraf**: Configurez les fichiers dans le dossier `telegraf/`

## Structure du projet

- `collect_metrics.py` - Script principal de collecte des données
- `my_influxdb_client.py` - Client InfluxDB personnalisé
- `router_supervisor/` - Application Django pour le tableau de bord
- `telegraf/` - Configuration Telegraf

## Dépannage

### Problèmes avec psycopg2-binary sur Python 3.13

Si vous rencontrez des erreurs lors de l'installation de psycopg2-binary avec Python 3.13, utilisez le mode minimal:

```bash
./start_collector_minimal.sh
```

### Erreurs de connexion à InfluxDB

Vérifiez que:
1. InfluxDB est en cours d'exécution
2. Les paramètres de connexion sont corrects dans `collect_metrics.py`

### Erreurs de connexion à PostgreSQL

Vérifiez que:
1. PostgreSQL est en cours d'exécution
2. Les paramètres de connexion sont corrects dans `router_supervisor/src/settings.py`
3. La base de données est créée avec les bonnes tables

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
