

# Telegraf Commands
```
sudo nano /etc/telegraf/telegraf.conf
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
