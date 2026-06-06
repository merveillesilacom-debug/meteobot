import pygame
import random

LARGEUR = 1024
HAUTEUR = 768
FPS = 30


class ElementGraphique:
    def __init__(self, image, fenetre, x=0, y=0):
        self.image = image
        self.fenetre = fenetre
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

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
        self.y1 = 0
        self.y2 = -lh
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
        self.vies = 3
        self.inv = False
        self.comp_inv = 0
        self.score = 0
        self.immunite_active = False
        self.comp_immunite = 0
        self.duree_immunite = 300
        self.ralenti_actif = False
        self.comp_ralenti = 0
        self.duree_ralenti = 180

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
        self.rect.x = max(0, min(self.rect.x, LARGEUR - self.rect.w))
        self.rect.y = max(0, min(self.rect.y, HAUTEUR - self.rect.h))

        if self.inv:
            self.comp_inv += 1
            if self.comp_inv > 30:
                self.inv = False

        if self.immunite_active:
            self.comp_immunite += 1
            if self.comp_immunite >= self.duree_immunite:
                self.immunite_active = False
                self.comp_immunite = 0

        if self.ralenti_actif:
            self.comp_ralenti += 1
            if self.comp_ralenti >= self.duree_ralenti:
                self.ralenti_actif = False
                self.comp_ralenti = 0

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
        self.comp_immunite = 0

    def activer_ralentissement(self):
        self.ralenti_actif = True
        self.comp_ralenti = 0

    def appliquer_degats(self):
        if self.immunite_active:
            return False
        if not self.inv:
            self.vies -= 1
            self.inv = True
            self.comp_inv = 0
            return True
        return False

    def appliquer_demi_degats(self):
        if self.immunite_active:
            return False
        if not self.inv:
            self.vies -= 0.5
            self.inv = True
            self.comp_inv = 0
            return True
        return False


class Balle(ElementGraphique):
    def __init__(self, image, fenetre, depballe_x=3.3, depballe_y=3.3):
        lw = fenetre.get_width()
        lh = fenetre.get_height()
        x = random.randint(0, lw - image.get_width())
        y = random.randint(0, lh - image.get_height())
        super().__init__(image, fenetre, x, y)
        self.depballe_x = depballe_x
        self.depballe_y = depballe_y

    def deplacer(self, facteur_vitesse=1.0, ralenti=False):
        lw, lh = self.fenetre.get_size()
        mult = 0.4 if ralenti else facteur_vitesse
        self.rect.x += self.depballe_x * mult
        self.rect.y += self.depballe_y * mult
        if self.rect.x < 0:
            self.rect.x = 0
            self.depballe_x = abs(self.depballe_x) + random.uniform(-0.3, 0.3)
        if self.rect.x + self.rect.w > lw:
            self.rect.x = lw - self.rect.w
            self.depballe_x = -(abs(self.depballe_x) + random.uniform(-0.3, 0.3))
        if self.rect.y < 0:
            self.rect.y = 0
            self.depballe_y = abs(self.depballe_y) + random.uniform(-0.3, 0.3)
        if self.rect.y + self.rect.h > lh:
            self.rect.y = lh - self.rect.h
            self.depballe_y = -(abs(self.depballe_y) + random.uniform(-0.3, 0.3))


class Fruit(ElementGraphique):
    def __init__(self, image, fenetre):
        lw = fenetre.get_width()
        image = pygame.transform.scale(image, (50, 50))
        x = random.randint(0, lw - 50)
        y = -50
        super().__init__(image, fenetre, x, y)
        self.vitesse = random.uniform(2.0, 4.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class BonusImmunite(ElementGraphique):
    def __init__(self, fenetre):
        lw = fenetre.get_width()
        taille = 48
        surf = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 215, 0), (taille // 2, taille // 2), taille // 2)
        pygame.draw.circle(surf, (200, 160, 0), (taille // 2, taille // 2), taille // 2, 3)
        font = pygame.font.Font(None, 32)
        txt = font.render("+1", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille // 2, taille // 2)))
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
        lw = fenetre.get_width()
        taille = 48
        surf = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (50, 150, 255), (taille // 2, taille // 2), taille // 2)
        pygame.draw.circle(surf, (30, 100, 200), (taille // 2, taille // 2), taille // 2, 3)
        font = pygame.font.Font(None, 26)
        txt = font.render("SLOW", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille // 2, taille // 2)))
        x = random.randint(0, lw - taille)
        y = -taille
        super().__init__(surf, fenetre, x, y)
        self.vitesse = random.uniform(1.5, 3.0)

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class BonusCoeur(ElementGraphique):
    def __init__(self, fenetre):
        lw = fenetre.get_width()
        taille = 48
        surf = pygame.Surface((taille, taille), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 80, 130), (taille // 2, taille // 2), taille // 2)
        pygame.draw.circle(surf, (200, 40, 90), (taille // 2, taille // 2), taille // 2, 3)
        font = pygame.font.Font(None, 34)
        txt = font.render("+V", True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=(taille // 2, taille // 2)))
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
        lw = fenetre.get_width()
        x = random.randint(0, lw - image.get_width())
        super().__init__(image, fenetre, x, -image.get_height())
        self.vitesse = vitesse

    def deplacer(self):
        self.rect.y += self.vitesse

    def hors_ecran(self):
        return self.rect.y > self.fenetre.get_height()


class FlashEcran:
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
    images["perso"] = pygame.image.load("perso.png").convert_alpha()
    images["fond"] = pygame.image.load("background.jpg").convert()
    images["balle"] = pygame.image.load("balle.png").convert_alpha()

    if pygame.image.get_extended():
        import os
        for nom in ["fraise", "pasteque"]:
            if os.path.exists(nom + ".png"):
                images[nom] = pygame.image.load(nom + ".png").convert_alpha()
            else:
                print("fichier " + nom + ".png non trouvé")
                images[nom] = None
    else:
        images["fraise"] = None
        images["pasteque"] = None

    
    import os
    for cle, fichier, volume in [
        ("son_collision", "collision.wav", 0.5),
        ("son_bonus", "bonus.wav", 0.6),
        ("son_game_over", "gameover.wav", 0.8),
    ]:
        if os.path.exists(fichier):
            images[cle] = pygame.mixer.Sound(fichier)
            images[cle].set_volume(volume)
        else:
            print(fichier + " non trouvé")
            images[cle] = None

    if os.path.exists("musique_fond.ogg"):
        pygame.mixer.music.load("musique_fond.ogg")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    else:
        print("musique_fond.ogg non trouvé")

    for cle_fond, fichier_fond in [("fond_v2", "landscape.png"), ("fond_v3", "Background3.jpg")]:
        if os.path.exists(fichier_fond):
            images[cle_fond] = pygame.image.load(fichier_fond).convert()
        else:
            images[cle_fond] = images["fond"]

    import os
    if os.path.exists("g5715.png"):
        images["bombe"] = pygame.transform.scale(
            pygame.image.load("g5715.png").convert_alpha(), (60, 80)
        )
    else:
        images["bombe"] = None

    return images


def jouer_son(images, cle):
    if images.get(cle):
        images[cle].stop()
        images[cle].play(maxtime=400)

def lancer_musique():
    import os
    if os.path.exists("musique_fond.ogg"):
        pygame.mixer.music.load("musique_fond.ogg")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)


def afficher_texte_centre(fenetre, texte, taille, couleur, cy):
    font = pygame.font.Font(None, taille)
    surf = font.render(texte, True, couleur)
    fenetre.blit(surf, surf.get_rect(center=(LARGEUR // 2, cy)))


def afficher_annonce_vague(fenetre, numero_vague):
    afficher_texte_centre(fenetre, "VAGUE  " + str(numero_vague), 80, (255, 220, 50), HAUTEUR // 2)
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
    ent = int(vies)
    demi = ".5" if (vies - ent) >= 0.5 else ""
    fenetre.blit(font.render("Vies: " + str(ent) + demi + " / " + str(int(max_vies)), True, (255, 255, 255)), (x + 5, y + 3))


def gerer_objets(liste, perso, flash, images, on_collision):
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
    fond_accueil = pygame.transform.scale(images["fond"], (LARGEUR, HAUTEUR))
    font_titre = pygame.font.Font(None, 108)
    font_bouton = pygame.font.Font(None, 48)
    font_info = pygame.font.Font(None, 30)

    continuer = True
    while continuer:
        horloge.tick(60)
        fenetre.blit(fond_accueil, (0, 0))

        
        s1 = font_titre.render("SURVIVAL", True, (255, 200, 50))
        s2 = font_titre.render("CHARACTER", True, (255, 245, 200))
        fenetre.blit(s1, s1.get_rect(center=(LARGEUR // 2, 150)))
        fenetre.blit(s2, s2.get_rect(center=(LARGEUR // 2, 260)))

        
        txt = font_bouton.render("APPUYEZ SUR ESPACE POUR JOUER", True, (255, 255, 255))
        fenetre.blit(txt, txt.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 80)))

        
        hint = font_info.render("ECHAP = Quitter", True, (180, 180, 180))
        fenetre.blit(hint, hint.get_rect(center=(LARGEUR // 2, HAUTEUR - 30)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_SPACE:
                    continuer = False


def reinitialiser_jeu(perso, images, fenetre):
    perso.vies = 3
    perso.score = 0
    perso.immunite_active = False
    perso.ralenti_actif = False
    perso.comp_immunite = 0
    perso.comp_ralenti = 0
    perso.rect.x = LARGEUR // 2 - perso.rect.w // 2
    perso.rect.y = HAUTEUR - perso.rect.h
    perso.inv = True
    perso.comp_inv = 0
    balles = [Balle(images["balle"], fenetre)]
    now = pygame.time.get_ticks()
    timers = {k: now for k in ("balle", "debut", "fruit", "bonus", "ralenti", "coeur")}
    return balles, timers



pygame.mixer.init()
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("SURVIVAL CHARACTER")

images = lire_images()

perso = Perso(
    images["perso"], fenetre,
    x=LARGEUR // 2 - images["perso"].get_width() // 2,
    y=HAUTEUR - images["perso"].get_height()
)
perso.inv = True
perso.comp_inv = 0

fond = Fond(images["fond"], fenetre, vitesse=2)
flash = FlashEcran(LARGEUR, HAUTEUR)
horloge = pygame.time.Clock()

ecran_accueil(fenetre, images)

balles, timers = reinitialiser_jeu(perso, images, fenetre)
fruits = []
bonus_immunite_liste = []
bonus_ralenti_liste = []
bonus_coeur_liste = []
bombes = []
td_bombe = 0

vague_actuelle = 1
score_prochaine_vague = 1000
game_over = False
son_game_over_joue = False
en_pause = False
nouveau_fond_img = None
nouveau_fond_y = -HAUTEUR
nbre_max_balle = 5

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

            if game_over and event.key == pygame.K_SPACE:
                balles, timers = reinitialiser_jeu(perso, images, fenetre)
                fruits = []
                bonus_immunite_liste = []
                bonus_ralenti_liste = []
                bonus_coeur_liste = []
                bombes = []
                td_bombe = 0
                game_over = False
                son_game_over_joue = False
                en_pause = False
                fond.y1 = 0
                fond.y2 = -HAUTEUR
                fond.image = pygame.transform.scale(images["fond"], (LARGEUR, HAUTEUR))
                vague_actuelle = 1
                score_prochaine_vague = 1000
                nouveau_fond_img = None
                nouveau_fond_y = -HAUTEUR
                afficher_annonce_vague(fenetre, vague_actuelle)
                lancer_musique()

            if en_pause and event.key == pygame.K_u:
                en_pause = False
                pygame.mixer.music.unpause()

    fond.actif = not game_over
    fond.deplacer()
    fond.afficher()

    if en_pause and not game_over:
        afficher_texte_centre(fenetre, "PAUSE", 100, (255, 255, 255), HAUTEUR // 2 - 40)
        afficher_texte_centre(fenetre, "Appuyez sur U pour reprendre", 36, (200, 200, 200), HAUTEUR // 2 + 40)
        pygame.display.flip()
        horloge.tick(FPS)
        continue

    if perso.vies <= 0 and not game_over:
        game_over = True
        if not son_game_over_joue:
            pygame.mixer.music.stop()
            jouer_son(images, "son_game_over")
            son_game_over_joue = True

    if game_over:
        perso.afficher()
        afficher_texte_centre(fenetre, "GAME OVER", 100, (255, 0, 0), HAUTEUR // 2 - 60)
        afficher_texte_centre(fenetre, "Score: " + str(perso.score), 60, (255, 255, 255), HAUTEUR // 2 + 20)
        afficher_texte_centre(fenetre, "ESPACE = rejouer  |  ECHAP = quitter", 30, (255, 255, 255), HAUTEUR - 40)

    else:
        perso.deplacer()
        perso.score += 1

        temps_ecoule = (now - timers["debut"]) / 1000.0
        facteur_vitesse = min(1.0 + (temps_ecoule / 30.0) * 0.5, 3.0)

      
        if perso.score >= score_prochaine_vague:
            vague_actuelle += 1
            score_prochaine_vague += 1000
            if vague_actuelle == 2 and images.get("fond_v2"):
                nouveau_fond_img = pygame.transform.scale(images["fond_v2"], (LARGEUR, HAUTEUR))
                nouveau_fond_y = -HAUTEUR
                td_bombe = now + 5000
            elif vague_actuelle == 3 and images.get("fond_v3"):
                nouveau_fond_img = pygame.transform.scale(images["fond_v3"], (LARGEUR, HAUTEUR))
                nouveau_fond_y = -HAUTEUR
            afficher_annonce_vague(fenetre, vague_actuelle)
            timers["balle"] = pygame.time.get_ticks()

      
        if nouveau_fond_img is not None:
            nouveau_fond_y += fond.vitesse
            fenetre.blit(nouveau_fond_img, (0, nouveau_fond_y))
            if nouveau_fond_y >= 0:
                fond.image = nouveau_fond_img
                fond.y1 = 0
                fond.y2 = -HAUTEUR
                nouveau_fond_img = None

        perso.afficher()

        
        if vague_actuelle >= 2 and images.get("bombe") and td_bombe > 0 and now >= td_bombe:
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
            else:
                bombe.afficher()
                bombes_restantes.append(bombe)
        bombes = bombes_restantes

        
        if now - timers["balle"] >= 6000:
            max_balles = min(3 + vague_actuelle, nbre_max_balle)
            if len(balles) < max_balles:
                v = 3.3 * facteur_vitesse
                balles.append(Balle(
                    images["balle"], fenetre,
                    depballe_x=random.choice([-1, 1]) * v,
                    depballe_y=random.choice([-1, 1]) * v
                ))
            timers["balle"] = now

        
        if now - timers["fruit"] >= 10000:
            type_fruit = random.choice(["fraise", "pasteque"])
            if images.get(type_fruit):
                fruits.append(Fruit(images[type_fruit], fenetre))
            timers["fruit"] = now

       
        if now - timers["bonus"] >= 15000:
            bonus_immunite_liste.append(BonusImmunite(fenetre))
            timers["bonus"] = now

        
        if now - timers["ralenti"] >= 20000:
            bonus_ralenti_liste.append(BonusRalenti(fenetre))
            timers["ralenti"] = now

       
        if now - timers["coeur"] >= 25000:
            bonus_coeur_liste.append(BonusCoeur(fenetre))
            timers["coeur"] = now

        
        for balle in balles:
            balle.deplacer(facteur_vitesse, perso.ralenti_actif)
            balle.afficher()

        
        for balle in balles:
            if perso.collide(balle):
                if perso.appliquer_degats():
                    flash.declencher((255, 0, 0))
                    jouer_son(images, "son_collision")

        
        def on_fruit(obj):
            if perso.appliquer_demi_degats():
                flash.declencher((255, 100, 0))
                jouer_son(images, "son_collision")

        def on_immunite(obj):
            perso.activer_immunite()
            flash.declencher((255, 215, 0))
            jouer_son(images, "son_bonus")

        def on_ralenti(obj):
            perso.activer_ralentissement()
            flash.declencher((50, 150, 255))
            jouer_son(images, "son_bonus")

        def on_coeur(obj):
            perso.vies = min(perso.vies + 0.5, 3)
            flash.declencher((255, 80, 130))
            jouer_son(images, "son_bonus")

        fruits = gerer_objets(fruits, perso, flash, images, on_fruit)
        bonus_immunite_liste = gerer_objets(bonus_immunite_liste, perso, flash, images, on_immunite)
        bonus_ralenti_liste = gerer_objets(bonus_ralenti_liste, perso, flash, images, on_ralenti)
        bonus_coeur_liste = gerer_objets(bonus_coeur_liste, perso, flash, images, on_coeur)

        flash.update()
        flash.afficher(fenetre)

        # Affichage HUD
        font_hud = pygame.font.Font(None, 36)
        font_leg = pygame.font.Font(None, 24)
        fenetre.blit(font_hud.render("Score: " + str(perso.score), True, (255, 255, 255)), (10, 10))
        fenetre.blit(font_hud.render("Vague: " + str(vague_actuelle), True, (255, 220, 50)), (10, 45))
        pct_diff = int((facteur_vitesse - 1.0) / 2.0 * 100)
        fenetre.blit(font_leg.render("Difficulte: " + str(pct_diff) + "%", True, (200, 200, 255)), (10, 80))
        dessiner_barre_vie(fenetre, perso.vies, 3)

        if perso.immunite_active:
            s = font_hud.render("IMMUNITE: " + str((perso.duree_immunite - perso.comp_immunite) // 30) + "s", True, (255, 215, 0))
            fenetre.blit(s, s.get_rect(center=(LARGEUR // 2, 20)))

        if perso.ralenti_actif:
            s = font_hud.render("SLOW: " + str((perso.duree_ralenti - perso.comp_ralenti) // 30) + "s", True, (50, 200, 255))
            fenetre.blit(s, s.get_rect(center=(LARGEUR // 2, 55)))

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()