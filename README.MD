# Nadzorni FuzzyAgent

Ovaj projekat predstavlja demonstraciju primene **Fuzzy logike** (uključujući fazifikaciju, evaluaciju pravila i defazifikaciju) u kontekstu donošenja odluka autonomnog softverskog agenta. Glavni cilj ovog projekta **nije sama igra**, već prikazivanje načina na koji sistemi za zaključivanje zasnovani na fuzzy logici funkcionišu i kako se mogu iskoristiti za simulaciju inteligentnog ponašanja agenta na osnovu nepreciznih i kompleksnih ulaznih parametara.

## Kako Fuzzy logika funkcioniše u ovom projektu?

Fuzzy kontroler, koji se nalazi u direktorijumu `fazi/`, prima ulazne podatke iz okruženja (simulacije), pretvara ih u stepen pripadnosti za različite vrednosti (fazifikacija), evaluira postavljen set pravila, a zatim defazifikuje rezultate kako bi se donele jasne (crisp) odluke o parametrima ponašanja agenta.

### Ulazi (Fuzzy promenljive)
Sistem se oslanja na 5 ulaznih promenljivih koje opisuju šta agent trenutno opaža u okruženju:
- **Vizuelna:** *nejasna | delimična | jasna* (Zavisi od udaljenosti i da li je igrač u zaklonu)
- **Zvuk:** *tišina | šum | pucanj* (Zavisi od brzine/kretanja igrača i akcije pucanja)
- **Pokrivenost:** *retka | srednja | gusta* (Koliko je igrač efikasno skriven u žbunju)
- **Detekcija:** *niska | srednja | visoka*
- **Ugao:** *ispred | bok | iza* (Smer i ugao pod kojim se igrač nalazi u odnosu na vizuelni konus agenta)

### Izlazi (Odluke i ponašanje)
Na osnovu ulaza, agent generiše sledeće izlaze primenom definisanih fuzzy pravila:
- **Angažovanje:** *ignoriši | traži | označi*
- **Brzina:** *patrolna | oprezna | fokusirana*
- **Upornost:** *kratkotrajna | zadržana | uporna*

Na bazi agregacije ovih izlaznih vrednosti donosi se konačna odluka o aktivnom **stanju** agenta: `MIRNO` 🟢, `UPOZORENJE` 🟡 ili `POTVRĐENO` 🔴.

## Arhitektura koda

Projekat je strukturisan na sledeći način:

- `fazi/` - Ovde je implementiran kompletan Fuzzy Inference System (FIS).
  - `skupovi.py`: Definisan univerzum diskursa i funkcije pripadnosti (membership functions - trougaone i trapezoidne krive).
  - `pravila.py`: Baza fuzzy pravila preklapanja stanja oslanjajući se na minimum (T-norme) i maksimume (S-norme).
  - `zakljucivanje.py`: Modul koji povezuje sve korake (od fazifikacije preko aktivacije do defazifikacije).
  - `defazifikacija.py`: Upotrebljeni *Centroid* metod za pretvaranje mekih (fuzzy) vrednosti nazad u realne brojeve prepoznatljive Pygame kodu.
- `agent/` - Modul koji spaja izlaze iz fuzzy sistema sa samim entitetom agenta, upravlja njegovim stanjem i tranzicijama (`nadzornik.py` i `stanja.py`).
- `igra/` - Pygame vizuelna simulacija napravljena da generiše ulaze agentu, kako bi demonstrirala vizuelnu promenu parametara uživo i učinila testiranje sistema preglednim.
- `main.py` - Glavna skripta za inicijalizaciju i instanciranje rada simulacije.

## Pokretanje projekta

Da biste pokrenuli sistem, potrebno je preuzeti odgovarajuće Python pakete koji podržavaju scikit-fuzzy logiku i pygame okruženje.

### Instalacija biblioteka
Sve neophodne biblioteke navedene su u fajlu `potrebne biblioteke.txt`. Možete ih brzo instalirati pokretanjem komande:

```bash
pip install scikit-fuzzy numpy scipy pygame
```

### Startovanje simulacije
Nakon uspešne instalacije svih paketa, okruženje pokrećete kroz *main* fajl:

```bash
python main.py
```

### Kontrole unutar okruženja
Igra služi kao laboratorija u kojoj generišete šum i otkrivate se iz zaklona kako biste videli kako rad fuzzy mašine transformiše te ulaze u reakciju:
- **W, A, S, D** ili **Strelice na tastaturi**: Kretanje igrača (koje pravi zvukove/šumove i privlači pažnju na malom dometu).
- **Q**: Pucanj pištoljem (stvara maksimalni trenutni nivo zvuka i momentalno aktivira visoko angažovanje agenta).
- Koristite **žbunje (prepreke)** kako biste testirali `pokrivenost` sistem. Ako se tu krijete, agentu će biti teže da vas vizuelno primeti.

U **HUD interfejsu (sa leve strane)** možete uživo vizuelno ispratiti trenutne (fazifikovane) nivoe senzornih ulaza i način sa kojim reaguju na njih sami izlazi i trenutno stanje.

---
*Ovaj demonstracioni komad uspešno pokazuje zašto se implementacije mekog računarstva (Soft Computing) ponašaju prirodnije i "pametnije" od tradicionalnih tvrdih grananja sa `if-else` petljama prilikom postojanja nesigurnosti i dvosmislenosti u procenama.*
