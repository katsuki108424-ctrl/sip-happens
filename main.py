print ("Welcome to Sip Happens!")
import json
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
try:
    with open("donnees.json", "r", encoding="utf-8") as fichier:
        donnees = json.load (fichier)
        objectif = donnees.get("objectif", 2000)
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
progression_initiale = (quantite_bue / objectif) * 100
intervalle_rappel = 30 * 60 * 1000
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
    messagebox.showinfo(
        "Sip Happens!",
        "Petite pause : Pense à boire de l'eau!"
    )
    fenetre.after(intervalle_rappel, afficher_rappel)

fenetre.after(intervalle_rappel, afficher_rappel)
fenetre.mainloop()
