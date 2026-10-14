"""
clean_quotes.py
───────────────
Nettoie tous les guillemets des colonnes 'text' et 'text_normalized'
du dataset Darija pour éviter les problèmes lors de la labélisation
(TamperMonkey + Gemini Pro) et de la fusion des fichiers JSON.

Guillemets supprimés :
  "   (guillemet droit ASCII — LE plus problématique)
  "   (guillemet typographique gauche)
  "   (guillemet typographique droite)
  «   (guillemet français gauche)
  »   (guillemet français droite)

Usage :
    python clean_quotes.py <entree.csv> [sortie.csv]
"""

import pandas as pd
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────
import sys
if len(sys.argv) < 2:
    sys.exit("Usage : python clean_quotes.py <entree.csv> [sortie.csv]")
INPUT_FILE  = sys.argv[1]                                   # fichier source
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else str(Path(INPUT_FILE).with_name(Path(INPUT_FILE).stem + "_sans_guillemets.csv"))

# Colonnes à nettoyer
COLS_TO_CLEAN = ['text', 'text_normalized']

# Tous les guillemets à supprimer (remplacés par rien)
QUOTES_TO_REMOVE = [
    '"',   # guillemet droit ASCII  — le plus problématique
    '\u201c',  # "  guillemet typographique gauche
    '\u201d',  # "  guillemet typographique droite
    '\u00ab',  # «  guillemet français gauche
    '\u00bb',  # »  guillemet français droite
]

# ── Chargement ────────────────────────────────────────────────────────
print(f'Chargement : {INPUT_FILE}')
df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig', low_memory=False)
print(f'  {len(df):,} textes · {df.shape[1]} colonnes')

# ── Comptage avant nettoyage ──────────────────────────────────────────
print()
print('Guillemets détectés AVANT nettoyage :')
total_before = 0
for col in COLS_TO_CLEAN:
    for q in QUOTES_TO_REMOVE:
        n = df[col].astype(str).str.contains(q, regex=False, na=False).sum()
        if n > 0:
            total_before += n
            print(f'  {col:<20} {repr(q):<8} → {n:>4} textes concernés')

print(f'\n  Total lignes avec guillemets : {total_before}')

# ── Nettoyage ─────────────────────────────────────────────────────────
print()
print('Nettoyage en cours...')

df_clean = df.copy()

for col in COLS_TO_CLEAN:
    # Convertir en str pour éviter les NaN
    df_clean[col] = df_clean[col].astype(str)
    # Supprimer chaque type de guillemet
    for q in QUOTES_TO_REMOVE:
        df_clean[col] = df_clean[col].str.replace(q, '', regex=False)
    # Remplacer 'nan' (str) par chaîne vide si la colonne était vide
    df_clean[col] = df_clean[col].replace('nan', '')
    print(f'  ✓ {col} nettoyé')

# ── Comptage après nettoyage ──────────────────────────────────────────
print()
print('Guillemets restants APRÈS nettoyage :')
total_after = 0
for col in COLS_TO_CLEAN:
    for q in QUOTES_TO_REMOVE:
        n = df_clean[col].str.contains(q, regex=False, na=False).sum()
        if n > 0:
            total_after += n
            print(f'  {col:<20} {repr(q):<8} → {n:>4} (problème !)')

if total_after == 0:
    print('  ✓ Aucun guillemet restant — nettoyage complet')

# ── Vérification : exemples avant/après ───────────────────────────────
print()
print('Exemples de corrections appliquées :')
for col in COLS_TO_CLEAN:
    mask = df[col].astype(str).str.contains('"', regex=False, na=False)
    changed = df[mask].index[:3]
    for idx in changed:
        avant  = df.loc[idx, col]
        apres  = df_clean.loc[idx, col]
        if avant != apres:
            print(f'\n  [{col}]')
            print(f'    AVANT : {str(avant)[:100]}')
            print(f'    APRÈS : {str(apres)[:100]}')

# ── Sauvegarde ────────────────────────────────────────────────────────
print()
print(f'Sauvegarde : {OUTPUT_FILE}')
df_clean.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

# Vérification du fichier sauvegardé
df_check = pd.read_csv(OUTPUT_FILE, encoding='utf-8-sig', low_memory=False)
print(f'  ✓ {len(df_check):,} textes sauvegardés')
print(f'  ✓ {df_check.shape[1]} colonnes préservées')
print(f'  ✓ Colonnes : {df_check.columns.tolist()}')

print()
print('=' * 55)
print(f'  TERMINÉ')
print(f'  Guillemets supprimés : {total_before}')
print(f'  Fichier propre       : {OUTPUT_FILE}')
print('=' * 55)