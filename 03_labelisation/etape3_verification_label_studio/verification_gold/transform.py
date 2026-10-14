"""
Transforme mon_data_final.json → label_studio_tasks.json
Compatible avec le labeling_config.xml fourni.

Usage: python transform.py mon_data_final.json
"""
import json, sys

input_file  = sys.argv[1] if len(sys.argv) > 1 else "mon_data_final.json"
output_file = "label_studio_tasks.json"

with open(input_file, encoding='utf-8') as f:
    data = json.load(f)

tasks = []
for entry in data:
    label = entry.get("label", "")
    tasks.append({
        "data": {
            "text":         entry.get("text", ""),
            "entry_id":     entry.get("id", ""),
            "manuel_label": label          # ← affiché dans le bandeau bleu
        },
        "predictions": [{
            "model_version": "gemini-pro",
            "result": [{
                "from_name": "label",
                "to_name":   "text",
                "type":      "choices",
                "value":     {"choices": [label]}
            }]
        }] if label else []
    })

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)

print(f"✅ {len(tasks)} entrées transformées → {output_file}")