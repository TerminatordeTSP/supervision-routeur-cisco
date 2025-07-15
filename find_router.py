#!/usr/bin/env python3
"""
Script pour détecter l'adresse IP du routeur
"""

import subprocess
import socket
import sys
import ipaddress
import platform

def get_default_gateway():
    """Récupère l'adresse IP de la passerelle par défaut"""
    try:
        if platform.system() == "Windows":
            # Windows : utilise route print
            result = subprocess.run(['route', 'print', '0.0.0.0'], 
                                  capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if '0.0.0.0' in line and 'Network Destination' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]  # Gateway
        else:
            # Linux/Mac : utilise ip route
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        parts = line.split()
                        return parts[2]
            
            # Fallback pour Mac
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'gateway:' in line:
                    return line.split(':')[1].strip()
    except Exception as e:
        print(f"Erreur lors de la détection de la passerelle : {e}")
    
    return None

def get_local_ip():
    """Récupère l'adresse IP locale"""
    try:
        # Connexion à une adresse externe pour obtenir l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Erreur lors de la détection de l'IP locale : {e}")
        return None

def test_ping(ip):
    """Test si une adresse IP répond au ping"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ping', '-n', '1', ip], 
                                  capture_output=True, text=True, timeout=3)
        else:
            result = subprocess.run(['ping', '-c', '1', ip], 
                                  capture_output=True, text=True, timeout=3)
        return result.returncode == 0
    except Exception:
        return False

def test_snmp(ip, community="public"):
    """Test si SNMP est accessible"""
    try:
        # Test simple avec snmpwalk (si disponible)
        result = subprocess.run(['snmpwalk', '-v2c', '-c', community, ip, 'sysName'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False

def main():
    print("🔍 Détection de la configuration réseau...")
    
    # Obtenir l'IP locale
    local_ip = get_local_ip()
    if local_ip:
        print(f"📍 Adresse IP locale : {local_ip}")
    
    # Obtenir la passerelle par défaut
    gateway = get_default_gateway()
    if gateway:
        print(f"🌐 Passerelle par défaut : {gateway}")
        
        # Test ping
        if test_ping(gateway):
            print(f"✅ Ping vers {gateway} : OK")
        else:
            print(f"❌ Ping vers {gateway} : ÉCHEC")
        
        # Test SNMP
        if test_snmp(gateway):
            print(f"✅ SNMP vers {gateway} : OK")
        else:
            print(f"❌ SNMP vers {gateway} : ÉCHEC ou communauté incorrecte")
    else:
        print("❌ Impossible de détecter la passerelle par défaut")
    
    # Suggestions d'adresses communes
    common_gateways = ["192.168.1.1", "192.168.0.1", "10.0.0.1", "172.16.0.1"]
    print("\n🔍 Test des adresses communes...")
    
    for ip in common_gateways:
        if ip != gateway:  # Ne pas tester deux fois la même adresse
            if test_ping(ip):
                print(f"✅ {ip} répond au ping")
            else:
                print(f"❌ {ip} ne répond pas")

if __name__ == "__main__":
    main()
