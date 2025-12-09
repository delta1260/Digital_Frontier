import json
import random
import re

# ==========================================
# 1. DICTIONNAIRE DES ENTITÉS
# ==========================================
ENTITIES = {
    "APP_NAME": [
        "Word", "Excel", "PowerPoint", "Spotify", "Discord", "Chrome", "Firefox", "Edge",
        "Visual Studio Code", "Teams", "Outlook", "Calculatrice", "Steam",
        "Netflix", "OneNote", "Zoom", "Photoshop", "Notion", "Trello", "VLC", "WhatsApp"
    ],
    "WEBSITE_NAME": [
        "Google", "YouTube", "Moodle", "Wikipedia", "ChatGPT", "Amazon", "Facebook",
        "Twitter", "Instagram", "LinkedIn", "Mon ENT", "Gmail", "GitHub", "StackOverflow"
    ],
    "SEARCH_QUERY": [
        "les animaux d'Afrique", "la météo de demain", "recette de crêpes",
        "cours de marketing", "date de la révolution française", "exercices de maths",
        "résultats foot", "comment apprendre python", "c'est quoi le NLP",
        "comparatif smartphone", "résumé du livre 1984"
    ],
    "DEVICE_NAME": [
        "casque", "souris", "écran", "moniteur", "télé", "projecteur", 
        "enceinte", "bluetooth", "imprimante", "webcam", "AirPods"
    ],
    "WINDOW_POSITION": [
        "gauche", "droite", "haut", "bas", "plein écran", 
        "coin haut gauche", "coin bas droite", "centre"
    ],
    "TIME_DURATION": [
        "10 minutes", "5 min", "une heure", "30 secondes", "25 min", "2h", "un quart d'heure"
    ],
    "TIME_POINT": [
        "8h00", "demain", "midi", "maintenant", "ce soir", "18h30", "lundi prochain", "14h"
    ],
    "VALUE_NUMBER": [
        "10%", "50%", "100%", "20", "trente", "max", "minimum", "à fond", "un peu", "moyen"
    ],
    "DESKTOP_REF": [
        "suivant", "précédent", "2", "3", "travail", "jeux", "droite", "gauche"
    ],
    "SETTING_PAGE": [
        "Wifi", "Bluetooth", "Son", "Mise à jour", "Affichage", "Batterie", "Confidentialité"
    ],
    "CALENDAR_EVENT": [
        "Dentiste", "Réunion", "Cours de maths", "Examen", "Anniversaire", "Apéro"
    ],
    "SCREENSHOT_TYPE": [
        "écran", "fenêtre", "zone", "complet"
    ]
}

# ==========================================
# 2. TEMPLATES
# ==========================================
TEMPLATES = {
    "os.open_app": ["Ouvre {APP_NAME}", "Lance {APP_NAME}", "Démarre {APP_NAME}", "Je veux utiliser {APP_NAME}"],
    "os.close_app": ["Ferme {APP_NAME}", "Quitte {APP_NAME}", "Arrête {APP_NAME}"],
    "os.force_quit_app": ["Force l'arrêt de {APP_NAME}", "Tue le processus {APP_NAME}", "Kill {APP_NAME}"],
    "os.browser_open_url": ["Va sur {WEBSITE_NAME}", "Ouvre le site {WEBSITE_NAME}", "Connecte-moi à {WEBSITE_NAME}"],
    "os.browser_search": ["Cherche {SEARCH_QUERY}", "Google {SEARCH_QUERY}", "Trouve des infos sur {SEARCH_QUERY}"],
    "os.browser_new_tab": ["Nouvel onglet", "Ouvre un onglet"],
    "os.browser_close_tab": ["Ferme l'onglet", "Ferme cette page"],
    "os.browser_incognito": ["Ouvre {WEBSITE_NAME} en privé", "Mode incognito"],
    "os.snap_window": ["Mets ça à {WINDOW_POSITION}", "Ancre {APP_NAME} à {WINDOW_POSITION}", "Colle la fenêtre à {WINDOW_POSITION}"],
    "os.maximize_window": ["Mets en plein écran", "Maximise la fenêtre"],
    "os.show_desktop": ["Montre le bureau", "Cache tout"],
    "os.volume_set": ["Mets le son à {VALUE_NUMBER}", "Volume {VALUE_NUMBER}"],
    "os.volume_up": ["Monte le son", "Augmente le volume", "Plus fort"],
    "os.volume_down": ["Baisse le son", "Diminue le volume", "Moins fort"],
    "os.brightness_set": ["Luminosité à {VALUE_NUMBER}", "Eclaire l'écran à {VALUE_NUMBER}"],
    "os.brightness_up": ["Augmente la luminosité", "Eclaire plus l'écran"],
    "os.brightness_down": ["Baisse la luminosité", "Assombris l'écran"],
    "os.system_shutdown": ["Éteins le PC", "Arrêt système"],
    "os.system_restart": ["Redémarre", "Reboot le PC"],
    "os.system_lock": ["Verrouille la session", "Lock screen"],
    "os.wifi_on": ["Active le wifi", "Mets internet"],
    "os.wifi_off": ["Coupe le wifi", "Désactive internet"],
    "os.bluetooth_connect": ["Connecte mon {DEVICE_NAME}", "Appaire le {DEVICE_NAME}"],
    "os.bluetooth_disconnect": ["Déconnecte le {DEVICE_NAME}", "Oublie le {DEVICE_NAME}"],
    "os.timer_start": ["Minuteur de {TIME_DURATION}", "Timer {TIME_DURATION}", "Lance un chrono de {TIME_DURATION}"],
    "os.alarm_create": ["Réveille-moi à {TIME_POINT}", "Alarme {TIME_POINT}"],
    "os.calendar_add_event": ["Ajoute {CALENDAR_EVENT} pour {TIME_POINT}", "Rappelle-moi {CALENDAR_EVENT} à {TIME_POINT}"],
    "os.media_play": ["Play", "Lecture", "Reprends la musique"],
    "os.media_pause": ["Pause", "Mets en pause"],
    "os.media_next": ["Suivant", "Next", "Chanson suivante"],
    "os.media_prev": ["Précédent", "Retour"],
    "os.screenshot_capture": ["Capture {SCREENSHOT_TYPE}", "Fais un screenshot {SCREENSHOT_TYPE}"],
    "os.open_settings": ["Ouvre les paramètres {SETTING_PAGE}", "Réglages {SETTING_PAGE}"],
    "os.clipboard_copy": ["Copier", "Copie ça"],
    "os.clipboard_paste": ["Coller", "Colle ici"]
}

# ==========================================
# 3. GÉNÉRATEUR SIMPLE
# ==========================================
def generate_simple_dataset(samples_per_template=50):
    dataset = []
    print(f"🔄 Génération du dataset simplifié...")
    
    for intent, patterns in TEMPLATES.items():
        for pattern in patterns:
            for _ in range(samples_per_template):
                text = pattern
                # On stocke juste [valeur, label] sans position
                entities_list = []
                
                # Fonction interne pour remplacer et stocker
                def replace_match(match):
                    label = match.group(1)
                    if label in ENTITIES:
                        value = random.choice(ENTITIES[label])
                        entities_list.append((value, label))
                        return value
                    return match.group(0)

                # Remplacement magique via Regex
                text = re.sub(r"\{(\w+)\}", replace_match, text)
                
                dataset.append({
                    "text": text,
                    "intent": intent,
                    "entities": entities_list # Pas de start/end, juste la liste !
                })
    
    return dataset

if __name__ == "__main__":
    data = generate_simple_dataset(samples_per_template=60) # Tu peux augmenter ici
    random.shuffle(data)
    
    filename = "dataset.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Terminé ! {len(data)} phrases générées dans '{filename}'.")
    print("Ce fichier est propre : pas de chiffres, pas de prises de tête.")