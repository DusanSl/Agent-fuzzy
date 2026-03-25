# game/simulation.py
import pygame
import math
import sys
import random
from agent.snitch import Snitch
from agent.states import StanjeSnitcha, BOJE_STANJA
from game.renderer import Renderer

# ─────────────────────────────────────────
# Konstante
# ─────────────────────────────────────────
SIRINA        = 1100
VISINA        = 700
FPS           = 60
BOJA_POZADINE = (15, 15, 25)
BOJA_IGRACA   = (30, 144, 255)

UGAO_KONUSA   = 90
DUZINA_KONUSA = 200

TRAJANJE_POTVRDJENO = 60 * FPS
TRAJANJE_WARNING_MIN = 5  * FPS
TRAJANJE_WARNING_MAX = 35 * FPS
DELAY_POTVRDJENO    = int(3.5 * FPS)

# Brzina Snitcha po stanjima — fuzzy izlaz [0,1] skalira unutar opsega
# MIRNO:      1.5 – 2.0  (patrolna)
# UPOZORENJE: 1.8 – 2.2  (oprezna)
# POTVRĐENO:  2.2 – 2.6  (fokusirana)
BRZINA_POCETNA = 1.5

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

ZVUK_KORAKA_BASE = 0.35


class Igrica:
    def __init__(self):
        pygame.init()
        self.ekran  = pygame.display.set_mode((SIRINA, VISINA))
        pygame.display.set_caption("FuzzySnitch — Nadzorni Agent")
        self.sat    = pygame.time.Clock()
        self.font_m = pygame.font.SysFont("consolas", 16)
        self.font_v = pygame.font.SysFont("consolas", 22, bold=True)

        # Renderer
        self.renderer = Renderer(self.ekran, self.font_m, self.font_v, SIRINA, VISINA)

        # Agent
        self.snitch            = Snitch(ime="Snitch-01")
        self.snitch_pos        = list(RUTA_PATROLE[0])
        self.snitch_ugao       = 0.0
        self.snitch_brzina     = BRZINA_POCETNA
        self.cilj_patrole      = 1
        self.stanje            = StanjeSnitcha.MIRNO

        # Tajmeri
        self.potvrdjeno_tajmer = 0
        self.warning_tajmer    = 0
        self.warning_centar    = None
        self.vidi_tajmer       = 0

        # Igrač
        self.igrac_pos         = [500, 350]
        self.igrac_brzina      = 3.0
        self.igrac_krece       = False

        # Zvuk
        self.zvuk_val          = 0.0

    # ─────────────────────────────────────────
    # Fuzzy brzina → stvarna brzina
    # ─────────────────────────────────────────
    def azuriraj_brzinu(self):
        """
        Fuzzy brzina [0, 1] utiče na kretanje u sva tri stanja,
        ali sa različitim opsezima — stanja se ne preklapaju.
          MIRNO:       1.5 – 2.0  (patrolna, spora)
          UPOZORENJE:  1.8 – 2.2  (oprezna, malo brža)
          POTVRĐENO:   2.2 – 2.6  (fokusirana, najbrža)
        """
        b = self.snitch.brzina  # crisp vrednost iz FIS-a [0, 1]
        if self.stanje == StanjeSnitcha.POTVRĐENO:
            self.snitch_brzina = 2.2 + b * 0.4
        elif self.stanje == StanjeSnitcha.UPOZORENJE:
            self.snitch_brzina = 1.8 + b * 0.4
        else:
            self.snitch_brzina = 1.5 + b * 0.5

    # ─────────────────────────────────────────
    # Fuzzy upornost → trajanje kruženja
    # ─────────────────────────────────────────
    def fuzzy_warning_tajmer(self) -> int:
        """
        Fuzzy upornost [0, 1] određuje koliko dugo snitch kruži.
          kratkotrajna (~0.0) → 5s
          zadrzana     (~0.5) → 20s
          uporna       (~1.0) → 35s
        """
        u = self.snitch.upornost
        return int(TRAJANJE_WARNING_MIN + u * (TRAJANJE_WARNING_MAX - TRAJANJE_WARNING_MIN))

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
                vizuelna *= 0.45

        # Detekcija
        detekcija = max(0.0, 1.0 - dist / 500)
        if iza_zbuna:
            detekcija *= 0.55

        # Pokrivenost
        zbun_faktor = 0.0
        for (bx, by, br) in ZBUNJEVI:
            d = self.distanca(self.igrac_pos, (bx, by))
            if d < br + 30:
                zbun_faktor = max(zbun_faktor, 1.0 - (d / (br + 30)))

        dist_faktor     = min(1.0, dist / 600)
        kretanje_faktor = 0.2 if self.igrac_krece else 0.0
        pokrivenost     = min(1.0, dist_faktor * 0.4 + zbun_faktor * 0.6 - kretanje_faktor)
        pokrivenost     = max(0.0, pokrivenost)

        # Zvuk
        if self.igrac_krece:
            zvuk_koraka   = ZVUK_KORAKA_BASE * (1.0 - min(1.0, dist / 600))
            self.zvuk_val = max(self.zvuk_val, zvuk_koraka)
        self.zvuk_val = max(0.0, self.zvuk_val - 0.008)

        ugao_do_igraca = self.ugao_do(self.snitch_pos, self.igrac_pos)
        ugaona_razlika = abs((ugao_do_igraca - self.snitch_ugao + 180) % 360 - 180)

        return {
            "vizuelna":    round(min(vizuelna, 1.0), 3),
            "zvuk":        round(min(self.zvuk_val, 1.0), 3),
            "pokrivenost": round(min(pokrivenost, 1.0), 3),
            "detekcija":   round(min(detekcija, 1.0), 3),
            "ugao":        round(ugaona_razlika, 1),
        }

    # ─────────────────────────────────────────
    # Logika stanja
    # ─────────────────────────────────────────
    def azuriraj_stanje(self, novo_stanje: StanjeSnitcha, zvuk: float):
        u_konusu  = self.u_konusu()
        iza_zbuna = self.iza_zbuna()

        if u_konusu and not iza_zbuna:
            self.vidi_tajmer += 1
        elif u_konusu and iza_zbuna:
            self.vidi_tajmer = max(0, self.vidi_tajmer - 1)
        else:
            if self.stanje == StanjeSnitcha.UPOZORENJE:
                self.vidi_tajmer = max(0, self.vidi_tajmer - 1)
            else:
                self.vidi_tajmer = max(0, self.vidi_tajmer - 3)

        # POTVRĐENO
        if u_konusu and not iza_zbuna:
            self.stanje            = StanjeSnitcha.POTVRĐENO
            self.potvrdjeno_tajmer = TRAJANJE_POTVRDJENO
            self.warning_centar    = None
            self.warning_tajmer    = 0
            self.vidi_tajmer       = 0

        # UPOZORENJE
        elif novo_stanje == StanjeSnitcha.UPOZORENJE or (u_konusu and iza_zbuna):
            if self.stanje != StanjeSnitcha.POTVRĐENO:
                self.stanje = StanjeSnitcha.UPOZORENJE

                if zvuk >= 0.9 and self.warning_centar is not None:
                    self.warning_centar = tuple(map(int, self.igrac_pos))
                    self.warning_tajmer = self.fuzzy_warning_tajmer()

                if self.warning_centar is None:
                    self.aktivacioni_zvuk     = zvuk
                    self.aktivaciona_vizuelna = self.snitch.angazovanje
                    if zvuk > 0.1:
                        self.warning_centar = tuple(map(int, self.igrac_pos))
                    else:
                        self.warning_centar = tuple(map(int, self.snitch_pos))
                    self.warning_tajmer = self.fuzzy_warning_tajmer()

        # MIRNO
        else:
            if self.stanje not in (StanjeSnitcha.POTVRĐENO, StanjeSnitcha.UPOZORENJE):
                self.stanje = StanjeSnitcha.MIRNO

        # Odbrojavanje — POTVRĐENO
        if self.potvrdjeno_tajmer > 0:
            self.potvrdjeno_tajmer -= 1
            if self.potvrdjeno_tajmer == 0:
                self.vidi_tajmer = 0
                self.stanje = StanjeSnitcha.MIRNO

        # Odbrojavanje — UPOZORENJE
        if self.warning_tajmer > 0 and self.stanje == StanjeSnitcha.UPOZORENJE:
            self.warning_tajmer -= 1
            if self.warning_tajmer == 0:
                self.warning_centar = None
                self.stanje = StanjeSnitcha.MIRNO

    # ─────────────────────────────────────────
    # Kretanje Snitcha
    # ─────────────────────────────────────────
    def pomeri_snitcha(self):
        b = self.snitch_brzina   # fuzzy-diktirana brzina

        if self.stanje == StanjeSnitcha.POTVRĐENO:
            dist = self.distanca(self.snitch_pos, self.igrac_pos)
            if dist > 20:
                dx = (self.igrac_pos[0] - self.snitch_pos[0]) / dist
                dy = (self.igrac_pos[1] - self.snitch_pos[1]) / dist
                self.snitch_pos[0] += dx * b
                self.snitch_pos[1] += dy * b
            self.snitch_ugao = self.ugao_do(self.snitch_pos, self.igrac_pos)

        elif self.stanje == StanjeSnitcha.UPOZORENJE and self.warning_centar:
            ugao_rad = math.radians(pygame.time.get_ticks() * 0.05)
            cx, cy   = self.warning_centar
            self.snitch_pos[0] = cx + math.cos(ugao_rad) * 80
            self.snitch_pos[1] = cy + math.sin(ugao_rad) * 80
            self.snitch_ugao   = math.degrees(ugao_rad) + 90

        else:
            cilj = RUTA_PATROLE[self.cilj_patrole]
            dist = self.distanca(self.snitch_pos, cilj)
            if dist < 5:
                self.cilj_patrole = (self.cilj_patrole + 1) % len(RUTA_PATROLE)
            else:
                dx = (cilj[0] - self.snitch_pos[0]) / dist
                dy = (cilj[1] - self.snitch_pos[1]) / dist
                self.snitch_pos[0] += dx * b
                self.snitch_pos[1] += dy * b
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
                        self.zvuk_val = random.uniform(0.30, 1.0)

            tasteri = pygame.key.get_pressed()
            self.pomeri_igraca(tasteri)

            # FIS → fuzzy izlazi → ažuriraj stanje → ažuriraj brzinu → pomeri
            ulazi       = self.izracunaj_ulaze()
            novo_stanje = self.snitch.proceni(
                vizuelna=ulazi["vizuelna"],
                zvuk=ulazi["zvuk"],
                pokrivenost=ulazi["pokrivenost"],
                detekcija=ulazi["detekcija"],
                ugao=ulazi["ugao"],
            )
            self.azuriraj_stanje(novo_stanje, ulazi["zvuk"])
            self.azuriraj_brzinu()   # ← posle stanja, čita novo stanje
            self.pomeri_snitcha()

            boja_stanja = BOJE_STANJA[self.stanje]
            self.ekran.fill(BOJA_POZADINE)
            self.renderer.crtaj_zbunjeve(ZBUNJEVI)
            self.renderer.crtaj_warning_zonu(self.warning_centar, self.stanje)
            self.renderer.crtaj_konus(
                self.snitch_pos, self.snitch_ugao,
                boja_stanja, UGAO_KONUSA, DUZINA_KONUSA,
            )
            self.renderer.crtaj_snitcha(self.snitch_pos, self.snitch_ugao, boja_stanja)
            self.renderer.crtaj_igraca(self.igrac_pos, BOJA_IGRACA)
            self.renderer.crtaj_hud(
                ulazi, self.snitch.status(), self.stanje,
                self.vidi_tajmer, DELAY_POTVRDJENO,
                self.potvrdjeno_tajmer, self.warning_tajmer, FPS,
            )

            pygame.display.flip()
            self.sat.tick(FPS)


if __name__ == "__main__":
    igrica = Igrica()
    igrica.pokreni()