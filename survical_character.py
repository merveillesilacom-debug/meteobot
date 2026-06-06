import pygame
import sys
import math
import random
import json


NIVEAUX = {
    1: {"fichier": "background.jpg", "nom": "Verdure",        "couleur": (80,  200, 80)},
    2: {"fichier": "sky1.png",       "nom": "Dans les cieux", "couleur": (100, 180, 255)},
    3: {"fichier": "marsmid.png",    "nom": "Surface de Mars","couleur": (180, 80,  40)},
}

SCORE_PAR_NIVEAU = 500



def ecran_accueil(fenetre, largeur, hauteur):
    horloge_acc = pygame.time.Clock()
    tick = 0

    font_titre = pygame.font.Font(None, 108)
    font_sous  = pygame.font.Font(None, 34)
    font_btn   = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 26)

    try:
        bg = pygame.image.load("background.jpg").convert()
        bg = pygame.transform.scale(bg, (largeur, hauteur))
    except:
        bg = pygame.Surface((largeur, hauteur))
        for fy in range(hauteur):
            ratio = fy / hauteur
            pygame.draw.line(bg, (int(10+ratio*30), int(10+ratio*20), int(40+ratio*80)),
                             (0, fy), (largeur, fy))

    overlay = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    for fy in range(hauteur):
        ratio = fy / hauteur
        alpha = int(80 + ratio * 120)
        overlay.fill((0, 0, 0, alpha), pygame.Rect(0, fy, largeur, 1))

    try:
        perso_orig = pygame.image.load("perso.png").convert_alpha()
        perso_img  = pygame.transform.scale(perso_orig, (120, 160))
        use_perso  = True
    except:
        use_perso = False

    particules = [{
        "x": random.uniform(0, largeur),
        "y": random.uniform(0, hauteur),
        "vy": random.uniform(-0.5, -0.1),
        "r": random.randint(1, 3),
        "alpha": random.randint(60, 180),
        "c": random.choice([(255,215,0),(255,180,50),(255,255,200),(200,160,255)])
    } for _ in range(70)]

    btns = [
        {"label": "JOUER",   "action": "jouer",   "y": hauteur - 260},
        {"label": "QUITTER", "action": "quitter",  "y": hauteur - 190},
    ]
    btn_w, btn_h = 280, 55
    for b in btns:
        b["rect"] = pygame.Rect(largeur//2 - btn_w//2, b["y"], btn_w, btn_h)

    def dessiner_brume(surf, tk):
        bs = pygame.Surface((largeur, 120), pygame.SRCALPHA)
        for bx in range(0, largeur, 4):
            bh = int(40 + 30 * math.sin(bx * 0.02 + tk * 0.03))
            ba = int(60 + 30 * math.sin(bx * 0.015 + tk * 0.02))
            pygame.draw.line(bs, (180, 200, 255, ba), (bx, 120), (bx, 120 - bh))
        surf.blit(bs, (0, hauteur - 120))

    while True:
        horloge_acc.tick(60)
        tick += 1

        fenetre.blit(bg, (0, 0))
        fenetre.blit(overlay, (0, 0))
        dessiner_brume(fenetre, tick)

        psurf = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
        for p in particules:
            p["y"] += p["vy"]
            if p["y"] < -5:
                p["y"] = hauteur + 5
                p["x"] = random.uniform(0, largeur)
            pygame.draw.circle(psurf, (*p["c"], p["alpha"]),
                               (int(p["x"]), int(p["y"])), p["r"])
        fenetre.blit(psurf, (0, 0))

        if use_perso:
            bob    = int(6 * math.sin(tick * 0.07))
            halo_r = int(85 + 12 * math.sin(tick * 0.05))
            hsurf  = pygame.Surface((halo_r*2, halo_r*2), pygame.SRCALPHA)
            pygame.draw.circle(hsurf, (255, 215, 0, 55), (halo_r, halo_r), halo_r)
            cx, cy = largeur//2, hauteur - 310
            fenetre.blit(hsurf, (cx - halo_r, cy - halo_r + bob))
            fenetre.blit(perso_img, perso_img.get_rect(center=(cx, cy + bob)))

        lueur = int(200 + 55 * math.sin(tick * 0.04))
        for dx, dy in [(3,3),(-3,3)]:
            sh = font_titre.render("SURVIVAL",  True, (60, 40, 0))
            sc = font_titre.render("CHARACTER", True, (60, 40, 0))
            fenetre.blit(sh, sh.get_rect(center=(largeur//2+dx, 118+dy)))
            fenetre.blit(sc, sc.get_rect(center=(largeur//2+dx, 208+dy)))
        lg = font_titre.render("SURVIVAL", True, (255, lueur, 0))
        lg.set_alpha(70)
        
        fenetre.blit(lg, lg.get_rect(center=(largeur//2, 115)))
        
        s1 = font_titre.render("SURVIVAL",  True, (255, lueur, 50))
        s2 = font_titre.render("CHARACTER", True, (255, 245, 200))
        
        fenetre.blit(s1, s1.get_rect(center=(largeur//2, 115)))
        fenetre.blit(s2, s2.get_rect(center=(largeur//2, 205)))
        
        ref1 = pygame.transform.flip(s1, False, True); ref1.set_alpha(30)
        ref2 = pygame.transform.flip(s2, False, True); ref2.set_alpha(30)
        
        fenetre.blit(ref1, ref1.get_rect(center=(largeur//2, 165)))
        fenetre.blit(ref2, ref2.get_rect(center=(largeur//2, 255)))
        
        pygame.draw.line(fenetre, (255, lueur, 0), (80, 250), (largeur-80, 250), 2)
        acc = font_sous.render("Le monde bascule.  Survivez.", True, (200, 180, 255))
        fenetre.blit(acc, acc.get_rect(center=(largeur//2, 278)))

        mx, my = pygame.mouse.get_pos()
        for b in btns:
            survol = b["rect"].collidepoint(mx, my)
            coul   = (80, 60, 20, 220) if survol else (30, 20, 5, 180)
            bord   = (255, lueur, 0)   if survol else (140, 100, 20)
            bsurf  = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            pygame.draw.rect(bsurf, coul, bsurf.get_rect(), border_radius=10)
            pygame.draw.rect(bsurf, (*bord, 255), bsurf.get_rect(), width=2, border_radius=10)
            fenetre.blit(bsurf, b["rect"].topleft)
            coul_txt = (255, lueur, 50) if survol else (220, 200, 140)
            txt = font_btn.render(b["label"], True, coul_txt)
            fenetre.blit(txt, txt.get_rect(center=b["rect"].center))

        hint = font_small.render("ESPACE = Jouer  |  ECHAP = Quitter", True, (100, 100, 100))
        fenetre.blit(hint, hint.get_rect(center=(largeur//2, hauteur - 25)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in btns:
                    if b["rect"].collidepoint(event.pos):
                        if b["action"] == "quitter":
                            pygame.quit(); sys.exit()
                        elif b["action"] == "jouer":
                            return


def lire_images(fenetre):
    images = {}
    lw, lh = fenetre.get_size()

    images["perso"] = pygame.image.load("perso.png").convert_alpha()
    images["balle"] = pygame.image.load("balle.png").convert_alpha()

    
    try:
        img_bombe = pygame.image.load("g5715.png").convert_alpha()
        images["bombe"] = pygame.transform.scale(img_bombe, (50, 60))
    except Exception as e:
        print(f"g5715.png non trouve : {e}")
        surf = pygame.Surface((50, 60), pygame.SRCALPHA)
        pygame.draw.circle(surf, (40, 40, 40), (25, 40), 22)
        images["bombe"] = surf

   
    try:
        img_meteor = pygame.image.load("Meteor1.png").convert_alpha()
        images["meteor"] = pygame.transform.scale(img_meteor, (55, 55))
    except Exception as e:
        print(f"Meteor1.png non trouve : {e}")
        surf = pygame.Surface((55, 55), pygame.SRCALPHA)
        pygame.draw.circle(surf, (160, 80, 40), (27, 27), 27)
        images["meteor"] = surf

    
    surf_imm = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf_imm, (255, 215, 0), (20, 20), 20)
    pygame.draw.circle(surf_imm, (255, 255, 180), (20, 20), 12)
    images["bonus_immunite"] = surf_imm

    
    surf_ral = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf_ral, (50, 150, 255), (20, 20), 20)
    pygame.draw.circle(surf_ral, (180, 220, 255), (20, 20), 12)
    images["bonus_ralenti"] = surf_ral

    
    for num, niveau in NIVEAUX.items():
        try:
            img = pygame.image.load(niveau["fichier"]).convert()
            images[f"fond_{num}"] = pygame.transform.scale(img, (lw, lh))
            print(f"Niveau {num} ({niveau['fichier']}) charge.")
        except Exception as e:
            print(f"Fond {niveau['fichier']} non trouve : {e}")
            surf = pygame.Surface((lw, lh))
            surf.fill(niveau["couleur"])
            images[f"fond_{num}"] = surf

    images["son_collision"] = None
    images["son_game_over"] = None

    try:
        images["son_game_over"] = pygame.mixer.Sound("game_over.mp3")
        images["son_game_over"].set_volume(0.8)
    except:
        print("game_over.mp3 non trouve")

    try:
        images["son_collision"] = pygame.mixer.Sound("collision.wav")
        images["son_collision"].set_volume(0.5)
    except:
        print("collision.wav non trouve (optionnel)")

    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        print("musique_fond.OGG non trouve")

    return images


def sauvegarder_partie(perso, balles, game_over):
    donnees = {
        'perso': {
            'x': perso.rect.x, 'y': perso.rect.y,
            'vies': perso.vies, 'score': perso.score,
            'inv': perso.inv,   'comp_inv': perso.comp_inv
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
        print("Partie sauvegardee !")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")
        return False


def charger_partie(perso, images, fenetre):
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
            balle.rect.x     = bd['x'];  balle.rect.y     = bd['y']
            balle.depballe_x = bd['depballe_x']
            balle.depballe_y = bd['depballe_y']
            balles.append(balle)
        game_over = donnees['game_over']
        print("Partie chargee !")
        return balles, game_over
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
        lw, lh = fenetre.get_size()
        self.image = pygame.transform.scale(image, (lw, lh))
        self.y1 = 0;  self.y2 = -lh
        self.haut = lh;  self.actif = False

    def changer_niveau(self, images, num_niveau):
        self.image = images[f"fond_{num_niveau}"]

    def deplacer(self):
        if not self.actif:
            return
        self.y1 += self.vitesse;  self.y2 += self.vitesse
        if self.y1 >= self.haut: self.y1 = self.y2 - self.haut
        if self.y2 >= self.haut: self.y2 = self.y1 - self.haut

    def afficher(self):
        self.fenetre.blit(self.image, (0, self.y1))
        self.fenetre.blit(self.image, (0, self.y2))


class Perso(ElementGraphique):
    DUREE_IMMUNITE = 7 * 30   # 7 s a 30 FPS
    DUREE_RALENTI  = 5 * 30   # 5 s a 30 FPS

    def __init__(self, image, fenetre, x=0, y=0):
        super().__init__(image, fenetre, x, y)
        self.vies            = 3
        self.inv             = False
        self.comp_inv        = 0
        self.score           = 0
        self.immunite_active = False
        self.comp_immunite   = 0
        self.ralenti_actif   = False
        self.comp_ralenti    = 0

    def activer_immunite(self):
        self.immunite_active = True
        self.comp_immunite   = 0
        self.inv             = True
        self.comp_inv        = 0

    def activer_ralentissement(self):
        self.ralenti_actif = True
        self.comp_ralenti  = 0

    def deplacer(self):
        if touches[pygame.K_DOWN]:  self.rect.y += 3
        if touches[pygame.K_UP]:    self.rect.y -= 3
        if touches[pygame.K_LEFT]:  self.rect.x -= 3
        if touches[pygame.K_RIGHT]: self.rect.x += 3
        self.rect.x = max(0, min(self.rect.x, largeur - self.rect.w))
        self.rect.y = max(0, min(self.rect.y, hauteur - self.rect.h))
        if self.inv and not self.immunite_active:
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = False
        if self.immunite_active:
            self.comp_immunite += 1
            if self.comp_immunite >= self.DUREE_IMMUNITE:
                self.immunite_active = False
                self.inv             = False
        if self.ralenti_actif:
            self.comp_ralenti += 1
            if self.comp_ralenti >= self.DUREE_RALENTI:
                self.ralenti_actif = False

    def appliquer_degats(self):
        if not self.inv:
            self.vies    -= 1
            self.inv      = True
            self.comp_inv = 0
            print(f"aie! vies: {self.vies}")
            return True
        return False


class Balle(ElementGraphique):
    def __init__(self, image, fenetre, depballe_x=3.3, depballe_y=3.3):
        lw, lh = fenetre.get_size()
        x = random.randint(0, lw - image.get_width())
        y = random.randint(0, lh - image.get_height())
        super().__init__(image, fenetre, x, y)
        self.depballe_x = depballe_x
        self.depballe_y = depballe_y

    def deplacer(self, ralenti=False):
        facteur = 0.4 if ralenti else 1.0
        lw, lh = self.fenetre.get_size()
        self.rect.x += self.depballe_x * facteur
        self.rect.y += self.depballe_y * facteur
        if self.rect.x < 0:
            self.rect.x = 0;  self.depballe_x = -self.depballe_x
        if self.rect.x + self.rect.w > lw:
            self.rect.x = lw - self.rect.w;  self.depballe_x = -self.depballe_x
        if self.rect.y < 0:
            self.rect.y = 0;  self.depballe_y = -self.depballe_y
        if self.rect.y + self.rect.h > lh:
            self.rect.y = lh - self.rect.h;  self.depballe_y = -self.depballe_y


class Bombe(ElementGraphique):
    def __init__(self, image, fenetre):
        lw = fenetre.get_width()
        x  = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse_base = random.uniform(2.5, 5.0)

    def deplacer(self, ralenti=False):
        facteur = 0.4 if ralenti else 1.0
        self.rect.y += self.vitesse_base * facteur
        lh = self.fenetre.get_height()
        if self.rect.y > lh:
            lw = self.fenetre.get_width()
            self.rect.x = random.randint(0, lw - self.rect.w)
            self.rect.y = -self.rect.h
            self.vitesse_base = random.uniform(2.5, 5.0)


class Meteore(ElementGraphique):
    def __init__(self, image, fenetre):
        lw = fenetre.get_width()
        x  = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse_base = random.uniform(4.0, 8.0)
        self.angle        = 0
        self.image_orig   = image

    def deplacer(self, ralenti=False):
        facteur = 0.4 if ralenti else 1.0
        self.rect.y += self.vitesse_base * facteur
        self.angle   = (self.angle + 4) % 360
        lh = self.fenetre.get_height()
        if self.rect.y > lh:
            lw = self.fenetre.get_width()
            self.rect.x = random.randint(0, lw - self.rect.w)
            self.rect.y = -self.rect.h
            self.vitesse_base = random.uniform(4.0, 8.0)

    def afficher(self):
        img_rot  = pygame.transform.rotate(self.image_orig, self.angle)
        rect_rot = img_rot.get_rect(center=self.rect.center)
        self.fenetre.blit(img_rot, rect_rot)


class BonusTombant(ElementGraphique):
    def __init__(self, image, fenetre, vitesse=2.5):
        lw = fenetre.get_width()
        x  = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse = vitesse

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


def BonusImmunite(image, fenetre):
    return BonusTombant(image, fenetre, vitesse=random.uniform(2.0, 3.5))

def BonusRalenti(image, fenetre):
    return BonusTombant(image, fenetre, vitesse=random.uniform(2.0, 3.5))




def afficher_annonce_niveau(fenetre, largeur, hauteur, num_niveau):
    nom     = NIVEAUX[num_niveau]["nom"]
    couleur = NIVEAUX[num_niveau]["couleur"]
    font_grand = pygame.font.Font(None, 80)
    font_petit = pygame.font.Font(None, 40)
    for alpha in range(255, 0, -5):
        overlay = pygame.Surface((largeur, hauteur))
        overlay.set_alpha(alpha // 3)
        overlay.fill((0, 0, 0))
        fenetre.blit(overlay, (0, 0))
        surf1 = font_grand.render(f"NIVEAU {num_niveau}", True, couleur)
        surf2 = font_petit.render(nom, True, (255, 255, 255))
        fenetre.blit(surf1, surf1.get_rect(center=(largeur//2, hauteur//2 - 30)))
        fenetre.blit(surf2, surf2.get_rect(center=(largeur//2, hauteur//2 + 50)))
        pygame.display.flip()
        pygame.time.delay(16)

pygame.mixer.init()
pygame.init()

largeur = 640
hauteur = 480
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Survival Character")

ecran_accueil(fenetre, largeur, hauteur)

images = lire_images(fenetre)
niveau_actuel         = 1
score_prochain_niveau = SCORE_PAR_NIVEAU

td_balle              = pygame.time.get_ticks()
intervalle_balle      = 6000
nbre_max_balle        = 6
td_sauvegarde         = pygame.time.get_ticks()
intervalle_sauvegarde = 5000
td_debut_jeu          = pygame.time.get_ticks()

bombes               = []
bonus_immunite_liste = []
bonus_ralenti_liste  = []
meteores             = []

td_bombe             = pygame.time.get_ticks()
intervalle_bombe     = 8000
td_bonus_imm         = pygame.time.get_ticks()
intervalle_bonus_imm = 15000
td_bonus_ral         = pygame.time.get_ticks()
intervalle_bonus_ral = 12000
td_meteor            = pygame.time.get_ticks()
intervalle_meteor    = 5000

perso = Perso(images["perso"], fenetre,
              x=largeur // 2 - images["perso"].get_width() // 2,
              y=hauteur - images["perso"].get_height())
perso.inv      = True
perso.comp_inv = 0

fond   = Fond(images[f"fond_{niveau_actuel}"], fenetre, vitesse=2)
balles = [Balle(images["balle"], fenetre)]

horloge = pygame.time.Clock()

game_over          = False
son_game_over_joue = False
continuer          = True

while continuer:

    horloge.tick(30)
    touches = pygame.key.get_pressed()

    if touches[pygame.K_ESCAPE]:
        continuer = False

    fond.actif = not game_over
    fond.deplacer()
    fond.afficher()

    if perso.vies <= 0 and not game_over:
        game_over = True
        if not son_game_over_joue:
            if images["son_game_over"]:
                images["son_game_over"].play()
            son_game_over_joue = True
            pygame.mixer.music.stop()

  
    if game_over:
        for balle in balles:
            balle.afficher()
        perso.afficher()

        font_go = pygame.font.Font(None, 100)
        surf = font_go.render("GAME OVER", True, (255, 0, 0))
        fenetre.blit(surf, surf.get_rect(center=(largeur//2, hauteur//2)))

        font_sc = pygame.font.Font(None, 60)
        surf = font_sc.render(f"Score: {perso.score}", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur//2, hauteur//2 + 80)))

        temps_survie = perso.score // 30
        font_t = pygame.font.Font(None, 40)
        surf = font_t.render(f"Temps de survie: {temps_survie} s", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur//2, hauteur//2 + 140)))

        font_r = pygame.font.Font(None, 30)
        surf = font_r.render("ESPACE pour rejouer  |  ECHAP pour quitter", True, (255, 255, 255))
        fenetre.blit(surf, surf.get_rect(center=(largeur//2, hauteur//2 + 200)))

    
    else:
        perso.afficher()
        perso.deplacer()
        perso.score += 1

        temps_actuel = pygame.time.get_ticks()
        ralenti      = perso.ralenti_actif

        
        if perso.score >= score_prochain_niveau and niveau_actuel < len(NIVEAUX):
            niveau_actuel += 1
            score_prochain_niveau += SCORE_PAR_NIVEAU
            fond.changer_niveau(images, niveau_actuel)
            afficher_annonce_niveau(fenetre, largeur, hauteur, niveau_actuel)
            print(f"Passage au niveau {niveau_actuel} !")

        if temps_actuel - td_sauvegarde >= intervalle_sauvegarde:
            sauvegarder_partie(perso, balles, game_over)
            td_sauvegarde = temps_actuel

       
        if temps_actuel - td_balle >= intervalle_balle:
            if len(balles) < nbre_max_balle:
                balles.append(Balle(images["balle"], fenetre))
                td_balle = temps_actuel

    
        for balle in balles:
            balle.deplacer(ralenti=ralenti)
            balle.afficher()
        for balle in balles:
            if perso.collide(balle):
                touche = perso.appliquer_degats()
                if touche and images["son_collision"]:
                    images["son_collision"].play()

        if niveau_actuel >= 2:

            if temps_actuel - td_bombe >= intervalle_bombe:
                bombes.append(Bombe(images["bombe"], fenetre))
                td_bombe = temps_actuel

            if temps_actuel - td_bonus_imm >= intervalle_bonus_imm:
                bonus_immunite_liste.append(BonusImmunite(images["bonus_immunite"], fenetre))
                td_bonus_imm = temps_actuel

            if temps_actuel - td_bonus_ral >= intervalle_bonus_ral:
                bonus_ralenti_liste.append(BonusRalenti(images["bonus_ralenti"], fenetre))
                td_bonus_ral = temps_actuel

            for bombe in bombes:
                bombe.deplacer(ralenti=ralenti)
                bombe.afficher()
            for bombe in bombes:
                if perso.collide(bombe):
                    touche = perso.appliquer_degats()
                    if touche and images["son_collision"]:
                        images["son_collision"].play()

            restants = []
            for bonus in bonus_immunite_liste:
                bonus.deplacer()
                if not bonus.hors_ecran():
                    if perso.collide(bonus):
                        perso.activer_immunite()
                    else:
                        bonus.afficher()
                        restants.append(bonus)
            bonus_immunite_liste = restants

            restants_ral = []
            for bonus in bonus_ralenti_liste:
                bonus.deplacer()
                if not bonus.hors_ecran():
                    if perso.collide(bonus):
                        perso.activer_ralentissement()
                    else:
                        bonus.afficher()
                        restants_ral.append(bonus)
            bonus_ralenti_liste = restants_ral

        
        if niveau_actuel >= 3:

            if temps_actuel - td_meteor >= intervalle_meteor:
                meteores.append(Meteore(images["meteor"], fenetre))
                td_meteor = temps_actuel

            for meteor in meteores:
                meteor.deplacer(ralenti=ralenti)
                meteor.afficher()
            for meteor in meteores:
                if perso.collide(meteor):
                    touche = perso.appliquer_degats()
                    if touche and images["son_collision"]:
                        images["son_collision"].play()

        
        font_hud = pygame.font.Font(None, 36)
        font_niv = pygame.font.Font(None, 28)

        fenetre.blit(font_hud.render(f"Score: {perso.score}", True, (255, 255, 255)), (10, 10))
        fenetre.blit(font_hud.render(f"Vies: {perso.vies}", True, (255, 255, 255)), (10, 50))

        nom_niveau  = NIVEAUX[niveau_actuel]["nom"]
        couleur_niv = NIVEAUX[niveau_actuel]["couleur"]
        fenetre.blit(font_niv.render(f"Niveau {niveau_actuel} - {nom_niveau}", True, couleur_niv), (10, 90))

        if niveau_actuel < len(NIVEAUX):
            score_debut = (niveau_actuel - 1) * SCORE_PAR_NIVEAU
            progression = max(0, min(1, (perso.score - score_debut) / SCORE_PAR_NIVEAU))
            pygame.draw.rect(fenetre, (80, 80, 80),  (10, 120, 150, 10))
            pygame.draw.rect(fenetre, couleur_niv,   (10, 120, int(150 * progression), 10))

        if perso.immunite_active:
            sec = (perso.DUREE_IMMUNITE - perso.comp_immunite) // 30 + 1
            surf_i = font_hud.render(f"IMMUNITE: {sec}s", True, (255, 215, 0))
            fenetre.blit(surf_i, surf_i.get_rect(center=(largeur//2, 20)))

        if perso.ralenti_actif:
            sec = (perso.DUREE_RALENTI - perso.comp_ralenti) // 30 + 1
            surf_r = font_hud.render(f"SLOW: {sec}s", True, (50, 180, 255))
            fenetre.blit(surf_r, surf_r.get_rect(center=(largeur//2, 55)))

       
        font_leg = pygame.font.Font(None, 22)
        fenetre.blit(font_leg.render(
            "Or = Immunite 7s  |  Bleu = Ralentit 5s",
            True, (220, 220, 100)), (10, hauteur - 20))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continuer = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_l and game_over:
                resultats = charger_partie(perso, images, fenetre)
                if resultats[0] is not None:
                    balles, game_over    = resultats
                    bombes               = []
                    meteores             = []
                    bonus_immunite_liste = []
                    bonus_ralenti_liste  = []
                    son_game_over_joue   = False
                    t = pygame.time.get_ticks()
                    td_balle = td_sauvegarde = td_debut_jeu = t
                    td_bombe = td_bonus_imm = td_bonus_ral = td_meteor = t
                    if not game_over:
                        try:
                            pygame.mixer.music.load("musique_fond.OGG")
                            pygame.mixer.music.set_volume(0.3)
                            pygame.mixer.music.play(-1)
                        except:
                            pass

            if event.key == pygame.K_SPACE and game_over:
                perso.vies            = 3
                perso.score           = 0
                perso.rect.x          = largeur // 2 - perso.rect.w // 2
                perso.rect.y          = hauteur - perso.rect.h
                perso.inv             = True
                perso.comp_inv        = 0
                perso.immunite_active = False
                perso.ralenti_actif   = False
                balles                = [Balle(images["balle"], fenetre)]
                bombes                = []
                meteores              = []
                bonus_immunite_liste  = []
                bonus_ralenti_liste   = []
                game_over             = False
                son_game_over_joue    = False
                niveau_actuel         = 1
                score_prochain_niveau = SCORE_PAR_NIVEAU
                fond.changer_niveau(images, niveau_actuel)
                fond.y1 = 0;  fond.y2 = -hauteur
                t = pygame.time.get_ticks()
                td_balle = td_debut_jeu = t
                td_bombe = td_bonus_imm = td_bonus_ral = td_meteor = t
                try:
                    pygame.mixer.music.load("musique_fond.OGG")
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                except:
                    pass

            elif event.key == pygame.K_ESCAPE:
                continuer = False

pygame.mixer.music.stop()
pygame.quit()

