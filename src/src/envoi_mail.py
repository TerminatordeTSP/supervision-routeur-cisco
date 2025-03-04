import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration du serveur SMTP
SMTP_SERVER = "z.imt.fr"
SMTP_PORT = 587  # 465 si SSL, 587 avec STARTTLS
USERNAME = "ryan.zerhouni@telecom-sudparis.eu"
PASSWORD = "Azertyuiop007**"  # Utilise un mot de passe d'application si 2FA activé

# Création du message
msg = MIMEMultipart()
msg["From"] = "supervision@fisa.com"
msg["To"] = "ryzer62@gmail.com"
msg["Subject"] = "Test Email Python"

body = "Ceci est un test d'envoi d'email en Python."
msg.attach(MIMEText(body, "plain"))

try:
    # Connexion au serveur SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()  # Identification
    server.starttls()  # Sécurisation de la connexion
    server.ehlo()

    # Connexion avec authentification
    server.login(USERNAME, PASSWORD)

    # Envoi du mail
    server.sendmail(USERNAME, msg["To"], msg.as_string())
    print("✅ E-mail envoyé avec succès !")

except smtplib.SMTPAuthenticationError:
    print("❌ Erreur : Problème d'authentification. Vérifie ton email et mot de passe.")
except smtplib.SMTPException as e:
    print(f"❌ Erreur SMTP : {e}")
except Exception as e:
    print(f"❌ Erreur : {e}")
finally:
    try:
        server.quit()
    except:
        pass  # Évite l'erreur si 'server' n'est pas défini