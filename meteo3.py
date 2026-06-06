import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_meteo(ville):
    url = f"https://wttr.in/{ville}?format=3"
    try:
        reponse = requests.get(url, timeout=5)
        if reponse.status_code == 200:
            return reponse.text.strip()
        else:
            return f"{ville} : ville introuvable"
    except:
        return f"{ville} : erreur de connexion"

def envoyer_email(expediteur, mot_de_passe, destinataire, contenu):
    msg = MIMEMultipart()
    msg["From"] = expediteur
    msg["To"] = destinataire
    msg["Subject"] = "📍 Rapport Météo Automatique"
    
    msg.attach(MIMEText(contenu, "plain"))
    
    try:
        serveur = smtplib.SMTP("smtp.gmail.com", 587)
        serveur.starttls()
        serveur.login(expediteur, mot_de_passe)
        serveur.sendmail(expediteur, destinataire, msg.as_string())
        serveur.quit()
        print("✅ Email envoyé avec succès !")
    except Exception as e:
        print(f"❌ Erreur email : {e}")

def main():
    print("=== Météo par Email ===\n")
    
    saisie = input("Tes villes (séparées par virgule) : ")
    saisie = saisie.replace(";", ",")
    villes = [v.strip() for v in saisie.split(",") if v.strip()]
    
    date = datetime.now().strftime("%d-%m-%Y %H:%M")
    contenu = f"RAPPORT MÉTÉO — {date}\n{'='*35}\n\n"
    
    for ville in villes:
        print(f"Récupération : {ville}...")
        meteo = get_meteo(ville)
        contenu += f"📍 {meteo}\n"
    
    print("\n" + contenu)
    
    envoyer = input("Envoyer par email ? (oui/non) : ")
    if envoyer.lower() == "oui":
        expediteur = input("Ton email Gmail : ")
        mot_de_passe = input("Ton mot de passe d'application : ")
        destinataire = input("Email du destinataire : ")
        envoyer_email(expediteur, mot_de_passe, destinataire, contenu)

main()