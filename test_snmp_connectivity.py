#!/usr/bin/env python3
"""
Script de test pour vérifier la connectivité SNMP avec le routeur
"""

import subprocess
import sys
import time
from datetime import datetime

def test_ping(host):
    """Test la connectivité ping vers le routeur"""
    print(f"🔄 Test de ping vers {host}...")
    try:
        result = subprocess.run(['ping', '-c', '3', host], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ping vers {host} réussi")
            return True
        else:
            print(f"❌ Ping vers {host} échoué")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du ping: {e}")
        return False

def test_snmp_walk(host, community="public"):
    """Test la connectivité SNMP avec snmpwalk"""
    print(f"🔄 Test SNMP walk vers {host} avec community '{community}'...")
    try:
        # Test avec l'OID system
        result = subprocess.run(['snmpwalk', '-v2c', '-c', community, host, '1.3.6.1.2.1.1.1.0'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ SNMP walk vers {host} réussi")
            print(f"   Réponse: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ SNMP walk vers {host} échoué")
            print(f"   Stderr: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du SNMP walk: {e}")
        return False

def test_specific_oids(host, community="public"):
    """Test des OIDs spécifiques utilisés par Telegraf"""
    oids = {
        "hostname": "1.3.6.1.2.1.1.5.0",
        "uptime": "1.3.6.1.2.1.1.3.0",
        "cpu_5min": "1.3.6.1.4.1.9.2.1.58.0",
        "cpu_0_usage": "1.3.6.1.4.1.9.9.109.1.1.1.1.8.7",
        "ram_used": "1.3.6.1.4.1.9.9.48.1.1.1.5.1",
        "ram_free": "1.3.6.1.4.1.9.9.48.1.1.1.6.1",
    }
    
    print(f"🔄 Test des OIDs spécifiques sur {host}...")
    success_count = 0
    
    for name, oid in oids.items():
        try:
            result = subprocess.run(['snmpget', '-v2c', '-c', community, host, oid], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ {name} ({oid}): {result.stdout.strip()}")
                success_count += 1
            else:
                print(f"❌ {name} ({oid}): Pas de réponse ou erreur")
        except Exception as e:
            print(f"❌ {name} ({oid}): Erreur - {e}")
    
    print(f"📊 Résultat: {success_count}/{len(oids)} OIDs répondent")
    return success_count > 0

def test_telegraf_connectivity():
    """Test la connectivité depuis le conteneur Telegraf"""
    print("🔄 Test de connectivité depuis le conteneur Telegraf...")
    try:
        # Exécuter snmpwalk depuis le conteneur telegraf
        result = subprocess.run([
            'docker', 'exec', 'telegraf', 'snmpwalk', '-v2c', '-c', 'public', 
            '172.16.10.41', '1.3.6.1.2.1.1.1.0'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Connectivité SNMP depuis Telegraf réussie")
            return True
        else:
            print("❌ Connectivité SNMP depuis Telegraf échouée")
            print(f"   Stderr: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test Telegraf: {e}")
        return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🔍 DIAGNOSTIC DE CONNECTIVITÉ SNMP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    host = "172.16.10.41"
    community = "public"
    
    # Tests séquentiels
    tests = [
        ("Ping", lambda: test_ping(host)),
        ("SNMP Walk", lambda: test_snmp_walk(host, community)),
        ("OIDs spécifiques", lambda: test_specific_oids(host, community)),
        ("Telegraf Container", test_telegraf_connectivity)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Pause entre les tests
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:20} : {status}")
    
    successful_tests = sum(1 for _, result in results if result)
    print(f"\nRésultat global: {successful_tests}/{len(results)} tests réussis")
    
    # Recommandations
    print("\n" + "=" * 60)
    print("💡 RECOMMANDATIONS")
    print("=" * 60)
    
    if successful_tests == 0:
        print("❌ Aucun test n'a réussi. Vérifiez:")
        print("   - La connectivité réseau vers 172.16.10.41")
        print("   - La configuration SNMP sur le routeur")
        print("   - La community string ('public' par défaut)")
    elif successful_tests < len(results):
        print("⚠️  Quelques tests ont échoué. Vérifiez:")
        print("   - La configuration des OIDs spécifiques")
        print("   - Les permissions SNMP sur le routeur")
        print("   - La connectivité depuis le conteneur Telegraf")
    else:
        print("✅ Tous les tests ont réussi!")
        print("   - La connectivité SNMP fonctionne correctement")
        print("   - Vérifiez les logs de Telegraf pour d'autres problèmes")

if __name__ == "__main__":
    main()
