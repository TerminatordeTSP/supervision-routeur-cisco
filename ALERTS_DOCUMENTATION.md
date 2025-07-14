# Système d'Alertes pour Router Supervisor

## 📋 Vue d'ensemble

J'ai implémenté un système d'alertes complet pour votre application de supervision de routeurs Cisco. Le système détecte automatiquement les dépassements de seuils dans les métriques et génère des alertes consultables via une interface web dédiée.

## 🎯 Fonctionnalités implémentées

### 1. Modèles de données
- **Alert** : Gestion complète des alertes avec sévérité, statut, timestamps
- **AlertRule** : Règles personnalisées pour la génération d'alertes
- **AlertHistory** : Historique des changements d'état des alertes

### 2. Service d'alertes (`AlertService`)
- Vérification automatique des seuils lors du traitement des métriques
- Création d'alertes en temps réel quand les seuils sont dépassés
- Résolution automatique quand les valeurs redeviennent normales
- Support des règles personnalisées d'alertes
- Système de cooldown pour éviter le spam d'alertes

### 3. Interface web d'alertes
- **Dashboard des alertes** (`/alerts/`) : Vue d'ensemble avec statistiques
- **Liste des alertes** (`/alerts/list/`) : Liste filtrable et paginée
- **Détail d'une alerte** (`/alerts/alert/<id>/`) : Informations complètes
- **Administration** : Interface admin pour gérer les alertes et règles

### 4. Actions sur les alertes
- **Acquitter** : Marquer comme vue par un opérateur
- **Résoudre** : Marquer comme traitée
- **Ignorer** : Marquer comme non pertinente
- **Historique** : Traçabilité de tous les changements

### 5. Types de seuils supportés
- **CPU** : Dépassement du pourcentage d'utilisation
- **RAM** : Dépassement de la mémoire en MB
- **Traffic** : Dépassement du trafic en Mbps
- **Interface** : Métriques spécifiques aux interfaces

## 🏗️ Architecture

### Structure des fichiers créés
```
router_supervisor/
├── alerts_app/                    # Nouvelle application Django
│   ├── models.py                  # Modèles Alert, AlertRule, AlertHistory
│   ├── services.py                # Service AlertService
│   ├── views.py                   # Vues web pour les alertes
│   ├── admin.py                   # Interface d'administration
│   ├── urls.py                    # URLs de l'application
│   ├── templates/alerts_app/      # Templates HTML
│   │   ├── dashboard.html         # Dashboard principal
│   │   ├── alerts_list.html       # Liste des alertes
│   │   └── base_alerts.html       # Template de base
│   └── management/commands/
│       └── setup_alerts.py        # Commande de configuration
├── api_app/
│   └── metrics_handlers.py        # Modifié pour intégrer les alertes
└── src/
    ├── settings.py                # Modifié pour inclure alerts_app
    └── urls.py                    # Modifié pour inclure /alerts/
```

### Intégration avec l'existant
- **metrics_handlers.py** : Modifié pour vérifier les seuils automatiquement
- **settings.py** : Ajout de l'application alerts_app
- **urls.py** : Ajout des routes /alerts/

## 🚀 Installation et utilisation

### Scripts fournis
1. **install_alerts.sh** : Installation complète du système
2. **start_server.sh** : Démarrage du serveur de développement

### URLs principales
- Dashboard des alertes : `http://localhost:8000/alerts/`
- Liste des alertes : `http://localhost:8000/alerts/list/`
- Administration : `http://localhost:8000/admin/`
- API JSON : `http://localhost:8000/alerts/api/summary/`

## 📊 Types d'alertes supportés

### Sévérités
- **CRITICAL** : Critique (rouge)
- **HIGH** : Élevée (orange)
- **MEDIUM** : Moyenne (jaune)
- **LOW** : Faible (vert)

### Statuts
- **ACTIVE** : Alerte active nécessitant une attention
- **ACKNOWLEDGED** : Acquittée par un opérateur
- **RESOLVED** : Résolue, problème corrigé
- **DISMISSED** : Ignorée, fausse alerte

### Types d'alertes
- **THRESHOLD** : Dépassement de seuil
- **INTERFACE_DOWN** : Interface hors service
- **HIGH_ERROR_RATE** : Taux d'erreur élevé
- **CONNECTIVITY** : Problème de connectivité

## ⚙️ Configuration

### Seuils automatiques
Le système utilise les seuils configurés dans le modèle `Threshold` de chaque routeur :
- `cpu` : Seuil CPU en pourcentage
- `ram` : Seuil mémoire en MB  
- `traffic` : Seuil trafic en Mbps

### Règles personnalisées
Via le modèle `AlertRule`, vous pouvez créer des règles spécifiques :
- Conditions personnalisées (>, >=, <, <=, =, !=)
- Sévérité et type d'alerte configurables
- Cooldown configurable entre alertes
- Filtrage par routeur/interface spécifique

## 🔄 Fonctionnement automatique

### Traitement des métriques
Quand une métrique est reçue via l'API (`/api/receive-metrics/`) :
1. La valeur est comparée aux seuils configurés
2. Si dépassement → création automatique d'une alerte
3. Si retour à la normale → résolution automatique de l'alerte
4. Vérification des règles personnalisées
5. Application du cooldown pour éviter les doublons

### Exemple de flux
```
Métrique CPU = 98% reçue pour Routeur-A
↓
Seuil CPU Routeur-A = 80%
↓ 
98% > 80% → DÉPASSEMENT DÉTECTÉ
↓
Création automatique d'une alerte CRITIQUE
↓
Alerte visible dans /alerts/ et /admin/
```

## 🎨 Interface utilisateur

### Dashboard des alertes
- Résumé des alertes actives par sévérité
- Répartition par type d'alerte
- Liste des alertes récentes (24h)
- Top routeurs avec le plus d'alertes
- Actions rapides (filtres prédéfinis)

### Liste des alertes
- Filtrage par statut, sévérité, routeur, type
- Recherche textuelle
- Tri par date, sévérité
- Pagination
- Actions en lot
- Auto-refresh optionnel

### Détail d'une alerte
- Informations complètes
- Historique des changements
- Alertes similaires
- Actions disponibles

## 🔧 Administration

### Interface admin Django
- Gestion des alertes avec filtres avancés
- Gestion des règles d'alertes
- Historique des changements
- Actions en lot (acquitter, résoudre)
- Badges de couleur pour la sévérité

## 📈 API REST

### Endpoints disponibles
- `GET /alerts/api/summary/` : Résumé des alertes
- `GET /alerts/api/count/` : Compteurs d'alertes actives
- `POST /alerts/alert/<id>/acknowledge/` : Acquitter
- `POST /alerts/alert/<id>/resolve/` : Résoudre

## 🎯 Points d'extension futurs

1. **Notifications** : Email, SMS, Slack, etc.
2. **Escalade** : Escalade automatique selon la durée
3. **Maintenance** : Mode maintenance pour suspendre les alertes
4. **Métriques personnalisées** : Support de nouveaux types de métriques
5. **Corrélation** : Groupement d'alertes liées
6. **Machine Learning** : Détection d'anomalies
7. **Intégrations** : ITSM, monitoring tools, etc.

## 🐛 Dépannage

### Problèmes courants
1. **Module router_supervisor non trouvé** : Utiliser `PYTHONPATH` dans les commandes
2. **Alertes non générées** : Vérifier que les routeurs ont des seuils configurés
3. **Migrations échouées** : Utiliser les migrations manuelles fournies

### Logs à vérifier
- Logs Django pour les erreurs d'import
- Logs de l'API pour le traitement des métriques
- Logs du service d'alertes pour la création d'alertes

## ✅ Prêt à utiliser !

Le système d'alertes est maintenant complètement intégré à votre application. À chaque réception de métrique dépassant un seuil, une alerte sera automatiquement créée et visible dans l'interface web dédiée.
