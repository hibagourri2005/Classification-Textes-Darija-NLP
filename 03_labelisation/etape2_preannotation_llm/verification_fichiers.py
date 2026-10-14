import os

def verifier_presence_fichiers(folder_input, folder_output):
    # Récupérer la liste des fichiers .json dans chaque dossier
    files_in = set([f for f in os.listdir(folder_input) if f.endswith('.json')])
    files_out = set([f for f in os.listdir(folder_output) if f.endswith('.json')])
    
    # Calculer la différence (ce qui est dans l'input mais pas dans l'output)
    manquants = files_in - files_out
    
    print(f"--- Rapport de présence des fichiers ---")
    print(f"📁 Dossier Input  : {len(files_in)} fichiers")
    print(f"📁 Dossier Output : {len(files_out)} fichiers")
    print("-" * 40)

    if not manquants:
        print("✅ Succès : Tous les fichiers de l'input sont présents dans l'output.")
    else:
        print(f"❌ ERREUR : {len(manquants)} fichier(s) manquant(s) dans l'output.")
        print("Liste des fichiers manquants :")
        for f in sorted(manquants):
            print(f"   - {f}")
            
    # Optionnel : Vérifier s'il y a des fichiers dans l'output qui ne devraient pas y être
    en_trop = files_out - files_in
    if en_trop:
        print(f"\nℹ️ Note : {len(en_trop)} fichier(s) supplémentaire(s) trouvé(s) dans l'output (non présents dans l'input).")

# Utilisation
# Remplacez par vos vrais noms de dossiers
_ici = os.path.dirname(os.path.abspath(__file__))
verifier_presence_fichiers(os.path.join(_ici, 'llm_batches'), os.path.join(_ici, 'Gemini_Chats_Export'))