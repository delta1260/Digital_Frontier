import spacy
import sys

# Codes couleurs pour rendre le terminal lisible
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    model_path = "model_output/model-best"
    print(f"{Colors.HEADER}⏳ Chargement du modèle depuis '{model_path}'...{Colors.ENDC}")
    
    try:
        nlp = spacy.load(model_path)
        print(f"{Colors.GREEN}✅ Modèle chargé ! Tape 'exit' pour quitter.{Colors.ENDC}")
    except OSError:
        print(f"{Colors.RED}❌ Impossible de trouver le modèle.{Colors.ENDC}")
        print("As-tu bien lancé 'python train.py' avant ?")
        sys.exit(1)

    print("-" * 60)

    while True:
        try:
            text = input(f"\n{Colors.BLUE}Phrase : {Colors.ENDC}")
        except KeyboardInterrupt:
            break
        
        if text.lower() in ["exit", "quit", "q"]:
            break
        if not text.strip():
            continue

        # Analyse par le modèle
        doc = nlp(text)

        # 1. Extraction de l'INTENT
        if doc.cats:
            # On cherche la catégorie avec le score le plus élevé
            best_intent = max(doc.cats, key=doc.cats.get)
            score = doc.cats[best_intent]
            
            # Affichage graphique de la confiance
            confidence_percent = int(score * 100)
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            color = Colors.GREEN if score > 0.7 else Colors.YELLOW
            if score < 0.4: color = Colors.RED

            print(f"🎯 Intent : {Colors.BOLD}{best_intent}{Colors.ENDC}")
            print(f"📊 Confiance : {color}[{bar}] {confidence_percent}%{Colors.ENDC}")
        else:
            print(f"{Colors.RED}⚠️ Aucun intent détecté.{Colors.ENDC}")

        # 2. Extraction des ENTITÉS
        if doc.ents:
            print(f"🧩 Entités ({len(doc.ents)}) :")
            for ent in doc.ents:
                print(f"   • {Colors.YELLOW}{ent.label_}{Colors.ENDC} : \"{ent.text}\"")
        else:
            print(f"🧩 Entités : {Colors.BOLD}Aucune{Colors.ENDC}")

if __name__ == "__main__":
    main()