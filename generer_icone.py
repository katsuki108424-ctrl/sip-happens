"""Genere l'icone Windows de Sip Happens depuis la mascotte existante."""

from pathlib import Path

from PIL import Image


DOSSIER_APPLICATION = Path(__file__).resolve().parent
SOURCE = DOSSIER_APPLICATION / "assets" / "mascotte" / "axolotl-neutre.png"
DOSSIER_ICONE = DOSSIER_APPLICATION / "assets" / "icon"
CHEMIN_ICONE = DOSSIER_ICONE / "sip-happens.ico"


def generer_icone():
    DOSSIER_ICONE.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE).convert("RGBA") as mascotte:
        # Le visage reste reconnaissable, même dans une petite icône Windows.
        cadrage = mascotte.crop((80, 50, 1030, 1000))
        cadrage.thumbnail((230, 230), Image.Resampling.LANCZOS)
        icone = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        position = (
            (icone.width - cadrage.width) // 2,
            (icone.height - cadrage.height) // 2,
        )
        icone.alpha_composite(cadrage, position)
        icone.save(
            CHEMIN_ICONE,
            format="ICO",
            sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                   (128, 128), (256, 256)],
        )
    return CHEMIN_ICONE


if __name__ == "__main__":
    print(f"Icône créée : {generer_icone()}")
