import pygame
import sys
import math
import random

pygame.init()
LARGEUR, HAUTEUR = 1024, 768
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Accueil - Style RPG Épique")
horloge = pygame.time.Clock()

font_titre  = pygame.font.Font(None, 108)
font_sous   = pygame.font.Font(None, 34)
font_btn    = pygame.font.Font(None, 48)
font_small  = pygame.font.Font(None, 26)

tick = 0

# ── Fond background.png ──
try:
    bg = pygame.image.load("background.png").convert()
    bg = pygame.transform.scale(bg, (LARGEUR, HAUTEUR))
except:
    bg = pygame.Surface((LARGEUR, HAUTEUR))
    for fy in range(HAUTEUR):
        ratio = fy / HAUTEUR
        pygame.draw.line(bg, (int(10+ratio*30), int(10+ratio*20), int(40+ratio*80)),
                         (0, fy), (LARGEUR, fy))

# Overlay dégradé sombre
overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
for fy in range(HAUTEUR):
    ratio = fy / HAUTEUR
    alpha = int(80 + ratio * 120)
    overlay.fill((0, 0, 0, alpha), pygame.Rect(0, fy, LARGEUR, 1))

# ── Brume du sol ──
def dessiner_brume(surf, tick):
    bs = pygame.Surface((LARGEUR, 120), pygame.SRCALPHA)
    for bx in range(0, LARGEUR, 4):
        bh = int(40 + 30 * math.sin(bx * 0.02 + tick * 0.03))
        ba = int(60 + 30 * math.sin(bx * 0.015 + tick * 0.02))
        pygame.draw.line(bs, (180, 200, 255, ba), (bx, 120), (bx, 120 - bh))
    surf.blit(bs, (0, HAUTEUR - 120))

# ── Personnage animé ──
try:
    perso_orig = pygame.image.load("perso.png").convert_alpha()
    perso_img  = pygame.transform.scale(perso_orig, (120, 160))
    use_perso  = True
except:
    use_perso = False

# ── Particules dorées ──
particules = [{
    "x": random.uniform(0, LARGEUR),
    "y": random.uniform(0, HAUTEUR),
    "vy": random.uniform(-0.5, -0.1),
    "r": random.randint(1, 3),
    "alpha": random.randint(60, 180),
    "c": random.choice([(255,215,0),(255,180,50),(255,255,200),(200,160,255)])
} for _ in range(70)]

# ── Boutons ──
btns = [
    {"label": "⚔  JOUER",    "action": "jouer",   "y": HAUTEUR - 260},
    {"label": "⚙  OPTIONS",  "action": "options",  "y": HAUTEUR - 190},
    {"label": "✖  QUITTER",  "action": "quitter",  "y": HAUTEUR - 120},
]
btn_w, btn_h = 280, 55
for b in btns:
    b["rect"] = pygame.Rect(LARGEUR//2 - btn_w//2, b["y"], btn_w, btn_h)

while True:
    horloge.tick(60)
    tick += 1

    # ── Fond + overlay ──
    fenetre.blit(bg, (0, 0))
    fenetre.blit(overlay, (0, 0))

    # ── Brume ──
    dessiner_brume(fenetre, tick)

    # ── Particules dorées ──
    psurf = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    for p in particules:
        p["y"] += p["vy"]
        if p["y"] < -5:
            p["y"] = HAUTEUR + 5
            p["x"] = random.uniform(0, LARGEUR)
        pygame.draw.circle(psurf, (*p["c"], p["alpha"]),
                           (int(p["x"]), int(p["y"])), p["r"])
    fenetre.blit(psurf, (0, 0))

    # ── Personnage animé (bob) ──
    if use_perso:
        bob    = int(6 * math.sin(tick * 0.07))
        halo_r = int(85 + 12 * math.sin(tick * 0.05))
        hsurf  = pygame.Surface((halo_r*2, halo_r*2), pygame.SRCALPHA)
        pygame.draw.circle(hsurf, (255, 215, 0, 55), (halo_r, halo_r), halo_r)
        cx, cy = LARGEUR//2, HAUTEUR - 310
        fenetre.blit(hsurf, (cx - halo_r, cy - halo_r + bob))
        fenetre.blit(perso_img, perso_img.get_rect(center=(cx, cy + bob)))

    # ── Titre doré avec reflet ──
    lueur = int(200 + 55 * math.sin(tick * 0.04))
    # Ombre
    for dx, dy in [(3,3),(-3,3)]:
        sh = font_titre.render("SURVIVAL",  True, (60, 40, 0))
        sc = font_titre.render("CHARACTER", True, (60, 40, 0))
        fenetre.blit(sh, sh.get_rect(center=(LARGEUR//2+dx, 118+dy)))
        fenetre.blit(sc, sc.get_rect(center=(LARGEUR//2+dx, 208+dy)))
    # Lueur dorée
    lg = font_titre.render("SURVIVAL", True, (255, lueur, 0))
    lg.set_alpha(70)
    fenetre.blit(lg, lg.get_rect(center=(LARGEUR//2, 115)))
    # Texte principal
    s1 = font_titre.render("SURVIVAL",  True, (255, lueur, 50))
    s2 = font_titre.render("CHARACTER", True, (255, 245, 200))
    fenetre.blit(s1, s1.get_rect(center=(LARGEUR//2, 115)))
    fenetre.blit(s2, s2.get_rect(center=(LARGEUR//2, 205)))

    # Reflet (texte retourné, semi-transparent)
    ref1 = pygame.transform.flip(s1, False, True)
    ref1.set_alpha(30)
    ref2 = pygame.transform.flip(s2, False, True)
    ref2.set_alpha(30)
    fenetre.blit(ref1, ref1.get_rect(center=(LARGEUR//2, 165)))
    fenetre.blit(ref2, ref2.get_rect(center=(LARGEUR//2, 255)))

    # Ligne déco dorée
    pygame.draw.line(fenetre, (255, lueur, 0), (80, 250), (LARGEUR-80, 250), 2)

    # Accroche
    acc = font_sous.render("Le monde bascule.  Survivez.", True, (200, 180, 255))
    fenetre.blit(acc, acc.get_rect(center=(LARGEUR//2, 278)))

    # ── 3 Boutons ──
    mx, my = pygame.mouse.get_pos()
    for b in btns:
        survol = b["rect"].collidepoint(mx, my)
        coul   = (80, 60, 20, 220)  if survol else (30, 20, 5, 180)
        bord   = (255, lueur, 0)    if survol else (140, 100, 20)
        bsurf  = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
        pygame.draw.rect(bsurf, coul, bsurf.get_rect(), border_radius=10)
        pygame.draw.rect(bsurf, (*bord, 255), bsurf.get_rect(), width=2, border_radius=10)
        fenetre.blit(bsurf, b["rect"].topleft)
        coul_txt = (255, lueur, 50) if survol else (220, 200, 140)
        txt = font_btn.render(b["label"], True, coul_txt)
        fenetre.blit(txt, txt.get_rect(center=b["rect"].center))

    hint = font_small.render("ESPACE = Jouer  |  ECHAP = Quitter", True, (100, 100, 100))
    fenetre.blit(hint, hint.get_rect(center=(LARGEUR//2, HAUTEUR - 25)))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                print("JOUER"); pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in btns:
                if b["rect"].collidepoint(event.pos):
                    if b["action"] == "quitter":
                        pygame.quit(); sys.exit()
                    else:
                        print(b["action"]); pygame.quit(); sys.exit()
