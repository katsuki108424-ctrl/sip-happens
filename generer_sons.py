import math
import random
import struct
import wave
from pathlib import Path


DOSSIER_SONS = Path(__file__).parent / "assets" / "sounds"
DOSSIER_SONS.mkdir(parents=True, exist_ok=True)


def fondu(t, debut, duree):
    """Enveloppe douce qui apparaît vite puis disparaît progressivement."""
    if t < debut or t >= debut + duree:
        return 0.0

    position = (t - debut) / duree
    attaque = min(position / 0.06, 1.0)
    disparition = (1.0 - position) ** 2.4
    return attaque * disparition


def creer_son_bulle():
    frequence_echantillonnage = 44_100
    duree = 0.82
    volume = 0.42
    nombre_echantillons = int(frequence_echantillonnage * duree)
    chemin = DOSSIER_SONS / "bulle.wav"
    random.seed(7)

    echantillons = []
    phase_bulle = 0.0

    for index in range(nombre_echantillons):
        temps = index / frequence_echantillonnage

        # Corps de la bulle : un "bloup" rond dont la hauteur remonte rapidement.
        progression_bulle = min(temps / 0.30, 1.0)
        frequence_bulle = 240 + 720 * (progression_bulle ** 1.7)
        phase_bulle += 2 * math.pi * frequence_bulle / frequence_echantillonnage
        enveloppe_bulle = fondu(temps, 0.0, 0.34)
        bulle = (
            math.sin(phase_bulle)
            + 0.28 * math.sin(2 * phase_bulle + 0.4)
        ) * enveloppe_bulle

        # Petit "pop" humide au départ, pour rendre la bulle plus naturelle.
        enveloppe_pop = math.exp(-temps * 42)
        pop = (
            0.32 * math.sin(2 * math.pi * 125 * temps)
            + 0.10 * (random.random() * 2 - 1)
        ) * enveloppe_pop

        # Trois notes cristallines donnent le côté magique sans masquer la bulle.
        scintillement = 0.0
        notes = (
            (0.16, 1174.66, 0.30, 0.18),
            (0.25, 1567.98, 0.34, 0.14),
            (0.36, 2093.00, 0.38, 0.10),
        )
        for debut, frequence, longueur, intensite in notes:
            env = fondu(temps, debut, longueur)
            temps_note = max(temps - debut, 0)
            vibration = 1 + 0.006 * math.sin(2 * math.pi * 7 * temps_note)
            scintillement += (
                math.sin(2 * math.pi * frequence * vibration * temps_note)
                + 0.22 * math.sin(2 * math.pi * frequence * 2 * temps_note)
            ) * env * intensite

        echantillons.append((0.78 * bulle) + pop + scintillement)

    # Deux échos courts donnent de l'espace et une traînée féerique.
    son_sec = echantillons.copy()
    for retard, intensite in ((0.075, 0.20), (0.145, 0.10)):
        decalage = int(retard * frequence_echantillonnage)
        for index in range(decalage, nombre_echantillons):
            echantillons[index] += son_sec[index - decalage] * intensite

    # Normalisation sûre, puis fondu final pour éviter tout clic.
    maximum = max(abs(valeur) for valeur in echantillons) or 1
    facteur = volume * 32_767 / maximum

    with wave.open(str(chemin), "w") as fichier:
        fichier.setnchannels(1)
        fichier.setsampwidth(2)
        fichier.setframerate(frequence_echantillonnage)

        for index, valeur in enumerate(echantillons):
            temps_restant = duree - index / frequence_echantillonnage
            fondu_final = min(temps_restant / 0.06, 1.0)
            echantillon = int(valeur * facteur * fondu_final)
            fichier.writeframesraw(struct.pack("<h", echantillon))

    return chemin


chemin_cree = creer_son_bulle()
print(f"Son bulle magique créé : {chemin_cree}")
