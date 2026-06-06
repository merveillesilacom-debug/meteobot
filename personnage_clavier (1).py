import pygame
import sys
import math

# ─────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────
LARGEUR      = 800
HAUTEUR      = 600
FPS          = 60
VITESSE_WALK = 4
VITESSE_RUN  = 9   # si on maintient SHIFT

# ─────────────────────────────────────────
#  INITIALISATION
# ─────────────────────────────────────────
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Personnage animé")
horloge = pygame.time.Clock()

# ─────────────────────────────────────────
#  CHARGEMENT DU PERSONNAGE
# ─────────────────────────────────────────
try:
    perso_img_orig = pygame.image.load("woman_h1.png").convert_alpha()
    perso_img_orig = pygame.transform.scale(perso_img_orig, (80, 140))
    print("Personnage chargé !")
except Exception as e:
    print(f"woman_h1.png non trouvé — personnage de remplacement.")
    perso_img_orig = pygame.Surface((80, 140), pygame.SRCALPHA)
    pygame.draw.rect(perso_img_orig, (70, 100, 200), pygame.Rect(20, 40, 40, 60))
    pygame.draw.ellipse(perso_img_orig, (255, 210, 170), pygame.Rect(22, 10, 36, 36))
    pygame.draw.rect(perso_img_orig, (50, 50, 80), pygame.Rect(20, 100, 16, 35))
    pygame.draw.rect(perso_img_orig, (50, 50, 80), pygame.Rect(44, 100, 16, 35))

IMG_W = perso_img_orig.get_width()
IMG_H = perso_img_orig.get_height()

# ── Découpe haut / bas du corps ──────────
SPLIT        = int(IMG_H * 0.62)
haut_rect    = pygame.Rect(0, 0,     IMG_W, SPLIT)
bas_rect     = pygame.Rect(0, SPLIT, IMG_W, IMG_H - SPLIT)

haut_img     = perso_img_orig.subsurface(haut_rect).copy()
bas_img_orig = perso_img_orig.subsurface(bas_rect).copy()

BAS_H = bas_img_orig.get_height()
BAS_W = bas_img_orig.get_width()

# ── Position de départ ──
x = float(LARGEUR  // 2 - IMG_W // 2)
y = float(HAUTEUR - IMG_H - 20)

# ─────────────────────────────────────────
#  ÉTAT ANIMATION
# ─────────────────────────────────────────
angle_anim   = 0.0
direction    = 1
en_mouvement = False
en_course    = False

# ─────────────────────────────────────────
#  FOND DÉGRADÉ
# ─────────────────────────────────────────
fond = pygame.Surface((LARGEUR, HAUTEUR))
for fy in range(HAUTEUR):
    ratio = fy / HAUTEUR
    r = int(10 + ratio * 20)
    g = int(10 + ratio * 15)
    b = int(50 + ratio * 60)
    pygame.draw.line(fond, (r, g, b), (0, fy), (LARGEUR, fy))
pygame.draw.rect(fond, (30, 30, 30), pygame.Rect(0, HAUTEUR - 20, LARGEUR, 20))
pygame.draw.line(fond, (80, 80, 80), (0, HAUTEUR - 20), (LARGEUR, HAUTEUR - 20), 2)

# ─────────────────────────────────────────
#  FONT
# ─────────────────────────────────────────
font     = pygame.font.SysFont("consolas", 18)
font_big = pygame.font.SysFont("consolas", 22, bold=True)

# ─────────────────────────────────────────
#  FONCTION ANIMATION
# ─────────────────────────────────────────
def construire_frame(angle, rapide, dir):
    amplitude_bob  = 5.0 if rapide else 2.5
    amplitude_jamb = 14.0 if rapide else 8.0

    surf = pygame.Surface((IMG_W, IMG_H + 10), pygame.SRCALPHA)

    # Haut du corps : bobbing vertical
    bob = math.sin(angle) * amplitude_bob
    surf.blit(haut_img, (0, int(bob)))

    # Jambe gauche
    jambe_g     = bas_img_orig.subsurface(pygame.Rect(0, 0, BAS_W // 2, BAS_H)).copy()
    angle_g     = math.sin(angle) * amplitude_jamb
    jambe_g_rot = pygame.transform.rotate(jambe_g, angle_g)
    surf.blit(jambe_g_rot, (0, SPLIT + int(bob * 0.3)))

    # Jambe droite (déphasée de π)
    jambe_d     = bas_img_orig.subsurface(pygame.Rect(BAS_W // 2, 0, BAS_W - BAS_W // 2, BAS_H)).copy()
    angle_d     = math.sin(angle + math.pi) * amplitude_jamb
    jambe_d_rot = pygame.transform.rotate(jambe_d, angle_d)
    surf.blit(jambe_d_rot, (BAS_W // 2, SPLIT + int(bob * 0.3)))

    # Retourner si gauche
    if dir == -1:
        surf = pygame.transform.flip(surf, True, False)

    return surf

# ─────────────────────────────────────────
#  BOUCLE PRINCIPALE
# ─────────────────────────────────────────
while True:
    horloge.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

    touches    = pygame.key.get_pressed()
    en_course  = touches[pygame.K_LSHIFT] or touches[pygame.K_RSHIFT]
    vitesse    = VITESSE_RUN if en_course else VITESSE_WALK

    dx, dy       = 0, 0
    en_mouvement = False

    if touches[pygame.K_LEFT]  or touches[pygame.K_q]:
        dx -= vitesse; direction = -1; en_mouvement = True
    if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
        dx += vitesse; direction =  1; en_mouvement = True
    if touches[pygame.K_UP]    or touches[pygame.K_z]:
        dy -= vitesse; en_mouvement = True
    if touches[pygame.K_DOWN]  or touches[pygame.K_s]:
        dy += vitesse; en_mouvement = True

    x += dx
    y += dy
    x = max(0, min(x, LARGEUR - IMG_W))
    y = max(0, min(y, HAUTEUR - IMG_H - 20))

    # Avancement cycle animation
    if en_mouvement:
        angle_anim += 0.20 if en_course else 0.12
    else:
        angle_anim *= 0.75   # retour doux à position neutre

    # Frame animée
    frame = construire_frame(angle_anim, en_course, direction)

    # Dessin
    fenetre.blit(fond, (0, 0))
    fenetre.blit(frame, (int(x), int(y)))

    # HUD
    etat    = "COURSE" if en_course else ("MARCHE" if en_mouvement else "ARRET")
    couleur = (255, 180, 50) if en_course else (150, 220, 150) if en_mouvement else (160, 160, 160)
    fenetre.blit(font_big.render(etat, True, couleur), (10, 10))
    fenetre.blit(font.render("fleches / ZQSD  |  SHIFT = courir  |  ECHAP = quitter",
                             True, (160, 160, 160)), (180, 14))

    pygame.display.flip()
