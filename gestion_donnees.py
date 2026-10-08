"""Chargement et sauvegarde fiables des donnees de Sip Happens."""

import json
import os
from datetime import date
from pathlib import Path


VALEURS_PAR_DEFAUT = {
    "quantite_bue": 0,
    "objectif": 2000,
    "taille_verre": 250,
    "minutes_rappel": 30,
    "rappels_actifs": True,
    "son_actif": True,
    "date": date.today().isoformat(),
    "dernier_verre": 0,
    "historique": {},
}

TAILLES_VERRE_AUTORISEES = (150, 250, 330, 500)
INTERVALLES_AUTORISES = (30, 45, 60, 90)


def chemin_donnees_utilisateur():
    """Retourne un emplacement personnel, hors du dossier publie sur GitHub."""
    dossier_local = os.environ.get("LOCALAPPDATA")
    dossier_base = Path(dossier_local) if dossier_local else Path.home()
    return dossier_base / "Sip Happens" / "donnees.json"


def _entier_valide(valeur, defaut, minimum, maximum, autorisees=None):
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        return defaut
    if not minimum <= valeur <= maximum:
        return defaut
    if autorisees is not None and valeur not in autorisees:
        return defaut
    return valeur


def valider_donnees(donnees, aujourd_hui=None):
    """Nettoie les donnees et remet la consommation a zero un nouveau jour."""
    aujourd_hui = aujourd_hui or date.today().isoformat()
    if not isinstance(donnees, dict):
        donnees = {}

    historique_brut = donnees.get("historique", {})
    historique = {}
    if isinstance(historique_brut, dict):
        for jour, quantite in historique_brut.items():
            try:
                date.fromisoformat(jour)
            except (TypeError, ValueError):
                continue
            quantite_validee = _entier_valide(quantite, 0, 0, 1_000_000)
            if quantite_validee > 0:
                historique[jour] = quantite_validee

    date_sauvegardee = donnees.get("date")
    meme_jour = date_sauvegardee == aujourd_hui
    quantite_sauvegardee = _entier_valide(
        donnees.get("quantite_bue"), 0, 0, 1_000_000
    )
    if not meme_jour and quantite_sauvegardee > 0:
        try:
            date.fromisoformat(date_sauvegardee)
        except (TypeError, ValueError):
            pass
        else:
            historique[date_sauvegardee] = quantite_sauvegardee

    historique = dict(sorted(historique.items())[-30:])

    resultat = {
        "objectif": _entier_valide(donnees.get("objectif"), 2000, 1, 20_000),
        "taille_verre": _entier_valide(
            donnees.get("taille_verre"),
            250,
            1,
            2_000,
            TAILLES_VERRE_AUTORISEES,
        ),
        "minutes_rappel": _entier_valide(
            donnees.get("minutes_rappel"),
            30,
            1,
            1_440,
            INTERVALLES_AUTORISES,
        ),
        "rappels_actifs": (
            donnees.get("rappels_actifs")
            if isinstance(donnees.get("rappels_actifs"), bool)
            else True
        ),
        "son_actif": (
            donnees.get("son_actif")
            if isinstance(donnees.get("son_actif"), bool)
            else True
        ),
        "date": aujourd_hui,
        "historique": historique,
    }

    resultat["quantite_bue"] = (
        quantite_sauvegardee if meme_jour else 0
    )
    resultat["dernier_verre"] = (
        _entier_valide(donnees.get("dernier_verre"), 0, 0, 2_000)
        if meme_jour
        else 0
    )
    resultat["dernier_verre"] = min(
        resultat["dernier_verre"], resultat["quantite_bue"]
    )
    return resultat


def ajouter_verre(quantite_bue, taille_verre):
    """Ajoute un verre et memorise sa taille pour permettre une annulation exacte."""
    return quantite_bue + taille_verre, taille_verre


def annuler_dernier_verre(quantite_bue, dernier_verre):
    """Annule au maximum une fois le dernier verre effectivement ajoute."""
    if dernier_verre <= 0 or dernier_verre > quantite_bue:
        return quantite_bue, 0
    return quantite_bue - dernier_verre, 0


def charger_donnees(chemin=None, ancien_chemin=None, aujourd_hui=None):
    """Charge les donnees ou renvoie des valeurs sures si le fichier est absent/invalide."""
    chemin = Path(chemin) if chemin else chemin_donnees_utilisateur()
    ancien_chemin = Path(ancien_chemin) if ancien_chemin else None
    source = chemin

    if not source.exists() and ancien_chemin and ancien_chemin.exists():
        source = ancien_chemin

    try:
        with source.open("r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeError):
        donnees = {}

    return valider_donnees(donnees, aujourd_hui)


def sauvegarder_donnees(donnees, chemin=None):
    """Sauvegarde atomiquement pour eviter un JSON coupe ou partiellement ecrit."""
    chemin = Path(chemin) if chemin else chemin_donnees_utilisateur()
    chemin.parent.mkdir(parents=True, exist_ok=True)
    temporaire = chemin.with_suffix(".tmp")

    try:
        with temporaire.open("w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, ensure_ascii=False, indent=2)
        try:
            temporaire.replace(chemin)
        except PermissionError:
            # Certains environnements Windows isoles autorisent l'ecriture,
            # mais refusent le renommage atomique d'un fichier temporaire.
            with chemin.open("w", encoding="utf-8") as fichier:
                json.dump(donnees, fichier, ensure_ascii=False, indent=2)
            temporaire.unlink(missing_ok=True)
    except OSError:
        try:
            temporaire.unlink(missing_ok=True)
        except OSError:
            pass
        raise
