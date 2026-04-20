from fazi.zakljucivanje import pokreni_fis
from agent.stanja import StanjeAgenta, string_u_stanje


class Agent:

    def __init__(self, ime: str = "Agent-01"):
        self.ime         = ime
        self.stanje      = StanjeAgenta.MIRNO
        self.angazovanje = 0.0
        self.brzina      = 0.0
        self.upornost    = 0.0

        self.vizuelna    = 0.0
        self.zvuk        = 0.0
        self.pokrivenost = 0.0
        self.detekcija   = 0.0
        self.ugao        = 90.0

    def proceni(self, vizuelna, zvuk, pokrivenost, detekcija, ugao=90.0, ispisi=False):

        self.vizuelna    = vizuelna
        self.zvuk        = zvuk
        self.pokrivenost = pokrivenost
        self.detekcija   = detekcija
        self.ugao        = ugao

        rezultat = pokreni_fis(vizuelna, zvuk, pokrivenost, detekcija, ugao, ispisi=ispisi)

        self.angazovanje = rezultat["angazovanje"]
        self.brzina      = rezultat["brzina"]
        self.upornost    = rezultat["upornost"]
        self.stanje      = string_u_stanje(rezultat["stanje"])

        return self.stanje

    def status(self) -> dict:
        return {
            "ime":         self.ime,
            "stanje":      self.stanje,
            "angazovanje": self.angazovanje,
            "brzina":      self.brzina,
            "upornost":    self.upornost,
            "ulazi": {
                "vizuelna":    self.vizuelna,
                "zvuk":        self.zvuk,
                "pokrivenost": self.pokrivenost,
                "detekcija":   self.detekcija,
                "ugao":        self.ugao,
            },
        }