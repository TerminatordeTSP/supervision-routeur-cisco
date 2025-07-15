#!/usr/bin/env python3
"""
Script de diagnostic InfluxDB pour vérifier les données collectées
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "BQSixul3bdmN-KtFDG_BPfUgSDGc1ZIntJ-QYa2fiIQjA_2psFN2z21AOmxD2s8fpStGlj8YWyvTCckOeCrFJA=="
INFLUX_ORG = "telecom-sudparis"
INFLUX_BUCKET = "router-metrics"

def test_influxdb_connection():
    """Test la connexion à InfluxDB"""
    print("🔄 Test de connexion à InfluxDB...")
    try:
        response = requests.get(f"{INFLUX_URL}/ping", timeout=5)
        if response.status_code == 204:
            print("✅ InfluxDB est accessible")
            return True
        else:
            print(f"❌ InfluxDB répond avec le code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion InfluxDB: {e}")
        return False

def query_influxdb(query):
    """Exécute une requête Flux sur InfluxDB"""
    headers = {
        'Authorization': f'Token {INFLUX_TOKEN}',
        'Content-Type': 'application/vnd.flux'
    }
    
    try:
        response = requests.post(
            f"{INFLUX_URL}/api/v2/query?org={INFLUX_ORG}",
            headers=headers,
            data=query,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ Erreur requête InfluxDB: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return None

def check_bucket_data():
    """Vérifie les données dans le bucket"""
    print(f"🔄 Vérification des données dans le bucket '{INFLUX_BUCKET}'...")
    
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> group(columns: ["_measurement"])
      |> count()
    '''
    
    result = query_influxdb(query)
    if result:
        print("✅ Données trouvées dans le bucket:")
        print(result)
        return True
    else:
        print("❌ Aucune donnée trouvée dans le bucket")
        return False

def check_snmp_metrics():
    """Vérifie les métriques SNMP spécifiques"""
    print("🔄 Vérification des métriques SNMP...")
    
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -30m)
      |> filter(fn: (r) => r["_measurement"] == "snmp")
      |> group(columns: ["_field"])
      |> count()
    '''
    
    result = query_influxdb(query)
    if result:
        print("✅ Métriques SNMP trouvées:")
        print(result)
        return True
    else:
        print("❌ Aucune métrique SNMP trouvée")
        return False

def check_latest_metrics():
    """Vérifie les dernières métriques"""
    print("🔄 Vérification des dernières métriques...")
    
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -10m)
      |> filter(fn: (r) => r["_measurement"] == "snmp" or r["_measurement"] == "ping")
      |> last()
    '''
    
    result = query_influxdb(query)
    if result:
        print("✅ Dernières métriques:")
        print(result)
        return True
    else:
        print("❌ Aucune métrique récente trouvée")
        return False

def check_telegraf_metrics():
    """Vérifie les métriques collectées par Telegraf"""
    print("🔄 Vérification des métriques Telegraf...")
    
    measurements = ["snmp", "ping", "cpu", "mem", "system"]
    
    for measurement in measurements:
        query = f'''
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -30m)
          |> filter(fn: (r) => r["_measurement"] == "{measurement}")
          |> count()
        '''
        
        result = query_influxdb(query)
        if result and "0" not in result:
            print(f"✅ {measurement}: Données présentes")
        else:
            print(f"❌ {measurement}: Pas de données")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🔍 DIAGNOSTIC INFLUXDB")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {INFLUX_URL}")
    print(f"Bucket: {INFLUX_BUCKET}")
    print(f"Organisation: {INFLUX_ORG}")
    print()
    
    # Tests séquentiels
    tests = [
        ("Connexion InfluxDB", test_influxdb_connection),
        ("Données dans le bucket", check_bucket_data),
        ("Métriques SNMP", check_snmp_metrics),
        ("Dernières métriques", check_latest_metrics),
        ("Métriques Telegraf", check_telegraf_metrics)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:25} : {status}")
    
    successful_tests = sum(1 for _, result in results if result)
    print(f"\nRésultat global: {successful_tests}/{len(results)} tests réussis")
    
    # Recommandations
    print("\n" + "=" * 60)
    print("💡 RECOMMANDATIONS")
    print("=" * 60)
    
    if successful_tests == 0:
        print("❌ Aucun test n'a réussi. Vérifiez:")
        print("   - Que le conteneur InfluxDB est démarré")
        print("   - La configuration du token et de l'organisation")
        print("   - Les ports (8086) sont accessibles")
    elif successful_tests < len(results):
        print("⚠️  Quelques tests ont échoué. Vérifiez:")
        print("   - La configuration de Telegraf")
        print("   - Les données SNMP sont collectées")
        print("   - Les logs de Telegraf pour plus de détails")
    else:
        print("✅ Tous les tests ont réussi!")
        print("   - InfluxDB fonctionne correctement")
        print("   - Les données sont collectées")

if __name__ == "__main__":
    main()
