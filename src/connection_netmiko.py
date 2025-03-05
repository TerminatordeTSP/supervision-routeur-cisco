import csv
from netmiko import ConnectHandler

# Définir les informations de connexion au routeur
device = {
    'device_type': 'cisco_ios',
    'host': '172.16.10.41',  # Adresse IP ou nom d'hôte
    'username': 'admin',    # Nom d'utilisateur
    'password': 'cbwEU97scx6FQACS',    # Mot de passe
    'secret': 'Admin123INT',      # Mot de passe enable
}

def convert_bytes_to_mb(bytes_value):
    """Convertit des octets en mégaoctets (MB)."""
    return round(bytes_value / (1024 * 1024), 2)

def parse_cpu(cpu_output):
    """Extrait l'utilisation moyenne du CPU sur une minute."""
    if "one minute:" in cpu_output:
        return cpu_output.split("one minute:")[1].split(";")[0].strip()
    return "Données CPU introuvables"

def parse_ram(ram_output):
    """Extrait les informations sur la RAM (totale, utilisée, libre) et les convertit en MB."""
    parts = ram_output.split()
    if len(parts) >= 6:
        total = convert_bytes_to_mb(int(parts[3]))
        used = convert_bytes_to_mb(int(parts[5]))
        free = convert_bytes_to_mb(int(parts[7]))
        return {
            "Total (MB)": total,
            "Utilisée (MB)": used,
            "Libre (MB)": free,
        }
    return {"Total (MB)": 0, "Utilisée (MB)": 0, "Libre (MB)": 0}

def parse_version(version_output):
    """Extrait la version logicielle IOS."""
    for line in version_output.splitlines():
        if "Cisco IOS XE Software, Version" in line:
            return line.split("Version")[1].strip()
    return "Version logicielle introuvable"

try:
    # Se connecter au routeur
    connection = ConnectHandler(**device)
    connection.enable()

    # Récupérer les données
    cpu_output = connection.send_command('show processes cpu | include one minute')
    ram_output = connection.send_command('show processes memory | include Processor Pool Total')
    version_output = connection.send_command('show version')

    # Analyser les sorties
    cpu_usage = parse_cpu(cpu_output)
    ram_usage = parse_ram(ram_output)
    ios_version = parse_version(version_output)

    # Enregistrer dans un fichier CSV
    csv_file = "data_routeur.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Écrire l'en-tête
        writer.writerow(["Donnée", "Valeur"])
        # Écrire les données
        writer.writerow(["Utilisation CPU", cpu_usage])
        writer.writerow(["RAM Totale (MB)", ram_usage["Total (MB)"]])
        writer.writerow(["RAM Utilisée (MB)", ram_usage["Utilisée (MB)"]])
        writer.writerow(["RAM Libre (MB)", ram_usage["Libre (MB)"]])
        writer.writerow(["Version Logicielle", ios_version])


    # Fermer la connexion
    connection.disconnect()

except Exception as e:
    print(f"Une erreur s'est produite : {e}")