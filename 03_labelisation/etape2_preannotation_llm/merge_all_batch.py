import os
import json

def fusionner_outputs(folder_output, output_filename):
    all_data = []
    # Liste et tri des fichiers pour garder l'ordre (batch_0, batch_1...)
    files = sorted([f for f in os.listdir(folder_output) if f.endswith('.json')])
    
    print(f"Fusion de {len(files)} fichiers en cours...")

    for filename in files:
        file_path = os.path.join(folder_output, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            print(f"Erreur lors de la lecture de {filename}: {e}")

    # Sauvegarde du fichier global
    with open(output_filename, 'w', encoding='utf-8') as f_out:
        json.dump(all_data, f_out, indent=4, ensure_ascii=False)
    
    print(f"✅ Fusion terminée ! Fichier créé : {output_filename}")
    print(f"Nombre total d'éléments : {len(all_data)}")

# Utilisation
_ici = os.path.dirname(os.path.abspath(__file__))
fusionner_outputs(os.path.join(_ici, 'Gemini_Chats_Export'), os.path.join(_ici, 'merged_output.json'))