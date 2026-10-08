import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gestion_donnees import (
    ajouter_verre,
    annuler_dernier_verre,
    charger_donnees,
    sauvegarder_donnees,
    valider_donnees,
)


class GestionDonneesTests(unittest.TestCase):
    def test_fichier_absent_utilise_les_valeurs_par_defaut(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            donnees = charger_donnees(Path(dossier) / "absent.json", aujourd_hui="2026-10-08")
        self.assertEqual(donnees["quantite_bue"], 0)
        self.assertEqual(donnees["objectif"], 2000)

    def test_json_corrompu_ne_provoque_pas_de_plantage(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "donnees.json"
            chemin.write_text("{pas du json", encoding="utf-8")
            donnees = charger_donnees(chemin, aujourd_hui="2026-10-08")
        self.assertEqual(donnees["quantite_bue"], 0)

    def test_nouveau_jour_remet_la_consommation_a_zero(self):
        donnees = valider_donnees(
            {
                "date": "2026-10-07",
                "quantite_bue": 1250,
                "dernier_verre": 250,
                "objectif": 1800,
            },
            aujourd_hui="2026-10-08",
        )
        self.assertEqual(donnees["quantite_bue"], 0)
        self.assertEqual(donnees["dernier_verre"], 0)
        self.assertEqual(donnees["objectif"], 1800)
        self.assertEqual(donnees["historique"]["2026-10-07"], 1250)

    def test_valeurs_invalides_sont_remplacees(self):
        donnees = valider_donnees(
            {
                "date": "2026-10-08",
                "quantite_bue": -10,
                "objectif": 0,
                "taille_verre": 999,
                "minutes_rappel": "vite",
                "rappels_actifs": "oui",
            },
            aujourd_hui="2026-10-08",
        )
        self.assertEqual(donnees["quantite_bue"], 0)
        self.assertEqual(donnees["objectif"], 2000)
        self.assertEqual(donnees["taille_verre"], 250)
        self.assertEqual(donnees["minutes_rappel"], 30)
        self.assertIs(donnees["rappels_actifs"], True)
        self.assertIs(donnees["son_actif"], True)

    def test_sauvegarde_et_relecture(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "donnees.json"
            attendu = valider_donnees(
                {"date": "2026-10-08", "quantite_bue": 500},
                aujourd_hui="2026-10-08",
            )
            sauvegarder_donnees(attendu, chemin)
            relu = json.loads(chemin.read_text(encoding="utf-8"))
        self.assertEqual(relu, attendu)

    def test_ajout_et_annulation_utilisent_la_taille_du_verre_ajoute(self):
        quantite, dernier = ajouter_verre(500, 250)
        self.assertEqual((quantite, dernier), (750, 250))

        # Changer ensuite le réglage du verre ne doit pas modifier l'annulation.
        quantite, dernier = annuler_dernier_verre(quantite, dernier)
        self.assertEqual((quantite, dernier), (500, 0))

        quantite, dernier = annuler_dernier_verre(quantite, dernier)
        self.assertEqual((quantite, dernier), (500, 0))

    def test_sauvegarde_fonctionne_si_windows_refuse_le_renommage(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as dossier:
            chemin = Path(dossier) / "donnees.json"
            with mock.patch.object(Path, "replace", side_effect=PermissionError):
                sauvegarder_donnees({"objectif": 2000}, chemin)
            relu = json.loads(chemin.read_text(encoding="utf-8"))
        self.assertEqual(relu["objectif"], 2000)

    def test_historique_ignore_les_entrees_invalides_et_garde_30_jours(self):
        historique = {
            f"2026-09-{jour:02d}": jour * 100 for jour in range(1, 31)
        }
        historique["date-invalide"] = 500
        donnees = valider_donnees(
            {"date": "2026-10-08", "historique": historique},
            aujourd_hui="2026-10-08",
        )
        self.assertEqual(len(donnees["historique"]), 30)
        self.assertNotIn("date-invalide", donnees["historique"])


if __name__ == "__main__":
    unittest.main()
