"""
Kompas: lista zadań, mapa myśli i timer Pomodoro w jednym programie.

Wymaga biblioteki CustomTkinter:  pip install customtkinter
Dane zapisują się automatycznie w pliku kompas.json obok tego programu.
"""

import json
import math
import time
import uuid
from datetime import date
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont

import customtkinter as ctk

# ======================= USTAWIENIA I KOLORY =======================

PLIK_DANYCH = Path(__file__).with_name("kompas.json")

# Każdy kolor to para: (jasny motyw, ciemny motyw)
AKCENT = ("#2E6B58", "#3F9A7C")
AKCENT_HOVER = ("#245646", "#32806A")
TLO = ("#EDF1EE", "#111815")
PANEL = ("#FFFFFF", "#19221E")
TEKST = ("#1C2A25", "#E3EBE6")
SZARY = ("#5C6E67", "#93A59D")
LINIA = ("#C8D3CD", "#2E3B36")
GALEZIE = {
    1: ("#2E6B58", "#6CC2A4"),  # zielony
    2: ("#C97F12", "#F0B252"),  # bursztynowy
    3: ("#4F63C4", "#93A3F2"),  # niebieski
    4: ("#B4483A", "#E58474"),  # czerwony
}
PRIORYTETY = {1: "Niski", 2: "Średni", 3: "Wysoki"}
KOLOR_PRIORYTETU = {1: SZARY, 2: GALEZIE[3], 3: GALEZIE[2]}

TRYBY = {
    "praca": {"minuty": 25, "nazwa": "Praca", "kolor": AKCENT},
    "przerwa": {"minuty": 5, "nazwa": "Przerwa", "kolor": GALEZIE[2]},
    "dluga": {"minuty": 15, "nazwa": "Długa przerwa", "kolor": GALEZIE[3]},
}


def kolor(para):
    """Zwykły tk.Canvas nie rozumie par kolorów, więc wybieramy jeden według motywu."""
    return para[1] if ctk.get_appearance_mode() == "Dark" else para[0]


def nowe_id():
    return uuid.uuid4().hex[:8]


def dzisiaj():
    return str(date.today())


# ======================= DANE: WCZYTYWANIE I ZAPIS =======================

def domyslne_dane():
    return {
        "widok": "zadania",
        "filtr": "Wszystkie",
        "zadania": [
            {"id": nowe_id(), "tekst": "Przeczytać o pętlach w Pythonie", "prio": 3, "zrobione": False},
            {"id": nowe_id(), "tekst": "Rozpisać pomysły na mapie myśli", "prio": 2, "zrobione": False},
            {"id": nowe_id(), "tekst": "Zainstalować Pythona i VS Code", "prio": 2, "zrobione": True},
            {"id": nowe_id(), "tekst": "Kupić kawę", "prio": 1, "zrobione": False},
        ],
        "mapa": {
            "wybrany": "root",
            "wezly": [
                {"id": "root", "tekst": "Nauka programowania", "x": 500, "y": 300, "rodzic": None, "k": 1,
                 "notatka": "Przykładowa mapa. Zmień ją po swojemu."},
                {"id": "a", "tekst": "Python", "x": 260, "y": 175, "rodzic": "root", "k": 1, "notatka": ""},
                {"id": "a1", "tekst": "Zmienne i pętle", "x": 115, "y": 75, "rodzic": "a", "k": 1, "notatka": ""},
                {"id": "a2", "tekst": "Funkcje", "x": 100, "y": 265, "rodzic": "a", "k": 1, "notatka": ""},
                {"id": "b", "tekst": "Projekty", "x": 745, "y": 175, "rodzic": "root", "k": 2,
                 "notatka": "Najlepiej uczyć się na własnych programach."},
                {"id": "b1", "tekst": "Lista zadań", "x": 890, "y": 75, "rodzic": "b", "k": 2, "notatka": ""},
                {"id": "b2", "tekst": "Gra w zgadywanie", "x": 880, "y": 265, "rodzic": "b", "k": 2, "notatka": ""},
                {"id": "c", "tekst": "Zasoby", "x": 745, "y": 440, "rodzic": "root", "k": 3, "notatka": ""},
                {"id": "d", "tekst": "Nawyki", "x": 260, "y": 440, "rodzic": "root", "k": 4, "notatka": ""},
                {"id": "d1", "tekst": "30 minut dziennie", "x": 130, "y": 540, "rodzic": "d", "k": 4, "notatka": ""},
            ],
        },
        "pomodoro": {"zadanie": "", "data": dzisiaj(), "sesje": 0},
    }


def wczytaj_dane():
    try:
        with open(PLIK_DANYCH, encoding="utf-8") as f:
            dane = json.load(f)
        baza = domyslne_dane()
        baza.update(dane)
        return baza
    except (OSError, json.JSONDecodeError):
        return domyslne_dane()


# ======================= GŁÓWNE OKNO =======================

class Kompas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kompas")
        self.geometry("1200x760")
        self.minsize(960, 640)
        self.configure(fg_color=TLO)

        self.dane = wczytaj_dane()
        if self.dane["pomodoro"]["data"] != dzisiaj():
            self.dane["pomodoro"].update(data=dzisiaj(), sesje=0)

        # Czcionki
        self.f_logo = ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        self.f_tytul = ctk.CTkFont(family="Segoe UI", size=30, weight="bold")
        self.f_zwykla = ctk.CTkFont(family="Segoe UI", size=14)
        self.f_mala = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        self.f_gruba = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.f_przekreslona = ctk.CTkFont(family="Segoe UI", size=14, overstrike=True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.zbuduj_menu()
        self.widoki = {
            "zadania": WidokZadan(self, self),
            "mapa": WidokMapy(self, self),
            "skupienie": WidokSkupienia(self, self),
        }
        for widok in self.widoki.values():
            widok.grid(row=0, column=1, sticky="nsew", padx=32, pady=26)
            widok.grid_remove()

        self.odswiez_wszystko()
        self.pokaz(self.dane.get("widok", "zadania"))
        self.protocol("WM_DELETE_WINDOW", self.zamknij)

    # ---------- menu boczne ----------
    def zbuduj_menu(self):
        menu = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=PANEL)
        menu.grid(row=0, column=0, sticky="ns")
        menu.grid_propagate(False)

        ctk.CTkLabel(menu, text="◆ Kompas", font=self.f_logo, text_color=AKCENT).pack(
            anchor="w", padx=22, pady=(28, 24))

        self.przyciski_menu = {}
        for klucz, nazwa in [("zadania", "Zadania"), ("mapa", "Mapa myśli"), ("skupienie", "Skupienie")]:
            b = ctk.CTkButton(menu, text=nazwa, anchor="w", height=40, corner_radius=8,
                              font=self.f_zwykla, fg_color="transparent", text_color=TEKST,
                              hover_color=LINIA, command=lambda k=klucz: self.pokaz(k))
            b.pack(fill="x", padx=12, pady=3)
            self.przyciski_menu[klucz] = (b, nazwa)

        ctk.CTkLabel(menu, text="Dane zapisują się\nw pliku kompas.json", justify="left",
                     text_color=SZARY, font=ctk.CTkFont(size=12)).pack(side="bottom", anchor="w", padx=22, pady=20)

    def pokaz(self, klucz):
        self.dane["widok"] = klucz
        for k, widok in self.widoki.items():
            if k == klucz:
                widok.grid()
            else:
                widok.grid_remove()
        for k, (b, _) in self.przyciski_menu.items():
            aktywny = k == klucz
            b.configure(fg_color=AKCENT if aktywny else "transparent",
                        text_color=("#FFFFFF", "#FFFFFF") if aktywny else TEKST,
                        hover_color=AKCENT_HOVER if aktywny else LINIA)
        if klucz == "mapa":
            self.widoki["mapa"].rysuj()
        self.zapisz()

    def odswiez_liczniki(self):
        liczby = {
            "zadania": sum(not z["zrobione"] for z in self.dane["zadania"]),
            "mapa": len(self.dane["mapa"]["wezly"]),
            "skupienie": self.dane["pomodoro"]["sesje"],
        }
        for k, (b, nazwa) in self.przyciski_menu.items():
            b.configure(text=f"{nazwa}   ·   {liczby[k]}")

    def odswiez_wszystko(self):
        self.widoki["zadania"].odswiez()
        self.widoki["skupienie"].odswiez_liste_zadan()
        self.odswiez_liczniki()

    # ---------- zapis ----------
    def zapisz(self):
        try:
            with open(PLIK_DANYCH, "w", encoding="utf-8") as f:
                json.dump(self.dane, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print("Nie udało się zapisać danych:", e)

    def zamknij(self):
        self.zapisz()
        self.destroy()


# ======================= WIDOK: ZADANIA =======================

class WidokZadan(ctk.CTkFrame):
    FILTRY = ["Wszystkie", "Do zrobienia", "Zrobione"]

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Zadania", font=app.f_tytul, text_color=TEKST).pack(anchor="w")
        self.podsumowanie = ctk.CTkLabel(self, text="", text_color=SZARY, font=app.f_zwykla)
        self.podsumowanie.pack(anchor="w")
        self.pasek = ctk.CTkProgressBar(self, height=8, progress_color=AKCENT, fg_color=LINIA)
        self.pasek.pack(fill="x", pady=(10, 18))

        # Formularz dodawania
        formularz = ctk.CTkFrame(self, fg_color="transparent")
        formularz.pack(fill="x")
        self.pole = ctk.CTkEntry(formularz, placeholder_text="Co jest do zrobienia?", height=40, font=app.f_zwykla)
        self.pole.pack(side="left", fill="x", expand=True)
        self.pole.bind("<Return>", lambda e: self.dodaj())
        self.priorytet = ctk.CTkOptionMenu(formularz, values=list(PRIORYTETY.values()), width=120, height=40,
                                           fg_color=AKCENT, button_color=AKCENT_HOVER,
                                           button_hover_color=AKCENT_HOVER)
        self.priorytet.set("Średni")
        self.priorytet.pack(side="left", padx=8)
        ctk.CTkButton(formularz, text="Dodaj", width=100, height=40, fg_color=AKCENT, hover_color=AKCENT_HOVER,
                      font=app.f_gruba, command=self.dodaj).pack(side="left")

        # Filtry
        self.filtr = ctk.CTkSegmentedButton(self, values=self.FILTRY, command=self.zmien_filtr,
                                            selected_color=AKCENT, selected_hover_color=AKCENT_HOVER)
        self.filtr.set(app.dane.get("filtr", "Wszystkie"))
        self.filtr.pack(anchor="w", pady=(18, 10))

        self.lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista.pack(fill="both", expand=True)

    def dodaj(self):
        tekst = self.pole.get().strip()
        if not tekst:
            return
        prio = next(k for k, v in PRIORYTETY.items() if v == self.priorytet.get())
        self.app.dane["zadania"].append({"id": nowe_id(), "tekst": tekst, "prio": prio, "zrobione": False})
        self.pole.delete(0, "end")
        self.app.zapisz()
        self.app.odswiez_wszystko()

    def zmien_filtr(self, wartosc):
        self.app.dane["filtr"] = wartosc
        self.app.zapisz()
        self.odswiez()

    def przelacz(self, zadanie, wartosc):
        zadanie["zrobione"] = bool(wartosc)
        self.app.zapisz()
        self.app.odswiez_wszystko()

    def usun(self, zadanie):
        self.app.dane["zadania"].remove(zadanie)
        if self.app.dane["pomodoro"]["zadanie"] == zadanie["id"]:
            self.app.dane["pomodoro"]["zadanie"] = ""
        self.app.zapisz()
        self.app.odswiez_wszystko()

    def skup_sie(self, zadanie):
        self.app.dane["pomodoro"]["zadanie"] = zadanie["id"]
        self.app.widoki["skupienie"].odswiez_liste_zadan()
        self.app.pokaz("skupienie")

    def odswiez(self):
        for dziecko in self.lista.winfo_children():
            dziecko.destroy()

        zadania = self.app.dane["zadania"]
        # Najpierw niezrobione, w środku od najwyższego priorytetu
        widoczne = sorted(zadania, key=lambda z: (z["zrobione"], -z["prio"]))
        filtr = self.app.dane.get("filtr", "Wszystkie")
        if filtr == "Do zrobienia":
            widoczne = [z for z in widoczne if not z["zrobione"]]
        elif filtr == "Zrobione":
            widoczne = [z for z in widoczne if z["zrobione"]]

        for z in widoczne:
            wiersz = ctk.CTkFrame(self.lista, fg_color=PANEL, corner_radius=10, border_width=1, border_color=LINIA)
            wiersz.pack(fill="x", pady=4)

            zmienna = ctk.IntVar(value=int(z["zrobione"]))
            ctk.CTkCheckBox(wiersz, text=z["tekst"], variable=zmienna, onvalue=1, offvalue=0,
                            fg_color=AKCENT, hover_color=AKCENT_HOVER,
                            font=self.app.f_przekreslona if z["zrobione"] else self.app.f_zwykla,
                            text_color=SZARY if z["zrobione"] else TEKST,
                            command=lambda z=z, v=zmienna: self.przelacz(z, v.get())
                            ).pack(side="left", padx=14, pady=12, fill="x", expand=True)

            ctk.CTkButton(wiersz, text="✕", width=32, height=28, fg_color="transparent", text_color=SZARY,
                          hover_color=LINIA, command=lambda z=z: self.usun(z)).pack(side="right", padx=(0, 10))
            if not z["zrobione"]:
                ctk.CTkButton(wiersz, text="Skup się", width=80, height=28, fg_color="transparent",
                              text_color=SZARY, hover_color=LINIA,
                              command=lambda z=z: self.skup_sie(z)).pack(side="right")
            ctk.CTkLabel(wiersz, text=PRIORYTETY[z["prio"]], font=self.app.f_gruba,
                         text_color=KOLOR_PRIORYTETU[z["prio"]]).pack(side="right", padx=10)

        if not widoczne:
            ctk.CTkLabel(self.lista, text="Nic tu nie ma. Dodaj zadanie w polu powyżej.",
                         text_color=SZARY).pack(pady=30)

        zrobione = sum(z["zrobione"] for z in zadania)
        self.podsumowanie.configure(text=f"Do zrobienia: {len(zadania) - zrobione}  ·  Zrobione: {zrobione}")
        self.pasek.set(zrobione / len(zadania) if zadania else 0)


# ======================= WIDOK: MAPA MYŚLI =======================

class WidokMapy(ctk.CTkFrame):
    SZER, WYS = 1000, 600  # "świat" mapy; rysunek skaluje się do rozmiaru okna

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.przeciagany = None
        self.rozmiary = {}
        self.skala, self.ox, self.oy = 1, 0, 0
        self.czcionka = tkfont.Font(family="Segoe UI", size=11)
        self.czcionka_gl = tkfont.Font(family="Segoe UI", size=13, weight="bold")

        ctk.CTkLabel(self, text="Mapa myśli", font=app.f_tytul, text_color=TEKST).pack(anchor="w")
        ctk.CTkLabel(self, text="Kliknij pomysł, żeby go wybrać i edytować. Przeciągnij go myszką, żeby przesunąć.",
                     text_color=SZARY, font=app.f_zwykla).pack(anchor="w", pady=(0, 14))

        # Pasek narzędzi
        pasek = ctk.CTkFrame(self, fg_color="transparent")
        pasek.pack(fill="x", pady=(0, 10))
        self.pole = ctk.CTkEntry(pasek, height=38, font=app.f_zwykla)
        self.pole.pack(side="left", fill="x", expand=True)
        self.pole.bind("<KeyRelease>", self.zmien_tekst)

        self.kolory = {}
        for k, para in GALEZIE.items():
            b = ctk.CTkButton(pasek, text="", width=28, height=28, corner_radius=14, fg_color=para,
                              hover_color=para, border_width=0, border_color=TEKST,
                              command=lambda k=k: self.zmien_kolor(k))
            b.pack(side="left", padx=3)
            self.kolory[k] = b

        ctk.CTkButton(pasek, text="+ Dodaj gałąź", height=38, fg_color=AKCENT, hover_color=AKCENT_HOVER,
                      font=app.f_gruba, command=self.dodaj).pack(side="left", padx=(10, 6))
        self.przycisk_usun = ctk.CTkButton(pasek, text="Usuń", width=80, height=38, fg_color="transparent",
                                           border_width=1, border_color=LINIA, text_color=TEKST,
                                           hover_color=LINIA, command=self.usun)
        self.przycisk_usun.pack(side="left")

        # Płótno
        ramka = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=12, border_width=1, border_color=LINIA)
        ramka.pack(fill="both", expand=True)
        self.plotno = tk.Canvas(ramka, highlightthickness=0, bg=kolor(PANEL))
        self.plotno.pack(fill="both", expand=True, padx=6, pady=6)
        self.plotno.bind("<Configure>", lambda e: self.rysuj())
        self.plotno.bind("<ButtonPress-1>", self.nacisniecie)
        self.plotno.bind("<B1-Motion>", self.ruch)
        self.plotno.bind("<ButtonRelease-1>", self.puszczenie)

        # Notatka
        ctk.CTkLabel(self, text="NOTATKA DO WYBRANEGO POMYSŁU", font=app.f_mala, text_color=SZARY).pack(
            anchor="w", pady=(12, 4))
        self.notatka = ctk.CTkTextbox(self, height=90, font=app.f_zwykla, border_width=1, border_color=LINIA)
        self.notatka.pack(fill="x")
        self.notatka.bind("<KeyRelease>", self.zmien_notatke)

        self.synchronizuj_edytor()

    # ---------- pomocnicze ----------
    @property
    def mapa(self):
        return self.app.dane["mapa"]

    def wezel(self, wid):
        return next((w for w in self.mapa["wezly"] if w["id"] == wid), None)

    def dzieci(self, wid):
        return [w for w in self.mapa["wezly"] if w["rodzic"] == wid]

    def na_ekran(self, x, y):
        return self.ox + x * self.skala, self.oy + y * self.skala

    def na_swiat(self, px, py):
        return (px - self.ox) / self.skala, (py - self.oy) / self.skala

    def zaokraglony(self, x1, y1, x2, y2, r, **opcje):
        punkty = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
                  x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.plotno.create_polygon(punkty, smooth=True, **opcje)

    # ---------- rysowanie ----------
    def rysuj(self):
        c = self.plotno
        c.delete("all")
        c.configure(bg=kolor(PANEL))
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10 or h < 10:
            return
        self.skala = min(w / self.SZER, h / self.WYS)
        self.ox = (w - self.SZER * self.skala) / 2
        self.oy = (h - self.WYS * self.skala) / 2

        # 1) Linie: krzywa Béziera przybliżona punktami
        for n in self.mapa["wezly"]:
            if not n["rodzic"]:
                continue
            p = self.wezel(n["rodzic"])
            x1, y1 = self.na_ekran(p["x"], p["y"])
            x2, y2 = self.na_ekran(n["x"], n["y"])
            sx = (x1 + x2) / 2
            punkty = []
            for i in range(21):
                t = i / 20
                u = 1 - t
                bx = u**3 * x1 + 3 * u**2 * t * sx + 3 * u * t**2 * sx + t**3 * x2
                by = u**3 * y1 + 3 * u**2 * t * y1 + 3 * u * t**2 * y2 + t**3 * y2
                punkty += [bx, by]
            c.create_line(punkty, fill=kolor(GALEZIE[n["k"]]), width=4 if not p["rodzic"] else 2.5,
                          capstyle="round", smooth=True)

        # 2) Węzły
        for n in self.mapa["wezly"]:
            glowny = not n["rodzic"]
            czc = self.czcionka_gl if glowny else self.czcionka
            szer = czc.measure(n["tekst"] or "…") + 36
            wys = 46 if glowny else 34
            self.rozmiary[n["id"]] = (szer, wys)
            x, y = self.na_ekran(n["x"], n["y"])
            kol = kolor(GALEZIE[n["k"]])

            if n["id"] == self.mapa["wybrany"]:
                self.zaokraglony(x - szer / 2 - 6, y - wys / 2 - 6, x + szer / 2 + 6, y + wys / 2 + 6,
                                 wys / 2 + 6, fill="", outline=kolor(TEKST), dash=(4, 3), width=1.5)
            self.zaokraglony(x - szer / 2, y - wys / 2, x + szer / 2, y + wys / 2, wys / 2,
                             fill=kol if glowny else kolor(PANEL), outline=kol, width=2.5)
            c.create_text(x, y, text=n["tekst"] or "…", font=czc,
                          fill=kolor(PANEL) if glowny else kolor(TEKST))

    # ---------- mysz ----------
    def trafiony(self, px, py):
        for n in reversed(self.mapa["wezly"]):
            szer, wys = self.rozmiary.get(n["id"], (0, 0))
            x, y = self.na_ekran(n["x"], n["y"])
            if abs(px - x) <= szer / 2 and abs(py - y) <= wys / 2:
                return n
        return None

    def nacisniecie(self, e):
        n = self.trafiony(e.x, e.y)
        if not n:
            return
        sx, sy = self.na_swiat(e.x, e.y)
        self.przeciagany = (n, sx - n["x"], sy - n["y"])
        self.mapa["wybrany"] = n["id"]
        self.synchronizuj_edytor()
        self.rysuj()

    def ruch(self, e):
        if not self.przeciagany:
            return
        n, dx, dy = self.przeciagany
        sx, sy = self.na_swiat(e.x, e.y)
        n["x"] = max(50, min(self.SZER - 50, sx - dx))
        n["y"] = max(25, min(self.WYS - 25, sy - dy))
        self.rysuj()

    def puszczenie(self, e):
        if self.przeciagany:
            self.przeciagany = None
            self.app.zapisz()

    # ---------- edycja ----------
    def synchronizuj_edytor(self):
        n = self.wezel(self.mapa["wybrany"]) or self.wezel("root")
        self.mapa["wybrany"] = n["id"]
        self.pole.delete(0, "end")
        self.pole.insert(0, n["tekst"])
        self.notatka.delete("1.0", "end")
        self.notatka.insert("1.0", n.get("notatka", ""))
        self.przycisk_usun.configure(state="normal" if n["rodzic"] else "disabled")
        for k, b in self.kolory.items():
            b.configure(border_width=3 if k == n["k"] else 0)

    def zmien_tekst(self, e=None):
        self.wezel(self.mapa["wybrany"])["tekst"] = self.pole.get()[:40]
        self.rysuj()
        self.app.zapisz()

    def zmien_notatke(self, e=None):
        self.wezel(self.mapa["wybrany"])["notatka"] = self.notatka.get("1.0", "end-1c")
        self.app.zapisz()

    def zmien_kolor(self, k):
        def maluj(wid):
            self.wezel(wid)["k"] = k
            for d in self.dzieci(wid):
                maluj(d["id"])
        maluj(self.mapa["wybrany"])
        self.synchronizuj_edytor()
        self.rysuj()
        self.app.zapisz()

    def dodaj(self):
        p = self.wezel(self.mapa["wybrany"])
        ile = len(self.dzieci(p["id"]))
        # Nowe gałęzie rozchodzą się wachlarzem, z dala od rodzica
        if p["rodzic"]:
            r = self.wezel(p["rodzic"])
            baza, rozrzut, odl = math.atan2(p["y"] - r["y"], p["x"] - r["x"]), 0.55, 150
        else:
            baza, rozrzut, odl = -math.pi / 2, 1.1, 210
        kat = baza + (1 if ile % 2 else -1) * math.ceil(ile / 2) * rozrzut
        nowy = {
            "id": nowe_id(), "tekst": "Nowy pomysł", "rodzic": p["id"], "notatka": "",
            "k": p["k"] if p["rodzic"] else ile % 4 + 1,
            "x": max(60, min(self.SZER - 60, p["x"] + math.cos(kat) * odl)),
            "y": max(30, min(self.WYS - 30, p["y"] + math.sin(kat) * odl * 0.8)),
        }
        self.mapa["wezly"].append(nowy)
        self.mapa["wybrany"] = nowy["id"]
        self.synchronizuj_edytor()
        self.rysuj()
        self.app.odswiez_liczniki()
        self.app.zapisz()
        self.pole.focus()
        self.pole.select_range(0, "end")

    def usun(self):
        n = self.wezel(self.mapa["wybrany"])
        if not n["rodzic"]:
            return
        do_usuniecia = set()

        def zbierz(wid):
            do_usuniecia.add(wid)
            for d in self.dzieci(wid):
                zbierz(d["id"])
        zbierz(n["id"])
        self.mapa["wezly"] = [w for w in self.mapa["wezly"] if w["id"] not in do_usuniecia]
        self.mapa["wybrany"] = n["rodzic"]
        self.synchronizuj_edytor()
        self.rysuj()
        self.app.odswiez_liczniki()
        self.app.zapisz()


# ======================= WIDOK: SKUPIENIE (POMODORO) =======================

class WidokSkupienia(ctk.CTkFrame):
    BEZ_ZADANIA = "— bez konkretnego zadania —"

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.tryb = "praca"
        self.zostalo = TRYBY["praca"]["minuty"] * 60
        self.dziala = False
        self.koniec = 0
        self.id_after = None
        self.id_zadan = []

        ctk.CTkLabel(self, text="Skupienie", font=app.f_tytul, text_color=TEKST).pack(anchor="w")
        ctk.CTkLabel(self, text="Technika Pomodoro: 25 minut pracy bez rozpraszaczy, potem 5 minut przerwy. "
                                "Co czwarta przerwa jest dłuższa.",
                     text_color=SZARY, font=app.f_zwykla, wraplength=700, justify="left").pack(anchor="w", pady=(0, 20))

        uklad = ctk.CTkFrame(self, fg_color="transparent")
        uklad.pack(fill="both", expand=True)

        # Lewa kolumna: tarcza
        lewa = ctk.CTkFrame(uklad, fg_color="transparent")
        lewa.pack(side="left", anchor="n")
        self.tryby = ctk.CTkSegmentedButton(lewa, values=[t["nazwa"] for t in TRYBY.values()],
                                            command=self.wybierz_tryb, selected_color=AKCENT,
                                            selected_hover_color=AKCENT_HOVER)
        self.tryby.pack(fill="x", pady=(0, 16))
        self.tarcza = tk.Canvas(lewa, width=300, height=300, highlightthickness=0, bg=kolor(TLO))
        self.tarcza.pack()
        przyciski = ctk.CTkFrame(lewa, fg_color="transparent")
        przyciski.pack(pady=16)
        self.przycisk_start = ctk.CTkButton(przyciski, text="Start", width=120, height=40, fg_color=AKCENT,
                                            hover_color=AKCENT_HOVER, font=app.f_gruba, command=self.start_pauza)
        self.przycisk_start.pack(side="left", padx=5)
        ctk.CTkButton(przyciski, text="Od nowa", width=120, height=40, fg_color="transparent", border_width=1,
                      border_color=LINIA, text_color=TEKST, hover_color=LINIA,
                      command=lambda: self.ustaw_tryb(self.tryb)).pack(side="left", padx=5)

        # Prawa kolumna: zadanie i statystyki
        prawa = ctk.CTkFrame(uklad, fg_color="transparent")
        prawa.pack(side="left", fill="both", expand=True, padx=(48, 0), anchor="n")
        ctk.CTkLabel(prawa, text="NAD CZYM PRACUJESZ?", font=app.f_mala, text_color=SZARY).pack(anchor="w")
        self.wybor_zadania = ctk.CTkOptionMenu(prawa, values=[self.BEZ_ZADANIA], height=38, dynamic_resizing=False,
                                               width=360, fg_color=AKCENT, button_color=AKCENT_HOVER,
                                               button_hover_color=AKCENT_HOVER, command=self.wybierz_zadanie)
        self.wybor_zadania.pack(anchor="w", pady=(4, 28))

        ctk.CTkLabel(prawa, text="DZISIAJ", font=app.f_mala, text_color=SZARY).pack(anchor="w")
        self.licznik = ctk.CTkLabel(prawa, text="0", font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
                                    text_color=TEKST)
        self.licznik.pack(anchor="w")
        ctk.CTkLabel(prawa, text="ukończonych sesji pracy (cel: 8)", text_color=SZARY,
                     font=app.f_zwykla).pack(anchor="w")
        self.kropki = tk.Canvas(prawa, width=340, height=30, highlightthickness=0, bg=kolor(TLO))
        self.kropki.pack(anchor="w", pady=10)

        self.ustaw_tryb("praca")

    # ---------- lista zadań do wyboru ----------
    def odswiez_liste_zadan(self):
        otwarte = [z for z in self.app.dane["zadania"] if not z["zrobione"]]
        self.id_zadan = [""] + [z["id"] for z in otwarte]
        wartosci = [self.BEZ_ZADANIA] + [z["tekst"] for z in otwarte]
        self.wybor_zadania.configure(values=wartosci)
        wybrane = self.app.dane["pomodoro"]["zadanie"]
        if wybrane not in self.id_zadan:
            wybrane = self.app.dane["pomodoro"]["zadanie"] = ""
        self.wybor_zadania.set(wartosci[self.id_zadan.index(wybrane)])

    def wybierz_zadanie(self, wartosc):
        wartosci = self.wybor_zadania.cget("values")
        self.app.dane["pomodoro"]["zadanie"] = self.id_zadan[wartosci.index(wartosc)]
        self.app.zapisz()

    # ---------- timer ----------
    def wybierz_tryb(self, nazwa):
        klucz = next(k for k, t in TRYBY.items() if t["nazwa"] == nazwa)
        self.ustaw_tryb(klucz)

    def ustaw_tryb(self, klucz):
        self.zatrzymaj()
        self.tryb = klucz
        self.zostalo = TRYBY[klucz]["minuty"] * 60
        self.tryby.set(TRYBY[klucz]["nazwa"])
        self.odswiez_tarcze()

    def start_pauza(self):
        if self.dziala:
            self.zatrzymaj()
        else:
            self.dziala = True
            self.koniec = time.time() + self.zostalo
            self.tik()
        self.odswiez_tarcze()

    def zatrzymaj(self):
        self.dziala = False
        if self.id_after:
            self.after_cancel(self.id_after)
            self.id_after = None

    def tik(self):
        self.zostalo = max(0, round(self.koniec - time.time()))
        if self.zostalo == 0:
            self.zakoncz()
            return
        self.odswiez_tarcze()
        self.id_after = self.after(250, self.tik)

    def zakoncz(self):
        self.zatrzymaj()
        self.dzwiek()
        # Wyciągnij okno na wierzch, żeby było widać koniec sesji
        self.app.deiconify()
        self.app.lift()
        if self.tryb == "praca":
            self.app.dane["pomodoro"]["sesje"] += 1
            self.app.zapisz()
            self.app.odswiez_liczniki()
            self.ustaw_tryb("dluga" if self.app.dane["pomodoro"]["sesje"] % 4 == 0 else "przerwa")
        else:
            self.ustaw_tryb("praca")

    def dzwiek(self):
        try:
            import winsound  # dostępne tylko na Windowsie
            winsound.Beep(660, 300)
            winsound.Beep(880, 400)
        except (ImportError, RuntimeError):
            self.bell()

    # ---------- rysowanie tarczy ----------
    def odswiez_tarcze(self):
        c = self.tarcza
        c.delete("all")
        c.configure(bg=kolor(TLO))
        calosc = TRYBY[self.tryb]["minuty"] * 60
        ulamek = self.zostalo / calosc
        m, s = divmod(self.zostalo, 60)

        c.create_oval(20, 20, 280, 280, outline=kolor(LINIA), width=14)
        if ulamek > 0:
            c.create_arc(20, 20, 280, 280, start=90, extent=-359.9 * ulamek, style="arc",
                         outline=kolor(TRYBY[self.tryb]["kolor"]), width=14)
        c.create_text(150, 140, text=f"{m:02d}:{s:02d}", font=("Consolas", 46, "bold"), fill=kolor(TEKST))
        opis = TRYBY[self.tryb]["nazwa"].upper() + ("" if self.dziala else "  ·  PAUZA")
        c.create_text(150, 190, text=opis, font=("Segoe UI", 10, "bold"), fill=kolor(SZARY))

        if self.dziala:
            self.przycisk_start.configure(text="Pauza")
            self.app.title(f"{m:02d}:{s:02d} · Kompas")
        else:
            self.przycisk_start.configure(text="Wznów" if self.zostalo < calosc else "Start")
            self.app.title("Kompas")

        # Licznik i kropki
        sesje = self.app.dane["pomodoro"]["sesje"]
        self.licznik.configure(text=str(sesje))
        k = self.kropki
        k.delete("all")
        k.configure(bg=kolor(TLO))
        for i in range(max(8, sesje)):
            x = 4 + i * 24
            if i < sesje:
                k.create_oval(x, 6, x + 16, 22, fill=kolor(GALEZIE[2]), outline="")
            else:
                k.create_oval(x, 6, x + 16, 22, outline=kolor(LINIA), width=2, dash=(3, 2))


# ======================= START PROGRAMU =======================

if __name__ == "__main__":
    ctk.set_appearance_mode("system")  # jasny lub ciemny, tak jak w Windowsie
    aplikacja = Kompas()
    aplikacja.mainloop()
