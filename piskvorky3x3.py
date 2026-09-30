import random
import tkinter as tk

VYHERNE_RADY = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Riadky
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Stĺpce
    (0, 4, 8), (2, 4, 6),             # Uhlopriečky
]

FARBY = {
    "pozadie": "#f2f4f7", "panel": "#ffffff", "text": "#172033", "sive": "#5a6478",
    "policko": "#eef1f6", "policko_nad": "#e0e5ef", "x": "#1f4bd8", "o": "#d4572a",
    "vyhra": "#cfeecf", "akcent": "#1f4bd8", "akcent_nad": "#3a63e6", "akcent_text": "#ffffff",
}


def najdi_vyhru(d):
    for rad in VYHERNE_RADY:
        a, b, c = rad
        if d[a] and d[a] == d[b] == d[c]:
            return d[a], rad
    return None


# Počítač najprv skúsi vyhrať, potom zablokovať súpera, potom stred, inak náhodne
def tah_pocitaca(doska):
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
        self.configure(bg=FARBY["pozadie"], padx=16, pady=16)

        self.skore = {"X": 0, "O": 0, "remiza": 0}
        self.rezim = "dvaja"
        self.casovac = None

        ram = tk.Frame(self, bg=FARBY["panel"], padx=20, pady=16)
        ram.pack()

        tk.Label(ram, text="Piškvorky", bg=FARBY["panel"], fg=FARBY["text"],
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))

        # Výber režimu
        rezimy = tk.Frame(ram, bg=FARBY["panel"])
        rezimy.pack(pady=(0, 10))
        self.tlacidla_rezimu = {}
        for kluc, popis in (("dvaja", "Dvaja hráči"), ("pocitac", "Proti počítaču")):
            t = tk.Button(rezimy, text=popis, bd=0, padx=12, pady=4, cursor="hand2",
                          font=("Segoe UI", 10), command=lambda k=kluc: self.zmen_rezim(k))
            t.pack(side="left", padx=3)
            self.tlacidla_rezimu[kluc] = t

        self.stav = tk.Label(ram, bg=FARBY["panel"], fg=FARBY["text"],
                             font=("Segoe UI", 12, "bold"))
        self.stav.pack(pady=(0, 8))

        # Doska
        mriezka = tk.Frame(ram, bg=FARBY["panel"])
        mriezka.pack()
        self.policka = []
        for i in range(9):
            p = tk.Button(mriezka, text="", width=3, height=1, bd=0, relief="flat",
                          font=("Segoe UI", 36, "bold"), bg=FARBY["policko"],
                          activebackground=FARBY["policko_nad"], cursor="hand2",
                          command=lambda i=i: self.tah_hraca(i))
            p.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            self.policka.append(p)

        # Skóre
        self.skore_text = tk.Label(ram, bg=FARBY["panel"], fg=FARBY["sive"],
                                   font=("Segoe UI", 11))
        self.skore_text.pack(pady=10)

        tk.Button(ram, text="Nová hra", bd=0, padx=18, pady=6, cursor="hand2",
                  bg=FARBY["akcent"], fg=FARBY["akcent_text"],
                  activebackground=FARBY["akcent_nad"], activeforeground=FARBY["akcent_text"],
                  font=("Segoe UI", 11, "bold"), command=self.nova_hra).pack()

        self.zmen_rezim("dvaja")

    def zmen_rezim(self, rezim):
        self.rezim = rezim
        for kluc, t in self.tlacidla_rezimu.items():
            aktivny = kluc == rezim
            t.config(bg=FARBY["akcent"] if aktivny else FARBY["policko"],
                     fg=FARBY["akcent_text"] if aktivny else FARBY["sive"])
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
                bg=FARBY["vyhra"] if i in vyherny_rad else FARBY["policko"],
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
            self.stav.config(text=f"Vyhráva {znak}!")
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
            self.stav.config(text="Počítač premýšľa...")
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
