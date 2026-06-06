import pygame
import sys
import math
import random

pygame.init()
LARGEUR, HAUTEUR = 1024, 768
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Accueil - Style Cinématique")
horloge = pygame.time.Clock()

font_titre  = pygame.font.Font(None, 110)
font_sous   = pygame.font.Font(None, 36)
font_btn    = pygame.font.Font(None, 52)

# ── Particules de feu en bas ──
feu = [{"x": random.uniform(0, LARGEUR), "y": random.uniform(HAUTEUR-120, HAUTEUR),
        "vy": random.uniform(-1.5, -0.5), "r": random.randint(2, 6),
        "alpha": random.randint(100, 220),
        "c": random.choice([(255,80,0),(255,140,0),(255,200,50),(200,30,0)])}
       for _ in range(120)]

# ── Texte lettre par lettre ──
TITRE1  = "SURVIVAL"
TITRE2  = "CHARACTER"
lettres_affichees = 0
tick = 0

# Silhouette personnage
try:
    perso_orig = pygame.image.load("perso.png").convert_alpha()
    perso_img  = pygame.transform.scale(perso_orig, (110, 160))
    # Convertir en silhouette noire
    silhouette = perso_img.copy()
    for x in range(silhouette.get_width()):
        for y in range(silhouette.get_height()):
            r,g,b,a = silhouette.get_at((x,y))
            if a > 10:
                silhouette.set_at((x,y),(0,0,0,a))
    use_sil = True
except:
    use_sil = False

btn_rect = pygame.Rect(LARGEUR//2 - 120, HAUTEUR - 140, 240, 55)

while True:
    horloge.tick(60)
    tick += 1

    # Avancement texte machine à écrire
    if tick % 4 == 0:
        lettres_affichees = min(lettres_affichees + 1, len(TITRE1) + len(TITRE2))

    # ── Fond noir ──
    fenetre.fill((0, 0, 0))

    # ── Lueur rouge/orange en bas ──
    for iy in range(200):
        ratio = iy / 200
        alpha = int(180 * (1 - ratio))
        r = int(180 * (1 - ratio * 0.5))
        g = int(60  * (1 - ratio))
        surf_line = pygame.Surface((LARGEUR, 1), pygame.SRCALPHA)
        surf_line.fill((r, g, 0, alpha))
        fenetre.blit(surf_line, (0, HAUTEUR - 200 + iy))

    # ── Particules feu ──
    psurf = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    for p in feu:
        p["y"] += p["vy"]
        p["alpha"] -= 1
        if p["y"] < HAUTEUR - 200 or p["alpha"] <= 0:
            p["y"]    = random.uniform(HAUTEUR-80, HAUTEUR)
            p["x"]    = random.uniform(0, LARGEUR)
            p["alpha"]= random.randint(150, 220)
            p["vy"]   = random.uniform(-1.5, -0.4)
        pygame.draw.circle(psurf, (*p["c"], p["alpha"]),
                           (int(p["x"]), int(p["y"])), p["r"])
    fenetre.blit(psurf, (0,0))

    # ── Silhouette personnage ──
    if use_sil:
        halo_r = int(90 + 15 * math.sin(tick * 0.05))
        halo_s = pygame.Surface((halo_r*2, halo_r*2), pygame.SRCALPHA)
        pygame.draw.circle(halo_s, (255, 80, 0, 60), (halo_r, halo_r), halo_r)
        cx = LARGEUR//2
        cy = HAUTEUR - 220
        fenetre.blit(halo_s, (cx - halo_r, cy - halo_r))
        fenetre.blit(silhouette, silhouette.get_rect(center=(cx, cy)))

    # ── Titre machine à écrire ──
    t1 = TITRE1[:min(lettres_affichees, len(TITRE1))]
    t2 = TITRE2[:max(0, lettres_affichees - len(TITRE1))]
    lueur = int(180 + 75 * math.sin(tick * 0.04))
    if t1:
        s1 = font_titre.render(t1, True, (255, lueur, 50))
        fenetre.blit(s1, s1.get_rect(center=(LARGEUR//2, 160)))
    if t2:
        s2 = font_titre.render(t2, True, (255, 255, 255))
        fenetre.blit(s2, s2.get_rect(center=(LARGEUR//2, 260)))

    # Curseur clignotant
    total = len(TITRE1) + len(TITRE2)
    if lettres_affichees < total and tick % 20 < 10:
        pygame.draw.rect(fenetre, (255,200,50), pygame.Rect(LARGEUR//2 + 20, 130, 8, 70))

    # Ligne séparatrice
    pygame.draw.line(fenetre, (200, 50, 0), (100, 300), (LARGEUR-100, 300), 2)

    # Accroche
    acc = font_sous.render("Un seul survivra.", True, (180, 100, 80))
    fenetre.blit(acc, acc.get_rect(center=(LARGEUR//2, 330)))

    # ── Bouton JOUER clignotant ──
    if tick % 60 < 45:
        txt_btn = font_btn.render("[ APPUYEZ POUR JOUER ]", True, (255,255,255))
        fenetre.blit(txt_btn, txt_btn.get_rect(center=btn_rect.center))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                print("JOUER"); pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_rect.collidepoint(event.pos):
                print("JOUER"); pygame.quit(); sys.exit()
