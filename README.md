# 👁 EyeRest

Application de protection des yeux (règle 20-20-20).  
Légère, moderne, avec détection automatique fullscreen/jeu/vidéo.

---

## Fonctionnalités

- ⏱ Intervalles et durée de pause configurables
- 🎮 Détection automatique fullscreen / jeu / vidéo (via Windows API)
- 🌿 Overlay plein écran animé pendant la pause avec compte à rebours
- 🔔 Icône systray avec menu contextuel
- 🚀 Démarrage avec Windows (registre HKCU)
- 🔕 Option : démarrer directement en arrière-plan
- 🪶 Ultra-léger : ~1 tick/seconde, aucun polling actif

---

## Installation rapide (script Python)

```bash
# 1. Cloner / décompresser le dossier
cd eyerest

# 2. Installer la dépendance
pip install PyQt6

# 3. Lancer
python main.py
```

---

## Compiler en .exe autonome (optionnel)

```bash
pip install pyinstaller
pyinstaller eyerest.spec
# L'exe se trouve dans dist/EyeRest.exe
```

---

## Structure des fichiers

```
eyerest/
├── main.py               # Point d'entrée
├── requirements.txt
├── eyerest.spec          # PyInstaller spec
└── app/
    ├── __init__.py
    ├── settings.py       # Persistance JSON (AppData\EyeRest\settings.json)
    ├── detector.py       # Détection fullscreen/jeu/vidéo (ctypes Windows API)
    ├── timer_engine.py   # Logique du minuteur (1 QTimer à 1 Hz)
    ├── break_overlay.py  # Overlay plein écran semi-transparent
    ├── main_window.py    # Interface principale (ring animé + settings)
    ├── tray.py           # Icône systray + menu
    └── startup.py        # Registre Windows démarrage auto
```

---

## Comment fonctionne la détection fullscreen ?

L'app utilise trois méthodes via l'API Windows (ctypes, aucun paquet tiers) :

1. **`SHQueryUserNotificationState`** — détecte les apps D3D (jeux), le mode présentation et "occupé"
2. **Comparaison rect fenêtre / rect moniteur** — détecte tout plein écran générique
3. **Liste de processus connus** — VLC, MPC-HC, PotPlayer, MPV…

Si la pause est supprimée, elle reste en file d'attente et se déclenche dès que le fullscreen se termine.

---

## Configuration sauvegardée dans

`%APPDATA%\EyeRest\settings.json`
