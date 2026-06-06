import pygame
import random
import json
import os
import math
from datetime import datetime

LARGEUR, HAUTEUR = 1024, 768
FPS = 30

largeur = LARGEUR
hauteur = HAUTEUR


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
        return True
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")
        return False

def charger_partie(perso, images, fenetre):
    if not os.path.exists('sauvegarde.json'):
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
        return balles, donnees['game_over']
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None, False


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
        self.ralenti_actif   = False
        self.comp_ralenti    = 0
        self.duree_ralenti   = 180

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

        if self.inv:
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = False

        if self.immunite_active:
            self.comp_immunite += 1
            if self.comp_immunite >= self.duree_immunite:
                self.immunite_active = False
                self.comp_immunite   = 0

        if self.ralenti_actif:
            self.comp_ralenti += 1
            if self.comp_ralenti >= self.duree_ralenti:
                self.ralenti_actif = False
                self.comp_ralenti  = 0

    def afficher(self):
        if self.inv and (self.comp_inv // 5) % 2 == 0:
            img_temp = self.image.copy()
            img_temp.set_alpha(80)
            self.fenetre.blit(img_temp, self.rect)
        elif self.immunite_active:
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
            return True
        return False

    def appliquer_demi_degats(self):
        if self.immunite_active:
            return
        if not self.inv:
            self.vies    -= 0.5
            self.inv      = True
            self.comp_inv = 0
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
            self.rect.x     = 0
            self.depballe_x = abs(self.depballe_x) + random.uniform(-0.3, 0.3)
        if self.rect.x + self.rect.w > lw:
            self.rect.x     = lw - self.rect.w
            self.depballe_x = -(abs(self.depballe_x) + random.uniform(-0.3, 0.3))
        if self.rect.y < 0:
            self.rect.y     = 0
            self.depballe_y = abs(self.depballe_y) + random.uniform(-0.3, 0.3)
        if self.rect.y + self.rect.h > lh:
            self.rect.y     = lh - self.rect.h
            self.depballe_y = -(abs(self.depballe_y) + random.uniform(-0.3, 0.3))


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
        pygame.draw.circle(surf, (255, 215, 0), (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (200, 160, 0), (taille//2, taille//2), taille//2, 3)
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
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 48
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (50, 150, 255), (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (30, 100, 200), (taille//2, taille//2), taille//2, 3)
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
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 48
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 80, 130), (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (200, 40, 90),  (taille//2, taille//2), taille//2, 3)
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



class Bombe(ElementGraphique):
    def __init__(self, image, fenetre, vitesse):
        lw    = fenetre.get_width()
        x     = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse = vitesse

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class Particule:
    def __init__(self, x, y, couleur=(255, 80, 0)):
        self.x = x
        self.y = y
        angle   = random.uniform(0, 2 * math.pi)
        vitesse = random.uniform(2, 6)
        self.vx     = math.cos(angle) * vitesse
        self.vy     = math.sin(angle) * vitesse
        self.duree  = random.randint(15, 30)
        self.age    = 0
        self.couleur= couleur
        self.rayon  = random.randint(3, 7)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.2
        self.age += 1

    def afficher(self, fenetre):
        r = min(255, self.couleur[0])
        g = max(0, self.couleur[1] - self.age * 4)
        b = self.couleur[2]
        rayon_actuel = max(1, int(self.rayon * (1 - self.age / self.duree)))
        pygame.draw.circle(fenetre, (r, g, b), (int(self.x), int(self.y)), rayon_actuel)

    def est_mort(self):
        return self.age >= self.duree


class FlashEcran:
    def __init__(self, largeur, hauteur):
        self.surf   = pygame.Surface((largeur, hauteur))
        self.actif  = False
        self.alpha  = 0
        self.couleur= (255, 0, 0)

    def declencher(self, couleur=(255, 0, 0)):
        self.couleur = couleur
        self.alpha   = 120
        self.actif   = True

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
    images["perso"] = pygame.image.load("perso.png").convert_alpha()
    images["fond"]  = pygame.image.load("background.jpg").convert()
    images["balle"] = pygame.image.load("balle.png").convert_alpha()

    for nom in ["fraise", "pasteque"]:
        try:
            images[nom] = pygame.image.load(f"{nom}.png").convert_alpha()
        except:
            print(f"fichier {nom}.png non trouvé")
            images[nom] = None

    for cle, fichier, volume in [
        ("son_collision", "collision.wav",  0.5),
        ("son_bonus",     "bonus.wav",      0.6),
        ("son_game_over", "gameover.wav",   0.8),
    ]:
        try:
            images[cle] = pygame.mixer.Sound(fichier)
            images[cle].set_volume(volume)
        except:
            print(f"{fichier} non trouvé")
            images[cle] = None

    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        print("musique_fond.OGG non trouvé")

    for cle_fond, fichier_fond in [("fond_v2", "landscape.png"), ("fond_v3", "Background3.jpg")]:
        try:
            images[cle_fond] = pygame.image.load(fichier_fond).convert()
        except:
            images[cle_fond] = images["fond"]

    try:
        images["bombe"] = pygame.transform.scale(pygame.image.load("g5715.png").convert_alpha(), (60, 80))
    except:
        images["bombe"] = None


    return images


def jouer_son(images, cle):
    if images.get(cle):
        images[cle].play()

def lancer_musique():
    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        pass

def lancer_particules(liste, cx, cy, couleur, n=15):
    for _ in range(n):
        liste.append(Particule(cx, cy, couleur))

def afficher_texte_centre(fenetre, texte, taille, couleur, cy):
    font = pygame.font.Font(None, taille)
    surf = font.render(texte, True, couleur)
    fenetre.blit(surf, surf.get_rect(center=(LARGEUR // 2, cy)))

def afficher_annonce_vague(fenetre, numero_vague):
    afficher_texte_centre(fenetre, f"VAGUE  {numero_vague}", 80, (255, 220, 50), HAUTEUR // 2)
    pygame.display.flip()
    pygame.time.wait(1200)

def dessiner_barre_vie(fenetre, vies, max_vies, x=10, y=105, largeur_barre=200, hauteur_barre=22):
    ratio = max(0, vies / max_vies)
    pygame.draw.rect(fenetre, (80, 0, 0), (x, y, largeur_barre, hauteur_barre), border_radius=8)
    if ratio > 0:
        couleur = (int(255 * (1 - ratio)), int(220 * ratio), 0)
        pygame.draw.rect(fenetre, couleur, (x, y, int(largeur_barre * ratio), hauteur_barre), border_radius=8)
    pygame.draw.rect(fenetre, (200, 200, 200), (x, y, largeur_barre, hauteur_barre), width=2, border_radius=8)
    font = pygame.font.Font(None, 24)
    ent  = int(vies)
    demi = "½" if (vies - ent) >= 0.5 else ""
    fenetre.blit(font.render(f"Vies: {ent}{demi} / {int(max_vies)}", True, (255, 255, 255)), (x + 5, y + 3))

def gerer_objets(liste, perso, flash, images, particules, on_collision):
    restants = []
    for obj in liste:
        obj.deplacer()
        if obj.hors_ecran():
            continue
        if perso.collide(obj):
            on_collision(obj)
        else:
            obj.afficher()
            restants.append(obj)
    return restants


def ecran_accueil(fenetre, images):
    horloge = pygame.time.Clock()

    fond_accueil = pygame.Surface((LARGEUR, HAUTEUR))
    for y in range(HAUTEUR):
        ratio = y / HAUTEUR
        r = int(10 + ratio * 30)
        g = int(10 + ratio * 20)
        b = int(40 + ratio * 80)
        pygame.draw.line(fond_accueil, (r, g, b), (0, y), (LARGEUR, y))

    font_titre  = pygame.font.Font(None, 90)
    font_sous   = pygame.font.Font(None, 36)
    font_bouton = pygame.font.Font(None, 50)
    font_hs     = pygame.font.Font(None, 28)

    perso_img = pygame.transform.scale(images["perso"], (120, 120))

    btn_w, btn_h = 260, 65
    btn_x = LARGEUR // 2 - btn_w // 2
    btn_y = HAUTEUR - 140
    rect_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    etoiles = [(random.randint(0, LARGEUR), random.randint(0, HAUTEUR),
                random.uniform(0.3, 1.5)) for _ in range(80)]
    angle_brillance = 0
    highscores = charger_highscores()

    while True:
        horloge.tick(60)
        angle_brillance += 3

        fenetre.blit(fond_accueil, (0, 0))

        for ex, ey, eb in etoiles:
            lum = int(150 + 105 * abs(math.cos(math.radians(angle_brillance * eb))))
            pygame.draw.circle(fenetre, (lum, lum, lum), (int(ex), int(ey)), int(eb))

        pygame.draw.line(fenetre, (255, 200, 0), (60, 70), (LARGEUR - 60, 70), 2)

        for texte, couleur, cy in [("SURVIVAL", (255, 220, 50), 120), ("CHARACTER", (255, 255, 255), 205)]:
            surf = font_titre.render(texte, True, couleur)
            fenetre.blit(surf, surf.get_rect(center=(LARGEUR // 2, cy)))

        pygame.draw.line(fenetre, (255, 200, 0), (60, 240), (LARGEUR - 60, 240), 2)

        perso_rect = perso_img.get_rect(center=(LARGEUR // 2, 320))
        halo_r = int(75 + 10 * abs(math.cos(math.radians(angle_brillance))))
        pygame.draw.circle(fenetre, (80, 80, 160), perso_rect.center, halo_r)
        fenetre.blit(perso_img, perso_rect)

        if highscores:
            hs_titre = font_hs.render("MEILLEURS SCORES", True, (255, 215, 0))
            fenetre.blit(hs_titre, hs_titre.get_rect(center=(LARGEUR - 140, 280)))
            for i, hs in enumerate(highscores[:3]):
                c = [(255, 215, 0), (192, 192, 192), (205, 127, 50)][i]
                txt = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, c)
                fenetre.blit(txt, txt.get_rect(center=(LARGEUR - 140, 305 + i * 25)))

        mx, my = pygame.mouse.get_pos()
        survol = rect_btn.collidepoint(mx, my)
        pygame.draw.rect(fenetre, (50, 200, 100) if survol else (30, 140, 70),   rect_btn, border_radius=14)
        pygame.draw.rect(fenetre, (150, 255, 150) if survol else (80, 200, 100), rect_btn, width=3, border_radius=14)
        surf_btn = font_bouton.render("JOUER", True, (255, 255, 255))
        fenetre.blit(surf_btn, surf_btn.get_rect(center=rect_btn.center))

        surf_esc = font_sous.render("ECHAP pour quitter", True, (180, 180, 180))
        fenetre.blit(surf_esc, surf_esc.get_rect(center=(LARGEUR // 2, HAUTEUR - 30)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); exit()
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_btn.collidepoint(event.pos):
                    return


def reinitialiser_jeu(perso, images, fenetre):
    perso.vies            = 3
    perso.score           = 0
    perso.immunite_active = False
    perso.ralenti_actif   = False
    perso.comp_immunite   = 0
    perso.comp_ralenti    = 0
    perso.rect.x          = LARGEUR // 2 - perso.rect.w // 2
    perso.rect.y          = HAUTEUR - perso.rect.h
    perso.inv             = True
    perso.comp_inv        = 0
    balles = [Balle(images["balle"], fenetre)]
    now = pygame.time.get_ticks()
    timers = {k: now for k in ("balle", "sauvegarde", "debut", "fruit", "bonus", "ralenti", "coeur")}
    return balles, timers


pygame.mixer.init()
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("SURVIVAL CHARACTER")

images = lire_images()

perso = Perso(images["perso"], fenetre,
              x=LARGEUR // 2 - images["perso"].get_width() // 2,
              y=HAUTEUR - images["perso"].get_height())
perso.inv      = True
perso.comp_inv = 0

fond    = Fond(images["fond"], fenetre, vitesse=2)
flash   = FlashEcran(LARGEUR, HAUTEUR)
horloge = pygame.time.Clock()

ecran_accueil(fenetre, images)

balles, timers = reinitialiser_jeu(perso, images, fenetre)
fruits              = []
bonus_immunite_liste= []
bonus_ralenti_liste = []
bonus_coeur_liste   = []
particules          = []

vague_actuelle        = 1
score_prochaine_vague = 1000
game_over             = False
son_game_over_joue    = False
en_pause              = False
nouveau_fond_img      = None
nouveau_fond_y        = -HAUTEUR
bombes                = []
td_bombe              = 0


nbre_max_balle        = 5

afficher_annonce_vague(fenetre, vague_actuelle)

continuer = True

while continuer:
    horloge.tick(FPS)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                continuer = False

            if event.key == pygame.K_p and not game_over:
                en_pause = True
                pygame.mixer.music.pause()

            if game_over:
                if event.key == pygame.K_SPACE:
                    balles, timers = reinitialiser_jeu(perso, images, fenetre)
                    fruits               = []
                    bonus_immunite_liste = []
                    bonus_ralenti_liste  = []
                    bonus_coeur_liste    = []
                    particules           = []
                    game_over            = False
                    son_game_over_joue   = False
                    en_pause             = False
                    fond.y1, fond.y2     = 0, -HAUTEUR
                    fond.image           = pygame.transform.scale(images["fond"], (LARGEUR, HAUTEUR))
                    vague_actuelle       = 1
                    score_prochaine_vague= 1000
                    nouveau_fond_img     = None
                    nouveau_fond_y       = -HAUTEUR
                    bombes               = []
                    td_bombe             = 0
                    afficher_annonce_vague(fenetre, vague_actuelle)
                    lancer_musique()

                elif event.key == pygame.K_l:
                    result = charger_partie(perso, images, fenetre)
                    if result[0] is not None:
                        balles, game_over    = result
                        fruits               = []
                        bonus_immunite_liste = []
                        bonus_ralenti_liste  = []
                        bonus_coeur_liste    = []
                        son_game_over_joue   = False
                        timers               = {k: now for k in timers}
                        if not game_over:
                            lancer_musique()

            if en_pause and event.key == pygame.K_u:
                en_pause = False
                pygame.mixer.music.unpause()

    fond.actif = not game_over
    fond.deplacer()
    fond.afficher()

    if en_pause and not game_over:
        surf_pause = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        surf_pause.fill((0, 0, 0, 140))
        fenetre.blit(surf_pause, (0, 0))
        afficher_texte_centre(fenetre, "PAUSE", 100, (255, 255, 255), HAUTEUR // 2 - 40)
        afficher_texte_centre(fenetre, "Appuyez sur U pour reprendre", 36, (200, 200, 200), HAUTEUR // 2 + 40)
        pygame.display.flip()
        horloge.tick(FPS)
        continue

    if perso.vies <= 0 and not game_over:
        game_over = True
        sauvegarder_highscore(perso.score)
        if not son_game_over_joue:
            pygame.mixer.music.stop()
            jouer_son(images, "son_game_over")
            son_game_over_joue = True

    if game_over:
        for obj in balles + fruits + bonus_immunite_liste:
            obj.afficher()
        perso.afficher()

        afficher_texte_centre(fenetre, "GAME OVER",              100, (255, 0, 0),     HAUTEUR // 2 - 60)
        afficher_texte_centre(fenetre, f"Score: {perso.score}",   60, (255, 255, 255), HAUTEUR // 2 + 20)
        afficher_texte_centre(fenetre, f"Temps: {perso.score//30} s", 40, (255, 255, 255), HAUTEUR // 2 + 80)

        font_hs = pygame.font.Font(None, 32)
        surf_hs = font_hs.render("TOP SCORES", True, (255, 215, 0))
        fenetre.blit(surf_hs, surf_hs.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 130)))
        for i, hs in enumerate(charger_highscores()[:3]):
            c = [(255, 215, 0), (192, 192, 192), (205, 127, 50)][i]
            s = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, c)
            fenetre.blit(s, s.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 160 + i * 28)))

        afficher_texte_centre(fenetre, "ESPACE = rejouer  |  L = charger  |  ECHAP = quitter",
                              30, (255, 255, 255), HAUTEUR - 40)

    else:
        perso.afficher()
        perso.deplacer()
        perso.score += 1

        temps_ecoule    = (now - timers["debut"]) / 1000.0
        facteur_vitesse = min(1.0 + (temps_ecoule / 30.0) * 0.5, 3.0)

        if perso.score >= score_prochaine_vague:
            vague_actuelle        += 1
            score_prochaine_vague += 1000
            cle_fond = {2: "fond_v2", 3: "fond_v3"}.get(vague_actuelle)
            if cle_fond:
                nouveau_fond_img = pygame.transform.scale(images[cle_fond], (LARGEUR, HAUTEUR))
                nouveau_fond_y   = -HAUTEUR
            if vague_actuelle == 2:
                td_bombe = now + 5000
            afficher_annonce_vague(fenetre, vague_actuelle)
            timers["balle"] = pygame.time.get_ticks()

        if nouveau_fond_img is not None:
            nouveau_fond_y += fond.vitesse
            fenetre.blit(nouveau_fond_img, (0, nouveau_fond_y))
            if nouveau_fond_y >= 0:
                fond.image       = nouveau_fond_img
                fond.y1          = 0
                fond.y2          = -HAUTEUR
                nouveau_fond_img = None

        if vague_actuelle >= 2 and images["bombe"] and td_bombe > 0 and now >= td_bombe:
            if now - td_bombe >= 8000:
                vitesse_bombe = 2 + facteur_vitesse * 2
                bombes.append(Bombe(images["bombe"], fenetre, vitesse_bombe))
                td_bombe = now

        bombes_restantes = []
        for bombe in bombes:
            bombe.deplacer()
            if bombe.hors_ecran():
                continue
            if perso.collide(bombe):
                if perso.appliquer_degats():
                    flash.declencher((255, 50, 0))
                    jouer_son(images, "son_collision")
                    lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 50, 0), 20)
            else:
                bombe.afficher()
                bombes_restantes.append(bombe)
        bombes = bombes_restantes

        if now - timers["sauvegarde"] >= 5000:
            sauvegarder_partie(perso, balles, game_over)
            timers["sauvegarde"] = now

        if now - timers["balle"] >= 6000:
            max_balles = min(3 + vague_actuelle, nbre_max_balle)
            if len(balles) < max_balles:
                v = 3.3 * facteur_vitesse
                balles.append(Balle(images["balle"], fenetre,
                                    depballe_x=random.choice([-1, 1]) * v,
                                    depballe_y=random.choice([-1, 1]) * v))
            timers["balle"] = now

        if now - timers["fruit"] >= 10000:
            type_fruit = random.choice(["fraise", "pasteque"])
            if images[type_fruit]:
                fruits.append(Fruit(images[type_fruit], fenetre))
            timers["fruit"] = now

        if now - timers["bonus"] >= 15000:
            bonus_immunite_liste.append(BonusImmunite(fenetre))
            timers["bonus"] = now

        if now - timers["ralenti"] >= 20000:
            bonus_ralenti_liste.append(BonusRalenti(fenetre))
            timers["ralenti"] = now

        if now - timers["coeur"] >= 25000:
            bonus_coeur_liste.append(BonusCœur(fenetre))
            timers["coeur"] = now

        for balle in balles:
            balle.deplacer(facteur_vitesse, perso.ralenti_actif)
            balle.afficher()

        def on_fruit(obj):
            if perso.appliquer_demi_degats():
                flash.declencher((255, 100, 0))
                jouer_son(images, "son_collision")
                lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 100, 0), 10)

        def on_immunite(obj):
            perso.activer_immunite()
            flash.declencher((255, 215, 0))
            jouer_son(images, "son_bonus")
            lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 215, 0))

        def on_ralenti(obj):
            perso.activer_ralentissement()
            flash.declencher((50, 150, 255))
            jouer_son(images, "son_bonus")
            lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (50, 150, 255))

        def on_coeur(obj):
            perso.vies = min(perso.vies + 0.5, 3)
            flash.declencher((255, 80, 130))
            jouer_son(images, "son_bonus")
            lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 80, 130))

        fruits               = gerer_objets(fruits,               perso, flash, images, particules, on_fruit)
        bonus_immunite_liste = gerer_objets(bonus_immunite_liste,  perso, flash, images, particules, on_immunite)
        bonus_ralenti_liste  = gerer_objets(bonus_ralenti_liste,   perso, flash, images, particules, on_ralenti)
        bonus_coeur_liste    = gerer_objets(bonus_coeur_liste,     perso, flash, images, particules, on_coeur)

        for balle in balles:
            if perso.collide(balle):
                if perso.appliquer_degats():
                    flash.declencher((255, 0, 0))
                    jouer_son(images, "son_collision")
                    lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 80, 0), 20)

        particules = [p for p in particules if not p.est_mort()]
        for p in particules:
            p.update()
            p.afficher(fenetre)

        flash.update()
        flash.afficher(fenetre)

        font_hud = pygame.font.Font(None, 36)
        font_leg = pygame.font.Font(None, 24)

        fenetre.blit(font_hud.render(f"Score: {perso.score}", True, (255, 255, 255)), (10, 10))
        fenetre.blit(font_hud.render(f"Vague: {vague_actuelle}", True, (255, 220, 50)), (10, 45))

        pct_diff = int((facteur_vitesse - 1.0) / 2.0 * 100)
        fenetre.blit(font_leg.render(f"Difficulté: {pct_diff}%", True, (200, 200, 255)), (10, 80))

        dessiner_barre_vie(fenetre, perso.vies, 3)

        if perso.immunite_active:
            s = font_hud.render(f"IMMUNITE: {(perso.duree_immunite - perso.comp_immunite)//30}s", True, (255, 215, 0))
            fenetre.blit(s, s.get_rect(center=(LARGEUR // 2, 20)))

        if perso.ralenti_actif:
            s = font_hud.render(f"SLOW: {(perso.duree_ralenti - perso.comp_ralenti)//30}s", True, (50, 200, 255))
            fenetre.blit(s, s.get_rect(center=(LARGEUR // 2, 55)))

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()