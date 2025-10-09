import torch
from torchvision import transforms, datasets
from pathlib import Path
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

BASE = Path(__file__).resolve().parents[1]
SPLIT_DIR = BASE / 'data' / 'splits'
MODEL_PATH = BASE / 'ml' / 'models' / 'fruit_classifier.pt'
LOG_DIR = BASE / 'ml' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_model(path):
    data = torch.load(path, map_location='cpu')
    classes = data.get('classes')
    from torchvision import models
    import torch.nn as nn
    model = models.mobilenet_v2(pretrained=False)
    model.classifier[1] = nn.Linear(model.last_channel, len(classes))
    model.load_state_dict(data['model_state'])
    model.eval()
    return model, classes


def evaluate():
    if not MODEL_PATH.exists():
        print(f"Model not found: {MODEL_PATH}")
        return
    model, classes = load_model(MODEL_PATH)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    test_ds = datasets.ImageFolder(SPLIT_DIR / 'test', transform=transform)
    # Use num_workers=0 on Windows for compatibility
    from sys import platform as _platform
    num_workers = 0
    loader = torch.utils.data.DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=num_workers)

    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for imgs, labels in loader:
            outputs = model(imgs)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    acc = correct / total if total > 0 else 0.0
    print(f"Test accuracy: {acc:.4f} ({correct}/{total})")

    # confusion matrix and classification report
    try:
        from sklearn.metrics import confusion_matrix, classification_report
        cm = confusion_matrix(all_labels, all_preds)
        classes = test_ds.classes
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=False, fmt='d', xticklabels=classes, yticklabels=classes, cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title(f'Confusion Matrix (acc={acc:.4f})')
        cm_path = LOG_DIR / 'confusion_matrix.png'
        plt.tight_layout()
        plt.savefig(cm_path)
        print(f"Wrote confusion matrix to {cm_path}")

        report = classification_report(all_labels, all_preds, target_names=classes, output_dict=True)
        import csv
        report_path = LOG_DIR / 'classification_report.csv'
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['class','precision','recall','f1-score','support'])
            for cls in classes:
                r = report.get(cls, {})
                writer.writerow([cls, r.get('precision',0), r.get('recall',0), r.get('f1-score',0), r.get('support',0)])
        print(f"Wrote classification report to {report_path}")
    except Exception as e:
        print(f"Could not produce confusion matrix or report: {e}")


if __name__ == '__main__':
    evaluate()
