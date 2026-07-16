print ("Welcome to Sip Happens!")
import json
import ctypes
from datetime import date
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

DOSSIER_POLICES = Path(__file__).parent / "assets" / "fonts"

def charger_polices():
    fichiers_polices = [
        DOSSIER_POLICES / "kalam" / "Kalam-Regular.ttf",
        DOSSIER_POLICES / "kalam" / "Kalam-Bold.ttf",
        DOSSIER_POLICES / "patrick-hand" / "PatrickHand-Regular.ttf",
    ]

    for fichier_police in fichiers_polices:
        ctypes.windll.gdi32.AddFontResourceExW(
            str(fichier_police),
            0x10,
            0
        )

charger_polices()

try:
    with open("donnees.json", "r", encoding="utf-8") as fichier:
        donnees = json.load (fichier)
        objectif = donnees.get("objectif", 2000)
        taille_verre = donnees.get("taille_verre", 250)
        minutes_rappel = donnees.get("minutes_rappel", 30)
        rappels_actifs = donnees.get ("rappels_actifs", True)
        date_sauvegardee = donnees.get("date")
        date_aujourdhui = date.today().isoformat()
        if date_sauvegardee == date_aujourdhui:
            quantite_bue = donnees.get("quantite_bue", 0)
        else:
            quantite_bue = 0
except FileNotFoundError:
    quantite_bue = 0
    objectif = 2000
    taille_verre = 250
    minutes_rappel = 30
    rappels_actifs =  True
progression_initiale = (quantite_bue / objectif) * 100
intervalle_rappel = minutes_rappel * 60 * 1000
rappel_programme = None

def enregistrer_verre():
    global quantite_bue
    quantite_bue = quantite_bue + taille_verre
    progression = (quantite_bue / objectif) * 100
    pourcentage.config(text=f"{progression:.0f}%")
    compteur.config(text=f"{quantite_bue} ml / {objectif} ml")
    barre_progression.set(min(quantite_bue / objectif, 1))
    print (quantite_bue)
    sauvegarder_donnees()

    if quantite_bue >= objectif:
        titre.config(text="Youhou! Objectif atteint!🥳")
def annuler_verre():
    global quantite_bue

    if quantite_bue >= taille_verre:
        quantite_bue = quantite_bue - taille_verre
        progression = (quantite_bue / objectif) * 100
        pourcentage.config(text=f"{progression:.0f}%")
        compteur.config(text=f"{quantite_bue} ml / {objectif} ml")
        barre_progression.set(min(quantite_bue / objectif, 1))

        if quantite_bue < objectif:
            titre.config(text="Bienvenue sur Sip Happens!")

        print(quantite_bue)
        sauvegarder_donnees()

def sauvegarder_donnees():
    donnees = {
        "quantite_bue": quantite_bue,
        "objectif": objectif,
        "taille_verre": taille_verre,
        "minutes_rappel": minutes_rappel,
        "rappels_actifs": rappels_actifs,
        "date": date.today().isoformat()
    }

    with open("donnees.json","w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier)
def modifier_objectif():
    global objectif


    try:
        nouvel_objectif = int(champ_objectif.get())
    except ValueError:
        messagebox.showerror(
            "Valeur incorrecte",
            "Entre un objectif en chiffres uniquement"
        )
        return
    if nouvel_objectif <= 0:
        messagebox.showerror(
            "Valeur incorrecte",
            "L'objectif doit être supérieur à 0 ml"
        )
        return
    objectif = nouvel_objectif
    compteur.config(text=f"{quantite_bue} ml / {objectif} ml")

    progression = (quantite_bue / objectif) * 100
    pourcentage.config(text=f"{progression:.0f}%")

    barre_progression.set(min(quantite_bue / objectif, 1))
    print(objectif)
    sauvegarder_donnees()

def modifier_taille_verre():
    global taille_verre

    taille_verre = int(choix_taille_verre.get())
    print (taille_verre)
    sauvegarder_donnees()

def modifier_intervalle():
    global intervalle_rappel
    global minutes_rappel
    global rappel_programme

    minutes_rappel = int(choix_intervalle.get())
    intervalle_rappel = minutes_rappel * 60 * 1000

    if rappel_programme is not None:
        fenetre.after_cancel(rappel_programme)

    if rappels_actifs:
        rappel_programme = fenetre.after(
            intervalle_rappel,
            afficher_rappel
        )
    else:
        rappel_programme = None

    print (intervalle_rappel)
    sauvegarder_donnees()

def basculer_rappels():
    global rappels_actifs
    global rappel_programme

    rappels_actifs = not rappels_actifs

    if rappels_actifs:
        bouton_rappels.config(text="Désactiver les rappels")
        rappel_programme = fenetre.after(
            intervalle_rappel,
            afficher_rappel
        )
    else:
        bouton_rappels.config(text="Activer les rappels")

        if rappel_programme is not None:
            fenetre.after_cancel(rappel_programme)
            rappel_programme = None

    sauvegarder_donnees()    

def afficher_reglages():
    frame_principal.pack_forget()
    frame_reglages.pack()

def afficher_principal():
    frame_reglages.pack_forget()
    frame_principal.pack()    

ctk.set_appearance_mode("light")

fenetre = ctk.CTk()
fenetre.title("Sip Happens!")
fenetre.geometry("400x500")
fenetre.configure(fg_color="#DDF8FF")

frame_principal = ctk.CTkFrame(
    fenetre,
    fg_color="#DDF8FF"
    )
frame_principal.pack()
frame_reglages = ctk.CTkFrame(
    fenetre,
    fg_color="#DDF8FF",
    )
frame_reglages.pack()
titre = ctk.CTkLabel(
    frame_principal,
    text="Bienvenue sur Sip Happens!",
    fg_color="transparent",
    font=ctk.CTkFont(family="Kalam", size=28, weight="bold"),
    text_color="#8B00FF"
)
titre.pack(pady=(30, 20))

titre_reglages = ctk.CTkLabel(
    frame_reglages,
    text="Réglages",
    fg_color="transparent",
    font=ctk.CTkFont(family="Kalam", size=28, weight="bold"),
    text_color="#8B00FF"
)
titre_reglages.pack(pady=(22, 12))

texte_objectif = ctk.CTkLabel(
    frame_reglages,
    fg_color="transparent",
    text="Objectif du jour en ml",
    font=ctk.CTkFont(family="Patrick Hand", size=19),
    text_color="#006DFF"
)
texte_objectif.pack()
champ_objectif = ctk.CTkEntry(
    frame_reglages,
    width=220,
    height=38,
    corner_radius=12,
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    fg_color="#F3FCFF",
    text_color="#003CFF",
    border_color="#20CFFF",
    border_width=2
)
champ_objectif.insert(0, str(objectif))
champ_objectif.pack(pady=(2, 8))
bouton_objectif = ctk.CTkButton(
    frame_reglages,
    text="Modifier l'objectif",
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    width=220,
    height=38,
    corner_radius=13,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=modifier_objectif
)
bouton_objectif.pack(pady=(0, 10))
texte_taille_verre = ctk.CTkLabel(
    frame_reglages,
    fg_color="transparent",
    text="Taille du verre en ml",
    font=ctk.CTkFont(family="Patrick Hand", size=19),
    text_color="#006DFF"
)
texte_taille_verre.pack()
choix_taille_verre = ctk.CTkComboBox(
    frame_reglages,
    values=["150", "250", "330", "500"],
    state="readonly",
    width=220,
    height=38,
    corner_radius=12,
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    dropdown_font=ctk.CTkFont(family="Patrick Hand", size=17),
    fg_color="#F3FCFF",
    border_color="#20CFFF",
    button_color="#20CFFF",
    button_hover_color="#00AFCF",
    text_color="#003CFF",
    dropdown_fg_color="#F3FCFF",
    dropdown_hover_color="#D9F8FF",
    dropdown_text_color="#003CFF",
    command=lambda choix: modifier_taille_verre()
)
choix_taille_verre.set(str(taille_verre))
choix_taille_verre.pack(pady=(2, 10))
texte_intervalle = ctk.CTkLabel(
    frame_reglages,
    fg_color="transparent",
    text="Fréquence des rappels",
    font=ctk.CTkFont(family="Patrick Hand", size=19),
    text_color="#006DFF"
)
texte_intervalle.pack()
choix_intervalle = ctk.CTkComboBox(
    frame_reglages,
    values=["30", "45", "60", "90"],
    state="readonly",
    width=220,
    height=38,
    corner_radius=12,
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    dropdown_font=ctk.CTkFont(family="Patrick Hand", size=17),
    fg_color="#F3FCFF",
    border_color="#20CFFF",
    button_color="#20CFFF",
    button_hover_color="#00AFCF",
    text_color="#003CFF",
    dropdown_fg_color="#F3FCFF",
    dropdown_hover_color="#D9F8FF",
    dropdown_text_color="#003CFF",
    command=lambda choix: modifier_intervalle()
)
choix_intervalle.set(str(minutes_rappel))
choix_intervalle.pack(pady=(2, 10))

bouton_rappels = ctk.CTkButton(
    frame_reglages,
    text=(
        "Désactiver les rappels"
        if rappels_actifs
        else "Activer les rappels"
    ),
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    width=220,
    height=38,
    corner_radius=13,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=basculer_rappels
)
bouton_rappels.pack(pady=(0, 8))

bouton_retour = ctk.CTkButton(
    frame_reglages,
    text="Retour",
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    width=220,
    height=38,
    corner_radius=13,
    fg_color="#8B00FF",
    hover_color="#6D28D9",
    text_color="white",
    command=afficher_principal
)
bouton_retour.pack(pady=(0, 12))

frame_reglages.pack_forget()


compteur = ctk.CTkLabel(
    frame_principal,
    fg_color="transparent",
    text=f"{quantite_bue} ml / {objectif} ml",
    font=ctk.CTkFont(family="Patrick Hand", size=24),
    text_color="#006DFF"
    )
compteur.pack (pady=10)
pourcentage = ctk.CTkLabel(
    frame_principal,
    fg_color="transparent",
    font=ctk.CTkFont(family="Patrick Hand", size=21),
    text_color="#00AEEB",
    text=f"{progression_initiale:.0f}%")
pourcentage.pack ()
barre_progression = ctk.CTkProgressBar(
    frame_principal,
    width=300,
    height=18,
    corner_radius=9,
    fg_color="#D9F8FF",
    progress_color="#20CFFF"
)
barre_progression.set(min(quantite_bue / objectif, 1))
barre_progression.pack()
bouton_boire = ctk.CTkButton(
    frame_principal,
    text="Je viens de boire 💦", 
    font=ctk.CTkFont(family="Patrick Hand", size=21),
    fg_color="#20CFFF",
    text_color="#003CFF",
    hover_color="#00AFCF",
    width=260,
    height=52,
    corner_radius=18,
    border_width=2,
    border_color="#007EA7",
    command=enregistrer_verre
    )
bouton_boire.pack(pady=(25, 10))
frame_actions_secondaires = ctk.CTkFrame(
    frame_principal,
    fg_color="transparent"
)
frame_actions_secondaires.pack(pady=10)

bouton_annuler = ctk.CTkButton(
    frame_actions_secondaires,
    text="Annuler le dernier verre",
    font=ctk.CTkFont(family="Patrick Hand", size=17),
    width=145,
    height=40,
    corner_radius=14,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=annuler_verre
)
bouton_annuler.pack(side="left", padx=8)

bouton_ouvrir_reglages = ctk.CTkButton(
    frame_actions_secondaires,
    text="Réglages",
    font=ctk.CTkFont(family="Patrick Hand", size=17),
    width=145,
    height=40,
    corner_radius=14,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=afficher_reglages
)
bouton_ouvrir_reglages.pack(side="left", padx=8)

def afficher_rappel():
    global rappel_programme

    messagebox.showinfo(
        "Sip Happens!",
        "Petite pause : Pense à boire de l'eau!"
    )
    if rappels_actifs:
        rappel_programme = fenetre.after(
            intervalle_rappel,
            afficher_rappel
        )
    else:
        rappel_programme = None

if rappels_actifs:
    rappel_programme = fenetre.after(
        intervalle_rappel,
        afficher_rappel
    )

fenetre.mainloop()
