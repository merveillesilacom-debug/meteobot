import requests
from datetime import datetime

def get_meteo(ville):
    url = f"https://wttr.in/{ville}?format=3"
    reponse = requests.get(url)
    
    if reponse.status_code == 200:
        return reponse.text
    else:
        return None

def sauvegarder_rapport(ville, meteo):
    date = datetime.now().strftime("%d-%m-%Y %H:%M")
    nom_fichier = f"meteo_{ville}.txt"
    
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(f"=== RAPPORT MÉTÉO ===\n")
        f.write(f"Date : {date}\n")
        f.write(f"Ville : {ville}\n")
        f.write(f"Météo : {meteo}\n")
    
    print(f"Rapport sauvegardé dans '{nom_fichier}' !")

def main():
    print("=== Outil Météo ===")
    ville = input("Entre une ville : ")
    
    print(f"Récupération de la météo pour {ville}...")
    meteo = get_meteo(ville)
    
    if meteo:
        print(meteo)
        sauvegarder_rapport(ville, meteo)
    else:
        print(f"Erreur : ville '{ville}' introuvable !")

main()