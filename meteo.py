import requests

ville = input("Entre une ville : ")
url = f"https://wttr.in/{ville}?format=3"

reponse = requests.get(url)
print(reponse.text)