import pygame
import random
import json

# ─────────────────────────── Niveaux ─────────────────────────────────────────

NIVEAUX = {
    1: {"fichier": "background.jpg", "nom": "Verdure",        "couleur": (80,  200, 80)},
    2: {"fichier": "sky1.png",       "nom": "Dans les cieux", "couleur": (100, 180, 255)},
    3: {"fichier": "marsmid.png",    "nom": "Surface de Mars","couleur": (180, 80,  40)},
}

SCORE_PAR_NIVEAU = 500  # points pour passer au niveau suivant

# ─────────────────────────── Chargement ressources ───────────────────────────

def lire_images(fenetre):
    images = {}
    lw, lh = fenetre.get_size()

    images["perso"] = pygame.image.load("perso.png").convert_alpha()
    images["balle"] = pygame.image.load("balle.png").convert_alpha()

    try:
        img_bombe = pygame.image.load("g5715.png").convert_alpha()
        images["bombe"] = pygame.transform.scale(img_bombe, (55, 55))
    except Exception as e:
        print(f"g5715.png non trouvé : {e}")
        surf = pygame.Surface((55, 55))
        surf.fill((30, 30, 30))
        images["bombe"] = surf

    # Bonus immunité : cercle doré généré
    surf_bonus = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf_bonus, (255, 215, 0), (20, 20), 20)
    pygame.draw.circle(surf_bonus, (255, 255, 180), (20, 20), 12)
    images["bonus_immunite"] = surf_bonus

    # Chargement des fonds de chaque niveau
    for num, niveau in NIVEAUX.items():
        try:
            img = pygame.image.load(niveau["fichier"]).convert()
            images[f"fond_{num}"] = pygame.transform.scale(img, (lw, lh))
            print(f"Niveau {num} ({niveau['fichier']}) chargé.")
        except Exception as e:
            print(f"Fond {niveau['fichier']} non trouvé : {e}")
            surf = pygame.Surface((lw, lh))
            surf.fill(niveau["couleur"])
            images[f"fond_{num}"] = surf

    # Bombe
    try:
        img_bombe = pygame.image.load("g5715.png").convert_alpha()
        images["bombe"] = pygame.transform.scale(img_bombe, (50, 60))
    except Exception as e:
        print(f"g5715.png non trouvé : {e}")
        surf = pygame.Surface((50, 60), pygame.SRCALPHA)
        pygame.draw.circle(surf, (40, 40, 40), (25, 40), 22)
        images["bombe"] = surf

    # Bonus immunité : cercle doré
    surf_bonus = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf_bonus, (255, 215, 0), (20, 20), 20)
    pygame.draw.circle(surf_bonus, (255, 255, 180), (20, 20), 12)
    images["bonus_immunite"] = surf_bonus

    images["son_collision"] = None
    images["son_game_over"] = None

    try:
        images["son_game_over"] = pygame.mixer.Sound("game_over.mp3")
        images["son_game_over"].set_volume(0.8)
    except:
        print("game_over.mp3 non trouvé")

    try:
        images["son_collision"] = pygame.mixer.Sound("collision.wav")
        images["son_collision"].set_volume(0.5)
    except:
        print("collision.wav non trouvé (optionnel)")

    try:
        pygame.mixer.music.load("musique_fond.OGG")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        print("musique_fond.OGG non trouvé")

    return images


# ─────────────────────────── Sauvegarde ──────────────────────────────────────

def sauvegarder_partie(perso, balles, game_over):
    donnees = {
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
        print("Partie sauvegardée !")
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
            balle.rect.x     = bd['x']
            balle.rect.y     = bd['y']
            balle.depballe_x = bd['depballe_x']
            balle.depballe_y = bd['depballe_y']
            balles.append(balle)
        game_over = donnees['game_over']
        print("Partie chargée !")
        return balles, game_over
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None, False


# ─────────────────────────── Classes ─────────────────────────────────────────

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
    """Fond parallax avec support multi-niveaux."""
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

    def changer_niveau(self, images, num_niveau):
        """Remplace l'image du fond par celle du niveau donné."""
        self.image = images[f"fond_{num_niveau}"]

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
    DUREE_IMMUNITE = 7 * 30  # 7 secondes à 30 FPS

    def __init__(self, image, fenetre, x=0, y=0):
        super().__init__(image, fenetre, x, y)
        self.vies            = 3
        self.inv             = False
        self.comp_inv        = 0
        self.score           = 0
        self.immunite_active = False
        self.comp_immunite   = 0

    def activer_immunite(self):
        self.immunite_active = True
        self.comp_immunite   = 0
        self.inv             = True
        self.comp_inv        = 0

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
        # Invincibilité courte (après un coup)
        if self.inv and not self.immunite_active:
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = False
        # Immunité bonus (7 secondes)
        if self.immunite_active:
            self.comp_immunite += 1
            if self.comp_immunite >= self.DUREE_IMMUNITE:
                self.immunite_active = False
                self.inv             = False

    def appliquer_degats(self):
        """Perd 1 vie. Retourne True si vraiment touché."""
        if not self.inv:
            self.vies    -= 1
            self.inv      = True
            self.comp_inv = 0
            print(f"aie! vies: {self.vies}")
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



class Bombe(ElementGraphique):
    """Tombe du haut vers le bas, réapparaît en haut quand elle sort."""
    def __init__(self, image, fenetre):
        lw = fenetre.get_width()
        x  = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse = random.uniform(2.5, 5.0)

    def deplacer(self):
        self.rect.y += self.vitesse
        lh = self.fenetre.get_height()
        if self.rect.y > lh:
            lw = self.fenetre.get_width()
            self.rect.x = random.randint(0, lw - self.rect.w)
            self.rect.y = -self.rect.h
            self.vitesse = random.uniform(2.5, 5.0)


class BonusImmunite(ElementGraphique):
    """Cercle doré qui tombe du haut — donne 7 s d'immunité."""
    DUREE_IMMUNITE = 7 * 30  # 7 secondes à 30 FPS

    def __init__(self, image, fenetre):
        lw = fenetre.get_width()
        x  = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse = random.uniform(2.0, 3.5)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()




def afficher_annonce_niveau(fenetre, largeur, hauteur, num_niveau):
    """Affiche brièvement le nom du nouveau niveau."""
    nom = NIVEAUX[num_niveau]["nom"]
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
        fenetre.blit(surf1, surf1.get_rect(center=(largeur // 2, hauteur // 2 - 30)))
        fenetre.blit(surf2, surf2.get_rect(center=(largeur // 2, hauteur // 2 + 50)))
        pygame.display.flip()
        pygame.time.delay(16)


# ─────────────────────────── Initialisation ──────────────────────────────────

pygame.mixer.init()
pygame.init()

largeur = 640
hauteur = 480
fenetre = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Survival Character")

images = lire_images(fenetre)

# Niveau
niveau_actuel         = 1
score_prochain_niveau = SCORE_PAR_NIVEAU

# Timers
td_balle              = pygame.time.get_ticks()
intervalle_balle      = 6000
nbre_max_balle        = 6

td_sauvegarde         = pygame.time.get_ticks()
intervalle_sauvegarde = 5000

td_debut_jeu          = pygame.time.get_ticks()

# Bombes et bonus (actifs à partir du niveau 2)
bombes             = []
bonus_immunite_liste = []
td_bombe           = pygame.time.get_ticks()
intervalle_bombe   = 8000   # toutes les 8 secondes
td_bonus_imm       = pygame.time.get_ticks()
intervalle_bonus_imm = 15000  # toutes les 15 secondes

# Personnage
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

# ─────────────────────────── Boucle principale ───────────────────────────────

while continuer:

    horloge.tick(30)
    touches = pygame.key.get_pressed()

    if touches[pygame.K_ESCAPE]:
        continuer = False

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

        # ── Changement de niveau ─────────────────────────────────────────────
        if perso.score >= score_prochain_niveau and niveau_actuel < len(NIVEAUX):
            niveau_actuel += 1
            score_prochain_niveau += SCORE_PAR_NIVEAU
            fond.changer_niveau(images, niveau_actuel)
            afficher_annonce_niveau(fenetre, largeur, hauteur, niveau_actuel)
            print(f"Passage au niveau {niveau_actuel} !")

        # Sauvegarde auto
        if temps_actuel - td_sauvegarde >= intervalle_sauvegarde:
            sauvegarder_partie(perso, balles, game_over)
            td_sauvegarde = temps_actuel

        # Nouvelle balle
        if temps_actuel - td_balle >= intervalle_balle:
            if len(balles) < nbre_max_balle:
                balles.append(Balle(images["balle"], fenetre))
                td_balle = temps_actuel
                print(f"nouvelle balle! total: {len(balles)}")

        # Déplacement + affichage balles
        for balle in balles:
            balle.deplacer()
            balle.afficher()

        # Collisions balles → -1 vie
        for balle in balles:
            if perso.collide(balle):
                touche = perso.appliquer_degats()
                if touche and images["son_collision"]:
                    images["son_collision"].play()

        # ── Bombes et bonus (niveau 2+) ──────────────────────────────────────
        if niveau_actuel >= 2:

            # Spawn bombe
            if temps_actuel - td_bombe >= intervalle_bombe:
                bombes.append(Bombe(images["bombe"], fenetre))
                td_bombe = temps_actuel

            # Spawn bonus immunité
            if temps_actuel - td_bonus_imm >= intervalle_bonus_imm:
                bonus_immunite_liste.append(BonusImmunite(images["bonus_immunite"], fenetre))
                td_bonus_imm = temps_actuel

            # Déplacement + affichage bombes
            for bombe in bombes:
                bombe.deplacer()
                bombe.afficher()

            # Collisions bombes → -1 vie
            for bombe in bombes:
                if perso.collide(bombe):
                    touche = perso.appliquer_degats()
                    if touche and images["son_collision"]:
                        images["son_collision"].play()

            # Bonus immunité
            bonus_restants = []
            for bonus in bonus_immunite_liste:
                bonus.deplacer()
                if not bonus.hors_ecran():
                    if perso.collide(bonus):
                        perso.activer_immunite()
                        print("Immunité activée ! 7 secondes")
                    else:
                        bonus.afficher()
                        bonus_restants.append(bonus)
            bonus_immunite_liste = bonus_restants

            # Affichage timer immunité dans le HUD
            if perso.immunite_active:
                font_hud2 = pygame.font.Font(None, 36)
                ticks_restants = perso.DUREE_IMMUNITE - perso.comp_immunite
                secondes = ticks_restants // 30 + 1
                surf_imm = font_hud2.render(f"IMMUNITE: {secondes}s", True, (255, 215, 0))
                fenetre.blit(surf_imm, surf_imm.get_rect(center=(largeur // 2, 20)))

        # ── HUD ─────────────────────────────────────────────────────────────
        font_hud = pygame.font.Font(None, 36)
        font_niv = pygame.font.Font(None, 28)

        fenetre.blit(font_hud.render(f"Score: {perso.score}", True, (255, 255, 255)), (10, 10))
        fenetre.blit(font_hud.render(f"Vies: {perso.vies}", True, (255, 255, 255)), (10, 50))

        nom_niveau = NIVEAUX[niveau_actuel]["nom"]
        couleur_niv = NIVEAUX[niveau_actuel]["couleur"]
        fenetre.blit(font_niv.render(f"Niveau {niveau_actuel} - {nom_niveau}", True, couleur_niv), (10, 90))

        # Barre de progression vers le prochain niveau
        if niveau_actuel < len(NIVEAUX):
            score_debut = (niveau_actuel - 1) * SCORE_PAR_NIVEAU
            progression = (perso.score - score_debut) / SCORE_PAR_NIVEAU
            progression = max(0, min(1, progression))
            pygame.draw.rect(fenetre, (80, 80, 80), (10, 120, 150, 10))
            pygame.draw.rect(fenetre, couleur_niv, (10, 120, int(150 * progression), 10))

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
                    bombes               = []
                    bonus_immunite_liste = []
                    son_game_over_joue = False
                    td_balle = td_sauvegarde = td_debut_jeu = pygame.time.get_ticks()
                    td_bombe = td_bonus_imm = pygame.time.get_ticks()
                    if not game_over:
                        try:
                            pygame.mixer.music.load("musique_fond.OGG")
                            pygame.mixer.music.set_volume(0.3)
                            pygame.mixer.music.play(-1)
                        except:
                            print("musique_fond.OGG non trouvé")

            # Recommencer (ESPACE)
            if event.key == pygame.K_SPACE and game_over:
                perso.vies     = 3
                perso.score    = 0
                perso.rect.x   = largeur // 2 - perso.rect.w // 2
                perso.rect.y   = hauteur - perso.rect.h
                perso.inv      = True
                perso.comp_inv = 0
                balles                = [Balle(images["balle"], fenetre)]
                bombes                = []
                bonus_immunite_liste  = []
                game_over             = False
                son_game_over_joue    = False
                niveau_actuel         = 1
                score_prochain_niveau = SCORE_PAR_NIVEAU
                fond.changer_niveau(images, niveau_actuel)
                fond.y1 = 0
                fond.y2 = -hauteur
                td_balle = td_debut_jeu = pygame.time.get_ticks()
                td_bombe = td_bonus_imm = pygame.time.get_ticks()
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
