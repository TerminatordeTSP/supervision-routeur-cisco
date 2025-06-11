# Communication entre Telegraf et Django

Ce document décrit comment Telegraf collecte les données des routeurs Cisco et les envoie à l'application Django.

## Architecture

L'architecture du système est la suivante :

1. **Routeurs Cisco** : Envoient des données de télémétrie via gRPC
2. **Telegraf** : Collecte ces données et les transforme
3. **Application Django** : Reçoit les données via une API HTTP et les stocke en base de données

## Configuration Telegraf

Le fichier `telegraf.conf` est configuré pour :

- Recevoir les données des routeurs Cisco via gRPC sur le port 57500
- Transformer ces données au format JSON
- Envoyer les données formatées à l'API Django via HTTP POST

### Options importantes

```conf
# Entrée pour la télémétrie Cisco
[[inputs.cisco_telemetry_mdt]]
  transport = "grpc"
  service_address = ":57500"

# Sortie vers l'API Django
[[outputs.http]]
  url = "http://router_django:8080/api/metrics/"
  method = "POST"
  data_format = "json"
```

## API Django

L'application Django expose un endpoint API :

- **URL** : `/api/metrics/`
- **Méthode** : POST
- **Format** : JSON

Les données reçues sont traitées et stockées dans la base de données PostgreSQL.

## Tests et débogage

### Génération de données de test

Le script `generate_test_data.py` peut générer des données de test simulant les métriques des routeurs :

```bash
./generate_test_data.py --routers Router1 Router2 --output /tmp/metrics/router_data.json --print
```

### Envoi de données de test

Le script `send_test_data.py` permet d'envoyer des données de test à l'API :

```bash
./send_test_data.py --file /tmp/metrics/router_data.json --url http://localhost:8080/api/metrics/
```

Pour un envoi continu (simulation d'un flux de données) :

```bash
./send_test_data.py --dir /tmp/metrics --interval 30
```

## Modèle de données

Les données collectées sont stockées selon le modèle suivant :

- `Router` : Informations sur les routeurs
- `Interface` : Interfaces réseau des routeurs
- `KPI` : Indicateurs clés de performance (CPU, RAM, Traffic, etc.)
- `KPI_Interface_Log` : Enregistrements des valeurs de KPI pour chaque interface

## Configuration des routeurs Cisco

Pour configurer un routeur Cisco afin qu'il envoie des données de télémétrie, utilisez les commandes suivantes :

```
configure terminal
telemetry ietf subscription 1
 encoding encode-kvgpb
 filter xpath /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
 stream yang-push
 update-policy periodic 60000
 receiver ip address <adresse_ip_telegraf> 57500 protocol grpc-tcp
```

Où `<adresse_ip_telegraf>` est l'adresse IP du conteneur Telegraf.

## Dépannage

- Vérifiez les logs de Telegraf : `docker logs telegraf`
- Vérifiez les logs de l'application Django : `docker logs router_django`
- Consultez les fichiers de métriques générés dans `/tmp/metrics`

## Seuils et alertes

Le système utilise les modèles de seuils configurés dans l'application pour déclencher des alertes lorsque les métriques dépassent les valeurs définies.