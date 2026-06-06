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
    """Particule d'explosion avec traînée et fade-out lisse."""
    def __init__(self, x, y, couleur=(255, 80, 0), type_="normale"):
        self.x = x
        self.y = y
        self.type_ = type_
        angle = random.uniform(0, 2 * math.pi)
        if type_ == "etincelle":
            vitesse = random.uniform(4, 10)
            self.duree = random.randint(10, 20)
            self.rayon = random.randint(1, 3)
        elif type_ == "fumee":
            vitesse = random.uniform(0.5, 2)
            self.duree = random.randint(25, 45)
            self.rayon = random.randint(6, 14)
        else:
            vitesse = random.uniform(2, 7)
            self.duree = random.randint(15, 35)
            self.rayon = random.randint(3, 8)
        self.vx = math.cos(angle) * vitesse
        self.vy = math.sin(angle) * vitesse
        self.age = 0
        self.couleur = couleur
        self.historique = []  # traînée

    def update(self):
        self.historique.append((self.x, self.y))
        if len(self.historique) > 5:
            self.historique.pop(0)
        self.x += self.vx
        self.y += self.vy
        if self.type_ == "fumee":
            self.vy -= 0.15   # monte
            self.vx *= 0.97
        else:
            self.vy += 0.25   # gravité
        self.vx *= 0.98
        self.age += 1

    def afficher(self, fenetre):
        ratio = 1 - self.age / self.duree
        rayon_actuel = max(1, int(self.rayon * ratio))
        # Traînée
        for i, (hx, hy) in enumerate(self.historique):
            tr = max(1, int(rayon_actuel * (i / len(self.historique)) * 0.6))
            fade = int(180 * (i / len(self.historique)) * ratio)
            r = min(255, self.couleur[0])
            g = min(255, max(0, self.couleur[1]))
            b = min(255, self.couleur[2])
            surf_t = pygame.Surface((tr * 2 + 2, tr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf_t, (r, g, b, fade), (tr + 1, tr + 1), tr)
            fenetre.blit(surf_t, (int(hx) - tr - 1, int(hy) - tr - 1))
        # Particule principale
        r = min(255, self.couleur[0])
        g = min(255, max(0, self.couleur[1] - self.age * 3))
        b = min(255, self.couleur[2])
        alpha = int(255 * ratio)
        surf_p = pygame.Surface((rayon_actuel * 2 + 2, rayon_actuel * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf_p, (r, g, b, alpha), (rayon_actuel + 1, rayon_actuel + 1), rayon_actuel)
        fenetre.blit(surf_p, (int(self.x) - rayon_actuel - 1, int(self.y) - rayon_actuel - 1))

    def est_mort(self):
        return self.age >= self.duree


class FlashEcran:
    """Flash coloré sur tout l'écran + secousse caméra lors d'un événement."""
    def __init__(self, largeur, hauteur):
        self.surf   = pygame.Surface((largeur, hauteur))
        self.actif  = False
        self.alpha  = 0
        self.couleur = (255, 0, 0)
        # Secousse
        self.shake_force = 0
        self.shake_x     = 0
        self.shake_y     = 0

    def declencher(self, couleur=(255, 0, 0), shake=6):
        self.couleur     = couleur
        self.alpha       = 130
        self.actif       = True
        self.shake_force = shake

    def update(self):
        if self.actif:
            self.alpha -= 10
            if self.alpha <= 0:
                self.alpha = 0
                self.actif = False
        if self.shake_force > 0:
            self.shake_x = random.randint(-self.shake_force, self.shake_force)
            self.shake_y = random.randint(-self.shake_force, self.shake_force)
            self.shake_force = max(0, self.shake_force - 1)
        else:
            self.shake_x = 0
            self.shake_y = 0

    def afficher(self, fenetre):
        if self.actif and self.alpha > 0:
            self.surf.fill(self.couleur)
            self.surf.set_alpha(self.alpha)
            fenetre.blit(self.surf, (0, 0))


def lire_images():
    images = {}

    image = pygame.image.load("perso.png").convert_alpha()
    images["perso"] = image
    # Fond de fallback (background.jpg)
    try:
        image = pygame.image.load("background.jpg").convert()
    except:
        image = pygame.Surface((1024, 768))
        image.fill((10, 10, 40))
    images["fond"] = image

    # Fonds spécifiques par vague
    images["fonds_vagues"] = {}

    # Vague 1 — Ville la nuit (background.png)
    try:
        fond_v1 = pygame.image.load("background.png").convert()
        images["fonds_vagues"][1] = fond_v1
        print("background.png chargé pour la vague 1")
    except Exception as e:
        print(f"background.png non trouvé, fond par défaut pour vague 1 : {e}")
        images["fonds_vagues"][1] = image

    # Vague 2 — Mars / Monde extraterrestre (marsmid.png)
    try:
        fond_v2 = pygame.image.load("marsmid.png").convert()
        images["fonds_vagues"][2] = fond_v2
        print("marsmid.png chargé pour la vague 2")
    except Exception as e:
        print(f"marsmid.png non trouvé, fond par défaut pour vague 2 : {e}")
        images["fonds_vagues"][2] = image

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

    # ── Fond spatial avec nébuleuse générée ──────────────────────────────────
    fond_accueil = pygame.Surface((largeur, hauteur))
    for y in range(hauteur):
        ratio = y / hauteur
        r = int(5  + ratio * 15)
        g = int(0  + ratio * 10)
        b = int(30 + ratio * 60)
        pygame.draw.line(fond_accueil, (r, g, b), (0, y), (largeur, y))

    # Nébuleuses (cercles flous colorés)
    nebuleuses = [
        (200, 180, (80, 20, 120), 100),
        (800, 300, (20, 60, 140), 120),
        (500, 500, (120, 40, 40), 90),
        (150, 550, (20, 80, 100), 80),
        (900, 150, (60, 30, 110), 70),
    ]
    fond_nebuleuse = fond_accueil.copy()
    for nx, ny, nc, nr in nebuleuses:
        surf_neb = pygame.Surface((nr * 2, nr * 2), pygame.SRCALPHA)
        for rayon in range(nr, 0, -8):
            alpha = int(30 * (rayon / nr))
            pygame.draw.circle(surf_neb, (*nc, alpha), (nr, nr), rayon)
        fond_nebuleuse.blit(surf_neb, (nx - nr, ny - nr))

    # Étoiles fixes (grande et petite)
    etoiles = [
        (random.randint(0, largeur), random.randint(0, hauteur),
         random.uniform(0.4, 2.0), random.uniform(0, 2 * math.pi))
        for _ in range(120)
    ]

    # Particules flottantes (ambiance)
    class ParticuleFond:
        def __init__(self):
            self.x     = random.uniform(0, largeur)
            self.y     = random.uniform(0, hauteur)
            self.vx    = random.uniform(-0.4, 0.4)
            self.vy    = random.uniform(-0.8, -0.2)
            self.r     = random.uniform(1.5, 4)
            self.alpha = random.randint(80, 200)
            self.couleur = random.choice([
                (150, 100, 255), (80, 180, 255), (255, 160, 80), (255, 255, 180)
            ])
        def update(self):
            self.x += self.vx
            self.y += self.vy
            if self.y < -10:
                self.y = hauteur + 5
                self.x = random.uniform(0, largeur)

    particules_fond = [ParticuleFond() for _ in range(60)]

    font_titre  = pygame.font.Font(None, 110)
    font_sous   = pygame.font.Font(None, 36)
    font_bouton = pygame.font.Font(None, 54)
    font_hs     = pygame.font.Font(None, 28)
    font_leg    = pygame.font.Font(None, 22)

    perso_img = pygame.transform.scale(images["perso"], (140, 140))

    btn_w, btn_h = 280, 70
    btn_x = largeur // 2 - btn_w // 2
    btn_y = hauteur - 120
    rect_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    highscores    = charger_highscores()
    tick          = 0
    angle_halo    = 0

    # Mini aperçu des obstacles (dessinés une fois)
    def dessiner_apercu(fenetre, tick):
        """Affiche une rangée d'icônes d'obstacles en bas de l'écran."""
        items = [
            ("Balle",   (255, 80,  0)),
            ("Fruit",   (255, 50, 50)),
            ("-1 Manu", (200, 0,   0)),
            ("Bombe",   (30,  30,  30)),
        ]
        x0 = largeur // 2 - len(items) * 70 // 2
        y0 = hauteur - 200
        for i, (label, col) in enumerate(items):
            cx = x0 + i * 75 + 25
            pulse = int(5 * math.sin(tick * 0.06 + i))
            pygame.draw.circle(fenetre, col, (cx, y0 + pulse), 18)
            pygame.draw.circle(fenetre, (255, 255, 255), (cx, y0 + pulse), 18, 2)
            surf = font_leg.render(label, True, (220, 220, 220))
            fenetre.blit(surf, surf.get_rect(center=(cx, y0 + 30 + pulse)))

    while True:
        horloge.tick(60)
        tick       += 1
        angle_halo += 2

        # ── Fond + nébuleuse ──
        fenetre.blit(fond_nebuleuse, (0, 0))

        # ── Étoiles scintillantes ──
        for ex, ey, eb, ep in etoiles:
            lum = int(140 + 115 * math.sin(tick * 0.04 * eb + ep))
            r   = max(1, int(eb * 0.7))
            pygame.draw.circle(fenetre, (lum, lum, lum), (int(ex), int(ey)), r)

        # ── Particules flottantes ──
        for p in particules_fond:
            p.update()
            surf_p = pygame.Surface((int(p.r * 2 + 2), int(p.r * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf_p, (*p.couleur, p.alpha), (int(p.r) + 1, int(p.r) + 1), int(p.r))
            fenetre.blit(surf_p, (int(p.x - p.r), int(p.y - p.r)))

        # ── Ligne déco haut ──
        accent_r = int(180 + 75 * math.sin(tick * 0.03))
        accent_g = int(120 + 80 * math.sin(tick * 0.03 + 2))
        accent_c = (accent_r, accent_g, 50)
        pygame.draw.line(fenetre, accent_c, (50, 58), (largeur - 50, 58), 2)

        # ── Titre "SURVIVAL CHARACTER" avec effet lueur ──
        for offset, alpha_lueur in [(6, 40), (3, 80)]:
            surf_lueur = font_titre.render("SURVIVAL", True, (255, 200, 0))
            surf_lueur.set_alpha(alpha_lueur)
            fenetre.blit(surf_lueur, surf_lueur.get_rect(center=(largeur // 2 + offset, 130 + offset)))

        surf_s = font_titre.render("SURVIVAL", True, (255, 220, 60))
        fenetre.blit(surf_s, surf_s.get_rect(center=(largeur // 2, 130)))

        for offset, alpha_lueur in [(5, 40), (3, 80)]:
            surf_lueur2 = font_titre.render("CHARACTER", True, (200, 200, 255))
            surf_lueur2.set_alpha(alpha_lueur)
            fenetre.blit(surf_lueur2, surf_lueur2.get_rect(center=(largeur // 2 + offset, 230 + offset)))

        surf_c = font_titre.render("CHARACTER", True, (220, 220, 255))
        fenetre.blit(surf_c, surf_c.get_rect(center=(largeur // 2, 230)))

        pygame.draw.line(fenetre, accent_c, (50, 278), (largeur - 50, 278), 2)

        # ── Personnage avec halo pulsé multi-couche ──
        cx_perso = largeur // 2
        cy_perso = 370
        for rayon_h, alpha_h, couleur_h in [
            (90, 30, (100, 60, 200)),
            (70, 55, (80, 80, 220)),
            (52, 90, (60, 60, 180)),
        ]:
            pulse = int(8 * math.sin(tick * 0.05))
            surf_halo = pygame.Surface((( rayon_h + pulse) * 2, (rayon_h + pulse) * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf_halo, (*couleur_h, alpha_h),
                               (rayon_h + pulse, rayon_h + pulse), rayon_h + pulse)
            fenetre.blit(surf_halo, (cx_perso - rayon_h - pulse, cy_perso - rayon_h - pulse))

        bob = int(6 * math.sin(tick * 0.05))  # flottement vertical
        perso_rect = perso_img.get_rect(center=(cx_perso, cy_perso + bob))
        fenetre.blit(perso_img, perso_rect)

        # ── Meilleurs scores (panneau droit) ──
        if highscores:
            panel = pygame.Surface((250, 110), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 100))
            fenetre.blit(panel, (largeur - 270, 265))
            hs_titre = font_hs.render("🏆 MEILLEURS SCORES", True, (255, 215, 0))
            fenetre.blit(hs_titre, hs_titre.get_rect(center=(largeur - 145, 282)))
            for i, hs in enumerate(highscores[:3]):
                couleurs_hs = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
                txt = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, couleurs_hs[i])
                fenetre.blit(txt, txt.get_rect(center=(largeur - 145, 305 + i * 26)))

        # ── Aperçu des obstacles ──
        dessiner_apercu(fenetre, tick)

        # ── Bouton JOUER animé ──
        mx, my = pygame.mouse.get_pos()
        survol = rect_btn.collidepoint(mx, my)
        pulse_btn = int(4 * math.sin(tick * 0.08))
        if survol:
            couleur_btn  = (60, 220, 110)
            couleur_bord = (180, 255, 180)
        else:
            couleur_btn  = (30, 150, 75)
            couleur_bord = accent_c
        rect_anim = pygame.Rect(btn_x - pulse_btn, btn_y - pulse_btn // 2,
                                btn_w + pulse_btn * 2, btn_h + pulse_btn)
        pygame.draw.rect(fenetre, couleur_btn,  rect_anim, border_radius=16)
        pygame.draw.rect(fenetre, couleur_bord, rect_anim, width=3, border_radius=16)
        surf_btn = font_bouton.render("▶  JOUER", True, (255, 255, 255))
        fenetre.blit(surf_btn, surf_btn.get_rect(center=rect_anim.center))

        surf_esc = font_sous.render("ECHAP pour quitter  |  ESPACE pour jouer", True, (160, 160, 160))
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


# ── Ambiances par vague ──────────────────────────────────────────────────────
AMBIANCES = {
    1: {"nom": "Ville la nuit",        "teinte": (10,  10,  50),  "accent": (80,  80,  200)},
    2: {"nom": "Forêt fantastique",    "teinte": (5,   40,  15),  "accent": (40,  180, 60) },
    3: {"nom": "Monde souterrain",     "teinte": (50,  10,  5),   "accent": (200, 60,  20) },
    4: {"nom": "Dimension des ombres", "teinte": (25,  0,   50),  "accent": (140, 0,   200)},
    5: {"nom": "Abîme final",          "teinte": (0,   0,   0),   "accent": (220, 0,   0)  },
}


class Fond:
    """Fond parallax défilant vers le bas, avec teinte d'ambiance et image par vague."""
    def __init__(self, image, fenetre, vitesse=2, fonds_vagues=None):
        self.fenetre      = fenetre
        self.vitesse      = vitesse
        lw = fenetre.get_width()
        lh = fenetre.get_height()
        self.lw           = lw
        self.lh           = lh
        self.fonds_vagues = fonds_vagues or {}
        self.image_base   = pygame.transform.scale(image, (lw, lh))
        self.image        = self.image_base.copy()
        self.y1    = 0
        self.y2    = -lh
        self.haut  = lh
        self.actif = False
        # Transition de couleur
        self.teinte_actuelle = list(AMBIANCES[1]["teinte"])
        self.teinte_cible    = list(AMBIANCES[1]["teinte"])
        self.vitesse_transition = 1  # unités RGB par frame

    def changer_ambiance(self, vague):
        """Change l'image de fond si disponible + déclenche la transition de teinte."""
        # Changer l'image si une image spécifique existe pour cette vague
        if vague in self.fonds_vagues:
            nouvelle_image = pygame.transform.scale(
                self.fonds_vagues[vague], (self.lw, self.lh)
            )
            self.image_base = nouvelle_image
            self.image      = self.image_base.copy()
            print(f"Fond changé pour la vague {vague}")
        # Transition de teinte
        ambiance = AMBIANCES.get(vague, AMBIANCES[5])
        self.teinte_cible = list(ambiance["teinte"])

    def _interpoler_teinte(self):
        """Rapproche doucement la teinte actuelle de la teinte cible."""
        for i in range(3):
            if self.teinte_actuelle[i] < self.teinte_cible[i]:
                self.teinte_actuelle[i] = min(
                    self.teinte_actuelle[i] + self.vitesse_transition,
                    self.teinte_cible[i]
                )
            elif self.teinte_actuelle[i] > self.teinte_cible[i]:
                self.teinte_actuelle[i] = max(
                    self.teinte_actuelle[i] - self.vitesse_transition,
                    self.teinte_cible[i]
                )

    def _appliquer_teinte(self):
        """Applique un overlay coloré sur le fond pour créer l'ambiance."""
        self.image = self.image_base.copy()
        overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        overlay.fill((
            self.teinte_actuelle[0],
            self.teinte_actuelle[1],
            self.teinte_actuelle[2],
            90  # transparence : 0=invisible, 255=opaque
        ))
        self.image.blit(overlay, (0, 0))

    def deplacer(self):
        if not self.actif:
            return
        self._interpoler_teinte()
        self._appliquer_teinte()
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


class Manu(ElementGraphique):
    """Obstacle rouge -1 : enlève une vie entière au contact."""
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 52
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        # Cercle rouge vif
        pygame.draw.circle(surf, (200, 0, 0),   (taille//2, taille//2), taille//2)
        pygame.draw.circle(surf, (255, 60, 60),  (taille//2, taille//2), taille//2, 4)
        font = pygame.font.Font(None, 38)
        txt  = font.render("-1", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille//2, taille//2)))
        x = random.randint(0, lw - taille)
        y = -taille
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(2.5, 4.5)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class Bombe(ElementGraphique):
    """Bombe noire/orange : explose au contact et enlève 1 vie. Apparaît en vague 2+."""
    def __init__(self, fenetre):
        lw     = fenetre.get_width()
        taille = 56
        surf   = pygame.Surface((taille, taille), pygame.SRCALPHA)
        # Corps noir de la bombe
        pygame.draw.circle(surf, (30, 30, 30),   (taille//2, taille//2 + 4), taille//2 - 4)
        pygame.draw.circle(surf, (80, 80, 80),   (taille//2, taille//2 + 4), taille//2 - 4, 3)
        # Mèche orange en haut
        pygame.draw.line(surf, (255, 140, 0), (taille//2, taille//2 - 8), (taille//2 + 8, 4), 3)
        pygame.draw.circle(surf, (255, 220, 0), (taille//2 + 8, 4), 4)
        # Symbole 💥 texte
        font = pygame.font.Font(None, 26)
        txt  = font.render("BOOM", True, (255, 80, 0))
        surf.blit(txt, txt.get_rect(center=(taille//2, taille//2 + 6)))
        x = random.randint(0, lw - taille)
        y = -taille
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(2.0, 3.5)
        self.explose = False

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


MESSAGES_VAGUE = {
    1: "Le danger commence...",
    2: "Les créatures s'éveillent...",
    3: "Le monde bascule dans l'obscurité...",
    4: "Les ombres prennent vie...",
    5: "L'abîme vous engloutit...",
}

#───────── Annonce de vague ───────────────────────

def afficher_annonce_vague(fenetre, largeur, hauteur, numero_vague):
    ambiance = AMBIANCES.get(numero_vague, AMBIANCES[5])
    message  = MESSAGES_VAGUE.get(numero_vague, "Survivez encore...")
    accent   = ambiance["accent"]

    font_vague = pygame.font.Font(None, 90)
    font_nom   = pygame.font.Font(None, 44)
    font_msg   = pygame.font.Font(None, 32)

    # Overlay sombre
    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    fenetre.blit(overlay, (0, 0))

    # Ligne décorative haute
    pygame.draw.line(fenetre, accent, (80, hauteur//2 - 70), (largeur - 80, hauteur//2 - 70), 2)

    # Texte VAGUE N
    surf_v = font_vague.render(f"VAGUE  {numero_vague}", True, accent)
    fenetre.blit(surf_v, surf_v.get_rect(center=(largeur//2, hauteur//2 - 20)))

    # Nom de l'ambiance
    surf_n = font_nom.render(ambiance["nom"], True, (220, 220, 220))
    fenetre.blit(surf_n, surf_n.get_rect(center=(largeur//2, hauteur//2 + 50)))

    # Message narratif
    surf_m = font_msg.render(message, True, (160, 160, 160))
    fenetre.blit(surf_m, surf_m.get_rect(center=(largeur//2, hauteur//2 + 90)))

    # Ligne décorative basse
    pygame.draw.line(fenetre, accent, (80, hauteur//2 + 115), (largeur - 80, hauteur//2 + 115), 2)

    pygame.display.flip()
    pygame.time.wait(1800)


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

td_manu              = pygame.time.get_ticks()
intervalle_manu      = 8000   # toutes les 8s en vague 2+

td_bombe             = pygame.time.get_ticks()
intervalle_bombe     = 12000  # toutes les 12s en vague 2+

fruits               = []
bonus_immunite_liste = []
bonus_ralenti_liste  = []
bonus_coeur_liste    = []
manus_liste          = []
bombes_liste         = []
particules           = []

perso = Perso(images["perso"], fenetre,
              x=largeur // 2 - images["perso"].get_width() // 2,
              y=hauteur - images["perso"].get_height())
perso.inv      = True
perso.comp_inv = 0

fond   = Fond(images["fond"], fenetre, vitesse=2, fonds_vagues=images["fonds_vagues"])
fond.changer_ambiance(1)  # appliquer le fond de la vague 1 dès le début
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
td_manu          = pygame.time.get_ticks()
td_bombe         = pygame.time.get_ticks()
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
    # Offset de secousse caméra
    ox, oy = flash.shake_x, flash.shake_y
    fenetre.blit(fond.image, (ox, fond.y1 + oy))
    fenetre.blit(fond.image, (ox, fond.y2 + oy))

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
            fond.changer_ambiance(vague_actuelle)          # ← transition couleur
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

        # ── Manus (vague 2+) ──
        if vague_actuelle >= 2:
            if temps_actuel - td_manu >= intervalle_manu:
                manus_liste.append(Manu(fenetre))
                td_manu = temps_actuel

        # ── Bombes (vague 2+) ──
        if vague_actuelle >= 2:
            if temps_actuel - td_bombe >= intervalle_bombe:
                bombes_liste.append(Bombe(fenetre))
                td_bombe = temps_actuel

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

        # ── Manus (-1 vie) ──────────────────────────────────────────────────────
        manus_restants = []
        for manu in manus_liste:
            manu.deplacer()
            if manu.hors_ecran():
                continue
            if perso.collide(manu):
                touche = perso.appliquer_degats()
                if touche:
                    flash.declencher((180, 0, 0), shake=8)
                    if images.get("son_collision"):
                        images["son_collision"].play()
                    cx, cy = perso.rect.centerx, perso.rect.centery
                    for _ in range(18):
                        particules.append(Particule(cx, cy, (220, 0, 0), "normale"))
                    for _ in range(12):
                        particules.append(Particule(cx, cy, (255, 80, 80), "etincelle"))
                    for _ in range(6):
                        particules.append(Particule(cx, cy, (100, 0, 0), "fumee"))
            else:
                manu.afficher()
                manus_restants.append(manu)
        manus_liste = manus_restants

        # ── Bombes (explosion -1 vie) ────────────────────────────────────────────
        bombes_restantes = []
        for bombe in bombes_liste:
            bombe.deplacer()
            if bombe.hors_ecran():
                continue
            if perso.collide(bombe):
                touche = perso.appliquer_degats()
                if touche:
                    flash.declencher((255, 120, 0), shake=12)
                    if images.get("son_collision"):
                        images["son_collision"].play()
                    cx, cy = bombe.rect.centerx, bombe.rect.centery
                    # Grande explosion multi-couches
                    for _ in range(25):
                        particules.append(Particule(cx, cy, (255, 120, 0), "normale"))
                    for _ in range(20):
                        particules.append(Particule(cx, cy, (255, 220, 0), "etincelle"))
                    for _ in range(12):
                        particules.append(Particule(cx, cy, (80, 80, 80), "fumee"))
            else:
                bombe.afficher()
                bombes_restantes.append(bombe)
        bombes_liste = bombes_restantes

        # Collisions balles
        for balle in balles:
            if perso.collide(balle):
                touche = perso.appliquer_degats()
                if touche:
                    flash.declencher((255, 0, 0), shake=7)
                    if images.get("son_collision"):
                        images["son_collision"].play()
                    cx, cy = perso.rect.centerx, perso.rect.centery
                    for _ in range(15):
                        particules.append(Particule(cx, cy, (255, 50, 0), "normale"))
                    for _ in range(10):
                        particules.append(Particule(cx, cy, (255, 180, 0), "etincelle"))
                    for _ in range(5):
                        particules.append(Particule(cx, cy, (60, 60, 60), "fumee"))

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
            "🍓=-½vie  ⭐=Immunité  ❄=Slow  💗=+½vie  🔴=-1vie(vague2)  💣=Bombe(vague2)",
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
                    manus_liste           = []
                    bombes_liste          = []
                    son_game_over_joue    = False
                    td_balle = td_sauvegarde = td_debut_jeu = pygame.time.get_ticks()
                    td_fruit = td_bonus = td_bonus_ralenti = td_bonus_coeur = pygame.time.get_ticks()
                    td_manu = td_bombe = pygame.time.get_ticks()
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
                manus_liste           = []
                bombes_liste          = []
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
                td_manu = td_bombe = pygame.time.get_ticks()
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
