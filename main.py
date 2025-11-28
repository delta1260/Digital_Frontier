# Nom de ton fichier actuel (celui généré précédemment)
fichier_entree = 'dataset.json' 
# Nom du nouveau fichier que tu veux créer
fichier_sortie = 'dataset.json'

try:
    with open(fichier_entree, 'r', encoding='utf-8') as f_in:
        # On lit toutes les lignes et on enlève les espaces vides autour
        lignes = [line.strip() for line in f_in if line.strip()]

    # On construit le JSON final manuellement pour garder le formatage
    # On rejoint toutes les lignes avec une virgule et un saut de ligne ",\n"
    contenu_final = "[\n" + ",\n".join(lignes) + "\n]"

    with open(fichier_sortie, 'w', encoding='utf-8') as f_out:
        f_out.write(contenu_final)

    print(f"✅ Succès ! Fichier converti : {fichier_sortie}")
    print(f"Nombre d'entrées : {len(lignes)}")

except FileNotFoundError:
    print(f"❌ Erreur : Le fichier '{fichier_entree}' est introuvable.")