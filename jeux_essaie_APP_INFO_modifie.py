import pygame
import random
import json
import os
from datetime import datetime

def lire_images():
    images = {}

    image = pygame.image.load("perso.png").convert_alpha()
    images["perso"] = image
    image = pygame.image.load("background.jpg").convert()
    images["fond"] = image
    image = pygame.image.load("balle.png").convert_alpha()
    images["balle"] = image

    # Chargement des fruits
    try:
        image = pygame.image.load("fraise.png").convert_alpha()
        images["fraise"] = image
    except:
        print("fichier fraise.png non trouvé")
        images["fraise"] = None

    try:
        image = pygame.image.load("pasteque.png").convert_alpha()
        images["pasteque"] = image
    except:
        print("fichier pasteque.png non trouvé")
        images["pasteque"] = None

    font = pygame.font.Font(None, 34)
    image = font.render('<Escape> pour quitter', True, (255, 255, 255))
    images["texte1"] = image

    images["son_collision"] = None

    try:
        son_game_over = pygame.mixer.Sound("gameover.OGG")
        images["son_game_over"] = son_game_over
    except:
        print("fichier son gameover.OGG non trouvé")
        images["son_game_over"] = None

    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(1)
    except:
        print("fichier musique_fond.OGG non trouvé")

    return images



def ecran_accueil(fenetre, images, largeur, hauteur):
    """Affiche l'ecran d'accueil et attend un clic sur le bouton JOUER."""
    horloge = pygame.time.Clock()

    # Fond degrade sombre
    fond_accueil = pygame.Surface((largeur, hauteur))
    for y in range(hauteur):
        ratio = y / hauteur
        r = int(10  + ratio * 30)
        g = int(10  + ratio * 20)
        b = int(40  + ratio * 80)
        pygame.draw.line(fond_accueil, (r, g, b), (0, y), (largeur, y))

    # Titre
    font_titre   = pygame.font.Font(None, 90)
    font_sous    = pygame.font.Font(None, 36)
    font_bouton  = pygame.font.Font(None, 50)

    # Redimensionner le personnage pour l'ecran d'accueil
    perso_img = pygame.transform.scale(images["perso"], (120, 120))

    # Rectangle du bouton JOUER
    btn_w, btn_h = 260, 65
    btn_x = largeur // 2 - btn_w // 2
    btn_y = hauteur - 140
    rect_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    # Particules decoratives (etoiles)
    etoiles = [(random.randint(0, largeur), random.randint(0, hauteur),
                random.uniform(0.3, 1.5)) for _ in range(80)]

    angle_brillance = 0  # animation du bouton

    while True:
        horloge.tick(60)
        angle_brillance += 3

        # Fond
        fenetre.blit(fond_accueil, (0, 0))

        # Etoiles scintillantes
        for ex, ey, eb in etoiles:
            lum = int(150 + 105 * abs(pygame.math.Vector2(1, 0).rotate(angle_brillance * eb).x))
            pygame.draw.circle(fenetre, (lum, lum, lum), (int(ex), int(ey)), int(eb))

        # Ligne decorative haut
        pygame.draw.line(fenetre, (255, 200, 0), (60, 70), (largeur - 60, 70), 2)

        # Titre "SURVIVAL"
        surf_s = font_titre.render("SURVIVAL", True, (255, 220, 50))
        fenetre.blit(surf_s, surf_s.get_rect(center=(largeur // 2, 120)))

        # Titre "CHARACTER"
        surf_c = font_titre.render("CHARACTER", True, (255, 255, 255))
        fenetre.blit(surf_c, surf_c.get_rect(center=(largeur // 2, 205)))

        # Ligne decorative bas du titre
        pygame.draw.line(fenetre, (255, 200, 0), (60, 240), (largeur - 60, 240), 2)

        # Photo du personnage (centree)
        perso_rect = perso_img.get_rect(center=(largeur // 2, 320))
        # Halo lumineux derriere le perso
        halo_r = int(75 + 10 * abs(pygame.math.Vector2(1,0).rotate(angle_brillance).x))
        pygame.draw.circle(fenetre, (80, 80, 160), perso_rect.center, halo_r)
        fenetre.blit(perso_img, perso_rect)

        # Bouton JOUER avec effet hover
        mx, my = pygame.mouse.get_pos()
        survol = rect_btn.collidepoint(mx, my)
        couleur_btn  = (50, 200, 100) if survol else (30, 140, 70)
        couleur_bord = (150, 255, 150) if survol else (80, 200, 100)
        pygame.draw.rect(fenetre, couleur_btn,  rect_btn, border_radius=14)
        pygame.draw.rect(fenetre, couleur_bord, rect_btn, width=3, border_radius=14)

        surf_btn = font_bouton.render("JOUER", True, (255, 255, 255))
        fenetre.blit(surf_btn, surf_btn.get_rect(center=rect_btn.center))

        # Sous-texte
        surf_esc = font_sous.render("ECHAP pour quitter", True, (180, 180, 180))
        fenetre.blit(surf_esc, surf_esc.get_rect(center=(largeur // 2, hauteur - 30)))

        pygame.display.flip()

        # Evenements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return  # lancer le jeu
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_btn.collidepoint(event.pos):
                    return  # lancer le jeu


def sauvegarder_partie(perso, balles, game_over):
    donnees = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'perso': {
            'x': perso.rect.x,
            'y': perso.rect.y,
            'vies': perso.vies,
            'score': perso.score,
            'inv': perso.inv,
            'comp_inv': perso.comp_inv
        },
        'balles': [
            {'x': b.rect.x, 'y': b.rect.y,
             'depballe_x': b.depballe_x, 'depballe_y': b.depballe_y}
            for b in balles
        ],
        'game_over': game_over
    }
    try:
        with open('sauvegarde.json', 'w') as f:
            json.dump(donnees, f, indent=2)
        print(f"Partie sauvegardée à {donnees['timestamp']}")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")
        return False


def charger_partie(perso, images, fenetre):
    if not os.path.exists('sauvegarde.json'):
        print("Aucune sauvegarde trouvée")
        return None, False
    try:
        with open('sauvegarde.json', 'r') as f:
            donnees = json.load(f)
        perso.rect.x   = donnees['perso']['x']
        perso.rect.y   = donnees['perso']['y']
        perso.vies     = donnees['perso']['vies']
        perso.score    = donnees['perso']['score']
        perso.inv      = donnees['perso']['inv']
        perso.comp_inv = donnees['perso']['comp_inv']
        balles = []
        for bd in donnees['balles']:
            balle = Balle(images["balle"], fenetre)
            balle.rect.x    = bd['x']
            balle.rect.y    = bd['y']
            balle.depballe_x = bd['depballe_x']
            balle.depballe_y = bd['depballe_y']
            balles.append(balle)
        game_over = donnees['game_over']
        print(f"Partie chargée depuis {donnees['timestamp']}")
        return balles, game_over
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None, False


# ─────────────────────────── Classes ─────────────────────────────────────────

class ElementGraphique:
    def __init__(self, image, fenetre, x=0, y=0):
        self.image  = image
        self.fenetre = fenetre
        self.rect   = image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def afficher(self):
        self.fenetre.blit(self.image, self.rect)

    def collide(self, other):
        return self.rect.colliderect(other.rect)


class Fond:
    """Fond parallax : défile vers le bas (donne l'impression que le perso monte)"""
    def __init__(self, image, fenetre, vitesse=2):
        self.fenetre = fenetre
        self.vitesse = vitesse
        lw = fenetre.get_width()
        lh = fenetre.get_height()
        self.image = pygame.transform.scale(image, (lw, lh))
        self.y1   = 0
        self.y2   = -lh
        self.haut = lh
        self.actif = False

    def deplacer(self):
        if not self.actif:
            return
        self.y1 += self.vitesse
        self.y2 += self.vitesse
        if self.y1 >= self.haut:
            self.y1 = self.y2 - self.haut
        if self.y2 >= self.haut:
            self.y2 = self.y1 - self.haut

    def afficher(self):
        self.fenetre.blit(self.image, (0, self.y1))
        self.fenetre.blit(self.image, (0, self.y2))


class Perso(ElementGraphique):
    def __init__(self, image, fenetre, x=0, y=0):
        super().__init__(image, fenetre, x, y)
        self.vies     = 3
        self.inv      = False
        self.comp_inv = 0
        self.score    = 0
        # immunite_active : immunité accordée par le bonus +1 (dure plus longtemps)
        self.immunite_active  = False
        self.comp_immunite    = 0
        self.duree_immunite   = 300  # ~10 secondes à 30 fps

    def deplacer(self):
        if touches[pygame.K_DOWN]:
            self.rect.y += 3
        if touches[pygame.K_UP]:
            self.rect.y -= 3
        if touches[pygame.K_LEFT]:
            self.rect.x -= 3
        if touches[pygame.K_RIGHT]:
            self.rect.x += 3
        self.rect.x = max(0, min(self.rect.x, largeur - self.rect.w))
        self.rect.y = max(0, min(self.rect.y, hauteur - self.rect.h))
        # Invincibilité courte après dégâts
        if self.inv:
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = False
        # Immunité bonus
        if self.immunite_active:
            self.comp_immunite += 1
            if self.comp_immunite >= self.duree_immunite:
                self.immunite_active = False
                self.comp_immunite   = 0
                print("Immunité terminée !")

    def activer_immunite(self):
        self.immunite_active = True
        self.comp_immunite   = 0
        print("Immunité activée !")

    def appliquer_degats(self):
        """Perd 1 vie entière (balles) – bloqué si immunité active"""
        if self.immunite_active:
            return  # immunité : aucun dégât
        if not self.inv:
            self.vies -= 1
            self.inv      = True
            self.comp_inv = 0
            print(f"aie! vies: {self.vies}")

    def appliquer_demi_degats(self):
        """Perd une demi vie (fruits) – bloqué si immunité active"""
        if self.immunite_active:
            return  # immunité : aucun dégât
        if not self.inv:
            self.vies -= 0.5
            self.inv      = True
            self.comp_inv = 0
            print(f"fruit touché! vies: {self.vies}")


class Balle(ElementGraphique):
    def __init__(self, image, fenetre, depballe_x=3.3, depballe_y=3.3):
        lw = fenetre.get_width()
        lh = fenetre.get_height()
        x  = random.randint(0, lw - image.get_width())
        y  = random.randint(0, lh - image.get_height())
        super().__init__(image, fenetre, x, y)
        self.depballe_x = depballe_x
        self.depballe_y = depballe_y

    def deplacer(self):
        lw, lh = self.fenetre.get_size()
        self.rect.x += self.depballe_x
        self.rect.y += self.depballe_y
        if self.rect.x < 0:
            self.rect.x = 0
            self.depballe_x = -self.depballe_x
        if self.rect.x + self.rect.w > lw:
            self.rect.x = lw - self.rect.w
            self.depballe_x = -self.depballe_x
        if self.rect.y < 0:
            self.rect.y = 0
            self.depballe_y = -self.depballe_y
        if self.rect.y + self.rect.h > lh:
            self.rect.y = lh - self.rect.h
            self.depballe_y = -self.depballe_y


class Fruit(ElementGraphique):
    """Fruit dangereux : descend verticalement depuis le haut.
       Disparaît quand il atteint le bas de la fenêtre."""
    def __init__(self, image, fenetre):
        lw = fenetre.get_width()
        image = pygame.transform.scale(image, (50, 50))
        x = random.randint(0, lw - 50)
        y = -50  # spawn hors écran en haut
        super().__init__(image, fenetre, x, y)
        self.vitesse = random.uniform(2.0, 4.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        lh = self.fenetre.get_height()
        return self.rect.y > lh


class BonusImmunite(ElementGraphique):
    """Bonus +1 : descend verticalement depuis le haut.
       En cas de collision avec le personnage, octroie l'immunité.
       Disparaît quand il atteint le bas ou est collecté."""
    def __init__(self, fenetre):
        lw = fenetre.get_width()
        # Créer une surface dorée avec le texte "+1"
        taille = 48
        surf = pygame.Surface((taille, taille), pygame.SRCALPHA)
        # Cercle doré
        pygame.draw.circle(surf, (255, 215, 0), (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (200, 160, 0), (taille//2, taille//2), taille//2, 3)
        # Texte "+1"
        font = pygame.font.Font(None, 32)
        txt = font.render("+1", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille//2, taille//2)))

        x = random.randint(0, lw - taille)
        y = -taille  # spawn hors écran en haut
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(1.5, 3.0)
        self.collecte = False

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        lh = self.fenetre.get_height()
        return self.rect.y > lh


# ─────────────────────────── Initialisation ──────────────────────────────────

pygame.mixer.init()
pygame.init()

largeur = 640
hauteur = 480
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("SURVIVAL CHARACTER")

images = lire_images()

# Timers
td_balle          = pygame.time.get_ticks()
intervalle_balle  = 6000
nbre_max_balle    = 3   # ← réduit à 3 balles maximum

td_sauvegarde      = pygame.time.get_ticks()
intervalle_sauvegarde = 5000

td_debut_jeu      = pygame.time.get_ticks()
td_fruit          = pygame.time.get_ticks()
intervalle_fruit  = 10000  # 10 secondes

td_bonus          = pygame.time.get_ticks()
intervalle_bonus  = 15000  # bonus immunité toutes les 15 secondes

fruits = []
bonus_immunite_liste = []

# Personnage : bas, centré
perso = Perso(images["perso"], fenetre,
              x=largeur // 2 - images["perso"].get_width() // 2,
              y=hauteur - images["perso"].get_height())
perso.inv      = True
perso.comp_inv = 0

fond   = Fond(images["fond"], fenetre, vitesse=2)
balles = [Balle(images["balle"], fenetre)]

horloge = pygame.time.Clock()

game_over          = False
son_game_over_joue = False

# Afficher l'ecran d'accueil avant de commencer
ecran_accueil(fenetre, images, largeur, hauteur)

# Reinitialiser les timers apres l'ecran d'accueil
td_balle      = pygame.time.get_ticks()
td_sauvegarde = pygame.time.get_ticks()
td_fruit      = pygame.time.get_ticks()
td_bonus      = pygame.time.get_ticks()
td_debut_jeu  = pygame.time.get_ticks()

continuer = True

# ─────────────────────────── Boucle principale ───────────────────────────────

while continuer:

    horloge.tick(30)
    touches = pygame.key.get_pressed()

    if touches[pygame.K_ESCAPE]:
        continuer = False

    # Fond parallax (arrêté sur game over)
    fond.actif = not game_over
    fond.deplacer()
    fond.afficher()

    # Déclenchement game over
    if perso.vies <= 0 and not game_over:
        game_over = True
        if not son_game_over_joue:
            if images["son_game_over"]:
                images["son_game_over"].play()
            son_game_over_joue = True
            pygame.mixer.music.stop()

    # ── GAME OVER ────────────────────────────────────────────────────────────
    if game_over:
        for balle in balles:
            balle.afficher()
        for fruit in fruits:
            fruit.afficher()
        for bonus in bonus_immunite_liste:
            bonus.afficher()
        perso.afficher()

        font_go = pygame.font.Font(None, 100)
        surf = font_go.render("GAME OVER", True, (255, 0, 0))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2)))

        font_sc = pygame.font.Font(None, 60)
        surf = font_sc.render(f"Score: {perso.score}", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 + 80)))

        temps_survie = perso.score // 30
        font_t = pygame.font.Font(None, 40)
        surf = font_t.render(f"Temps de survie: {temps_survie} s", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 + 140)))

        font_r = pygame.font.Font(None, 30)
        surf = font_r.render("ESPACE pour rejouer  |  ECHAP pour quitter", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 + 200)))

    # ── JEU EN COURS ─────────────────────────────────────────────────────────
    else:
        perso.afficher()
        perso.deplacer()
        perso.score += 1

        temps_actuel = pygame.time.get_ticks()

        # Sauvegarde auto
        if temps_actuel - td_sauvegarde >= intervalle_sauvegarde:
            sauvegarder_partie(perso, balles, game_over)
            td_sauvegarde = temps_actuel

        # Nouvelle balle (max 3)
        if temps_actuel - td_balle >= intervalle_balle:
            if len(balles) < nbre_max_balle:
                balles.append(Balle(images["balle"], fenetre))
                td_balle = temps_actuel
                print(f"nouvelle balle! total: {len(balles)}")

        # Nouveau fruit toutes les 10 s (descend verticalement)
        if temps_actuel - td_fruit >= intervalle_fruit:
            type_fruit = random.choice(["fraise", "pasteque"])
            if images[type_fruit] is not None:
                nouveau_fruit = Fruit(images[type_fruit], fenetre)
                fruits.append(nouveau_fruit)
                print(f"nouveau fruit: {type_fruit}! total: {len(fruits)}")
            else:
                print(f"ERREUR: image {type_fruit} est None - PNG manquant?")
            td_fruit = temps_actuel

        # Nouveau bonus immunité toutes les 15 s
        if temps_actuel - td_bonus >= intervalle_bonus:
            bonus_immunite_liste.append(BonusImmunite(fenetre))
            td_bonus = temps_actuel
            print("Bonus immunité apparu !")

        # Deplacement + affichage balles
        for balle in balles:
            balle.deplacer()
            balle.afficher()

        # Deplacement + affichage fruits, suppression si hors écran
        fruits_restants = []
        for fruit in fruits:
            fruit.deplacer()
            if fruit.hors_ecran():
                print("fruit sorti par le bas")
                continue  # supprimé
            if perso.collide(fruit):
                perso.appliquer_demi_degats()
                # fruit consommé, ne pas le garder
            else:
                fruit.afficher()
                fruits_restants.append(fruit)
        fruits = fruits_restants

        # Deplacement + affichage bonus immunité
        bonus_restants = []
        for bonus in bonus_immunite_liste:
            bonus.deplacer()
            if bonus.hors_ecran():
                print("bonus immunité sorti par le bas")
                continue
            if perso.collide(bonus):
                perso.activer_immunite()
                print("Bonus immunité collecté !")
                # collecté, ne pas le garder
            else:
                bonus.afficher()
                bonus_restants.append(bonus)
        bonus_immunite_liste = bonus_restants

        # Collisions balles -> -1 vie (bloqué si immunité)
        for balle in balles:
            if perso.collide(balle):
                perso.appliquer_degats()

        # ── HUD ──────────────────────────────────────────────────────────────
        font_hud = pygame.font.Font(None, 36)
        fenetre.blit(font_hud.render(f"Score: {perso.score}", True, (255, 255, 255)), (10, 10))

        # Vies avec affichage demi-vie
        vies_ent     = int(perso.vies)
        demi_affiche = "½" if (perso.vies - vies_ent) >= 0.5 else ""
        fenetre.blit(font_hud.render(f"Vies: {vies_ent}{demi_affiche}", True, (255, 255, 255)), (10, 50))

        # Indicateur d'immunité active
        if perso.immunite_active:
            ticks_restants = perso.duree_immunite - perso.comp_immunite
            secondes       = ticks_restants // 30
            surf_imm = font_hud.render(f"IMMUNITE: {secondes}s", True, (255, 215, 0))
            fenetre.blit(surf_imm, surf_imm.get_rect(center=(largeur // 2, 20)))

        # Légende
        font_leg = pygame.font.Font(None, 24)
        fenetre.blit(font_leg.render("Fraise/Pasteque = -½ vie  |  +1 = Immunité", True, (255, 220, 80)), (10, 90))

    pygame.display.flip()

    # ── Événements clavier ───────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False

        if event.type == pygame.KEYDOWN:

            # Charger sauvegarde (touche L)
            if event.key == pygame.K_l and game_over:
                resultats = charger_partie(perso, images, fenetre)
                if resultats[0] is not None:
                    balles, game_over = resultats
                    fruits                = []
                    bonus_immunite_liste  = []
                    son_game_over_joue    = False
                    td_balle              = pygame.time.get_ticks()
                    td_sauvegarde         = pygame.time.get_ticks()
                    td_debut_jeu          = pygame.time.get_ticks()
                    td_fruit              = pygame.time.get_ticks()
                    td_bonus              = pygame.time.get_ticks()
                    if not game_over:
                        try:
                            pygame.mixer.music.load("musique_fond.OGG")
                            pygame.mixer.music.set_volume(0.3)
                            pygame.mixer.music.play(-1)
                        except:
                            print("musique_fond.OGG non trouvé")

            # Recommencer (ESPACE)
            if event.key == pygame.K_SPACE and game_over:
                perso.vies            = 3
                perso.score           = 0
                perso.immunite_active = False
                perso.comp_immunite   = 0
                perso.rect.x          = largeur // 2 - perso.rect.w // 2
                perso.rect.y          = hauteur - perso.rect.h
                perso.inv             = True
                perso.comp_inv        = 0
                balles                = [Balle(images["balle"], fenetre)]
                fruits                = []
                bonus_immunite_liste  = []
                game_over             = False
                son_game_over_joue    = False
                fond.y1               = 0
                fond.y2               = -hauteur
                td_balle              = pygame.time.get_ticks()
                td_debut_jeu          = pygame.time.get_ticks()
                td_fruit              = pygame.time.get_ticks()
                td_bonus              = pygame.time.get_ticks()
                try:
                    pygame.mixer.music.load("musique_fond.OGG")
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                except:
                    print("musique_fond.OGG non trouvé")

            elif event.key == pygame.K_ESCAPE:
                continuer = False

# ─────────────────────────── Fin ─────────────────────────────────────────────
pygame.mixer.music.stop()
pygame.quit()
