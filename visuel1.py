import pygame
import random
import json
import os
import math
from datetime import datetime

# ─── Constantes ───────────────────────────────────────────────────────────────
LARGEUR, HAUTEUR = 1024, 768
FPS              = 30
MAX_BALLES       = 5
DUREE_IMMUNITE   = 300  # ticks
DUREE_RALENTI    = 180  # ticks (~6s)
INTERVALLE_BALLE        = 6000   # ms
INTERVALLE_SAUVEGARDE   = 5000
INTERVALLE_FRUIT        = 10000
INTERVALLE_BONUS        = 15000
INTERVALLE_BONUS_RALENTI= 20000
INTERVALLE_BONUS_COEUR  = 25000


# ─── Highscores ───────────────────────────────────────────────────────────────
def charger_highscores():
    if not os.path.exists('highscores.json'):
        return []
    try:
        with open('highscores.json') as f:
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


# ─── Sauvegarde de partie ─────────────────────────────────────────────────────
def sauvegarder_partie(perso, balles, game_over):
    donnees = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'perso': {'x': perso.rect.x, 'y': perso.rect.y,
                  'vies': perso.vies, 'score': perso.score,
                  'inv': perso.inv, 'comp_inv': perso.comp_inv},
        'balles': [{'x': b.rect.x, 'y': b.rect.y,
                    'depballe_x': b.dx, 'depballe_y': b.dy} for b in balles],
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
        with open('sauvegarde.json') as f:
            d = json.load(f)
        perso.rect.x   = d['perso']['x']
        perso.rect.y   = d['perso']['y']
        perso.vies     = d['perso']['vies']
        perso.score    = d['perso']['score']
        perso.inv      = d['perso']['inv']
        perso.comp_inv = d['perso']['comp_inv']
        balles = []
        for bd in d['balles']:
            b = Balle(images["balle"], fenetre, bd['depballe_x'], bd['depballe_y'])
            b.rect.x = bd['x']
            b.rect.y = bd['y']
            balles.append(b)
        return balles, d['game_over']
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None, False


# ─── Chargement des ressources ────────────────────────────────────────────────
def charger_ressources():
    res = {}
    res["perso"] = pygame.image.load("perso.png").convert_alpha()
    res["fond"]  = pygame.image.load("background.jpg").convert()
    res["balle"] = pygame.image.load("balle.png").convert_alpha()

    for nom in ["fraise", "pasteque"]:
        try:
            res[nom] = pygame.image.load(f"{nom}.png").convert_alpha()
        except:
            print(f"{nom}.png non trouvé")
            res[nom] = None

    for cle, fichier, volume in [
        ("son_collision", "collision.wav",  0.5),
        ("son_bonus",     "bonus.wav",      0.6),
        ("son_game_over", "game_over.mp3",  0.8),
    ]:
        try:
            res[cle] = pygame.mixer.Sound(fichier)
            res[cle].set_volume(volume)
        except:
            print(f"{fichier} non trouvé")
            res[cle] = None

    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        print("musique_fond.OGG non trouvé")

    return res

def jouer_son(res, cle):
    if res.get(cle):
        res[cle].play()


# ─── Classes de base ──────────────────────────────────────────────────────────
class Sprite:
    """Sprite de base avec image, rect et affichage."""
    def __init__(self, image, fenetre, x=0, y=0):
        self.image   = image
        self.fenetre = fenetre
        self.rect    = image.get_rect(topleft=(x, y))

    def afficher(self):
        self.fenetre.blit(self.image, self.rect)

    def collide(self, other):
        return self.rect.colliderect(other.rect)


class ObjetTombant(Sprite):
    """Objet qui tombe du haut de l'écran."""
    def __init__(self, surf, fenetre, vitesse=None):
        x = random.randint(0, fenetre.get_width() - surf.get_width())
        super().__init__(surf, fenetre, x, -surf.get_height())
        self.vitesse = vitesse or random.uniform(1.5, 3.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


# ─── Classes du jeu ───────────────────────────────────────────────────────────
class Fond:
    def __init__(self, image, fenetre, vitesse=2):
        self.fenetre = fenetre
        self.vitesse = vitesse
        lw, lh       = fenetre.get_size()
        self.image   = pygame.transform.scale(image, (lw, lh))
        self.y1, self.y2 = 0, -lh
        self.haut    = lh
        self.actif   = False

    def deplacer(self):
        if not self.actif:
            return
        self.y1 += self.vitesse
        self.y2 += self.vitesse
        if self.y1 >= self.haut: self.y1 = self.y2 - self.haut
        if self.y2 >= self.haut: self.y2 = self.y1 - self.haut

    def afficher(self):
        self.fenetre.blit(self.image, (0, self.y1))
        self.fenetre.blit(self.image, (0, self.y2))


class Perso(Sprite):
    def __init__(self, image, fenetre, x=0, y=0):
        super().__init__(image, fenetre, x, y)
        self.vies            = 3
        self.score           = 0
        self.inv             = False
        self.comp_inv        = 0
        self.immunite_active = False
        self.comp_immunite   = 0
        self.ralenti_actif   = False
        self.comp_ralenti    = 0

    def deplacer(self):
        vitesse = 3
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT]:  self.rect.x -= vitesse
        if touches[pygame.K_RIGHT]: self.rect.x += vitesse
        if touches[pygame.K_UP]:    self.rect.y -= vitesse
        if touches[pygame.K_DOWN]:  self.rect.y += vitesse
        self.rect.clamp_ip(pygame.Rect(0, 0, LARGEUR, HAUTEUR))

        # Invincibilité courte après dégât
        if self.inv:
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = self.comp_inv = 0  # type: ignore

        # Immunité bonus
        if self.immunite_active:
            self.comp_immunite += 1
            if self.comp_immunite >= DUREE_IMMUNITE:
                self.immunite_active = False
                self.comp_immunite   = 0

        # Ralentissement
        if self.ralenti_actif:
            self.comp_ralenti += 1
            if self.comp_ralenti >= DUREE_RALENTI:
                self.ralenti_actif = False
                self.comp_ralenti  = 0

    def afficher(self):
        if self.inv and (self.comp_inv // 5) % 2 == 0:
            img = self.image.copy()
            img.set_alpha(80)
            self.fenetre.blit(img, self.rect)
        elif self.immunite_active:
            rayon = max(self.rect.w, self.rect.h) // 2 + 8
            pygame.draw.circle(self.fenetre, (255, 215, 0), self.rect.center, rayon, 3)
            self.fenetre.blit(self.image, self.rect)
        else:
            self.fenetre.blit(self.image, self.rect)

    def _peut_subir_degat(self):
        return not self.immunite_active and not self.inv

    def appliquer_degats(self, montant=1):
        if self._peut_subir_degat():
            self.vies    -= montant
            self.inv      = True
            self.comp_inv = 0
            return True
        return False

    def activer_immunite(self):
        self.immunite_active = True
        self.comp_immunite   = 0

    def activer_ralentissement(self):
        self.ralenti_actif = True
        self.comp_ralenti  = 0


class Balle(Sprite):
    def __init__(self, image, fenetre, dx=3.3, dy=3.3):
        lw, lh = fenetre.get_size()
        x = random.randint(0, lw - image.get_width())
        y = random.randint(0, lh - image.get_height())
        super().__init__(image, fenetre, x, y)
        self.dx = dx
        self.dy = dy

    def deplacer(self, facteur_vitesse=1.0, ralenti=False):
        lw, lh = self.fenetre.get_size()
        mult = 0.4 if ralenti else facteur_vitesse
        self.rect.x += self.dx * mult
        self.rect.y += self.dy * mult
        if self.rect.left < 0:
            self.rect.left = 0
            self.dx = abs(self.dx) + random.uniform(-0.3, 0.3)
        if self.rect.right > lw:
            self.rect.right = lw
            self.dx = -(abs(self.dx) + random.uniform(-0.3, 0.3))
        if self.rect.top < 0:
            self.rect.top = 0
            self.dy = abs(self.dy) + random.uniform(-0.3, 0.3)
        if self.rect.bottom > lh:
            self.rect.bottom = lh
            self.dy = -(abs(self.dy) + random.uniform(-0.3, 0.3))


class Fruit(ObjetTombant):
    def __init__(self, image, fenetre):
        surf = pygame.transform.scale(image, (50, 50))
        super().__init__(surf, fenetre, vitesse=random.uniform(2.0, 4.0))


def creer_bonus_surf(couleur, couleur_bord, texte, taille=48):
    """Crée la surface d'un bonus circulaire."""
    surf = pygame.Surface((taille, taille), pygame.SRCALPHA)
    pygame.draw.circle(surf, couleur,      (taille//2, taille//2), taille//2)
    pygame.draw.circle(surf, couleur_bord, (taille//2, taille//2), taille//2, 3)
    font = pygame.font.Font(None, 30)
    txt  = font.render(texte, True, (255, 255, 255))
    surf.blit(txt, txt.get_rect(center=(taille//2, taille//2)))
    return surf

class BonusImmunite(ObjetTombant):
    def __init__(self, fenetre):
        super().__init__(creer_bonus_surf((255, 215, 0), (200, 160, 0), "IMM"), fenetre)

class BonusRalenti(ObjetTombant):
    def __init__(self, fenetre):
        super().__init__(creer_bonus_surf((50, 150, 255), (30, 100, 200), "SLOW"), fenetre)

class BonusCoeur(ObjetTombant):
    def __init__(self, fenetre):
        super().__init__(creer_bonus_surf((255, 80, 130), (200, 40, 90), "+½"), fenetre)


# ─── Particules & Flash ───────────────────────────────────────────────────────
class Particule:
    def __init__(self, x, y, couleur=(255, 80, 0)):
        self.x, self.y = x, y
        angle    = random.uniform(0, 2 * math.pi)
        vitesse  = random.uniform(2, 6)
        self.vx  = math.cos(angle) * vitesse
        self.vy  = math.sin(angle) * vitesse
        self.duree  = random.randint(15, 30)
        self.age    = 0
        self.couleur= couleur
        self.rayon  = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.age += 1

    def afficher(self, fenetre):
        r = min(255, self.couleur[0])
        g = max(0, self.couleur[1] - self.age * 4)
        b = self.couleur[2]
        rayon = max(1, int(self.rayon * (1 - self.age / self.duree)))
        pygame.draw.circle(fenetre, (r, g, b), (int(self.x), int(self.y)), rayon)

    def est_mort(self):
        return self.age >= self.duree


class FlashEcran:
    def __init__(self):
        self.surf  = pygame.Surface((LARGEUR, HAUTEUR))
        self.alpha = 0
        self.actif = False
        self.couleur = (255, 0, 0)

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
        if self.actif:
            self.surf.fill(self.couleur)
            self.surf.set_alpha(self.alpha)
            fenetre.blit(self.surf, (0, 0))


# ─── Helpers d'affichage ──────────────────────────────────────────────────────
def dessiner_barre_vie(fenetre, vies, max_vies, x=10, y=105, larg=200, haut=22):
    ratio = max(0.0, vies / max_vies)
    pygame.draw.rect(fenetre, (80, 0, 0),       (x, y, larg, haut), border_radius=8)
    if ratio > 0:
        couleur = (int(255 * (1 - ratio)), int(220 * ratio), 0)
        pygame.draw.rect(fenetre, couleur, (x, y, int(larg * ratio), haut), border_radius=8)
    pygame.draw.rect(fenetre, (200, 200, 200),  (x, y, larg, haut), width=2, border_radius=8)
    font   = pygame.font.Font(None, 24)
    ent    = int(vies)
    demi   = "½" if (vies - ent) >= 0.5 else ""
    fenetre.blit(font.render(f"Vies: {ent}{demi} / {int(max_vies)}", True, (255, 255, 255)), (x + 5, y + 3))

def afficher_texte_centre(fenetre, texte, taille, couleur, cy):
    font = pygame.font.Font(None, taille)
    surf = font.render(texte, True, couleur)
    fenetre.blit(surf, surf.get_rect(center=(LARGEUR // 2, cy)))

def afficher_annonce_vague(fenetre, numero):
    afficher_texte_centre(fenetre, f"VAGUE  {numero}", 80, (255, 220, 50), HAUTEUR // 2)
    pygame.display.flip()
    pygame.time.wait(1200)

def lancer_particules(liste, cx, cy, couleur, n=15):
    for _ in range(n):
        liste.append(Particule(cx, cy, couleur))


# ─── Écran d'accueil ──────────────────────────────────────────────────────────
def ecran_accueil(fenetre, res):
    horloge = pygame.time.Clock()

    # Fond dégradé
    fond_acc = pygame.Surface((LARGEUR, HAUTEUR))
    for y in range(HAUTEUR):
        t = y / HAUTEUR
        pygame.draw.line(fond_acc, (int(10+t*30), int(10+t*20), int(40+t*80)), (0, y), (LARGEUR, y))

    perso_img = pygame.transform.scale(res["perso"], (120, 120))
    etoiles   = [(random.randint(0, LARGEUR), random.randint(0, HAUTEUR),
                  random.uniform(0.3, 1.5)) for _ in range(80)]

    btn_rect = pygame.Rect(LARGEUR//2 - 130, HAUTEUR - 140, 260, 65)
    highscores = charger_highscores()
    angle = 0

    font_titre  = pygame.font.Font(None, 90)
    font_bouton = pygame.font.Font(None, 50)
    font_hs     = pygame.font.Font(None, 28)
    font_sous   = pygame.font.Font(None, 36)

    while True:
        horloge.tick(60)
        angle += 3
        fenetre.blit(fond_acc, (0, 0))

        for ex, ey, eb in etoiles:
            lum = int(150 + 105 * abs(math.cos(math.radians(angle * eb))))
            pygame.draw.circle(fenetre, (lum, lum, lum), (int(ex), int(ey)), int(eb))

        pygame.draw.line(fenetre, (255, 200, 0), (60, 70),  (LARGEUR - 60, 70),  2)
        for texte, couleur, cy in [("SURVIVAL", (255, 220, 50), 120), ("CHARACTER", (255, 255, 255), 205)]:
            surf = font_titre.render(texte, True, couleur)
            fenetre.blit(surf, surf.get_rect(center=(LARGEUR // 2, cy)))
        pygame.draw.line(fenetre, (255, 200, 0), (60, 240), (LARGEUR - 60, 240), 2)

        perso_rect = perso_img.get_rect(center=(LARGEUR // 2, 320))
        halo_r = int(75 + 10 * abs(math.cos(math.radians(angle))))
        pygame.draw.circle(fenetre, (80, 80, 160), perso_rect.center, halo_r)
        fenetre.blit(perso_img, perso_rect)

        if highscores:
            fenetre.blit(font_hs.render("🏆 MEILLEURS SCORES", True, (255, 215, 0)),
                         font_hs.render("🏆 MEILLEURS SCORES", True, (255, 215, 0)).get_rect(center=(LARGEUR - 140, 280)))
            for i, hs in enumerate(highscores[:3]):
                c = [(255,215,0),(192,192,192),(205,127,50)][i]
                s = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, c)
                fenetre.blit(s, s.get_rect(center=(LARGEUR - 140, 305 + i * 25)))

        mx, my  = pygame.mouse.get_pos()
        survol  = btn_rect.collidepoint(mx, my)
        pygame.draw.rect(fenetre, (50,200,100) if survol else (30,140,70),   btn_rect, border_radius=14)
        pygame.draw.rect(fenetre, (150,255,150) if survol else (80,200,100), btn_rect, width=3, border_radius=14)
        surf_btn = font_bouton.render("JOUER", True, (255, 255, 255))
        fenetre.blit(surf_btn, surf_btn.get_rect(center=btn_rect.center))

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
                if btn_rect.collidepoint(event.pos):
                    return


# ─── Réinitialisation ─────────────────────────────────────────────────────────
def reset_jeu(perso, res, fenetre):
    perso.vies            = 3
    perso.score           = 0
    perso.inv             = True
    perso.comp_inv        = 0
    perso.immunite_active = False
    perso.ralenti_actif   = False
    perso.comp_immunite   = perso.comp_ralenti = 0
    perso.rect.topleft    = (LARGEUR//2 - perso.rect.w//2, HAUTEUR - perso.rect.h)
    balles = [Balle(res["balle"], fenetre)]
    now = pygame.time.get_ticks()
    timers = {k: now for k in ("balle", "sauvegarde", "debut", "fruit", "bonus", "ralenti", "coeur")}
    return balles, timers, 1, 1000

def lancer_musique():
    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        pass


# ─── Main ─────────────────────────────────────────────────────────────────────
pygame.mixer.init()
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("SURVIVAL CHARACTER")

res = charger_ressources()

perso = Perso(res["perso"], fenetre,
              x=LARGEUR//2 - res["perso"].get_width()//2,
              y=HAUTEUR   - res["perso"].get_height())
fond  = Fond(res["fond"], fenetre, vitesse=2)
flash = FlashEcran()

ecran_accueil(fenetre, res)

balles, timers, vague_actuelle, score_prochaine_vague = reset_jeu(perso, res, fenetre)
afficher_annonce_vague(fenetre, vague_actuelle)

fruits = bonus_imm = bonus_ral = bonus_coeur = particules = []
fruits, bonus_imm, bonus_ral, bonus_coeur, particules = [], [], [], [], []
game_over = en_pause = son_go_joue = False
horloge   = pygame.time.Clock()

# ─── Boucle principale ────────────────────────────────────────────────────────
while True:
    horloge.tick(FPS)
    now = pygame.time.get_ticks()

    # ── Événements ──────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_over = True  # force sortie propre via break ci-dessous si ESCAPE
                break

            if event.key == pygame.K_p and not game_over:
                en_pause = True
                pygame.mixer.music.pause()

            if game_over:
                if event.key == pygame.K_SPACE:
                    balles, timers, vague_actuelle, score_prochaine_vague = reset_jeu(perso, res, fenetre)
                    fruits = bonus_imm = bonus_ral = bonus_coeur = particules = []
                    fruits, bonus_imm, bonus_ral, bonus_coeur, particules = [], [], [], [], []
                    game_over = son_go_joue = en_pause = False
                    fond.y1, fond.y2 = 0, -HAUTEUR
                    afficher_annonce_vague(fenetre, vague_actuelle)
                    lancer_musique()

                elif event.key == pygame.K_l:
                    result = charger_partie(perso, res, fenetre)
                    if result[0] is not None:
                        balles, game_over = result
                        fruits = bonus_imm = bonus_ral = bonus_coeur = particules = []
                        fruits, bonus_imm, bonus_ral, bonus_coeur, particules = [], [], [], [], []
                        son_go_joue = False
                        timers = {k: now for k in timers}
                        if not game_over:
                            lancer_musique()

            if en_pause and event.key == pygame.K_u:
                en_pause = False
                pygame.mixer.music.unpause()
    else:
        # ── Rendu du fond ─────────────────────────────────────────────────────
        fond.actif = not game_over
        fond.deplacer()
        fond.afficher()

        # ── PAUSE ─────────────────────────────────────────────────────────────
        if en_pause:
            surf_p = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
            surf_p.fill((0, 0, 0, 140))
            fenetre.blit(surf_p, (0, 0))
            afficher_texte_centre(fenetre, "PAUSE", 100, (255, 255, 255), HAUTEUR//2 - 40)
            afficher_texte_centre(fenetre, "Appuyez sur U pour reprendre", 36, (200, 200, 200), HAUTEUR//2 + 40)
            pygame.display.flip()
            horloge.tick(FPS)
            continue

        # ── GAME OVER ─────────────────────────────────────────────────────────
        if perso.vies <= 0 and not game_over:
            game_over = True
            sauvegarder_highscore(perso.score)
            if not son_go_joue:
                pygame.mixer.music.stop()
                jouer_son(res, "son_game_over")
                son_go_joue = True

        if game_over:
            for obj in balles + fruits + bonus_imm:
                obj.afficher()
            perso.afficher()
            afficher_texte_centre(fenetre, "GAME OVER",            100, (255, 0, 0),     HAUTEUR//2 - 60)
            afficher_texte_centre(fenetre, f"Score: {perso.score}",  60, (255, 255, 255), HAUTEUR//2 + 20)
            afficher_texte_centre(fenetre, f"Temps: {perso.score//30} s", 40, (255, 255, 255), HAUTEUR//2 + 80)
            font_hs = pygame.font.Font(None, 32)
            surf_hs = font_hs.render("🏆 TOP SCORES", True, (255, 215, 0))
            fenetre.blit(surf_hs, surf_hs.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 130)))
            for i, hs in enumerate(charger_highscores()[:3]):
                c = [(255,215,0),(192,192,192),(205,127,50)][i]
                s = font_hs.render(f"{i+1}. {hs['score']}  ({hs['date']})", True, c)
                fenetre.blit(s, s.get_rect(center=(LARGEUR//2, HAUTEUR//2 + 160 + i*28)))
            afficher_texte_centre(fenetre, "ESPACE = rejouer  |  L = charger  |  ECHAP = quitter",
                                  30, (255, 255, 255), HAUTEUR - 40)

        # ── JEU EN COURS ──────────────────────────────────────────────────────
        else:
            perso.afficher()
            perso.deplacer()
            perso.score += 1

            temps_ecoule    = (now - timers["debut"]) / 1000.0
            facteur_vitesse = min(1.0 + (temps_ecoule / 30.0) * 0.5, 3.0)

            # Nouvelle vague
            if perso.score >= score_prochaine_vague:
                vague_actuelle       += 1
                score_prochaine_vague += 1000
                afficher_annonce_vague(fenetre, vague_actuelle)
                timers["balle"] = pygame.time.get_ticks()

            # Sauvegarde auto
            if now - timers["sauvegarde"] >= INTERVALLE_SAUVEGARDE:
                sauvegarder_partie(perso, balles, game_over)
                timers["sauvegarde"] = now

            # Nouvelle balle
            if now - timers["balle"] >= INTERVALLE_BALLE:
                max_b = min(3 + vague_actuelle, MAX_BALLES)
                if len(balles) < max_b:
                    v = 3.3 * facteur_vitesse
                    balles.append(Balle(res["balle"], fenetre,
                                        dx=random.choice([-1,1]) * v,
                                        dy=random.choice([-1,1]) * v))
                timers["balle"] = now

            # Nouveau fruit
            if now - timers["fruit"] >= INTERVALLE_FRUIT:
                t = random.choice(["fraise", "pasteque"])
                if res[t]:
                    fruits.append(Fruit(res[t], fenetre))
                timers["fruit"] = now

            # Bonus immunité
            if now - timers["bonus"] >= INTERVALLE_BONUS:
                bonus_imm.append(BonusImmunite(fenetre))
                timers["bonus"] = now

            # Bonus ralenti
            if now - timers["ralenti"] >= INTERVALLE_BONUS_RALENTI:
                bonus_ral.append(BonusRalenti(fenetre))
                timers["ralenti"] = now

            # Bonus coeur
            if now - timers["coeur"] >= INTERVALLE_BONUS_COEUR:
                bonus_coeur.append(BonusCoeur(fenetre))
                timers["coeur"] = now

            # Déplacement / affichage des balles
            for b in balles:
                b.deplacer(facteur_vitesse, perso.ralenti_actif)
                b.afficher()

            # Gestion générique des objets tombants
            def gerer_objets(liste, on_collision):
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

            def collision_fruit(obj):
                if perso.appliquer_degats(0.5):
                    flash.declencher((255, 100, 0))
                    jouer_son(res, "son_collision")
                    lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 100, 0), 10)

            def collision_immunite(obj):
                perso.activer_immunite()
                flash.declencher((255, 215, 0))
                jouer_son(res, "son_bonus")
                lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 215, 0))

            def collision_ralenti(obj):
                perso.activer_ralentissement()
                flash.declencher((50, 150, 255))
                jouer_son(res, "son_bonus")
                lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (50, 150, 255))

            def collision_coeur(obj):
                perso.vies = min(perso.vies + 0.5, 3)
                flash.declencher((255, 80, 130))
                jouer_son(res, "son_bonus")
                lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 80, 130))

            fruits      = gerer_objets(fruits,      collision_fruit)
            bonus_imm   = gerer_objets(bonus_imm,   collision_immunite)
            bonus_ral   = gerer_objets(bonus_ral,   collision_ralenti)
            bonus_coeur = gerer_objets(bonus_coeur, collision_coeur)

            # Collisions balles
            for b in balles:
                if perso.collide(b):
                    if perso.appliquer_degats(1):
                        flash.declencher((255, 0, 0))
                        jouer_son(res, "son_collision")
                        lancer_particules(particules, perso.rect.centerx, perso.rect.centery, (255, 80, 0), 20)

            # Particules
            particules = [p for p in particules if not p.est_mort()]
            for p in particules:
                p.update()
                p.afficher(fenetre)

            flash.update()
            flash.afficher(fenetre)

            # ── HUD ───────────────────────────────────────────────────────────
            font_hud = pygame.font.Font(None, 36)
            font_leg = pygame.font.Font(None, 24)

            fenetre.blit(font_hud.render(f"Score: {perso.score}", True, (255,255,255)), (10, 10))
            fenetre.blit(font_hud.render(f"Vague: {vague_actuelle}", True, (255,220,50)), (10, 45))
            pct = int((facteur_vitesse - 1.0) / 2.0 * 100)
            fenetre.blit(font_leg.render(f"Difficulté: {pct}%", True, (200,200,255)), (10, 80))

            dessiner_barre_vie(fenetre, perso.vies, 3)

            if perso.immunite_active:
                s = font_hud.render(f"⭐ IMMUNITE: {(DUREE_IMMUNITE - perso.comp_immunite)//30}s", True, (255,215,0))
                fenetre.blit(s, s.get_rect(center=(LARGEUR//2, 20)))

            if perso.ralenti_actif:
                s = font_hud.render(f"❄ SLOW: {(DUREE_RALENTI - perso.comp_ralenti)//30}s", True, (50,200,255))
                fenetre.blit(s, s.get_rect(center=(LARGEUR//2, 55)))

            fenetre.blit(font_leg.render(
                "🍓 = -½ vie  |  ⭐ = Immunité  |  ❄ = Ralentit balles  |  💗 = +½ vie",
                True, (255, 220, 80)), (10, HAUTEUR - 30))

        pygame.display.flip()
        continue

    break  # sortie de la boucle sur ESCAPE ou QUIT

pygame.mixer.music.stop()
pygame.quit()