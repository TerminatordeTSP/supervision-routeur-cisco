import requests
from requests.auth import HTTPBasicAuth
import json

# Paramètres de connexion RESTCONF
router_ip = "172.16.10.41"  # Adresse IP du routeur
username = "root"  # Nom d'utilisateur (RESTCONF)
password = "root"  # Mot de passe
restconf_url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics"

# Désactiver les avertissements SSL (utilisé ici car nous utilisons un certificat auto-signé)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Effectuer une requête GET pour récupérer les informations
try:
    headers = {
        "Accept": "application/yang-data+json"  # Indique que nous voulons les données en JSON
    }
    response = requests.get(
        url=restconf_url,
        auth=HTTPBasicAuth(username, password),
        headers=headers,
        verify=False  # Désactive la vérification SSL, utile pour certificats auto-signés
    )

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        print("Récupération des données réussie :")
        # Parse les données JSON
        data = response.json()
        print(json.dumps(data, indent=4))  # Affiche les données formatées
    else:
        print(f"Erreur : {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Une erreur est survenue : {str(e)}")
