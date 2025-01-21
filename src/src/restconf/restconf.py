import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Paramètres de connexion RESTCONF
router_ip = "172.16.10.41"  # Adresse IP du routeur
username = "root"
password = "root"
restconf_url = f"https://{router_ip}/restconf/data"

# Options pour SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

verify = False


def test_restconf_connection():
    """Test la communication RESTCONF avec le routeur."""
    headers = {"Accept": "application/yang-data+json"}
    try:
        response = requests.get(
            url=restconf_url,
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=False  # Désactiver SSL pour certificats auto-signés
        )
        if response.status_code == 200:
            print("Connexion RESTCONF réussie !")
            print(response.json())
        elif response.status_code == 401:
            print("Erreur 401 : Identifiants incorrects ou accès refusé.")
        elif response.status_code == 403:
            print("Erreur 403 : Accès interdit. Vérifiez vos permissions.")
        else:
            print(f"Erreur retour : {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erreur de connexion : {str(e)}")


if __name__ == "__main__":
    test_restconf_connection()