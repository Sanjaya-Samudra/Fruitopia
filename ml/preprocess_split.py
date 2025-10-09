import json
import random
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / 'data' / 'FruitImageDataset'
OUT_DIR = BASE / 'data' / 'splits'
META_FILE = BASE / 'ml' / 'metadata.json'
LABELS_FILE = BASE / 'ml' / 'labels.json'


def load_metadata():
    if META_FILE.exists():
        with open(META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # fallback: discover classes from data dir
    classes = [p.name for p in sorted(DATA_DIR.iterdir()) if p.is_dir()]
    return {'classes': classes}


def make_dirs():
    for split in ('train', 'val', 'test'):
        (OUT_DIR / split).mkdir(parents=True, exist_ok=True)


def split_dataset(train_ratio=0.7, val_ratio=0.15, seed=1337):
    meta = load_metadata()
    classes = meta.get('classes', [])
    class_to_idx = {c: i for i, c in enumerate(classes)}
    make_dirs()
    random.seed(seed)

    summary = { 'train': {}, 'val': {}, 'test': {} }
    totals = {'train': 0, 'val': 0, 'test': 0}

    for cls in classes:
        src = DATA_DIR / cls
        imgs = [p for p in src.iterdir() if p.is_file()]
        n = len(imgs)
        if n == 0:
            continue
        imgs_sorted = sorted(imgs)
        random.shuffle(imgs_sorted)

        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        # ensure at least 1 image in train if possible
        if n_train == 0 and n >= 1:
            n_train = 1
        # make sure we don't exceed available
        n_val = min(n_val, n - n_train)
        n_test = n - n_train - n_val

        train_imgs = imgs_sorted[:n_train]
        val_imgs = imgs_sorted[n_train:n_train + n_val]
        test_imgs = imgs_sorted[n_train + n_val:]

        for split_name, split_imgs in [('train', train_imgs), ('val', val_imgs), ('test', test_imgs)]:
            out_class_dir = OUT_DIR / split_name / cls
            out_class_dir.mkdir(parents=True, exist_ok=True)
            for p in split_imgs:
                shutil.copy2(p, out_class_dir / p.name)
            summary[split_name][cls] = len(split_imgs)
            totals[split_name] += len(split_imgs)

    # write labels
    with open(LABELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(class_to_idx, f, indent=2)

    print(f"Wrote labels to {LABELS_FILE}")
    print(f"Splits written to {OUT_DIR}")
    print("Summary per split:")
    for split in ('train', 'val', 'test'):
        print(f"  {split}: {totals[split]} images")

    # print per-class counts for first 10 classes for brevity and total counts all
    for split in ('train', 'val', 'test'):
        print(f"\nTop classes in {split}:")
        items = sorted(summary[split].items(), key=lambda kv: -kv[1])
        for cls, cnt in items[:10]:
            print(f"  {cls}: {cnt}")


if __name__ == '__main__':
    split_dataset()
