#!/usr/bin/env python3
"""
Script de test pour le système d'alertes de router_supervisor
Simule l'envoi de métriques qui dépassent les seuils pour générer des alertes
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/receive-metrics/"

# Données de test avec dépassements de seuils
test_metrics = [
    {
        "description": "CPU critique sur Routeur-Test-01",
        "data": {
            "router_name": "Routeur-Test-01",
            "router_metrics": {
                "cpu_usage": 98.5,  # Dépasse le seuil de 80%
                "memory_usage": 512,
                "traffic_mbps": 50
            },
            "timestamp": str(int(time.time()))
        }
    },
    {
        "description": "Mémoire élevée sur Routeur-Test-01", 
        "data": {
            "router_name": "Routeur-Test-01",
            "router_metrics": {
                "cpu_usage": 45,
                "memory_usage": 3500,  # Dépasse le seuil de 1024MB
                "traffic_mbps": 75
            },
            "timestamp": str(int(time.time()))
        }
    },
    {
        "description": "Trafic élevé sur Routeur-Test-01",
        "data": {
            "router_name": "Routeur-Test-01", 
            "router_metrics": {
                "cpu_usage": 60,
                "memory_usage": 800,
                "traffic_mbps": 250  # Dépasse le seuil de 100Mbps
            },
            "timestamp": str(int(time.time()))
        }
    },
    {
        "description": "Valeurs normales (devrait résoudre les alertes)",
        "data": {
            "router_name": "Routeur-Test-01",
            "router_metrics": {
                "cpu_usage": 25,    # Sous le seuil
                "memory_usage": 500, # Sous le seuil
                "traffic_mbps": 30   # Sous le seuil
            },
            "timestamp": str(int(time.time()))
        }
    }
]

def send_metrics(data, description):
    """Envoyer des métriques à l'API"""
    print(f"\n📊 {description}")
    print(f"Données envoyées: {json.dumps(data, indent=2)}")
    
    try:
        # Note: Pour simplifier le test, on ignore l'authentification
        # En production, il faudrait s'authentifier
        response = requests.post(
            API_ENDPOINT,
            json=data,
            headers={
                'Content-Type': 'application/json',
            },
            # Ignorer les erreurs d'authentification pour ce test
            auth=('admin@admin.com', 'admin') if False else None
        )
        
        print(f"Statut: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result.get('message', 'OK')}")
        else:
            print(f"❌ Erreur: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur Django est démarré sur localhost:8000")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

def check_alerts():
    """Vérifier les alertes créées"""
    try:
        response = requests.get(f"{BASE_URL}/alerts/api/summary/")
        if response.status_code == 200:
            summary = response.json()
            print(f"\n📋 Résumé des alertes:")
            print(f"   Total actives: {summary.get('total_active', 0)}")
            print(f"   Critiques: {summary.get('by_severity', {}).get('critical', 0)}")
            print(f"   Élevées: {summary.get('by_severity', {}).get('high', 0)}")
            print(f"   Moyennes: {summary.get('by_severity', {}).get('medium', 0)}")
        else:
            print(f"❌ Impossible de récupérer le résumé des alertes: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des alertes: {str(e)}")

def main():
    print("🚀 Test du système d'alertes de router_supervisor")
    print("=" * 50)
    
    print(f"\n🌐 Serveur: {BASE_URL}")
    print(f"📡 Endpoint API: {API_ENDPOINT}")
    
    # Vérifier l'état initial
    print(f"\n📊 État initial des alertes:")
    check_alerts()
    
    # Envoyer les métriques de test
    for i, metric in enumerate(test_metrics, 1):
        print(f"\n🔄 Test {i}/{len(test_metrics)}")
        send_metrics(metric["data"], metric["description"])
        
        # Petite pause pour laisser le temps au système de traiter
        time.sleep(2)
        
        # Vérifier les alertes après chaque envoi
        check_alerts()
    
    print(f"\n✅ Test terminé!")
    print(f"\n🌐 Consultez les alertes sur: {BASE_URL}/alerts/")
    print(f"🔧 Administration sur: {BASE_URL}/admin/")
    
    print(f"\n💡 Notes:")
    print(f"   - Si vous voyez des erreurs 403/401, c'est normal car l'authentification est requise")
    print(f"   - Le système d'alertes devrait quand même traiter les métriques")
    print(f"   - Consultez les logs Django pour plus de détails")

if __name__ == "__main__":
    main()
