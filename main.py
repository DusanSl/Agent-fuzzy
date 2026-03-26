# main.py
from agent.nadzornik import Agent
from fazi.defazifikacija import ispisi_izlaze


def main():
    print("=" * 48)
    print("  FaziAgent — Pokretanje sistema")
    print("=" * 48)

    snitch = Agent(ime="Agent-01")

    # Test scenariji
    scenariji = [
        {
            "naziv":       "Mirna patrolа — nema signala",
            "vizuelna":    0.10,
            "zvuk":        0.05,
            "pokrivenost": 0.80,
            "detekcija":   0.10,
        },
        {
            "naziv":       "Sumnjiv šum — delimična vidljivost",
            "vizuelna":    0.45,
            "zvuk":        0.55,
            "pokrivenost": 0.40,
            "detekcija":   0.50,
        },
        {
            "naziv":       "Pucanj — retka pokrivenost",
            "vizuelna":    0.55,
            "zvuk":        0.95,
            "pokrivenost": 0.30,
            "detekcija":   0.70,
        },
        {
            "naziv":       "Jasna vidljivost — uljez otkriven",
            "vizuelna":    0.90,
            "zvuk":        0.60,
            "pokrivenost": 0.15,
            "detekcija":   0.85,
        },
    ]

    for sc in scenariji:
        print(f"\n📡 Scenario: {sc['naziv']}")
        print(f"   Ulazi → vizuelna: {sc['vizuelna']}  "
              f"zvuk: {sc['zvuk']}  "
              f"pokrivenost: {sc['pokrivenost']}  "
              f"detekcija: {sc['detekcija']}")

        stanje = snitch.proceni(
            vizuelna=sc["vizuelna"],
            zvuk=sc["zvuk"],
            pokrivenost=sc["pokrivenost"],
            detekcija=sc["detekcija"],
            ispisi=True,
        )

    print("\n" + "=" * 48)
    print("  Sistem završio sa radom.")
    print("=" * 48)


if __name__ == "__main__":
    from igra.simulacija import Igrica
    igrica = Igrica()
    igrica.pokreni()