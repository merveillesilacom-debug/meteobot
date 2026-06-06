import pygame
import random
import json
import os
import math
from datetime import datetime


def charger_highscores():
    if not os.path.exists('highscores.json'):
        return []
    try:
        with open('highscores.json', 'r') as f:
            return json.load(f)
    except:
        return []

def sauvegarder_highscore(score):
    scores = charger_highscores()
    scores.append({'score': score, 'date': datetime.now().strftime("%d/%m/%Y")})
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    try:
        with open('highscores.json', 'w') as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde highscore: {e}")
    return scores


class Particule:
    """Petite particule d'explosion lors d'une collision."""
    def __init__(self, x, y, couleur=(255, 80, 0)):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        vitesse = random.uniform(2, 6)
        self.vx = math.cos(angle) * vitesse
        self.vy = math.sin(angle) * vitesse
        self.duree = random.randint(15, 30)
        self.age = 0
        self.couleur = couleur
        self.rayon = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # gravité légère
        self.age += 1

    def afficher(self, fenetre):
        alpha = max(0, 255 - int(255 * self.age / self.duree))
        r = min(255, self.couleur[0])
        g = max(0, self.couleur[1] - self.age * 4)
        b = self.couleur[2]
        rayon_actuel = max(1, int(self.rayon * (1 - self.age / self.duree)))
        pygame.draw.circle(fenetre, (r, g, b), (int(self.x), int(self.y)), rayon_actuel)

    def est_mort(self):
        return self.age >= self.duree


class FlashEcran:
    """Flash rouge/vert sur tout l'écran lors d'un événement."""
    def __init__(self, largeur, hauteur):
        self.surf = pygame.Surface((largeur, hauteur))
        self.actif = False
        self.alpha = 0
        self.couleur = (255, 0, 0)

    def declencher(self, couleur=(255, 0, 0)):
        self.couleur = couleur
        self.alpha = 120
        self.actif = True

    def update(self):
        if self.actif:
            self.alpha -= 8
            if self.alpha <= 0:
                self.alpha = 0
                self.actif = False

    def afficher(self, fenetre):
        if self.actif and self.alpha > 0:
            self.surf.fill(self.couleur)
            self.surf.set_alpha(self.alpha)
            fenetre.blit(self.surf, (0, 0))


def lire_images():
    images = {}

    image = pygame.image.load("perso.png").convert_alpha()
    images["perso"] = image
    image = pygame.image.load("background.jpg").convert()
    images["fond"] = image
    image = pygame.image.load("balle.png").convert_alpha()
    images["balle"] = image

    for nom in ["fraise", "pasteque"]:
        try:
            images[nom] = pygame.image.load(f"{nom}.png").convert_alpha()
        except:
            print(f"fichier {nom}.png non trouvé")
            images[nom] = None

    font = pygame.font.Font(None, 34)
    images["texte1"] = font.render('<Escape> pour quitter', True, (255, 255, 255))

    images["son_collision"] = None

    # Chargement du son game over
    try:
        images["son_game_over"] = pygame.mixer.Sound("game_over.mp3")
        images["son_game_over"].set_volume(0.8)
        print("Son game_over.mp3 chargé avec succès")
    except:
        print("game_over.mp3 non trouvé")
        images["son_game_over"] = None

    # Sons
    try:
        images["son_collision"] = pygame.mixer.Sound("collision.wav")
        images["son_collision"].set_volume(0.5)
    except:
        print("collision.wav non trouvé (optionnel)")

    try:
        images["son_bonus"] = pygame.mixer.Sound("bonus.wav")
        images["son_bonus"].set_volume(0.6)
    except:
        print("bonus.wav non trouvé (optionnel)")
        images["son_bonus"] = None

    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        print("musique_fond.OGG non trouvé")

    return images


# ______________creation ecran d'accueil________

def ecran_accueil(fenetre, images, largeur, hauteur):
    horloge = pygame.time.Clock()

    fond_accueil = pygame.Surface((largeur, hauteur))
    for y in range(hauteur):
        ratio = y / hauteur
        r = int(10 + ratio * 30)
        g = int(10 + ratio * 20)
        b = int(40 + ratio * 80)
        pygame.draw.line(fond_accueil, (r, g, b), (0, y), (largeur, y))

    font_titre  = pygame.font.Font(None, 90)
    font_sous   = pygame.font.Font(None, 36)
    font_bouton = pygame.font.Font(None, 50)
    font_hs     = pygame.font.Font(None, 28)

    perso_img = pygame.transform.scale(images["perso"], (120, 120))

    btn_w, btn_h = 260, 65
    btn_x = largeur // 2 - btn_w // 2
    btn_y = hauteur - 140
    rect_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    etoiles = [(random.randint(0, largeur), random.randint(0, hauteur),
                random.uniform(0.3, 1.5)) for _ in range(80)]
    angle_brillance = 0

    # Chargement des meilleurs scores
    highscores = charger_highscores()

    while True:
        horloge.tick(60)
        angle_brillance += 3

        fenetre.blit(fond_accueil, (0, 0))

        # Étoiles
        for ex, ey, eb in etoiles:
            lum = int(150 + 105 * abs(pygame.math.Vector2(1, 0).rotate(angle_brillance * eb).x))
            pygame.draw.circle(fenetre, (lum, lum, lum), (int(ex), int(ey)), int(eb))

        pygame.draw.line(fenetre, (255, 200, 0), (60, 70), (largeur - 60, 70), 2)

        surf_s = font_titre.render("SURVIVAL", True, (255, 220, 50))
        fenetre.blit(surf_s, surf_s.get_rect(center=(largeur // 2, 120)))
        surf_c = font_titre.render("CHARACTER", True, (255, 255, 255))
        fenetre.blit(surf_c, surf_c.get_rect(center=(largeur // 2, 205)))

        pygame.draw.line(fenetre, (255, 200, 0), (60, 240), (largeur - 60, 240), 2)

        perso_rect = perso_img.get_rect(center=(largeur // 2, 320))
        halo_r = int(75 + 10 * abs(pygame.math.Vector2(1, 0).rotate(angle_brillance).x))
        pygame.draw.circle(fenetre, (80, 80, 160), perso_rect.center, halo_r)
        fenetre.blit(perso_img, perso_rect)

        # Affichage des meilleurs scores
        if highscores:
            hs_titre = font_hs.render("🏆 MEILLEURS SCORES", True, (255, 215, 0))
            fenetre.blit(hs_titre, hs_titre.get_rect(center=(largeur - 140, 280)))
            for i, hs in enumerate(highscores[:3]):
                couleurs_hs = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
                txt = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, couleurs_hs[i])
                fenetre.blit(txt, txt.get_rect(center=(largeur - 140, 305 + i * 25)))

        # Bouton JOUER
        mx, my = pygame.mouse.get_pos()
        survol = rect_btn.collidepoint(mx, my)
        couleur_btn  = (50, 200, 100) if survol else (30, 140, 70)
        couleur_bord = (150, 255, 150) if survol else (80, 200, 100)
        pygame.draw.rect(fenetre, couleur_btn,  rect_btn, border_radius=14)
        pygame.draw.rect(fenetre, couleur_bord, rect_btn, width=3, border_radius=14)

        surf_btn = font_bouton.render("JOUER", True, (255, 255, 255))
        fenetre.blit(surf_btn, surf_btn.get_rect(center=rect_btn.center))

        surf_esc = font_sous.render("ECHAP pour quitter", True, (180, 180, 180))
        fenetre.blit(surf_esc, surf_esc.get_rect(center=(largeur // 2, hauteur - 30)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_btn.collidepoint(event.pos):
                    return


# ──────Sauvegarde / Chargement ───────────────

def sauvegarder_partie(perso, balles, game_over):
    donnees = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'perso': {
            'x': perso.rect.x, 'y': perso.rect.y,
            'vies': perso.vies, 'score': perso.score,
            'inv': perso.inv, 'comp_inv': perso.comp_inv
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
            balle.rect.x     = bd['x']
            balle.rect.y     = bd['y']
            balle.depballe_x = bd['depballe_x']
            balle.depballe_y = bd['depballe_y']
            balles.append(balle)
        game_over = donnees['game_over']
        print(f"Partie chargée depuis {donnees['timestamp']}")
        return balles, game_over
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None, False


# ──────── Classes ───────

class ElementGraphique:
    def __init__(self, image, fenetre, x=0, y=0):
        self.image   = image
        self.fenetre = fenetre
        self.rect    = image.get_rect()
        self.rect.x  = x
        self.rect.y  = y

    def afficher(self):
        self.fenetre.blit(self.image, self.rect)

    def collide(self, other):
        return self.rect.colliderect(other.rect)


class Fond:
    """Fond parallax défilant vers le bas."""
    def __init__(self, image, fenetre, vitesse=2):
        self.fenetre = fenetre
        self.vitesse = vitesse
        lw = fenetre.get_width()
        lh = fenetre.get_height()
        self.image = pygame.transform.scale(image, (lw, lh))
        self.y1    = 0
        self.y2    = -lh
        self.haut  = lh
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
        self.vies            = 3
        self.inv             = False
        self.comp_inv        = 0
        self.score           = 0
        self.immunite_active = False
        self.comp_immunite   = 0
        self.duree_immunite  = 300
        # Ralentissement bonus
        self.ralenti_actif   = False
        self.comp_ralenti    = 0
        self.duree_ralenti   = 180  # ~6s à 30fps

    def deplacer(self):
        vitesse_dep = 3
        touches = pygame.key.get_pressed()
        if touches[pygame.K_DOWN]:
            self.rect.y += vitesse_dep
        if touches[pygame.K_UP]:
            self.rect.y -= vitesse_dep
        if touches[pygame.K_LEFT]:
            self.rect.x -= vitesse_dep
        if touches[pygame.K_RIGHT]:
            self.rect.x += vitesse_dep
        self.rect.x = max(0, min(self.rect.x, largeur - self.rect.w))
        self.rect.y = max(0, min(self.rect.y, hauteur - self.rect.h))

        # Invincibilité courte après dégât
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

        # Ralentissement
        if self.ralenti_actif:
            self.comp_ralenti += 1
            if self.comp_ralenti >= self.duree_ralenti:
                self.ralenti_actif = False
                self.comp_ralenti  = 0
                print("Ralentissement terminé !")

    def afficher(self):
        """Affichage avec clignotement lisible pendant l'invincibilité."""
        if self.inv and (self.comp_inv // 5) % 2 == 0:
            img_temp = self.image.copy()
            img_temp.set_alpha(80)
            self.fenetre.blit(img_temp, self.rect)
        elif self.immunite_active:
            # Halo doré lors de l'immunité
            pygame.draw.circle(
                self.fenetre, (255, 215, 0),
                self.rect.center,
                max(self.rect.w, self.rect.h) // 2 + 8,
                3
            )
            self.fenetre.blit(self.image, self.rect)
        else:
            self.fenetre.blit(self.image, self.rect)

    def activer_immunite(self):
        self.immunite_active = True
        self.comp_immunite   = 0

    def activer_ralentissement(self):
        self.ralenti_actif = True
        self.comp_ralenti  = 0

    def appliquer_degats(self):
        if self.immunite_active:
            return
        if not self.inv:
            self.vies    -= 1
            self.inv      = True
            self.comp_inv = 0
            print(f"Aïe! vies: {self.vies}")
            return True  # dégât infligé
        return False

    def appliquer_demi_degats(self):
        if self.immunite_active:
            return
        if not self.inv:
            self.vies    -= 0.5
            self.inv      = True
            self.comp_inv = 0
            print(f"Fruit touché! vies: {self.vies}")
            return True
        return False


class Balle(ElementGraphique):
    def __init__(self, image, fenetre, depballe_x=3.3, depballe_y=3.3):
        lw = fenetre.get_width()
        lh = fenetre.get_height()
        x  = random.randint(0, lw - image.get_width())
        y  = random.randint(0, lh - image.get_height())
        super().__init__(image, fenetre, x, y)
        self.depballe_x = depballe_x
        self.depballe_y = depballe_y

    def deplacer(self, facteur_vitesse=1.0, ralenti=False):
        lw, lh = self.fenetre.get_size()
        mult = 0.4 if ralenti else facteur_vitesse
        self.rect.x += self.depballe_x * mult
        self.rect.y += self.depballe_y * mult
        if self.rect.x < 0:
            self.rect.x      = 0
            self.depballe_x  = abs(self.depballe_x) + random.uniform(-0.3, 0.3)
        if self.rect.x + self.rect.w > lw:
            self.rect.x      = lw - self.rect.w
            self.depballe_x  = -(abs(self.depballe_x) + random.uniform(-0.3, 0.3))
        if self.rect.y < 0:
            self.rect.y      = 0
            self.depballe_y  = abs(self.depballe_y) + random.uniform(-0.3, 0.3)
        if self.rect.y + self.rect.h > lh:
            self.rect.y      = lh - self.rect.h
            self.depballe_y  = -(abs(self.depballe_y) + random.uniform(-0.3, 0.3))


class Fruit(ElementGraphique):
    def __init__(self, image, fenetre):
        lw    = fenetre.get_width()
        image = pygame.transform.scale(image, (50, 50))
        x     = random.randint(0, lw - 50)
        y     = -50
        super().__init__(image, fenetre, x, y)
        self.vitesse = random.uniform(2.0, 4.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class BonusImmunite(ElementGraphique):
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 48
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 215, 0),   (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (200, 160, 0),   (taille//2, taille//2), taille//2, 3)
        font = pygame.font.Font(None, 32)
        txt  = font.render("+1", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille//2, taille//2)))
        x = random.randint(0, lw - taille)
        y = -taille
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(1.5, 3.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class BonusRalenti(ElementGraphique):
    """Bonus bleu : ralentit toutes les balles pendant quelques secondes."""
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 48
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (50, 150, 255),  (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (30, 100, 200),  (taille//2, taille//2), taille//2, 3)
        font = pygame.font.Font(None, 26)
        txt  = font.render("SLOW", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille//2, taille//2)))
        x = random.randint(0, lw - taille)
        y = -taille
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(1.5, 3.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class BonusCœur(ElementGraphique):
    """Bonus rose : redonne une demi-vie."""
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 48
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 80, 130),  (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (200, 40, 90),   (taille//2, taille//2), taille//2, 3)
        font = pygame.font.Font(None, 34)
        txt  = font.render("+½", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille//2, taille//2)))
        x = random.randint(0, lw - taille)
        y = -taille
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(1.5, 3.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


#─────── Barre de vie graphique ─────────

def dessiner_barre_vie(fenetre, vies, max_vies, x, y, largeur_barre=200, hauteur_barre=22):
    ratio   = max(0, vies / max_vies)
    # Fond de la barre
    pygame.draw.rect(fenetre, (80, 0, 0),   (x, y, largeur_barre, hauteur_barre), border_radius=8)
    # Remplissage
    if ratio > 0:
        couleur = (
            int(255 * (1 - ratio)),
            int(220 * ratio),
            0
        )
        fill_w = int(largeur_barre * ratio)
        pygame.draw.rect(fenetre, couleur, (x, y, fill_w, hauteur_barre), border_radius=8)
    # Contour
    pygame.draw.rect(fenetre, (200, 200, 200), (x, y, largeur_barre, hauteur_barre), width=2, border_radius=8)
    # Texte
    font_v = pygame.font.Font(None, 24)
    vies_ent     = int(vies)
    demi_affiche = "½" if (vies - vies_ent) >= 0.5 else ""
    txt = font_v.render(f"Vies: {vies_ent}{demi_affiche} / {int(max_vies)}", True, (255, 255, 255))
    fenetre.blit(txt, (x + 5, y + 3))


#───────── Annonce de vague ───────────────────────

def afficher_annonce_vague(fenetre, largeur, hauteur, numero_vague):
    font_vague = pygame.font.Font(None, 80)
    surf = font_vague.render(f"VAGUE  {numero_vague}", True, (255, 220, 50))
    fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2)))
    pygame.display.flip()
    pygame.time.wait(1200)


# ─────────────────────────── Initialisation ──────────────────────────────────

pygame.mixer.init()
pygame.init()

# Fenêtre plus grande : 1024x768
largeur = 1024
hauteur = 768
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("SURVIVAL CHARACTER")

images = lire_images()

# Timers
td_balle             = pygame.time.get_ticks()
intervalle_balle     = 6000
nbre_max_balle       = 5

td_sauvegarde        = pygame.time.get_ticks()
intervalle_sauvegarde = 5000

td_debut_jeu         = pygame.time.get_ticks()
td_fruit             = pygame.time.get_ticks()
intervalle_fruit     = 10000

td_bonus             = pygame.time.get_ticks()
intervalle_bonus     = 15000

td_bonus_ralenti     = pygame.time.get_ticks()
intervalle_bonus_ralenti = 20000

td_bonus_coeur       = pygame.time.get_ticks()
intervalle_bonus_coeur   = 25000

fruits               = []
bonus_immunite_liste = []
bonus_ralenti_liste  = []
bonus_coeur_liste    = []
particules           = []

perso = Perso(images["perso"], fenetre,
              x=largeur // 2 - images["perso"].get_width() // 2,
              y=hauteur - images["perso"].get_height())
perso.inv      = True
perso.comp_inv = 0

fond   = Fond(images["fond"], fenetre, vitesse=2)
balles = [Balle(images["balle"], fenetre)]

horloge = pygame.time.Clock()

flash   = FlashEcran(largeur, hauteur)

game_over          = False
son_game_over_joue = False
en_pause           = False

vague_actuelle    = 1
score_prochaine_vague = 1000  # nouvelle vague tous les 1000 pts

# Écran d'accueil
ecran_accueil(fenetre, images, largeur, hauteur)
afficher_annonce_vague(fenetre, largeur, hauteur, vague_actuelle)

# Réinitialiser les timers
td_balle      = pygame.time.get_ticks()
td_sauvegarde = pygame.time.get_ticks()
td_fruit      = pygame.time.get_ticks()
td_bonus      = pygame.time.get_ticks()
td_bonus_ralenti = pygame.time.get_ticks()
td_bonus_coeur   = pygame.time.get_ticks()
td_debut_jeu  = pygame.time.get_ticks()

continuer = True

#────── Boucle principale ───────────────

while continuer:

    horloge.tick(30)
    touches = pygame.key.get_pressed()

    if touches[pygame.K_ESCAPE]:
        continuer = False

    # Calcul de la difficulté progressive
    temps_ecoule       = (pygame.time.get_ticks() - td_debut_jeu) / 1000.0
    facteur_vitesse    = 1.0 + (temps_ecoule / 30.0) * 0.5   # +50% toutes les 30s
    facteur_vitesse    = min(facteur_vitesse, 3.0)            # cap à x3

    fond.actif = not game_over
    fond.deplacer()
    fond.afficher()

    # ── PAUSE ─────────────────────────────────────────────────────────────────
    if en_pause and not game_over:
        # Afficher un overlay semi-transparent
        surf_pause = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
        surf_pause.fill((0, 0, 0, 140))
        fenetre.blit(surf_pause, (0, 0))
        font_pause = pygame.font.Font(None, 100)
        txt_pause  = font_pause.render("PAUSE", True, (255, 255, 255))
        fenetre.blit(txt_pause, txt_pause.get_rect(center=(largeur // 2, hauteur // 2 - 40)))
        font_hint = pygame.font.Font(None, 36)
        txt_hint  = font_hint.render("Appuyez sur U pour reprendre", True, (200, 200, 200))
        fenetre.blit(txt_hint, txt_hint.get_rect(center=(largeur // 2, hauteur // 2 + 40)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continuer = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    en_pause = False
                    pygame.mixer.music.unpause()
                elif event.key == pygame.K_ESCAPE:
                    continuer = False
        horloge.tick(30)
        continue

    # Déclenchement game over
    if perso.vies <= 0 and not game_over:
        game_over = True
        sauvegarder_highscore(perso.score)
        if not son_game_over_joue:
            pygame.mixer.music.stop()           # arrêt musique de fond en premier
            if images["son_game_over"]:
                images["son_game_over"].play()  # lecture du son game over
            son_game_over_joue = True

    # ── GAME OVER ─
    if game_over:
        for balle in balles:
            balle.afficher()
        for fruit in fruits:
            fruit.afficher()
        for bonus in bonus_immunite_liste:
            bonus.afficher()
        perso.afficher()

        font_go = pygame.font.Font(None, 100)
        surf    = font_go.render("GAME OVER", True, (255, 0, 0))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 - 60)))

        font_sc = pygame.font.Font(None, 60)
        surf    = font_sc.render(f"Score: {perso.score}", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 + 20)))

        temps_survie = perso.score // 30
        font_t = pygame.font.Font(None, 40)
        surf   = font_t.render(f"Temps de survie: {temps_survie} s", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 + 80)))

        # Meilleurs scores sur l'écran game over
        highscores = charger_highscores()
        font_hs = pygame.font.Font(None, 32)
        surf    = font_hs.render("🏆 TOP SCORES", True, (255, 215, 0))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur // 2 + 130)))
        for i, hs in enumerate(highscores[:3]):
            couleurs_hs = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
            txt = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, couleurs_hs[i])
            fenetre.blit(txt, txt.get_rect(center=(largeur // 2, hauteur // 2 + 160 + i * 28)))

        font_r = pygame.font.Font(None, 30)
        surf   = font_r.render("ESPACE pour rejouer  |  ECHAP pour quitter", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur // 2, hauteur - 40)))

    # ── JEU EN COURS ─────────────────────────────────────────────────────────
    else:
        perso.afficher()
        perso.deplacer()
        perso.score += 1

        temps_actuel = pygame.time.get_ticks()

        # ── Vagues ──
        if perso.score >= score_prochaine_vague:
            vague_actuelle        += 1
            score_prochaine_vague += 1000
            afficher_annonce_vague(fenetre, largeur, hauteur, vague_actuelle)
            # Réinitialiser le fond pour éviter artefact
            td_balle = pygame.time.get_ticks()

        # Sauvegarde auto
        if temps_actuel - td_sauvegarde >= intervalle_sauvegarde:
            sauvegarder_partie(perso, balles, game_over)
            td_sauvegarde = temps_actuel

        # Nouvelle balle (max augmente avec les vagues)
        max_balles_vague = min(3 + vague_actuelle, nbre_max_balle)
        if temps_actuel - td_balle >= intervalle_balle:
            if len(balles) < max_balles_vague:
                vitesse_nouvelle = 3.3 * facteur_vitesse
                balles.append(Balle(images["balle"], fenetre,
                                    depballe_x=random.choice([-1, 1]) * vitesse_nouvelle,
                                    depballe_y=random.choice([-1, 1]) * vitesse_nouvelle))
                td_balle = temps_actuel

        # Fruits
        if temps_actuel - td_fruit >= intervalle_fruit:
            type_fruit = random.choice(["fraise", "pasteque"])
            if images[type_fruit] is not None:
                fruits.append(Fruit(images[type_fruit], fenetre))
            td_fruit = temps_actuel

        # Bonus immunité
        if temps_actuel - td_bonus >= intervalle_bonus:
            bonus_immunite_liste.append(BonusImmunite(fenetre))
            td_bonus = temps_actuel

        # Bonus ralentissement
        if temps_actuel - td_bonus_ralenti >= intervalle_bonus_ralenti:
            bonus_ralenti_liste.append(BonusRalenti(fenetre))
            td_bonus_ralenti = temps_actuel

        # Bonus cœur
        if temps_actuel - td_bonus_coeur >= intervalle_bonus_coeur:
            bonus_coeur_liste.append(BonusCœur(fenetre))
            td_bonus_coeur = temps_actuel

        # Balles (avec difficulté progressive et ralentissement)
        for balle in balles:
            balle.deplacer(facteur_vitesse=facteur_vitesse, ralenti=perso.ralenti_actif)
            balle.afficher()

        # Fruits
        fruits_restants = []
        for fruit in fruits:
            fruit.deplacer()
            if fruit.hors_ecran():
                continue
            if perso.collide(fruit):
                touche = perso.appliquer_demi_degats()
                if touche:
                    flash.declencher((255, 100, 0))
                    if images.get("son_collision"):
                        images["son_collision"].play()
                    for _ in range(10):
                        particules.append(Particule(perso.rect.centerx, perso.rect.centery, (255, 100, 0)))
            else:
                fruit.afficher()
                fruits_restants.append(fruit)
        fruits = fruits_restants

        # Bonus immunité
        bonus_restants = []
        for bonus in bonus_immunite_liste:
            bonus.deplacer()
            if bonus.hors_ecran():
                continue
            if perso.collide(bonus):
                perso.activer_immunite()
                flash.declencher((255, 215, 0))
                if images.get("son_bonus"):
                    images["son_bonus"].play()
                for _ in range(15):
                    particules.append(Particule(perso.rect.centerx, perso.rect.centery, (255, 215, 0)))
            else:
                bonus.afficher()
                bonus_restants.append(bonus)
        bonus_immunite_liste = bonus_restants

        # Bonus ralentissement
        ralenti_restants = []
        for bonus in bonus_ralenti_liste:
            bonus.deplacer()
            if bonus.hors_ecran():
                continue
            if perso.collide(bonus):
                perso.activer_ralentissement()
                flash.declencher((50, 150, 255))
                if images.get("son_bonus"):
                    images["son_bonus"].play()
                for _ in range(15):
                    particules.append(Particule(perso.rect.centerx, perso.rect.centery, (50, 150, 255)))
            else:
                bonus.afficher()
                ralenti_restants.append(bonus)
        bonus_ralenti_liste = ralenti_restants

        # Bonus cœur
        coeur_restants = []
        for bonus in bonus_coeur_liste:
            bonus.deplacer()
            if bonus.hors_ecran():
                continue
            if perso.collide(bonus):
                perso.vies = min(perso.vies + 0.5, 3)
                flash.declencher((255, 80, 130))
                if images.get("son_bonus"):
                    images["son_bonus"].play()
                for _ in range(15):
                    particules.append(Particule(perso.rect.centerx, perso.rect.centery, (255, 80, 130)))
            else:
                bonus.afficher()
                coeur_restants.append(bonus)
        bonus_coeur_liste = coeur_restants

        # Collisions balles
        for balle in balles:
            if perso.collide(balle):
                touche = perso.appliquer_degats()
                if touche:
                    flash.declencher((255, 0, 0))
                    if images.get("son_collision"):
                        images["son_collision"].play()
                    for _ in range(20):
                        particules.append(Particule(perso.rect.centerx, perso.rect.centery))

        # Particules
        particules_vivantes = []
        for p in particules:
            p.update()
            p.afficher(fenetre)
            if not p.est_mort():
                particules_vivantes.append(p)
        particules = particules_vivantes

        # Flash écran
        flash.update()
        flash.afficher(fenetre)

        # ── HUD ──────
        font_hud = pygame.font.Font(None, 36)
        font_leg = pygame.font.Font(None, 24)

        # Score et vague
        fenetre.blit(font_hud.render(f"Score: {perso.score}", True, (255, 255, 255)), (10, 10))
        fenetre.blit(font_hud.render(f"Vague: {vague_actuelle}", True, (255, 220, 50)), (10, 45))

        # Difficulté
        pct_diff = int((facteur_vitesse - 1.0) / 2.0 * 100)
        surf_diff = font_leg.render(f"Difficulté: {pct_diff}%", True, (200, 200, 255))
        fenetre.blit(surf_diff, (10, 80))

        # Barre de vie graphique
        dessiner_barre_vie(fenetre, perso.vies, 3, 10, 105, largeur_barre=200)

        # Indicateur immunité
        if perso.immunite_active:
            ticks_restants = perso.duree_immunite - perso.comp_immunite
            secondes       = ticks_restants // 30
            surf_imm = font_hud.render(f"⭐ IMMUNITE: {secondes}s", True, (255, 215, 0))
            fenetre.blit(surf_imm, surf_imm.get_rect(center=(largeur // 2, 20)))

        # Indicateur ralentissement
        if perso.ralenti_actif:
            ticks_restants = perso.duree_ralenti - perso.comp_ralenti
            secondes       = ticks_restants // 30
            surf_ral = font_hud.render(f"❄ SLOW: {secondes}s", True, (50, 200, 255))
            fenetre.blit(surf_ral, surf_ral.get_rect(center=(largeur // 2, 55)))

        # Légende des bonus
        fenetre.blit(font_leg.render(
            "🍓 = -½ vie  |  ⭐ = Immunité  |  ❄ = Ralentit balles  |  💗 = +½ vie",
            True, (255, 220, 80)), (10, hauteur - 30))

    pygame.display.flip()

    # ── Événements clavier ───────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False

        if event.type == pygame.KEYDOWN:
            # Pause
            if event.key == pygame.K_p and not game_over:
                en_pause = True
                pygame.mixer.music.pause()

            # Charger sauvegarde
            if event.key == pygame.K_l and game_over:
                resultats = charger_partie(perso, images, fenetre)
                if resultats[0] is not None:
                    balles, game_over = resultats
                    fruits              = []
                    bonus_immunite_liste  = []
                    bonus_ralenti_liste   = []
                    bonus_coeur_liste     = []
                    son_game_over_joue    = False
                    td_balle = td_sauvegarde = td_debut_jeu = pygame.time.get_ticks()
                    td_fruit = td_bonus = td_bonus_ralenti = td_bonus_coeur = pygame.time.get_ticks()
                    if not game_over:
                        try:
                            pygame.mixer.music.load("musique_fond.OGG")
                            pygame.mixer.music.set_volume(0.3)
                            pygame.mixer.music.play(-1)
                        except:
                            pass

            # Rejouer
            if event.key == pygame.K_SPACE and game_over:
                perso.vies            = 3
                perso.score           = 0
                perso.immunite_active = False
                perso.ralenti_actif   = False
                perso.comp_immunite   = 0
                perso.comp_ralenti    = 0
                perso.rect.x          = largeur // 2 - perso.rect.w // 2
                perso.rect.y          = hauteur - perso.rect.h
                perso.inv             = True
                perso.comp_inv        = 0
                balles                = [Balle(images["balle"], fenetre)]
                fruits                = []
                bonus_immunite_liste  = []
                bonus_ralenti_liste   = []
                bonus_coeur_liste     = []
                particules            = []
                game_over             = False
                son_game_over_joue    = False
                en_pause              = False
                fond.y1               = 0
                fond.y2               = -hauteur
                vague_actuelle        = 1
                score_prochaine_vague = 1000
                td_balle = td_debut_jeu = td_fruit = pygame.time.get_ticks()
                td_bonus = td_bonus_ralenti = td_bonus_coeur = pygame.time.get_ticks()
                afficher_annonce_vague(fenetre, largeur, hauteur, vague_actuelle)
                try:
                    pygame.mixer.music.load("musique_fond.OGG")
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                except:
                    pass

            elif event.key == pygame.K_ESCAPE:
                continuer = False

# ─────────────────────────── Fin ─────────────────────────────────────────────
pygame.mixer.music.stop()
pygame.quit()
