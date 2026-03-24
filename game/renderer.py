# game/renderer.py
import pygame
import math
from agent.states import StanjeSnitcha, BOJE_STANJA


class Renderer:
    def __init__(self, ekran, font_m, font_v, sirina: int, visina: int):
        self.ekran  = ekran
        self.font_m = font_m
        self.font_v = font_v
        self.SIRINA = sirina
        self.VISINA = visina

    def crtaj_zbunjeve(self, zbunjevi: list):
        for (bx, by, br) in zbunjevi:
            pygame.draw.circle(self.ekran, (34, 100, 34), (bx, by), br)
            pygame.draw.circle(self.ekran, (50, 140, 50), (bx, by), br, 2)

    def crtaj_konus(self, snitch_pos, snitch_ugao, boja_stanja,
                    ugao_konusa: int, duzina_konusa: int):
        ugao_rad  = math.radians(snitch_ugao)
        pola_ugao = math.radians(ugao_konusa / 2)
        tacke     = [tuple(map(int, snitch_pos))]

        for i in range(21):
            a = ugao_rad - pola_ugao + (i / 20) * math.radians(ugao_konusa)
            x = snitch_pos[0] + math.cos(a) * duzina_konusa
            y = snitch_pos[1] + math.sin(a) * duzina_konusa
            tacke.append((int(x), int(y)))

        povrsina = pygame.Surface((self.SIRINA, self.VISINA), pygame.SRCALPHA)
        r, g, b  = boja_stanja
        pygame.draw.polygon(povrsina, (r, g, b, 40),  tacke)
        pygame.draw.polygon(povrsina, (r, g, b, 120), tacke, 2)
        self.ekran.blit(povrsina, (0, 0))

    def crtaj_snitcha(self, snitch_pos, snitch_ugao, boja_stanja):
        sx, sy   = int(snitch_pos[0]), int(snitch_pos[1])
        pygame.draw.circle(self.ekran, boja_stanja,     (sx, sy), 16)
        pygame.draw.circle(self.ekran, (255, 255, 255), (sx, sy), 16, 2)
        ugao_rad = math.radians(snitch_ugao)
        nx = sx + int(math.cos(ugao_rad) * 22)
        ny = sy + int(math.sin(ugao_rad) * 22)
        pygame.draw.line(self.ekran, (255, 255, 255), (sx, sy), (nx, ny), 3)

    def crtaj_igraca(self, igrac_pos, boja_igraca):
        ix, iy = int(igrac_pos[0]), int(igrac_pos[1])
        pygame.draw.circle(self.ekran, boja_igraca,     (ix, iy), 12)
        pygame.draw.circle(self.ekran, (255, 255, 255), (ix, iy), 12, 2)

    def crtaj_warning_zonu(self, warning_centar, stanje):
        if warning_centar and stanje == StanjeSnitcha.UPOZORENJE:
            cx, cy   = int(warning_centar[0]), int(warning_centar[1])
            povrsina = pygame.Surface((self.SIRINA, self.VISINA), pygame.SRCALPHA)
            pygame.draw.circle(povrsina, (255, 215, 0, 30),  (cx, cy), 100)
            pygame.draw.circle(povrsina, (255, 215, 0, 150), (cx, cy), 100, 2)
            self.ekran.blit(povrsina, (0, 0))

    def crtaj_hud(self, ulazi: dict, status: dict, stanje: StanjeSnitcha,
                  vidi_tajmer: int, delay_potvrdjeno: int,
                  potvrdjeno_tajmer: int, warning_tajmer: int, fps: int):

        ikone = {
            StanjeSnitcha.MIRNO:      ">> MIRNO",
            StanjeSnitcha.UPOZORENJE: "!! UPOZORENJE",
            StanjeSnitcha.POTVRĐENO:  "## POTVRDJENO",
        }

        # HUD pozadina
        povrsina = pygame.Surface((310, 320), pygame.SRCALPHA)
        povrsina.fill((0, 0, 0, 160))
        self.ekran.blit(povrsina, (10, 10))

        # Stanje
        naziv = ikone.get(stanje, "MIRNO")
        tekst = self.font_v.render(naziv, True, BOJE_STANJA[stanje])
        self.ekran.blit(tekst, (20, 18))

        # Ulazi
        y = 55
        self.ekran.blit(self.font_m.render(
            "── ULAZI ───────────────────", True, (150, 150, 150)), (20, y)); y += 22
        for naziv_u, val in ulazi.items():
            if naziv_u == "ugao":
                traka_val = val / 180.0
                prikaz = f"{val:.1f}°"
            else:
                traka_val = val
                prikaz = f"{val:.2f} "

            traka  = "█" * int(traka_val * 15) + "░" * (15 - int(traka_val * 15))
            linija = f"{naziv_u:<14} {prikaz} {traka}"
            self.ekran.blit(self.font_m.render(linija, True, (200, 200, 200)), (20, y))
            y += 20

        # Izlazi
        y += 6
        self.ekran.blit(self.font_m.render(
            "── IZLAZI ──────────────────", True, (150, 150, 150)), (20, y)); y += 22
        for naziv_i, val in {
            "angazovanje": status["angazovanje"],
            "brzina":      status["brzina"],
            "upornost":    status["upornost"],
        }.items():
            traka  = "█" * int(val * 15) + "░" * (15 - int(val * 15))
            linija = f"{naziv_i:<14} {val:.2f} {traka}"
            self.ekran.blit(self.font_m.render(linija, True, (200, 220, 255)), (20, y))
            y += 20

        # Detekcija progress bar
        y += 8
        progres = min(vidi_tajmer / delay_potvrdjeno, 1.0)
        bar_sir = int(progres * 200)
        self.ekran.blit(
            self.font_m.render("Detekcija:", True, (150, 150, 150)), (20, y)); y += 18
        pygame.draw.rect(self.ekran, (60, 60, 60),  (20, y, 200, 10))
        pygame.draw.rect(self.ekran, (220, 50, 50), (20, y, bar_sir, 10))

        # Tajmeri
        y += 18
        if stanje == StanjeSnitcha.POTVRĐENO and potvrdjeno_tajmer > 0:
            sek = potvrdjeno_tajmer // fps
            self.ekran.blit(
                self.font_m.render(f"Alarm aktivan: {sek}s", True, (220, 50, 50)), (20, y))
        elif stanje == StanjeSnitcha.UPOZORENJE and warning_tajmer > 0:
            sek = warning_tajmer // fps
            self.ekran.blit(
                self.font_m.render(f"Verifikacija: {sek}s", True, (255, 215, 0)), (20, y))

        # Kontrole
        self.ekran.blit(
            self.font_m.render("WASD — kretanje   Q — pucanj", True, (120, 120, 120)),
            (20, self.VISINA - 30))