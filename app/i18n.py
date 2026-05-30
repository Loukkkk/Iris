"""
Internationalization — French and English.
"""

STRINGS = {
    "fr": {
        "app_name": "Iris",
        "app_subtitle": "Protection des yeux",
        "working": "🟢  En cours de travail",
        "on_break": "🌿  Pause — regardez au loin",
        "suppressed": "🎮  Fullscreen détecté — pause en attente",
        "paused": "⏸  En pause",
        "config_title": "Configuration",
        "work_interval": "Travail entre les pauses",
        "break_duration": "Durée de la pause",
        "hint": "📏  Regardez à 20 pieds (6 m) — règle 20-20-20",
        "options_title": "Options",
        "opt_fullscreen": "Ne pas alerter en plein écran / jeu / vidéo",
        "opt_background": "Réduire en arrière-plan à la fermeture",
        "opt_startup": "Démarrer avec Windows",
        "opt_startup_min": "   ↳  Démarrer directement en arrière-plan",
        "opt_language": "Langue / Language",
        "btn_pause": "⏸  Pause",
        "btn_resume": "▶  Reprendre",
        "btn_break_now": "Pause maintenant",
        "footer": "Règle 20-20-20 — toutes les 20 min, 20 sec à 20 pieds (6 m)",
        "tray_open": "Ouvrir Iris",
        "tray_pause": "⏸  Mettre en pause",
        "tray_resume": "▶  Reprendre",
        "tray_break": "🌿  Pause maintenant",
        "tray_quit": "Quitter",
        "break_title": "Pause pour vos yeux",
        "break_subtitle": "Regardez à 20 pieds (6 m) minimum",
        "break_skip": "Passer",
        "popup_startup_title": "Démarrage avec Windows activé",
        "popup_startup_body": "Si vous déplacez l'exécutable vers un autre dossier, relancez-le une fois pour que le démarrage automatique pointe vers le bon emplacement.",
        "popup_ok": "OK, compris",
        "min": " min",
        "sec": " sec",
        "before_break": "avant la pause",
        "seconds_left": "secondes restantes",
        "waiting": "en attente…",
        "tray_next": "Iris — prochaine pause dans",
        "tray_waiting": "Iris — en attente (fullscreen détecté)",
    },
    "en": {
        "app_name": "Iris",
        "app_subtitle": "Eye protection",
        "working": "🟢  Working",
        "on_break": "🌿  Break — look into the distance",
        "suppressed": "🎮  Fullscreen detected — break pending",
        "paused": "⏸  Paused",
        "config_title": "Configuration",
        "work_interval": "Work interval",
        "break_duration": "Break duration",
        "hint": "📏  Look 20 feet (6 m) away — 20-20-20 rule",
        "options_title": "Options",
        "opt_fullscreen": "Skip alert during fullscreen / games / video",
        "opt_background": "Minimize to tray on close",
        "opt_startup": "Start with Windows",
        "opt_startup_min": "   ↳  Start directly in background",
        "opt_language": "Langue / Language",
        "btn_pause": "⏸  Pause",
        "btn_resume": "▶  Resume",
        "btn_break_now": "Break now",
        "footer": "20-20-20 rule — every 20 min, look 20 ft away for 20 sec",
        "tray_open": "Open Iris",
        "tray_pause": "⏸  Pause",
        "tray_resume": "▶  Resume",
        "tray_break": "🌿  Break now",
        "tray_quit": "Quit",
        "break_title": "Eye break",
        "break_subtitle": "Look at least 20 feet (6 m) away",
        "break_skip": "Skip",
        "popup_startup_title": "Start with Windows enabled",
        "popup_startup_body": "If you move the executable to another folder, relaunch it once so the startup entry points to the correct location.",
        "popup_ok": "Got it",
        "min": " min",
        "sec": " sec",
        "before_break": "before break",
        "seconds_left": "seconds left",
        "waiting": "waiting…",
        "tray_next": "Iris — next break in",
        "tray_waiting": "Iris — waiting (fullscreen detected)",
    }
}


def detect_os_language() -> str:
    """Detect OS language, return 'fr' or 'en'."""
    try:
        import locale
        lang = locale.getdefaultlocale()[0] or ""
        if lang.startswith("fr"):
            return "fr"
    except Exception:
        pass
    try:
        import ctypes
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        # 0x040C = French France, 0x080C = French Belgium, etc.
        primary = lang_id & 0xFF
        if primary == 0x0C:  # French
            return "fr"
    except Exception:
        pass
    return "en"


class I18n:
    def __init__(self, settings):
        self._settings = settings
        # First launch: detect OS language
        if settings.get("language") is None:
            lang = detect_os_language()
            settings.set("language", lang)
        self._lang = settings.get("language", "en")

    def t(self, key: str) -> str:
        return STRINGS.get(self._lang, STRINGS["en"]).get(key, key)

    def set_language(self, lang: str):
        self._lang = lang
        self._settings.set("language", lang)

    @property
    def lang(self):
        return self._lang
