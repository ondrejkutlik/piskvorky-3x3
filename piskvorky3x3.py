"""Piškvorky 3 × 3 – grafická verzia (tkinter).

Python prepis webovej hry piskvorky3x3.html.
Dvaja hráči alebo proti jednoduchému počítaču.
Spustenie:  python piskvorky3x3.py
"""

import random
import tkinter as tk

VYHERNE_RADY = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # riadky
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # stĺpce
    (0, 4, 8), (2, 4, 6),             # uhlopriečky
]

FARBY = {
    "bg": "#f2f4f7", "surface": "#ffffff", "ink": "#172033", "muted": "#5a6478",
    "cell": "#eef1f6", "cell_hover": "#e0e5ef", "x": "#1f4bd8", "o": "#d4572a",
    "win": "#cfeecf", "accent": "#1f4bd8", "accent_ink": "#ffffff",
}


def najdi_vyhru(d):
    for rad in VYHERNE_RADY:
        a, b, c = rad
        if d[a] and d[a] == d[b] == d[c]:
            return d[a], rad
    return None


def tah_pocitaca(doska):
    """Jednoduchá AI: 1. vyhraj, 2. zablokuj súpera, 3. stred, 4. náhodné políčko."""
    volne = [i for i, z in enumerate(doska) if not z]
    for znak in ("O", "X"):
        for i in volne:
            kopia = doska.copy()
            kopia[i] = znak
            vyhra = najdi_vyhru(kopia)
            if vyhra and vyhra[0] == znak:
                return i
    if 4 in volne:
        return 4
    return random.choice(volne)


class Piskvorky(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Piškvorky")
        self.resizable(False, False)
        self.configure(bg=FARBY["bg"], padx=16, pady=16)

        self.skore = {"X": 0, "O": 0, "remiza": 0}
        self.rezim = "dvaja"
        self.casovac = None

        ram = tk.Frame(self, bg=FARBY["surface"], padx=20, pady=16)
        ram.pack()

        tk.Label(ram, text="Piškvorky", bg=FARBY["surface"], fg=FARBY["ink"],
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))

        # Výber režimu
        rezimy = tk.Frame(ram, bg=FARBY["surface"])
        rezimy.pack(pady=(0, 10))
        self.tlacidla_rezimu = {}
        for kluc, popis in (("dvaja", "Dvaja hráči"), ("pocitac", "Proti počítaču")):
            t = tk.Button(rezimy, text=popis, bd=0, padx=12, pady=4, cursor="hand2",
                          font=("Segoe UI", 10), command=lambda k=kluc: self.zmen_rezim(k))
            t.pack(side="left", padx=3)
            self.tlacidla_rezimu[kluc] = t

        self.stav = tk.Label(ram, bg=FARBY["surface"], fg=FARBY["ink"],
                             font=("Segoe UI", 12, "bold"))
        self.stav.pack(pady=(0, 8))

        # Doska
        mriezka = tk.Frame(ram, bg=FARBY["surface"])
        mriezka.pack()
        self.policka = []
        for i in range(9):
            p = tk.Button(mriezka, text="", width=3, height=1, bd=0, relief="flat",
                          font=("Segoe UI", 36, "bold"), bg=FARBY["cell"],
                          activebackground=FARBY["cell_hover"], cursor="hand2",
                          command=lambda i=i: self.tah_hraca(i))
            p.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            self.policka.append(p)

        # Skóre
        self.skore_text = tk.Label(ram, bg=FARBY["surface"], fg=FARBY["muted"],
                                   font=("Segoe UI", 11))
        self.skore_text.pack(pady=10)

        tk.Button(ram, text="Nová hra", bd=0, padx=18, pady=6, cursor="hand2",
                  bg=FARBY["accent"], fg=FARBY["accent_ink"],
                  activebackground="#3a63e6", activeforeground=FARBY["accent_ink"],
                  font=("Segoe UI", 11, "bold"), command=self.nova_hra).pack()

        self.zmen_rezim("dvaja")

    # ---------- priebeh hry ----------
    def zmen_rezim(self, rezim):
        self.rezim = rezim
        for kluc, t in self.tlacidla_rezimu.items():
            aktivny = kluc == rezim
            t.config(bg=FARBY["accent"] if aktivny else FARBY["cell"],
                     fg=FARBY["accent_ink"] if aktivny else FARBY["muted"])
        self.skore = {"X": 0, "O": 0, "remiza": 0}
        self.aktualizuj_skore()
        self.nova_hra()

    def nova_hra(self):
        if self.casovac:
            self.after_cancel(self.casovac)
            self.casovac = None
        self.doska = [""] * 9
        self.na_tahu = "X"
        self.koniec = False
        self.blokovane = False
        self.vykresli()
        self.stav.config(text="Na ťahu: X")

    def vykresli(self, vyherny_rad=()):
        for i, p in enumerate(self.policka):
            znak = self.doska[i]
            p.config(
                text=znak,
                fg=FARBY["x"] if znak == "X" else FARBY["o"],
                disabledforeground=FARBY["x"] if znak == "X" else FARBY["o"],
                bg=FARBY["win"] if i in vyherny_rad else FARBY["cell"],
                state="disabled" if self.koniec or znak else "normal",
            )

    def zahraj(self, index):
        self.doska[index] = self.na_tahu
        vyhra = najdi_vyhru(self.doska)

        if vyhra:
            znak, rad = vyhra
            self.koniec = True
            self.skore[znak] += 1
            self.vykresli(rad)
            self.stav.config(text=f"Vyhráva {znak}! 🎉")
            self.aktualizuj_skore()
            return

        if all(self.doska):
            self.koniec = True
            self.skore["remiza"] += 1
            self.vykresli()
            self.stav.config(text="Remíza.")
            self.aktualizuj_skore()
            return

        self.na_tahu = "O" if self.na_tahu == "X" else "X"
        self.vykresli()
        self.stav.config(text=f"Na ťahu: {self.na_tahu}")

    def tah_hraca(self, index):
        if self.koniec or self.blokovane or self.doska[index]:
            return
        self.zahraj(index)

        if self.rezim == "pocitac" and not self.koniec:
            self.blokovane = True
            self.stav.config(text="Počítač premýšľa…")
            self.casovac = self.after(450, self.tah_pocitaca)

    def tah_pocitaca(self):
        self.casovac = None
        self.zahraj(tah_pocitaca(self.doska))
        self.blokovane = False

    def aktualizuj_skore(self):
        s = self.skore
        self.skore_text.config(text=f"X: {s['X']}      Remízy: {s['remiza']}      O: {s['O']}")


if __name__ == "__main__":
    Piskvorky().mainloop()
