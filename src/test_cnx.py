import paramiko


def connect_and_fetch_info(hostname, username, password):
    """Connecte au serveur et récupère les informations système."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connexion SSH
        client.connect(hostname=hostname, username=username, password=password)

        # Commandes pour récupérer les informations système
        commands = {
            "RAM Usage": "free -h",
            "Disk Usage": "df -h",
            "CPU Usage": "top -b -n1 | grep 'Cpu(s)'",
            "Server Model": "uname -a",
            "CPU Info": "lscpu",
        }

        # Exécuter chaque commande et stocker les résultats
        results = {}
        for label, command in commands.items():
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if error:
                results[label] = f"Erreur : {error}"  # Stocke les erreurs éventuelles
            else:
                results[label] = output  # Stocke la sortie correcte

        return results

    finally:
        # Assurez-vous que la connexion est bien fermée
        client.close()


if __name__ == "__main__":
    # Informations de connexion
    server_hostname = "172.16.10.40"  # Remplacez par l'IP ou l'hôte de votre serveur
    username = "user"  # Remplacez par l'utilisateur
    password = "cbwEU97scx6FQACS"  # Remplacez par le mot de passe

    try:
        print("Connexion au serveur pour récupérer les informations...")
        system_info = connect_and_fetch_info(server_hostname, username, password)

        # Affichage des résultats
        for label, output in system_info.items():
            print(f"\n=== {label} ===")
            print(output)

    except Exception as e:
        print("Erreur lors de l'exécution :", str(e))

