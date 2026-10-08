# Sip Happens!

Sip Happens est une application de bureau de suivi d'hydratation, développée
et dirigée par **Anne-France Biérin**. Elle a été réalisée en Python avec
CustomTkinter pour rendre le suivi quotidien simple, coloré et encourageant.

## Fonctionnalités

- suivi de la quantité d'eau bue et de la progression quotidienne ;
- ajout d'un verre et annulation du dernier verre ajouté ;
- objectif quotidien personnalisable ;
- choix de la taille du verre : 150, 250, 330 ou 500 ml ;
- rappels configurables toutes les 30, 45, 60 ou 90 minutes ;
- activation, désactivation et test des rappels ;
- mascottes axolotls qui réagissent à la progression ;
- son de bulle lors de l'ajout d'un verre ;
- activation et désactivation du son depuis les réglages ;
- historique des consommations des 30 derniers jours ;
- sauvegarde automatique des réglages et de la consommation ;
- remise à zéro automatique de la consommation au changement de journée.

## Prérequis

- Windows 10 ou Windows 11 ;
- Python 3.10 ou une version plus récente ;
- `pip`, normalement inclus avec Python.

Pendant l'installation de Python, cochez l'option **Add Python to PATH**.

## Installation

Ouvrez PowerShell dans le dossier du projet, puis exécutez :

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

Si PowerShell refuse l'activation de l'environnement virtuel, l'application
peut aussi être lancée directement avec les commandes suivantes :

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Lancement

Avec l'environnement virtuel activé :

```powershell
py main.py
```

Les données personnelles ne sont pas enregistrées dans le dépôt. Elles sont
stockées dans le dossier Windows de l'utilisateur :
`%LOCALAPPDATA%\Sip Happens\donnees.json`.

## Vérification

Pour lancer les tests automatisés :

```powershell
py -m unittest discover -s tests -v
```

L'interface, les notifications visuelles et le son doivent également être
vérifiés manuellement sur Windows.

## Créer l'exécutable Windows

Installez les outils de construction puis lancez PyInstaller :

```powershell
py -m pip install -r requirements-build.txt
py -m PyInstaller --clean --noconfirm "Sip Happens.spec"
```

L'application portable est alors créée dans `dist\Sip Happens.exe`. Elle
contient les mascottes, les polices, le son et l'icône ; Python n'a pas besoin
d'être installé sur l'ordinateur qui l'utilise.

## Ressources

Les polices Kalam et Patrick Hand sont distribuées avec leurs fichiers de
licence OFL dans `assets/fonts`. Les mascottes, leurs fichiers sources et le
son utilisé par l'application se trouvent dans `assets`.
