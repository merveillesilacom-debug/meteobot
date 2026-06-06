import requests
from datetime import datetime

def get_meteo(ville):
    url = f"https://wttr.in/{ville}?format=3"
    try:
        reponse = requests.get(url, timeout=5)
        if reponse.status_code == 200:
            return reponse.text.strip()
        else:
            return "Ville introuvable"
    except:
        return "Erreur de connexion"

def rapport_multi(villes):
    date = datetime.now().strftime("%d-%m-%Y %H:%M")
    nom_fichier = "rapport_meteo.txt"
    
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(f"=== RAPPORT MÉTÉO MULTI-VILLES ===\n")
        f.write(f"Généré le : {date}\n")
        f.write(f"{'='*35}\n\n")
        
        for ville in villes:
            print(f"Récupération : {ville}...")
            meteo = get_meteo(ville)
            f.write(f"📍 {meteo}\n")
    
    print(f"\n✅ Rapport complet sauvegardé dans '{nom_fichier}' !")

def main():
    print("=== Météo Multi-Villes ===")
    print("Entre les villes séparées par des virgules")
    print("Exemple : Paris, Lyon, Abidjan\n")
    
    saisie = input("Tes villes : ")
    villes = saisie = saisie.replace(";", ",")
    villes = [v.strip() for v in saisie.split(",") if v.strip()]
    
    rapport_multi(villes)

main()