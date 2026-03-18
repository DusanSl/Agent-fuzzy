# agent/states.py
from enum import Enum


class StanjeSnitcha(Enum):
    MIRNO      = "MIRNO"
    UPOZORENJE = "UPOZORENJE"
    POTVRĐENO  = "POTVRĐENO"


BOJE_STANJA = {
    StanjeSnitcha.MIRNO:      (50,  205, 50),   # zelena
    StanjeSnitcha.UPOZORENJE: (255, 215, 0),    # žuta
    StanjeSnitcha.POTVRĐENO:  (220, 50,  50),   # crvena
}


def string_u_stanje(stanje: str) -> StanjeSnitcha:

    mapa = {
        "MIRNO":      StanjeSnitcha.MIRNO,
        "UPOZORENJE": StanjeSnitcha.UPOZORENJE,
        "POTVRĐENO":  StanjeSnitcha.POTVRĐENO,
    }
    return mapa.get(stanje, StanjeSnitcha.MIRNO)