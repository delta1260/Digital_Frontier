import spacy
import random
import json # Module nécessaire pour lire le fichier
import sys
import os
from spacy.training.example import Example
from spacy.util import minibatch, compounding

# --- 1. CHARGEMENT DES DONNÉES DEPUIS LE FICHIER ---
filename = 'dataset.json'

print(f"📂 Chargement des données depuis '{filename}'...")

if not os.path.exists(filename):
    print(f"❌ ERREUR : Le fichier '{filename}' est introuvable.")
    print("Assurez-vous qu'il est dans le même dossier que ce script.")
    sys.exit(1)

try:
    with open(filename, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    print(f"✅ {len(raw_data)} exemples chargés avec succès.")
except json.JSONDecodeError:
    print(f"❌ ERREUR : Le fichier '{filename}' n'est pas un JSON valide.")
    sys.exit(1)

# Création du mapping Intention -> Action Plan
intent_map = {}
for item in raw_data:
    if 'action_plan' in item:
        intent_map[item['intention']] = item['action_plan']

def format_data_for_spacy(json_data):
    training_data = []
    
    for item in json_data:
        text = item['instruction']
        intent = item['intention']
        slots = item.get('slots', {})
        
        candidates = []
        
        # 1. On identifie toutes les positions possibles pour chaque slot
        for label, value in slots.items():
            if not isinstance(value, str): continue
            
            start = text.find(value)
            if start != -1:
                end = start + len(value)
                # On stocke (début, fin, label, longueur)
                candidates.append((start, end, label))
        
        # 2. TRI CRITIQUE : On traite les entités les plus longues d'abord !
        # Cela permet de garder "rapport.pdf" et d'ignorer juste ".pdf" s'il y a conflit.
        candidates.sort(key=lambda x: x[1] - x[0], reverse=True)
        
        final_entities = []
        occupied_indices = set()
        
        # 3. Filtrage des chevauchements
        for start, end, label in candidates:
            # Vérifie si l'un des caractères est déjà pris
            collision = False
            for i in range(start, end):
                if i in occupied_indices:
                    collision = True
                    break
            
            if not collision:
                final_entities.append((start, end, label))
                # On marque ces indices comme occupés
                for i in range(start, end):
                    occupied_indices.add(i)
        
        # Formatage final
        annotation = {
            "cats": {intent: 1.0},
            "entities": final_entities
        }
        
        # Mettre les autres intentions à 0
        all_intents = set(d['intention'] for d in json_data)
        for i in all_intents:
            if i != intent:
                annotation["cats"][i] = 0.0
                
        training_data.append((text, annotation))
        
    return training_data

# --- 2. CONFIGURATION DU MODÈLE ---
print("⚙️  Initialisation du modèle NLP...")
nlp = spacy.blank("fr")

# Création des composants du pipeline
if "textcat" not in nlp.pipe_names:
    textcat = nlp.add_pipe("textcat", last=True)
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)

# Préparation des données formatées
TRAIN_DATA = format_data_for_spacy(raw_data)

# Ajout des étiquettes (labels) au modèle
unique_intents = set(d['intention'] for d in raw_data)
for intent in unique_intents:
    textcat.add_label(intent)

for text, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# --- 3. ENTRAÎNEMENT ---
print(f"🚀 Démarrage de l'entraînement sur {len(TRAIN_DATA)} phrases...")

# On désactive les autres composants s'il y en a pour se concentrer sur NER et TextCat
other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in ["ner", "textcat"]]

with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    
    # 30 itérations pour bien apprendre vu la taille du dataset
    for i in range(30):
        random.shuffle(TRAIN_DATA)
        losses = {}
        # Batching dynamique pour l'efficacité
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        
        for batch in batches:
            texts, annotations = zip(*batch)
            example = []
            for j in range(len(texts)):
                doc = nlp.make_doc(texts[j])
                example.append(Example.from_dict(doc, annotations[j]))
            
            nlp.update(example, drop=0.5, losses=losses)
        
        # Affichage simple de la progression
        if i % 5 == 0:
            print(f"   Epoch {i}: Pertes -> {losses}")

print("\n✅ Entraînement terminé !")
print("Le modèle connaît maintenant toutes les intentions de votre fichier JSON.\n")

# --- 4. BOUCLE INTERACTIVE ---
print("="*50)
print("MODE TEST INTERACTIF")
print("Tapez une commande (ex: 'Trouve le budget 2024') ou 'exit' pour quitter.")
print("="*50)

while True:
    try:
        user_input = input("\n👤 Vous > ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Au revoir !")
            break
        
        if not user_input.strip():
            continue

        # Analyse
        doc = nlp(user_input)

        # 1. Détection de l'intention
        if doc.cats:
            intent = max(doc.cats, key=doc.cats.get)
            score = doc.cats[intent]
        else:
            intent = "UNKNOWN"
            score = 0.0

        # 2. Récupération du plan d'action
        action = intent_map.get(intent, "unknown_action")

        # Affichage
        print(f"🤖 Intention : {intent} ({score:.1%})")
        print(f"⚙️  Action    : {action}")
        
        # 3. Affichage des entités (Slots)
        if doc.ents:
            print("📦 Paramètres détectés :")
            for ent in doc.ents:
                print(f"   - [{ent.label_}] : {ent.text}")
        else:
            print("📦 Aucun paramètre spécifique.")

    except KeyboardInterrupt:
        print("\nArrêt.")
        break