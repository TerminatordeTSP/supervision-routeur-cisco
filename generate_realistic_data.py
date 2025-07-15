#!/usr/bin/env python3
"""
Générateur de données réalistes pour le dashboard
Simule un routeur Cisco avec des métriques dynamiques
"""

import time
import random
import json
import requests
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration InfluxDB
INFLUX_URL = "http://influxdb:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

class RouterSimulator:
    def __init__(self, router_name="Cisco-Router-Main"):
        self.router_name = router_name
        self.base_cpu = 35.0
        self.base_memory = 60.0
        self.base_latency = 2.5
        self.base_load = 0.8
        self.uptime = 3600000  # 1000 heures en secondes
        
        # Variations pour rendre les données réalistes
        self.cpu_trend = 0
        self.memory_trend = 0
        self.load_trend = 0
        
    def generate_cpu_metrics(self):
        """Génère des métriques CPU réalistes avec variations"""
        # Variation graduelle avec pics occasionnels
        self.cpu_trend += random.uniform(-2, 2)
        self.cpu_trend = max(-15, min(15, self.cpu_trend))
        
        cpu_usage = self.base_cpu + self.cpu_trend + random.uniform(-5, 5)
        cpu_usage = max(10, min(95, cpu_usage))
        
        # Pic de charge occasionnel
        if random.random() < 0.05:  # 5% de chance
            cpu_usage = min(85, cpu_usage + random.uniform(20, 30))
        
        return {
            "cpu_0_usage": round(cpu_usage, 1),
            "usage_active": round(cpu_usage, 1),
            "usage_system": round(cpu_usage * 0.3, 1),
            "cpu_5min": round(cpu_usage * 1.1, 1)
        }
    
    def generate_memory_metrics(self):
        """Génère des métriques mémoire réalistes"""
        self.memory_trend += random.uniform(-1, 1)
        self.memory_trend = max(-10, min(10, self.memory_trend))
        
        memory_usage = self.base_memory + self.memory_trend + random.uniform(-3, 3)
        memory_usage = max(30, min(90, memory_usage))
        
        return {
            "used_percent": round(memory_usage, 1),
            "used": int(memory_usage * 20971520),  # Simule bytes (entier)
            "free": int((100 - memory_usage) * 20971520),
            "available": int((100 - memory_usage) * 20971520)
        }
    
    def generate_network_metrics(self):
        """Génère des métriques réseau réalistes"""
        # Latence avec variations
        latency = self.base_latency + random.uniform(-0.5, 1.5)
        latency = max(0.5, min(50, latency))
        
        # Perte de paquets occasionnelle
        packet_loss = 0
        if random.random() < 0.1:  # 10% de chance
            packet_loss = random.uniform(0.5, 5.0)
        
        return {
            "latency_ms": round(latency, 2),
            "average_response_ms": round(latency, 2),
            "percent_packet_loss": float(round(packet_loss, 1)),
            "packets_transmitted": 10,
            "packets_received": 10 - int(packet_loss / 10)
        }
    
    def generate_system_metrics(self):
        """Génère des métriques système réalistes"""
        self.load_trend += random.uniform(-0.1, 0.1)
        self.load_trend = max(-0.5, min(0.5, self.load_trend))
        
        load = self.base_load + self.load_trend + random.uniform(-0.2, 0.2)
        load = max(0.1, min(3.0, load))
        
        self.uptime += 10  # Incrémente l'uptime
        
        return {
            "load1": round(load, 2),
            "load5": round(load * 1.1, 2),
            "load15": round(load * 1.2, 2),
            "uptime": self.uptime
        }
    
    def generate_interface_metrics(self):
        """Génère des métriques d'interface réalistes"""
        interfaces = []
        
        for i in range(3):  # 3 interfaces
            interface_name = f"GigabitEthernet0/{i}"
            
            # Trafic variable selon l'interface
            if i == 0:  # Interface principale
                base_traffic = 450
            elif i == 1:  # Interface secondaire
                base_traffic = 200
            else:  # Interface de backup
                base_traffic = 50
            
            input_octets = base_traffic + random.uniform(-100, 100)
            output_octets = input_octets * random.uniform(0.8, 1.2)
            
            interfaces.append({
                "name": interface_name,
                "ifDescr": interface_name,
                "ifInOctets": int(max(0, input_octets)),
                "ifOutOctets": int(max(0, output_octets)),
                "ifInErrors": random.randint(0, 2),
                "ifOutErrors": random.randint(0, 1),
                "status": "up" if random.random() > 0.05 else "down"
            })
        
        return interfaces
    
    def generate_complete_metrics(self):
        """Génère un ensemble complet de métriques"""
        timestamp = datetime.now()
        
        return {
            "router_name": self.router_name,
            "timestamp": timestamp.isoformat(),
            "cpu": self.generate_cpu_metrics(),
            "memory": self.generate_memory_metrics(),
            "network": self.generate_network_metrics(),
            "system": self.generate_system_metrics(),
            "interfaces": self.generate_interface_metrics()
        }

def write_to_influxdb(metrics):
    """Écrit les métriques dans InfluxDB"""
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        timestamp = datetime.now()
        points = []
        
        # Métriques CPU
        for field, value in metrics["cpu"].items():
            point = Point("cpu").tag("hostname", metrics["router_name"]).field(field, value).time(timestamp)
            points.append(point)
        
        # Métriques mémoire
        for field, value in metrics["memory"].items():
            point = Point("mem").tag("hostname", metrics["router_name"]).field(field, value).time(timestamp)
            points.append(point)
        
        # Métriques réseau
        for field, value in metrics["network"].items():
            point = Point("ping").tag("hostname", metrics["router_name"]).field(field, value).time(timestamp)
            points.append(point)
        
        # Métriques système
        for field, value in metrics["system"].items():
            point = Point("system").tag("hostname", metrics["router_name"]).field(field, value).time(timestamp)
            points.append(point)
        
        # Métriques d'interface
        for interface in metrics["interfaces"]:
            for field, value in interface.items():
                if field not in ["name", "ifDescr"]:
                    point = Point("interfaces").tag("hostname", metrics["router_name"]).tag("interface", interface["name"]).field(field, value).time(timestamp)
                    points.append(point)
        
        write_api.write(bucket=INFLUX_BUCKET, record=points)
        client.close()
        
        print(f"✅ Métriques envoyées à InfluxDB: CPU={metrics['cpu']['cpu_0_usage']:.1f}%, MEM={metrics['memory']['used_percent']:.1f}%")
        return True
        
    except Exception as e:
        print(f"❌ Erreur InfluxDB: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Démarrage du générateur de données réalistes...")
    
    simulator = RouterSimulator()
    
    # Attendre qu'InfluxDB soit prêt
    print("⏳ Attente d'InfluxDB...")
    time.sleep(10)
    
    counter = 0
    while True:
        try:
            counter += 1
            
            # Générer les métriques
            metrics = simulator.generate_complete_metrics()
            
            # Écrire dans InfluxDB
            success = write_to_influxdb(metrics)
            
            if success:
                print(f"📊 Cycle #{counter} - Données générées et envoyées")
            else:
                print(f"⚠️  Cycle #{counter} - Erreur d'envoi")
            
            # Attendre avant la prochaine itération
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du générateur...")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
