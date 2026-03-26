# agent/stanja.py
from enum import Enum


class StanjeAgenta(Enum):
    MIRNO      = "MIRNO"
    UPOZORENJE = "UPOZORENJE"
    POTVRĐENO  = "POTVRĐENO"


BOJE_STANJA = {
    StanjeAgenta.MIRNO:      (50,  205, 50),   # zelena
    StanjeAgenta.UPOZORENJE: (255, 215, 0),    # žuta
    StanjeAgenta.POTVRĐENO:  (220, 50,  50),   # crvena
}


def string_u_stanje(stanje: str) -> StanjeAgenta:

    mapa = {
        "MIRNO":      StanjeAgenta.MIRNO,
        "UPOZORENJE": StanjeAgenta.UPOZORENJE,
        "POTVRĐENO":  StanjeAgenta.POTVRĐENO,
    }
    return mapa.get(stanje, StanjeAgenta.MIRNO)