import pygame
import random

def lire_images():
    # Lecture des images
    images = {}

    # lecture de l'image du perso
    image = pygame.image.load("perso.png").convert_alpha()
    images["perso"]=image
    image = pygame.image.load("background.jpg").convert()
    images["fond"]=image
    image = pygame.image.load("balle.png").convert_alpha()
    images["balle"]=image

    # Choix de la police pour le texte
    font = pygame.font.Font(None, 34)
    image = font.render('<Escape> pour quitter', True, (255, 255, 255))
    images["texte1"]=image

    #chargement du son
    try:
        son_collision = pygame.mixer.Sound("collision.OGG")
        images["son_collision"] = son_collision
    except:
        print("fichier son collision.OGG non trouvé")
        images["son_collision"] = None
        
    try:
        son_game_over = pygame.mixer.Sound("gameover.WAV")
        images["son_game_over"] = son_game_over
    except:
        print("fichier son gameover.WAAV non trouvé")
        images["son_game_over"] = None
    
    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # -1 pour boucler infiniment
    except:
        print("fichier musique_fond.OGG non trouvé")

    return images

class ElementGraphique:
    def __init__(self,image,fenetre,x=0, y=0):
        self.image=image
        self.fenetre = fenetre
        self.rect = image.get_rect()
        self.rect.x=x
        self.rect.y=y

    def afficher(self):
        self.fenetre.blit(self.image, self.rect)
        
    def collide(self, other):
        if self.rect.colliderect(other.rect):
            return True
        return False
 

class Perso(ElementGraphique):
    def __init__(self,image,fenetre,x=0, y=0):
        self.image=image
        self.fenetre = fenetre
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vies = 3
        self.inv = False
        self.comp_inv = 0
        self.score = 0
        
    def deplacer(self):
        if touches[pygame.K_DOWN]:
             self.rect.y+=3
        if touches[pygame.K_UP]:
             self.rect.y-=3
        if touches[pygame.K_LEFT] :
            self.rect.x-=3
        if touches[pygame.K_RIGHT] :
            self.rect.x+=3
        if self.rect.x < 0:
           self.rect.x = 0
        if self.rect.x + perso.rect.w > largeur:
           self.rect.x = largeur - perso.rect.w
        if self.rect.y < 0:
           self.rect.y = 0
        if self.rect.y + perso.rect.h > hauteur:
           self.rect.y = hauteur - perso.rect.h
        if self.inv :
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = False
                
    def appliquer_degats(self):
        if not self.inv:
            self.vies -= 1
            self.inv = True
            self.comp_inv = 0
            print(f"aie! vies restantes : {self.vies}")
    
#creation de la classe pour la balle

class Balle(ElementGraphique):
    def __init__(self,image,fenetre,depballe_x = 3.3,depballe_y = 3.3):
    
         largeur=fenetre.get_width()
         hauteur= fenetre.get_height()
         
         x = random.randint(0,largeur-image.get_width())
         y = random.randint(0,hauteur-image.get_height())
                
         super().__init__(image,fenetre,x,y)
        
         self.depballe_x =  depballe_x
         self.depballe_y = depballe_y 
        
    def deplacer(self):

        largeur,hauteur =self.fenetre.get_size()
        
       
        self.rect.x = self.rect.x + self.depballe_x
        self.rect.y = self.rect.y + self.depballe_y
        
        if self.rect.x < 0:
           self.rect.x = 0
           self.depballe_x=-self.depballe_x
            
        if  self.rect.x+ self.rect.w > largeur:
            self.rect.x = largeur - self.rect.w
            self.depballe_x = -self.depballe_x
            
        if self.rect.y < 0 :
           self.rect.y = 0
           self.depballe_y=-self.depballe_y
           
        if self.rect.y + self.rect.h > hauteur:  
            self.rect.y = hauteur - self.rect.h
            self.depballe_y = -self.depballe_y
            
#initialisation de la bibliotheque
pygame.mixer.init()

# Initialisation de la bibliotheque pygame
pygame.init()

#creation de la fenetre
largeur = 640
hauteur = 480
fenetre=pygame.display.set_mode((largeur,hauteur))

images = lire_images()

#timer pour les nouvelles balles
td_balle = pygame.time.get_ticks()
intervalle_balle = 6000
nbre_max_balle = 6

perso = Perso(images["perso"],fenetre,x=60,y=80)
perso.inv =True
perso.comp_inv =0

# lecture de l'image du fond
fond = ElementGraphique(images["fond"],fenetre)

balles=[ Balle(images["balle"],fenetre)]

#servira a regler l'horloge de jeu
horloge = pygame.time.Clock()

#ajout de la variable d'etat
game_over = False
son_game_over_joue = False

# servira a regler l'horloge du jeu
horloge = pygame.time.Clock()

# la boucle principale
i=1
continuer=True
while continuer == True:

    # fixons le nombre max de frames / secondes
    horloge.tick(30)

    i=i+1
    print (i)
    
    # on recupere l'etat du clavier
    touches = pygame.key.get_pressed()

    # si la touche ESC est enfoncee, on sortira
    if touches[pygame.K_ESCAPE]:
        continuer=False

    # Affichage du fond
    fond.afficher()
    

    # Vérifier si le jeu est terminé
    if perso.vies <= 0 and not game_over:
        game_over = True
        if not son_game_over_joue:
            if images["son_game_over"]:
                images["son_game_over"].play()
            son_game_over_joue = True
            pygame.mixer.music.stop()  # arrêter la musique de fond

    # SI LE JEU EST TERMINÉ
    if game_over:
        # Affichage de GAME OVER
        font_gameover = pygame.font.Font(None, 100)
        texte_gameover = font_gameover.render("GAME OVER", True, (255, 0, 0))
        rect_gameover = texte_gameover.get_rect(center=(largeur//2, hauteur//2))
        fenetre.blit(texte_gameover, rect_gameover)
        
        # Affichage du score final
        font_score = pygame.font.Font(None, 60)
        texte_score_final = font_score.render(f"Score: {perso.score}", True, (255, 255, 255))
        rect_score = texte_score_final.get_rect(center=(largeur//2, hauteur//2+80))
        fenetre.blit(texte_score_final, rect_score)
        
        # Affichage du temps de survie
        temps_survie = perso.score//30
        font_temps = pygame.font.Font(None, 40)
        texte_temps = font_temps.render(f"Temps de survie: {temps_survie} secondes", True, (255, 255, 255))
        rect_temps = texte_temps.get_rect(center=(largeur//2, hauteur//2+140))
        fenetre.blit(texte_temps, rect_temps)
        
        # Affichage du texte pour recommencer ou quitter
        font_restart = pygame.font.Font(None, 30)
        texte_restart = font_restart.render("Appuyez sur ESPACE pour rejouer ou ECHAP pour quitter", True, (255, 255, 255))
        rect_restart = texte_restart.get_rect(center=(largeur//2, hauteur//2+200))
        fenetre.blit(texte_restart, rect_restart)
        
    # SI LE JEU EST EN COURS
    else:
        # Affichage et déplacement du perso
        perso.afficher()
        perso.deplacer()
        perso.score += 1
        
        # Création des balles
        temps_actuel = pygame.time.get_ticks()
        
        if temps_actuel - td_balle >= intervalle_balle:
            if len(balles) < nbre_max_balle:
                new_balle = Balle(images["balle"], fenetre)
                balles.append(new_balle)
                td_balle = temps_actuel
                print(f"nouvelle balle créée! total: {len(balles)}")
        
        # Déplacement et affichage des balles
        for balle in balles:
            balle.deplacer()
            balle.afficher()
         
        # Détection des collisions
        for balle in balles:
            if perso.collide(balle):
                if images["son_collision"]:
                    images["son_collision"].play()  
                perso.appliquer_degats()
                
        # Affichage du texte (vies et score)
        font = pygame.font.Font(None, 36)
        texte_vies = font.render(f"Vies: {perso.vies}", True, (255, 255, 255))
        texte_score = font.render(f"Score: {perso.score}", True, (255, 255, 255))
        fenetre.blit(texte_score, (10, 10))
        fenetre.blit(texte_vies, (10, 60))

    # Rafraichissement
    pygame.display.flip()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False
        
        # Pour recommencer le jeu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_over:
                # Réinitialisation
                perso.vies = 3
                perso.score = 0
                perso.rect.x = 60
                perso.rect.y = 80
                perso.inv = True
                perso.comp_inv = 0
                balles = [Balle(images["balle"], fenetre)]
                game_over = False
                son_game_over_joue = False
                td_balle = pygame.time.get_ticks()
                
                # Redémarrer la musique de fond
                try:
                    pygame.mixer.music.load("musique_fond.OGG")
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                except:
                    print("fichier musique_fond.OGG non trouvé")
                    
            elif event.key == pygame.K_ESCAPE:
                continuer = False

# Arrêter la musique avant la fin
pygame.mixer.music.stop()
# Fin du programme principal
pygame.quit()
