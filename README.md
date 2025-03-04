# supervision-routeur-cisco

# Othmane Tairech

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
