from pygnmi.client import gNMIclient

# Paramètres de connexion
router_ip = "172.16.10.41"  # Adresse IP du routeur
router_port = 57400  # Port gNMI (par défaut 57400 pour TLS)
username = "user"  # Nom d'utilisateur
password = "cbwEU97scx6FQACS"  # Mot de passe

# Chemins YANG pour récupérer les données
paths = [
    "/memory-utilization",  # Métriques de la mémoire
    "/process-cpu",  # Métriques CPU
]

try:
    # Connexion au routeur Cisco via gNMI
    with gNMIclient(target=(router_ip, router_port), username=username, password=password, insecure=True) as client:
        # Effectuer une requête GET
        response = client.get(paths)

        # Afficher les données récupérées
        print("Données récupérées (RAM, CPU, Mémoire) :")
        for path, data in response["notification"][0]["update"].items():
            print(f"{path}: {data}")

except Exception as e:
    print(f"Erreur lors de la supervision gNMI : {e}")


