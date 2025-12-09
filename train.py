import spacy
import json
import random
import os
from spacy.tokens import DocBin
from spacy.cli.train import train
from spacy.cli.init_config import init_config

# CONFIGURATION
INPUT_FILE = "dataset.json"  # Le nouveau fichier
OUTPUT_DIR = "model_output"
TRAIN_FILE = "train.spacy"
DEV_FILE = "dev.spacy"

def convert_to_spacy(data, outfile):
    nlp = spacy.blank("fr")
    db = DocBin()
    
    success_count = 0
    
    for item in data:
        text = item['text']
        intent = item['intent']
        entities_list = item['entities'] # Format: [ ["Spotify", "APP_NAME"], ... ]

        doc = nlp.make_doc(text)
        ents = []
        
        # C'est ici que la magie opère : Alignement automatique
        for value, label in entities_list:
            # On cherche où commence le mot "Spotify" dans la phrase
            start = text.find(value)
            
            if start != -1:
                end = start + len(value)
                # On demande à spaCy de créer le span proprement
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span:
                    ents.append(span)
                else:
                    # Si spaCy n'arrive pas à aligner (rare avec cette méthode), on ignore silencieusement
                    pass
            
        # On attache les entités trouvées (en filtrant les conflits)
        doc.ents = spacy.util.filter_spans(ents)
        
        # On attache l'intent
        doc.cats[intent] = 1.0
        
        db.add(doc)
        success_count += 1
    
    db.to_disk(outfile)
    return success_count

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Erreur : Fichier {INPUT_FILE} introuvable.")
        print("Lance d'abord 'python generate_simple.py'")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Séparation Train/Test
    random.shuffle(data)
    split = int(len(data) * 0.8)
    train_data = data[:split]
    dev_data = data[split:]

    print(f"📊 Données : {len(data)} phrases.")
    print("🔄 Conversion et alignement automatique...")
    
    n_train = convert_to_spacy(train_data, TRAIN_FILE)
    n_dev = convert_to_spacy(dev_data, DEV_FILE)
    
    print(f"   - Train : {n_train} phrases prêtes")
    print(f"   - Dev   : {n_dev} phrases prêtes")

    # Création config
    print("⚙️  Config...")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    config_path = os.path.join(OUTPUT_DIR, "config.cfg")
    config = init_config(lang="fr", pipeline=["textcat", "ner"], optimize="efficiency")
    config.to_disk(config_path)

    # Entraînement
    print("🚀 Entraînement en cours...")
    try:
        train(
            config_path,
            OUTPUT_DIR,
            use_gpu=-1,
            overrides={
                "paths.train": TRAIN_FILE,
                "paths.dev": DEV_FILE,
                "training.max_epochs": 20
            }
        )
        print(f"✅ Terminé ! Modèle dans '{OUTPUT_DIR}/model-best'")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    main()