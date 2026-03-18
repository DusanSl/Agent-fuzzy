# agent/snitch.py
from fuzzy.inference import pokreni_fis
from agent.states import StanjeSnitcha, string_u_stanje


class Snitch:

    def __init__(self, ime: str = "Snitch-01"):
        self.ime              = ime
        self.stanje           = StanjeSnitcha.MIRNO
        self.angazovanje      = 0.0
        self.rizik            = 0.0
        self.urgentnost       = 0.0

        # HUD prikaz
        self.vizuelna         = 0.0
        self.zvuk             = 0.0
        self.pokrivenost      = 0.0
        self.detekcija        = 0.0

    def proceni(self, vizuelna, zvuk, pokrivenost, detekcija, ugao=90.0, ispisi=False):

        self.vizuelna    = vizuelna
        self.zvuk        = zvuk
        self.pokrivenost = pokrivenost
        self.detekcija   = detekcija
        self.ugao        = ugao

        rezultat = pokreni_fis(vizuelna, zvuk, pokrivenost, detekcija, ugao, ispisi=ispisi)

        self.angazovanje = rezultat["angazovanje"]
        self.rizik       = rezultat["rizik"]
        self.urgentnost  = rezultat["urgentnost"]
        self.stanje      = string_u_stanje(rezultat["stanje"])

        return self.stanje

    def status(self) -> dict:
        return {
            "ime":         self.ime,
            "stanje":      self.stanje,
            "angazovanje": self.angazovanje,
            "rizik":       self.rizik,
            "urgentnost":  self.urgentnost,
            "ulazi": {
                "vizuelna":    self.vizuelna,
                "zvuk":        self.zvuk,
                "pokrivenost": self.pokrivenost,
                "detekcija":   self.detekcija,
            },
        }