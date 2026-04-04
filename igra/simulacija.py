import pygame
import math
import sys
import random
from agent.nadzornik import Agent
from agent.stanja import StanjeAgenta, BOJE_STANJA
from igra.prikaz import Prikaz

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
        pygame.display.set_caption("Nadzorni FuzzyAgent")
        self.sat    = pygame.time.Clock()
        self.font_m = pygame.font.SysFont("consolas", 16)
        self.font_v = pygame.font.SysFont("consolas", 22, bold=True)

        self.renderer = Prikaz(self.ekran, self.font_m, self.font_v, SIRINA, VISINA)

        self.agent            = Agent(ime="Agent-01")
        self.agent_pos        = list(RUTA_PATROLE[0])
        self.agent_ugao       = 0.0
        self.agent_brzina     = BRZINA_POCETNA
        self.cilj_patrole      = 1
        self.stanje            = StanjeAgenta.MIRNO

        self.potvrdjeno_tajmer = 0
        self.warning_tajmer    = 0
        self.warning_centar    = None
        self.vidi_tajmer       = 0

        self.igrac_pos         = [500, 350]
        self.igrac_brzina      = 3.0
        self.igrac_krece       = False

        self.zvuk_val          = 0.0
        self.peak_zvuk         = 0.0
        self.lure_aktivan      = False

    # Fuzzy brzina → stvarna brzina
    def azuriraj_brzinu(self):
        b = self.agent.brzina
        if self.stanje == StanjeAgenta.POTVRĐENO:
            self.agent_brzina = 2.2 + b * 0.4
        elif self.stanje == StanjeAgenta.UPOZORENJE:
            self.agent_brzina = 1.8 + b * 0.4
        else:
            self.agent_brzina = 1.5 + b * 0.5

    def fuzzy_warning_tajmer(self) -> int:
        u = self.agent.upornost
        zvuk = getattr(self, "aktivacioni_zvuk", 0.5)
        zvuk_faktor = 1.0 + zvuk
        bazni = TRAJANJE_WARNING_MIN + u * (TRAJANJE_WARNING_MAX - TRAJANJE_WARNING_MIN)
        return int(min(TRAJANJE_WARNING_MAX, bazni * zvuk_faktor))

    def distanca(self, a, b) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def ugao_do(self, od, do) -> float:
        return math.degrees(math.atan2(do[1] - od[1], do[0] - od[0]))

    def u_konusu(self) -> bool:
        dist = self.distanca(self.agent_pos, self.igrac_pos)
        if dist > DUZINA_KONUSA:
            return False
        ugao_do_igraca = self.ugao_do(self.agent_pos, self.igrac_pos)
        razlika = abs((ugao_do_igraca - self.agent_ugao + 180) % 360 - 180)
        return razlika < UGAO_KONUSA / 2

    def iza_zbuna(self) -> bool:
        for (bx, by, br) in ZBUNJEVI:
            if self.distanca(self.igrac_pos, (bx, by)) < br + 10:
                return True
        return False

    # Ulazi
    def izracunaj_ulaze(self) -> dict:
        dist      = self.distanca(self.agent_pos, self.igrac_pos)
        u_konusu  = self.u_konusu()
        iza_zbuna = self.iza_zbuna()

        if not u_konusu:
            vizuelna = 0.0
        else:
            vizuelna = max(0.0, 1.0 - dist / DUZINA_KONUSA)
            if iza_zbuna:
                vizuelna *= 0.45

        detekcija = max(0.0, 1.0 - dist / 500)
        if iza_zbuna:
            detekcija *= 0.55

        zbun_faktor = 0.0
        for (bx, by, br) in ZBUNJEVI:
            d = self.distanca(self.igrac_pos, (bx, by))
            if d < br + 30:
                zbun_faktor = max(zbun_faktor, 1.0 - (d / (br + 30)))

        dist_faktor     = min(1.0, dist / 600)
        kretanje_faktor = 0.2 if self.igrac_krece else 0.0
        pokrivenost     = min(1.0, dist_faktor * 0.4 + zbun_faktor * 0.6 - kretanje_faktor)
        pokrivenost     = max(0.0, pokrivenost)

        if self.igrac_krece:
            zvuk_koraka   = ZVUK_KORAKA_BASE * (1.0 - min(1.0, dist / 600))
            self.zvuk_val = max(self.zvuk_val, zvuk_koraka)
        self.zvuk_val = max(0.0, self.zvuk_val - 0.008)

        ugao_do_igraca = self.ugao_do(self.agent_pos, self.igrac_pos)
        ugaona_razlika = abs((ugao_do_igraca - self.agent_ugao + 180) % 360 - 180)

        return {
            "vizuelna":    round(min(vizuelna, 1.0), 3),
            "zvuk":        round(min(self.zvuk_val, 1.0), 3),
            "pokrivenost": round(min(pokrivenost, 1.0), 3),
            "detekcija":   round(min(detekcija, 1.0), 3),
            "ugao":        round(ugaona_razlika, 1),
        }

    def azuriraj_stanje(self, novo_stanje: StanjeAgenta, zvuk: float):
        u_konusu  = self.u_konusu()
        iza_zbuna = self.iza_zbuna()

        if u_konusu and not iza_zbuna:
            self.vidi_tajmer += 1
        elif u_konusu and iza_zbuna:
            self.vidi_tajmer = max(0, self.vidi_tajmer - 1)
        else:
            if self.stanje == StanjeAgenta.UPOZORENJE:
                self.vidi_tajmer = max(0, self.vidi_tajmer - 1)
            else:
                self.vidi_tajmer = max(0, self.vidi_tajmer - 3)

        if u_konusu and not iza_zbuna:
            self.stanje            = StanjeAgenta.POTVRĐENO
            self.potvrdjeno_tajmer = TRAJANJE_POTVRDJENO
            self.warning_centar    = None
            self.warning_tajmer    = 0
            self.vidi_tajmer       = 0

        elif novo_stanje == StanjeAgenta.UPOZORENJE or (u_konusu and iza_zbuna) or zvuk >= 0.70:
            if self.stanje != StanjeAgenta.POTVRĐENO:
                self.stanje = StanjeAgenta.UPOZORENJE

                if self.warning_centar is None:
                    self.aktivacioni_zvuk     = zvuk
                    self.aktivaciona_vizuelna = self.agent.angazovanje
                    self.warning_centar = tuple(map(int, self.igrac_pos if zvuk > 0.1 else self.agent_pos))
                    self.warning_tajmer = self.fuzzy_warning_tajmer()
                    self.lure_aktivan   = zvuk >= 0.70
                elif self.peak_zvuk >= 0.70 and not self.lure_aktivan:
                    self.aktivacioni_zvuk = self.peak_zvuk
                    self.warning_centar   = tuple(map(int, self.igrac_pos))
                    self.warning_tajmer   = self.fuzzy_warning_tajmer()
                    self.lure_aktivan     = True

        else:
            if self.stanje not in (StanjeAgenta.POTVRĐENO, StanjeAgenta.UPOZORENJE):
                self.stanje = StanjeAgenta.MIRNO

        if self.potvrdjeno_tajmer > 0:
            self.potvrdjeno_tajmer -= 1
            if self.potvrdjeno_tajmer == 0:
                self.vidi_tajmer = 0
                self.stanje = StanjeAgenta.MIRNO

        if self.warning_tajmer > 0 and self.stanje == StanjeAgenta.UPOZORENJE:
            if self.lure_aktivan:
                otpadanje = 1.0
            else:
                otpadanje = max(0.1, 1.0 - self.agent.upornost)
            self.warning_tajmer = int(self.warning_tajmer - otpadanje)
            if self.warning_tajmer <= 0:
                self.warning_tajmer = 0
                self.warning_centar = None
                self.lure_aktivan   = False
                self.stanje = StanjeAgenta.MIRNO

    def pomeri_agenta(self):
        b = self.agent_brzina

        if self.stanje == StanjeAgenta.POTVRĐENO:
            dist = self.distanca(self.agent_pos, self.igrac_pos)
            if dist > 20:
                dx = (self.igrac_pos[0] - self.agent_pos[0]) / dist
                dy = (self.igrac_pos[1] - self.agent_pos[1]) / dist
                self.agent_pos[0] += dx * b
                self.agent_pos[1] += dy * b
            self.agent_ugao = self.ugao_do(self.agent_pos, self.igrac_pos)

        elif self.stanje == StanjeAgenta.UPOZORENJE and self.warning_centar:
            dist_do_centra = self.distanca(self.agent_pos, self.warning_centar)
            if self.lure_aktivan and dist_do_centra > 15:
                # Lure mod — ide direktno prema izvoru zvuka
                dx = (self.warning_centar[0] - self.agent_pos[0]) / dist_do_centra
                dy = (self.warning_centar[1] - self.agent_pos[1]) / dist_do_centra
                self.agent_pos[0] += dx * b
                self.agent_pos[1] += dy * b
                self.agent_ugao = self.ugao_do(self.agent_pos, self.warning_centar)
            else:
                if self.lure_aktivan and dist_do_centra <= 15:
                    self.lure_aktivan = False
                    self.peak_zvuk    = 0.0
                ugao_rad = math.radians(pygame.time.get_ticks() * 0.05)
                cx, cy   = self.warning_centar
                self.agent_pos[0] = cx + math.cos(ugao_rad) * 80
                self.agent_pos[1] = cy + math.sin(ugao_rad) * 80
                self.agent_ugao   = math.degrees(ugao_rad) + 90

        else:
            cilj = RUTA_PATROLE[self.cilj_patrole]
            dist = self.distanca(self.agent_pos, cilj)
            if dist < 5:
                self.cilj_patrole = (self.cilj_patrole + 1) % len(RUTA_PATROLE)
            else:
                dx = (cilj[0] - self.agent_pos[0]) / dist
                dy = (cilj[1] - self.agent_pos[1]) / dist
                self.agent_pos[0] += dx * b
                self.agent_pos[1] += dy * b
                self.agent_ugao    = self.ugao_do(self.agent_pos, cilj)

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

    def pokreni(self):
        while True:
            for dogadjaj in pygame.event.get():
                if dogadjaj.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if dogadjaj.type == pygame.KEYDOWN:
                    if dogadjaj.key == pygame.K_q:
                        self.zvuk_val = random.uniform(0.70, 1.0)
                        self.peak_zvuk = self.zvuk_val

            tasteri = pygame.key.get_pressed()
            self.pomeri_igraca(tasteri)

            ulazi       = self.izracunaj_ulaze()
            novo_stanje = self.agent.proceni(
                vizuelna=ulazi["vizuelna"],
                zvuk=ulazi["zvuk"],
                pokrivenost=ulazi["pokrivenost"],
                detekcija=ulazi["detekcija"],
                ugao=ulazi["ugao"],
            )
            self.azuriraj_stanje(novo_stanje, ulazi["zvuk"])
            self.azuriraj_brzinu()
            self.pomeri_agenta()

            boja_stanja = BOJE_STANJA[self.stanje]
            self.ekran.fill(BOJA_POZADINE)
            self.renderer.crtaj_zbunjeve(ZBUNJEVI)
            self.renderer.crtaj_warning_zonu(self.warning_centar, self.stanje)
            self.renderer.crtaj_konus(
                self.agent_pos, self.agent_ugao,
                boja_stanja, UGAO_KONUSA, DUZINA_KONUSA,
            )
            self.renderer.crtaj_agenta(self.agent_pos, self.agent_ugao, boja_stanja)
            self.renderer.crtaj_igraca(self.igrac_pos, BOJA_IGRACA)
            self.renderer.crtaj_hud(
                ulazi, self.agent.status(), self.stanje,
                self.vidi_tajmer, DELAY_POTVRDJENO,
                self.potvrdjeno_tajmer, self.warning_tajmer, FPS,
            )

            pygame.display.flip()
            self.sat.tick(FPS)


if __name__ == "__main__":
    igrica = Igrica()
    igrica.pokreni()