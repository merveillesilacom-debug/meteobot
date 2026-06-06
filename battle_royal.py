import random

class Perso():
    def __init__(self,son_nom, surnom):
        self.pv = 10
        self.nom = son_nom
        self.surnom = surnom
        self.degats = 2

    def attaquer(self, victime):
        print("moi, ", self.nom, "je vais te piler", victime.nom)

        victime.pv -= self.degats



arene = []

p = Perso("karadoc","le gras")
arene.append(p)

p = Perso("perseval","le presque malin")
arene.append(p)

p = Perso("jo","le clodo")
arene.append(p)

print("contenu de l'arene :")
print("-----------------------")
for perso in arene:
    print(perso.nom, perso.surnom)
print("-----------------------")

while len(arene)>1 :
    print("=========================baston=============")
    tirage = random.sample(arene, 2)
    attaquant = tirage[0]
    victime = tirage[1]

    attaquant.attaquer(victime)


    if victime.pv<=0 :
        print("Au revoir", victime.nom, victime.surnom)
        arene.remove(victime)

print("Vainqueur :", arene[0].nom, arene[0].surnom )
