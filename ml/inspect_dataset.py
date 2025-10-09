import os
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'FruitImageDataset'
OUT_FILE = Path(__file__).resolve().parents[0] / 'metadata.json'


def inspect_dataset(data_dir: Path):
    classes = []
    counts = {}
    samples = {}
    for entry in sorted(data_dir.iterdir()):
        if entry.is_dir():
            imgs = [p.name for p in entry.iterdir() if p.is_file()]
            counts[entry.name] = len(imgs)
            samples[entry.name] = imgs[:5]
            classes.append(entry.name)
    return classes, counts, samples


def main():
    if not DATA_DIR.exists():
        print(f"Data dir not found: {DATA_DIR}")
        return
    classes, counts, samples = inspect_dataset(DATA_DIR)
    meta = {
        'dataset_path': str(DATA_DIR),
        'num_classes': len(classes),
        'classes': classes,
        'counts': counts,
        'samples': samples,
    }
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    print(f"Wrote metadata to {OUT_FILE}")


if __name__ == '__main__':
    main()
