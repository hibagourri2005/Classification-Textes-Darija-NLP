"""
pipeline/exporter.py
Export du dataset en CSV et JSON avec statistiques.
"""

import json
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


class DatasetExporter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def export(self, df: pd.DataFrame, csv_path: Path):
        """Export CSV + JSON + rapport stats."""
        # CSV principal
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info(f"✓ CSV exporté : {csv_path} ({len(df)} lignes)")

        # JSON (optionnel, utile pour Label Studio)
        json_path = csv_path.with_suffix(".json")
        records = df.to_dict(orient="records")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ JSON exporté : {json_path}")

        # Rapport stats
        self._write_stats(df, csv_path.parent / "stats_report.txt")

    def _write_stats(self, df: pd.DataFrame, path: Path):
        """Génère un rapport textuel des statistiques du dataset."""
        lines = [
            "=" * 60,
            "RAPPORT DU DATASET DARIJA",
            "=" * 60,
            f"Total textes          : {len(df)}",
            f"Textes uniques        : {df['text'].nunique()}",
            f"Longueur moy. (chars) : {df['text'].str.len().mean():.1f}",
            f"Longueur med. (chars) : {df['text'].str.len().median():.1f}",
            "",
            "--- Par domaine ---",
        ]
        for domain, count in df["domain"].value_counts().items():
            pct = count / len(df) * 100
            lines.append(f"  {domain:20s} : {count:6d} ({pct:.1f}%)")

        lines += ["", "--- Par type de source ---"]
        for src, count in df["source_type"].value_counts().items():
            pct = count / len(df) * 100
            lines.append(f"  {src:30s} : {count:6d} ({pct:.1f}%)")

        lines += ["", "--- Par chaîne (top 20) ---"]
        for ch, count in df["channel_name"].value_counts().head(20).items():
            lines.append(f"  {ch:30s} : {count:6d}")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"✓ Rapport stats : {path}")
