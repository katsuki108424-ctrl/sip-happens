print ("Welcome to Sip Happens!")
import json
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
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
    barre_progression["value"] = min(quantite_bue, objectif)
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
        barre_progression["value"] = min(quantite_bue, objectif)

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

    barre_progression.config(maximum=objectif)
    barre_progression["value"] = min(quantite_bue, objectif)
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

fenetre = tk.Tk ()
fenetre.title("Sip Happens!")
fenetre.geometry("400x500")
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Eau.Horizontal.TProgressbar",
    background= "#20CFFF",
    troughcolor="#D9F8FF"
)
titre = tk.Label (fenetre, text="Bienvenue sur Sip Happens!",
font=("Segoe UI", 20, "bold")
)
titre.pack()
texte_objectif = tk.Label(
    fenetre,
    text="objectif du jour en ml"
)
texte_objectif.pack()
champ_objectif = tk.Entry(fenetre)
champ_objectif.insert(0, str(objectif))
champ_objectif.pack()
bouton_objectif = tk.Button(
    fenetre,
    text="modifier l'objectif",
    command=modifier_objectif
)
bouton_objectif.pack()
texte_taille_verre = tk.Label(
    fenetre,
    text="Taille du verre en ml"
)
texte_taille_verre.pack()
choix_taille_verre = ttk.Combobox(
    fenetre,
    values=[150, 250, 330, 500],
    state="readonly"
)
choix_taille_verre.set(taille_verre)

choix_taille_verre.bind(
    "<<ComboboxSelected>>",
    lambda evenement: modifier_taille_verre()
)
choix_taille_verre.pack()
texte_intervalle = tk.Label(
    fenetre,
    text="Fréquence des rappels"
)
texte_intervalle.pack()
choix_intervalle = ttk.Combobox(
    fenetre,
    values=[30, 45, 60, 90],
    state="readonly"
)
choix_intervalle.set(minutes_rappel)

choix_intervalle.bind(
    "<<ComboboxSelected>>",
    lambda evenement: modifier_intervalle()
)
choix_intervalle.pack()

bouton_rappels = tk.Button(
    fenetre,
    text=(
        "Désactiver les rappels"
        if rappels_actifs
        else "Activer les rappels"
    ),
    command=basculer_rappels
)
bouton_rappels.pack()
compteur = tk.Label (
    fenetre,
    text=f"{quantite_bue} ml / {objectif} ml"
    )
compteur.pack ()
pourcentage = tk.Label (
    fenetre,
    text=f"{progression_initiale:.0f}%")
pourcentage.pack ()
barre_progression = ttk.Progressbar(
    fenetre,
    style="Eau.Horizontal.TProgressbar",
    maximum=objectif,
    value=min(quantite_bue, objectif),
    length=300
)
barre_progression.pack()
bouton_boire = tk.Button (
    fenetre,
    text="Je viens de boire 💦", 
    command=enregistrer_verre
    )
bouton_boire.pack()
bouton_annuler = tk.Button(
    fenetre,
    text="Annuler le dernier verre",
    command=annuler_verre
)
bouton_annuler.pack()

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
