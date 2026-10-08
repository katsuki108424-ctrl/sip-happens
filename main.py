print ("Welcome to Sip Happens!")
import ctypes
import winsound
from datetime import date
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from gestion_donnees import (
    ajouter_verre,
    annuler_dernier_verre,
    chemin_donnees_utilisateur,
    charger_donnees,
    sauvegarder_donnees as ecrire_donnees,
)

DOSSIER_APPLICATION = Path(__file__).resolve().parent
DOSSIER_POLICES = DOSSIER_APPLICATION / "assets" / "fonts"
DOSSIER_MASCOTTE = DOSSIER_APPLICATION / "assets" / "mascotte"
DOSSIER_SONS = DOSSIER_APPLICATION / "assets" / "sounds"
SON_BULLE = DOSSIER_SONS / "bulle.wav"
CHEMIN_DONNEES = chemin_donnees_utilisateur()
ANCIEN_CHEMIN_DONNEES = DOSSIER_APPLICATION / "donnees.json"


def jouer_son_bulle():
    if son_actif and SON_BULLE.exists():
        try:
            winsound.PlaySound(
                str(SON_BULLE),
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except RuntimeError:
            # Le suivi reste utilisable si Windows ne peut pas lire le son.
            pass

def charger_polices():
    fichiers_polices = [
        DOSSIER_POLICES / "kalam" / "Kalam-Regular.ttf",
        DOSSIER_POLICES / "kalam" / "Kalam-Bold.ttf",
        DOSSIER_POLICES / "patrick-hand" / "PatrickHand-Regular.ttf",
    ]

    for fichier_police in fichiers_polices:
        if fichier_police.exists():
            try:
                ctypes.windll.gdi32.AddFontResourceExW(
                    str(fichier_police),
                    0x10,
                    0
                )
            except (AttributeError, OSError):
                pass

charger_polices()

donnees = charger_donnees(
    CHEMIN_DONNEES,
    ancien_chemin=ANCIEN_CHEMIN_DONNEES,
)
quantite_bue = donnees["quantite_bue"]
objectif = donnees["objectif"]
taille_verre = donnees["taille_verre"]
minutes_rappel = donnees["minutes_rappel"]
rappels_actifs = donnees["rappels_actifs"]
son_actif = donnees["son_actif"]
date_courante = donnees["date"]
dernier_verre = donnees["dernier_verre"]
historique = donnees["historique"]
progression_initiale = (quantite_bue / objectif) * 100
intervalle_rappel = minutes_rappel * 60 * 1000
rappel_programme = None
retour_mascotte_programme = None

messages_mascotte = {
    "neutre": ("C'est parti pour le défi !", "#006DFF"),
    "heureux": ("Bien joué, un verre de plus !", "#00AEEB"),
    "triste": ("Bois ! Tu vas finir tout desséché !", "#8B00FF"),
    "objectif": ("Youhouuuuu ! Objectif atteint !", "#8B00FF"),
}

def changer_mascotte(etat):
    nouvelle_image = images_mascotte[etat]
    label_mascotte.configure(image=nouvelle_image)
    label_mascotte.image = nouvelle_image
    texte_mascotte, couleur_mascotte = messages_mascotte[etat]
    message_mascotte.configure(
        text=texte_mascotte,
        text_color=couleur_mascotte
    )
    label_mascotte.update_idletasks()

def revenir_mascotte_neutre():
    global retour_mascotte_programme

    if quantite_bue < objectif:
        changer_mascotte("neutre")

    retour_mascotte_programme = None

def actualiser_progression():
    progression = (quantite_bue / objectif) * 100
    pourcentage.configure(text=f"{progression:.0f}%")
    compteur.configure(text=f"{quantite_bue} ml / {objectif} ml")
    barre_progression.set(min(quantite_bue / objectif, 1))

    if quantite_bue >= objectif:
        titre.configure(text="Youhou! Objectif atteint!🥳")
    else:
        titre.configure(text="Bienvenue sur Sip Happens!")

def verifier_changement_jour(programmer=True):
    global quantite_bue
    global dernier_verre
    global date_courante

    aujourd_hui = date.today().isoformat()
    if date_courante != aujourd_hui:
        if quantite_bue > 0:
            historique[date_courante] = quantite_bue
            while len(historique) > 30:
                del historique[sorted(historique)[0]]
        quantite_bue = 0
        dernier_verre = 0
        date_courante = aujourd_hui
        actualiser_progression()
        changer_mascotte("neutre")
        sauvegarder_donnees()

    if programmer:
        fenetre.after(60_000, verifier_changement_jour)

def enregistrer_verre():
    global quantite_bue
    global dernier_verre
    global retour_mascotte_programme

    verifier_changement_jour(programmer=False)
    jouer_son_bulle()
    quantite_bue, dernier_verre = ajouter_verre(quantite_bue, taille_verre)
    actualiser_progression()
    sauvegarder_donnees()

    if quantite_bue >= objectif:
        titre.configure(text="Youhou! Objectif atteint!🥳")
        changer_mascotte("objectif")
    else:
        changer_mascotte("heureux")

        if retour_mascotte_programme is not None:
            fenetre.after_cancel(retour_mascotte_programme)

        retour_mascotte_programme = fenetre.after(
            6000,
            revenir_mascotte_neutre
        )

def annuler_verre():
    global quantite_bue
    global dernier_verre

    verifier_changement_jour(programmer=False)
    ancienne_quantite = quantite_bue
    quantite_bue, dernier_verre = annuler_dernier_verre(
        quantite_bue, dernier_verre
    )
    if quantite_bue != ancienne_quantite:
        actualiser_progression()

        if quantite_bue < objectif:
            changer_mascotte("neutre")

        sauvegarder_donnees()

def sauvegarder_donnees():
    donnees = {
        "quantite_bue": quantite_bue,
        "objectif": objectif,
        "taille_verre": taille_verre,
        "minutes_rappel": minutes_rappel,
        "rappels_actifs": rappels_actifs,
        "son_actif": son_actif,
        "date": date_courante,
        "dernier_verre": dernier_verre,
        "historique": historique,
    }

    try:
        ecrire_donnees(donnees, CHEMIN_DONNEES)
    except OSError as erreur:
        messagebox.showerror(
            "Sauvegarde impossible",
            f"Sip Happens n'a pas pu sauvegarder vos données.\n\n{erreur}",
        )
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
    if nouvel_objectif > 20_000:
        messagebox.showerror(
            "Valeur incorrecte",
            "L'objectif ne peut pas dépasser 20 000 ml"
        )
        return
    verifier_changement_jour(programmer=False)
    objectif = nouvel_objectif
    actualiser_progression()
    changer_mascotte("objectif" if quantite_bue >= objectif else "neutre")
    sauvegarder_donnees()

def modifier_taille_verre():
    global taille_verre

    try:
        taille_verre = int(choix_taille_verre.get())
    except ValueError:
        choix_taille_verre.set(str(taille_verre))
        return
    sauvegarder_donnees()

def modifier_intervalle():
    global intervalle_rappel
    global minutes_rappel
    global rappel_programme

    try:
        minutes_rappel = int(choix_intervalle.get())
    except ValueError:
        choix_intervalle.set(str(minutes_rappel))
        return
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

    sauvegarder_donnees()

def basculer_rappels():
    global rappels_actifs
    global rappel_programme

    rappels_actifs = not rappels_actifs

    if rappels_actifs:
        bouton_rappels.configure(text="Désactiver les rappels")
        rappel_programme = fenetre.after(
            intervalle_rappel,
            afficher_rappel
        )
    else:
        bouton_rappels.configure(text="Activer les rappels")

        if rappel_programme is not None:
            fenetre.after_cancel(rappel_programme)
            rappel_programme = None

    sauvegarder_donnees()    

def basculer_son():
    global son_actif

    son_actif = not son_actif
    bouton_son.configure(
        text="Désactiver le son" if son_actif else "Activer le son"
    )
    sauvegarder_donnees()

def afficher_reglages():
    frame_principal.pack_forget()
    frame_historique.pack_forget()
    frame_reglages.pack()

def afficher_principal():
    frame_reglages.pack_forget()
    frame_historique.pack_forget()
    frame_principal.pack()    

def afficher_historique():
    frame_principal.pack_forget()
    frame_reglages.pack_forget()

    for enfant in contenu_historique.winfo_children():
        enfant.destroy()

    jours = dict(historique)
    if quantite_bue > 0:
        jours[date_courante] = quantite_bue

    if not jours:
        ctk.CTkLabel(
            contenu_historique,
            text="Aucune consommation enregistrée pour le moment.",
            font=ctk.CTkFont(family="Patrick Hand", size=18),
            text_color="#006DFF",
            wraplength=300,
        ).pack(pady=24)
    else:
        for jour, quantite in sorted(jours.items(), reverse=True):
            annee, mois, numero_jour = jour.split("-")
            texte_jour = "Aujourd'hui" if jour == date_courante else (
                f"{numero_jour}/{mois}/{annee}"
            )
            ctk.CTkLabel(
                contenu_historique,
                text=f"{texte_jour}    {quantite} ml",
                width=300,
                height=40,
                anchor="w",
                font=ctk.CTkFont(family="Patrick Hand", size=19),
                text_color="#003CFF",
            ).pack(padx=12, pady=3)

    frame_historique.pack()

def tester_rappel():
    verifier_changement_jour(programmer=False)
    quantite_avant_rappel = quantite_bue

    messagebox.showinfo(
        "Sip Happens!",
        "Petite pause : Pense à boire de l'eau!"
    )

    if quantite_bue == quantite_avant_rappel and quantite_bue < objectif:
        changer_mascotte("triste")

ctk.set_appearance_mode("light")

fenetre = ctk.CTk()
fenetre.title("Sip Happens!")
fenetre.geometry("400x680")
fenetre.configure(fg_color="#DDF8FF")

ressources_requises = [
    DOSSIER_MASCOTTE / "axolotl-neutre.png",
    DOSSIER_MASCOTTE / "axolotl-triste.png",
    DOSSIER_MASCOTTE / "axolotl-heureux.png",
    DOSSIER_MASCOTTE / "axolotl-objectif.png",
]
ressources_manquantes = [
    fichier.name for fichier in ressources_requises if not fichier.exists()
]
if ressources_manquantes:
    messagebox.showerror(
        "Ressources manquantes",
        "Ces mascottes sont introuvables :\n"
        + "\n".join(ressources_manquantes),
    )
    fenetre.destroy()
    raise SystemExit(1)

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
frame_historique = ctk.CTkFrame(
    fenetre,
    fg_color="#DDF8FF",
)
frame_historique.pack()
titre = ctk.CTkLabel(
    frame_principal,
    text="Bienvenue sur Sip Happens!",
    fg_color="transparent",
    font=ctk.CTkFont(family="Kalam", size=28, weight="bold"),
    text_color="#8B00FF"
)
titre.pack(pady=(30, 20))

images_mascotte = {
    "neutre": ctk.CTkImage(
        light_image=Image.open(DOSSIER_MASCOTTE / "axolotl-neutre.png"),
        size=(280, 187)
    ),
    "triste": ctk.CTkImage(
        light_image=Image.open(DOSSIER_MASCOTTE / "axolotl-triste.png"),
        size=(280, 187)
    ),
    "heureux": ctk.CTkImage(
        light_image=Image.open(DOSSIER_MASCOTTE / "axolotl-heureux.png"),
        size=(280, 187)
    ),
    "objectif": ctk.CTkImage(
        light_image=Image.open(DOSSIER_MASCOTTE / "axolotl-objectif.png"),
        size=(280, 187)
    ),
}

etat_mascotte_initial = (
    "objectif"
    if quantite_bue >= objectif
    else "neutre"
)

label_mascotte = ctk.CTkLabel(
    frame_principal,
    text="",
    image=images_mascotte[etat_mascotte_initial],
    fg_color="transparent"
)
label_mascotte.pack(pady=(0, 4))

message_initial, couleur_initiale = messages_mascotte[etat_mascotte_initial]
message_mascotte = ctk.CTkLabel(
    frame_principal,
    text=message_initial,
    fg_color="transparent",
    font=ctk.CTkFont(family="Patrick Hand", size=20),
    text_color=couleur_initiale
)
message_mascotte.pack(pady=(0, 4))

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

bouton_tester_rappel = ctk.CTkButton(
    frame_reglages,
    text="Tester un rappel",
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    width=220,
    height=38,
    corner_radius=13,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=tester_rappel
)
bouton_tester_rappel.pack(pady=(0, 8))

bouton_son = ctk.CTkButton(
    frame_reglages,
    text="Désactiver le son" if son_actif else "Activer le son",
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    width=220,
    height=38,
    corner_radius=13,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=basculer_son,
)
bouton_son.pack(pady=(0, 8))

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

titre_historique = ctk.CTkLabel(
    frame_historique,
    text="Historique",
    fg_color="transparent",
    font=ctk.CTkFont(family="Kalam", size=28, weight="bold"),
    text_color="#8B00FF",
)
titre_historique.pack(pady=(24, 14))

contenu_historique = ctk.CTkScrollableFrame(
    frame_historique,
    width=330,
    height=490,
    fg_color="#DDF8FF",
    scrollbar_button_color="#20CFFF",
    scrollbar_button_hover_color="#00AFCF",
)
contenu_historique.pack(padx=20)

bouton_retour_historique = ctk.CTkButton(
    frame_historique,
    text="Retour",
    font=ctk.CTkFont(family="Patrick Hand", size=18),
    width=220,
    height=38,
    corner_radius=13,
    fg_color="#8B00FF",
    hover_color="#6D28D9",
    text_color="white",
    command=afficher_principal,
)
bouton_retour_historique.pack(pady=12)
frame_historique.pack_forget()


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

bouton_historique = ctk.CTkButton(
    frame_principal,
    text="Historique",
    font=ctk.CTkFont(family="Patrick Hand", size=17),
    width=260,
    height=40,
    corner_radius=14,
    fg_color="#20CFFF",
    hover_color="#00AFCF",
    text_color="#003CFF",
    border_width=2,
    border_color="#007EA7",
    command=afficher_historique,
)
bouton_historique.pack(pady=(0, 10))

def afficher_rappel():
    global rappel_programme

    verifier_changement_jour(programmer=False)
    quantite_avant_rappel = quantite_bue

    messagebox.showinfo(
        "Sip Happens!",
        "Petite pause : Pense à boire de l'eau!"
    )

    if quantite_bue == quantite_avant_rappel and quantite_bue < objectif:
        changer_mascotte("triste")

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

def fermer_application():
    sauvegarder_donnees()
    fenetre.destroy()

fenetre.protocol("WM_DELETE_WINDOW", fermer_application)
verifier_changement_jour()
sauvegarder_donnees()
fenetre.mainloop()
