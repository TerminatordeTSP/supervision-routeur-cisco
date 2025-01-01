from ncclient import manager

# Paramètres de connexion
router_ip = '172.16.10.41'  # Adresse IP du routeur
username = 'root'  # Nom d'utilisateur
password = 'root'  # Mot de passe

# Connexion NetConf
with manager.connect(host=router_ip, port=830, username=username, password=password, hostkey_verify=False) as m:
    # Exécuter une requête pour récupérer les informations sur le système
    # Utiliser une requête YANG pour récupérer les statistiques du système
    filter = """
    <filter>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <cpu-utilization></cpu-utilization>
            <memory-usage></memory-usage>
        </native>
    </filter>
    """

    # Envoyer la requête NetConf
    response = m.get(filter)

    # Afficher la réponse (données récupérées)
    print(response.xml)
