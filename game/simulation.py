# game/simulation.py
import pygame
import math
import sys
from agent.snitch import Snitch
from agent.states import StanjeSnitcha, BOJE_STANJA

# ─────────────────────────────────────────
# Konstante
# ─────────────────────────────────────────
SIRINA         = 1100
VISINA         = 700
FPS            = 60
BOJA_POZADINE  = (15, 15, 25)
BOJA_IGRACA    = (30, 144, 255)

UGAO_KONUSA    = 90
DUZINA_KONUSA  = 200

# Trajanja u frameovima
TRAJANJE_POTVRDJENO = 60 * FPS   # 60 sekundi
TRAJANJE_WARNING    = 30 * FPS   # 30 sekundi

RUTA_PATROLE = [
    (200, 200),
    (700, 200),
    (700, 500),
    (200, 500),
]

ZBUNJEVI = [
    (350, 300, 35),
    (550, 200, 30),
    (250, 450, 40),
    (650, 380, 35),
    (450, 150, 25),
    (150, 350, 30),
    (750, 300, 38),
    (500, 480, 32),
]

# Zvuk koraka igrača
ZVUK_KORAKA_BASE = 0.35   # zvuk kad hoda
ZVUK_PUCNJA      = 0.95   # Q taster


class Igrica:
    def __init__(self):
        pygame.init()
        self.ekran  = pygame.display.set_mode((SIRINA, VISINA))
        pygame.display.set_caption("FuzzySnitch — Nadzorni Agent")
        self.sat    = pygame.time.Clock()
        self.font_m = pygame.font.SysFont("consolas", 16)
        self.font_v = pygame.font.SysFont("consolas", 22, bold=True)

        # Agent
        self.snitch          = Snitch(ime="Snitch-01")
        self.snitch_pos      = list(RUTA_PATROLE[0])
        self.snitch_ugao     = 0.0
        self.snitch_brzina   = 2.0
        self.cilj_patrole    = 1
        self.stanje          = StanjeSnitcha.MIRNO

        # Tajmeri stanja
        self.potvrdjeno_tajmer = 0
        self.warning_tajmer    = 0
        self.warning_centar    = None

        # Igrač
        self.igrac_pos    = [500, 350]
        self.igrac_brzina = 3.0
        self.igrac_krece  = False

        # Zvuk
        self.zvuk_val = 0.0

    # ─────────────────────────────────────────
    # Geometrija
    # ─────────────────────────────────────────
    def distanca(self, a, b) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def ugao_do(self, od, do) -> float:
        return math.degrees(math.atan2(do[1] - od[1], do[0] - od[0]))

    def u_konusu(self) -> bool:
        dist = self.distanca(self.snitch_pos, self.igrac_pos)
        if dist > DUZINA_KONUSA:
            return False
        ugao_do_igraca = self.ugao_do(self.snitch_pos, self.igrac_pos)
        razlika = abs((ugao_do_igraca - self.snitch_ugao + 180) % 360 - 180)
        return razlika < UGAO_KONUSA / 2

    def iza_zbuna(self) -> bool:
        for (bx, by, br) in ZBUNJEVI:
            if self.distanca(self.igrac_pos, (bx, by)) < br + 10:
                return True
        return False

    # ─────────────────────────────────────────
    # FIS ulazi
    # ─────────────────────────────────────────
    def izracunaj_ulaze(self) -> dict:
        dist      = self.distanca(self.snitch_pos, self.igrac_pos)
        u_konusu  = self.u_konusu()
        iza_zbuna = self.iza_zbuna()

        # Vizuelna pouzdanost
        if not u_konusu:
            vizuelna = 0.0
        else:
            vizuelna = max(0.0, 1.0 - dist / DUZINA_KONUSA)
            if iza_zbuna:
                vizuelna *= 0.3

        # Detekcija
        detekcija = max(0.0, 1.0 - dist / 500)
        if iza_zbuna:
            detekcija *= 0.5

        # Pokrivenost
        pokrivenost = 0.85 if iza_zbuna else max(0.1, dist / 600)

        # Zvuk — koraci + Q pucanj, opada vremenom
        if self.igrac_krece:
            self.zvuk_val = max(self.zvuk_val, ZVUK_KORAKA_BASE)
        self.zvuk_val = max(0.0, self.zvuk_val - 0.008)

        return {
            "vizuelna":    round(min(vizuelna,      1.0), 3),
            "zvuk":        round(min(self.zvuk_val, 1.0), 3),
            "pokrivenost": round(min(pokrivenost,   1.0), 3),
            "detekcija":   round(min(detekcija,     1.0), 3),
        }

    # ─────────────────────────────────────────
    # Logika stanja
    # ─────────────────────────────────────────
    def azuriraj_stanje(self, novo_stanje: StanjeSnitcha):
        """
        Pravila prelaza stanja:
        - POTVRĐENO → ostaje 60s čak i ako igrač pobegne
        - UPOZORENJE → kruži 30s oko zone
        - MIRNO      → samo ako nema aktivnih tajmera
        """
        if novo_stanje == StanjeSnitcha.POTVRĐENO:
            # Direktno POTVRĐENO — bez verifikacije ako je u konusu
            self.stanje            = StanjeSnitcha.POTVRĐENO
            self.potvrdjeno_tajmer = TRAJANJE_POTVRDJENO
            self.warning_centar    = None
            self.warning_tajmer    = 0

        elif novo_stanje == StanjeSnitcha.UPOZORENJE:
            if self.stanje == StanjeSnitcha.POTVRĐENO:
                pass   # ne degradiraj dok tajmer traje
            elif self.warning_centar is None:
                self.stanje         = StanjeSnitcha.UPOZORENJE
                self.warning_centar = tuple(self.igrac_pos)
                self.warning_tajmer = TRAJANJE_WARNING

        else:  # MIRNO
            if self.stanje == StanjeSnitcha.POTVRĐENO:
                pass   # čeka tajmer
            elif self.stanje == StanjeSnitcha.UPOZORENJE:
                pass   # čeka tajmer
            else:
                self.stanje = StanjeSnitcha.MIRNO

        # Odbrojavanje tajmera
        if self.potvrdjeno_tajmer > 0:
            self.potvrdjeno_tajmer -= 1
            if self.potvrdjeno_tajmer == 0:
                self.stanje = StanjeSnitcha.MIRNO

        if self.warning_tajmer > 0 and self.stanje == StanjeSnitcha.UPOZORENJE:
            self.warning_tajmer -= 1
            if self.warning_tajmer == 0:
                self.warning_centar = None
                self.stanje         = StanjeSnitcha.MIRNO

    # ─────────────────────────────────────────
    # Kretanje Snitcha
    # ─────────────────────────────────────────
    def pomeri_snitcha(self):
        if self.stanje == StanjeSnitcha.UPOZORENJE and self.warning_centar:
            ugao_rad = math.radians(pygame.time.get_ticks() * 0.05)
            cx, cy   = self.warning_centar
            self.snitch_pos[0] = cx + math.cos(ugao_rad) * 80
            self.snitch_pos[1] = cy + math.sin(ugao_rad) * 80
            self.snitch_ugao   = math.degrees(ugao_rad) + 90

        elif self.stanje == StanjeSnitcha.POTVRĐENO:
            # Okreće se prema igraču
            self.snitch_ugao = self.ugao_do(self.snitch_pos, self.igrac_pos)

        else:
            # Patrola
            cilj = RUTA_PATROLE[self.cilj_patrole]
            dist = self.distanca(self.snitch_pos, cilj)
            if dist < 5:
                self.cilj_patrole = (self.cilj_patrole + 1) % len(RUTA_PATROLE)
            else:
                dx = (cilj[0] - self.snitch_pos[0]) / dist
                dy = (cilj[1] - self.snitch_pos[1]) / dist
                self.snitch_pos[0] += dx * self.snitch_brzina
                self.snitch_pos[1] += dy * self.snitch_brzina
                self.snitch_ugao    = self.ugao_do(self.snitch_pos, cilj)

    # ─────────────────────────────────────────
    # Kretanje igrača
    # ─────────────────────────────────────────
    def pomeri_igraca(self, tasteri):
        dx, dy = 0, 0
        if tasteri[pygame.K_w] or tasteri[pygame.K_UP]:    dy -= 1
        if tasteri[pygame.K_s] or tasteri[pygame.K_DOWN]:  dy += 1
        if tasteri[pygame.K_a] or tasteri[pygame.K_LEFT]:  dx -= 1
        if tasteri[pygame.K_d] or tasteri[pygame.K_RIGHT]: dx += 1

        self.igrac_krece = (dx != 0 or dy != 0)

        if self.igrac_krece:
            duzina = math.hypot(dx, dy)
            self.igrac_pos[0] += (dx / duzina) * self.igrac_brzina
            self.igrac_pos[1] += (dy / duzina) * self.igrac_brzina

        self.igrac_pos[0] = max(10, min(SIRINA - 10, self.igrac_pos[0]))
        self.igrac_pos[1] = max(10, min(VISINA - 10, self.igrac_pos[1]))

    # ─────────────────────────────────────────
    # Crtanje
    # ─────────────────────────────────────────
    def crtaj_konus(self, boja_stanja):
        ugao_rad  = math.radians(self.snitch_ugao)
        pola_ugao = math.radians(UGAO_KONUSA / 2)
        tacke     = [tuple(map(int, self.snitch_pos))]

        for i in range(21):
            a = ugao_rad - pola_ugao + (i / 20) * math.radians(UGAO_KONUSA)
            x = self.snitch_pos[0] + math.cos(a) * DUZINA_KONUSA
            y = self.snitch_pos[1] + math.sin(a) * DUZINA_KONUSA
            tacke.append((int(x), int(y)))

        povrsina  = pygame.Surface((SIRINA, VISINA), pygame.SRCALPHA)
        r, g, b   = boja_stanja
        pygame.draw.polygon(povrsina, (r, g, b, 40),  tacke)
        pygame.draw.polygon(povrsina, (r, g, b, 120), tacke, 2)
        self.ekran.blit(povrsina, (0, 0))

    def crtaj_zbunjeve(self):
        for (bx, by, br) in ZBUNJEVI:
            pygame.draw.circle(self.ekran, (34, 100, 34), (bx, by), br)
            pygame.draw.circle(self.ekran, (50, 140, 50), (bx, by), br, 2)

    def crtaj_snitcha(self, boja_stanja):
        sx, sy   = int(self.snitch_pos[0]), int(self.snitch_pos[1])
        pygame.draw.circle(self.ekran, boja_stanja,    (sx, sy), 16)
        pygame.draw.circle(self.ekran, (255, 255, 255), (sx, sy), 16, 2)
        ugao_rad = math.radians(self.snitch_ugao)
        nx = sx + int(math.cos(ugao_rad) * 22)
        ny = sy + int(math.sin(ugao_rad) * 22)
        pygame.draw.line(self.ekran, (255, 255, 255), (sx, sy), (nx, ny), 3)

    def crtaj_igraca(self):
        ix, iy = int(self.igrac_pos[0]), int(self.igrac_pos[1])
        pygame.draw.circle(self.ekran, BOJA_IGRACA,     (ix, iy), 12)
        pygame.draw.circle(self.ekran, (255, 255, 255), (ix, iy), 12, 2)

    def crtaj_warning_zonu(self):
        if self.warning_centar and self.stanje == StanjeSnitcha.UPOZORENJE:
            cx, cy   = int(self.warning_centar[0]), int(self.warning_centar[1])
            povrsina = pygame.Surface((SIRINA, VISINA), pygame.SRCALPHA)
            pygame.draw.circle(povrsina, (255, 215, 0, 30),  (cx, cy), 100)
            pygame.draw.circle(povrsina, (255, 215, 0, 150), (cx, cy), 100, 2)
            self.ekran.blit(povrsina, (0, 0))

    def crtaj_hud(self, ulazi: dict):
        status = self.snitch.status()

        ikone = {
            StanjeSnitcha.MIRNO:      ">> MIRNO",
            StanjeSnitcha.UPOZORENJE: "!! UPOZORENJE",
            StanjeSnitcha.POTVRĐENO:  "## POTVRDJENO",
        }

        # HUD pozadina
        povrsina = pygame.Surface((310, 300), pygame.SRCALPHA)
        povrsina.fill((0, 0, 0, 160))
        self.ekran.blit(povrsina, (10, 10))

        # Stanje
        naziv = ikone.get(self.stanje, "MIRNO")
        tekst = self.font_v.render(naziv, True, BOJE_STANJA[self.stanje])
        self.ekran.blit(tekst, (20, 18))

        # Ulazi
        y = 55
        self.ekran.blit(self.font_m.render(
            "── ULAZI ───────────────────", True, (150, 150, 150)), (20, y)); y += 22
        for naziv_u, val in ulazi.items():
            traka  = "█" * int(val * 15) + "░" * (15 - int(val * 15))
            linija = f"{naziv_u:<14} {val:.2f} {traka}"
            self.ekran.blit(self.font_m.render(linija, True, (200, 200, 200)), (20, y))
            y += 20

        # Izlazi
        y += 6
        self.ekran.blit(self.font_m.render(
            "── IZLAZI ──────────────────", True, (150, 150, 150)), (20, y)); y += 22
        for naziv_i, val in {
            "angazovanje": status["angazovanje"],
            "rizik":       status["rizik"],
            "urgentnost":  status["urgentnost"],
        }.items():
            traka  = "█" * int(val * 15) + "░" * (15 - int(val * 15))
            linija = f"{naziv_i:<14} {val:.2f} {traka}"
            self.ekran.blit(self.font_m.render(linija, True, (200, 220, 255)), (20, y))
            y += 20

        # Tajmeri
        if self.stanje == StanjeSnitcha.POTVRĐENO and self.potvrdjeno_tajmer > 0:
            sek   = self.potvrdjeno_tajmer // FPS
            tekst = self.font_m.render(f"Alarm aktivan: {sek}s", True, (220, 50, 50))
            self.ekran.blit(tekst, (20, y + 6))
        elif self.stanje == StanjeSnitcha.UPOZORENJE and self.warning_tajmer > 0:
            sek   = self.warning_tajmer // FPS
            tekst = self.font_m.render(f"Verifikacija: {sek}s", True, (255, 215, 0))
            self.ekran.blit(tekst, (20, y + 6))

        # Kontrole
        self.ekran.blit(
            self.font_m.render("WASD — kretanje   Q — pucanj", True, (120, 120, 120)),
            (20, VISINA - 30))

    # ─────────────────────────────────────────
    # Glavni loop
    # ─────────────────────────────────────────
    def pokreni(self):
        while True:
            for dogadjaj in pygame.event.get():
                if dogadjaj.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if dogadjaj.type == pygame.KEYDOWN:
                    if dogadjaj.key == pygame.K_q:
                        self.zvuk_val = ZVUK_PUCNJA

            tasteri = pygame.key.get_pressed()
            self.pomeri_igraca(tasteri)
            self.pomeri_snitcha()

            ulazi      = self.izracunaj_ulaze()
            novo_stanje = self.snitch.proceni(
                vizuelna=ulazi["vizuelna"],
                zvuk=ulazi["zvuk"],
                pokrivenost=ulazi["pokrivenost"],
                detekcija=ulazi["detekcija"],
            )
            self.azuriraj_stanje(novo_stanje)

            boja_stanja = BOJE_STANJA[self.stanje]
            self.ekran.fill(BOJA_POZADINE)
            self.crtaj_zbunjeve()
            self.crtaj_warning_zonu()
            self.crtaj_konus(boja_stanja)
            self.crtaj_snitcha(boja_stanja)
            self.crtaj_igraca()
            self.crtaj_hud(ulazi)

            pygame.display.flip()
            self.sat.tick(FPS)


if __name__ == "__main__":
    igrica = Igrica()
    igrica.pokreni()