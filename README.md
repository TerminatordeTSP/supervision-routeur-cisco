

# Telegraf Commands
```
sudo vim /etc/telegraf/telegraf.conf
sudo systemctl status telegraf
sudo systemctl start telegraf
sudo systemctl stop telegraf
```

# Configure a gRPC Telemetry Subscription

## CPU
```
configure terminal
telemetry ietf subscription 1
encoding encode-kvgpb
filter xpath /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
stream yang-push
update-policy periodic 60000
receiver ip address 172.16.10.40 57500 protocol grpc-tcp
```

## MEMORY
```
configure terminal
telemetry ietf subscription 2
 encoding encode-kvgpb
 filter xpath /memory-ios-xe-oper:memory-statistics
 stream yang-push
 update-policy periodic 60000
 receiver ip address 172.16.10.40 57500 protocol grpc-tcp
```

## Page de configuration :
Pour accéder à la page de configuration des routeurs et des seuils :
http://127.0.0.1:8000/configuration/

A ce jour les opérations CRUD sont disponibles pour les seuils, pour les routeurs il manque que "suppression" et "mis à jour". 

## Page principale (Dashboard):
Pour accéder à la page de configuration des routeurs et des seuils :
http://127.0.0.1:8000/dashboard

A ce jour les opérations CRUD sont disponibles pour les seuils, pour les routeurs il manque que "suppression" et "mis à jour". 


## Lancement de la collecte des métriques :

1. créer le fichier `run.flag`

Ce fichier sert à **activer ou désactiver la collecte**.  
Tant qu’il est présent, le script continue de collecter les métriques toutes les **5 secondes**.

2. les commandes à taper pour le lancement 

touch run.flag  # 
python collect_metrics.py # pour lancer le script qui va lancer la collecte

3. Visualisation en temps réel dans le supervision-routeur-cisco/fichier metric_filtered.json

4. Arreter la collecte 

rm run.flag     # dans un autre terminal pour arrêter proprement la collecte (ou le supprimer manuellement)
