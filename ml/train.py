import os
import torch
import torch.nn as nn
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader
from pathlib import Path
import argparse
import json
import platform
import csv
import random
import numpy as np

BASE = Path(__file__).resolve().parents[1]
SPLIT_DIR = BASE / 'data' / 'splits'
# Allow experiments to set a custom model directory so multiple runs don't clobber each other
EXP_MODEL_DIR = os.environ.get('EXP_MODEL_DIR')
if EXP_MODEL_DIR:
    MODEL_DIR = Path(EXP_MODEL_DIR)
else:
    MODEL_DIR = BASE / 'ml' / 'models'
LOG_DIR = BASE / 'ml' / 'logs'
MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / 'fruit_classifier.pt'


def get_dataloaders(img_size=224, batch_size=16):
    # Allow selecting augmentation intensity via environment variable AUGMENT_LEVEL
    augment_level = os.environ.get('AUGMENT_LEVEL', 'baseline')
    if augment_level == 'none':
        train_transforms = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
        ])
    elif augment_level == 'strong':
        train_transforms = transforms.Compose([
            transforms.RandomResizedCrop(img_size, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.1),
            transforms.ToTensor(),
        ])
    else:
        # baseline
        train_transforms = transforms.Compose([
            transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.1, 0.1, 0.1, 0.05),
            transforms.ToTensor(),
        ])

    val_transforms = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
    ])

    # Remove any empty class directories (ImageFolder requires at least one file per class)
    for split in ('train', 'val'):
        split_path = SPLIT_DIR / split
        if not split_path.exists():
            continue
        for cls_dir in list(split_path.iterdir()):
            if cls_dir.is_dir():
                files = [p for p in cls_dir.iterdir() if p.is_file()]
                if len(files) == 0:
                    # remove empty class directory
                    try:
                        cls_dir.rmdir()
                    except Exception:
                        pass

    train_ds = datasets.ImageFolder(SPLIT_DIR / 'train', transform=train_transforms)
    val_ds = datasets.ImageFolder(SPLIT_DIR / 'val', transform=val_transforms)

    # On Windows, using num_workers>0 can cause issues in some environments
    num_workers = 0 if platform.system().lower().startswith('win') else 2
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return train_loader, val_loader, train_ds.classes


def train(epochs=3, lr=1e-3, device='cpu', batch_size=16, seed=1337):
    # reproducibility
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    train_loader, val_loader, classes = get_dataloaders(batch_size=batch_size)
    num_classes = len(classes)
    model = models.mobilenet_v2(pretrained=True)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    model.to(device)

    # Optionally use class-weighted loss (enable by setting env CLASS_WEIGHT=1)
    use_class_weight = os.environ.get('CLASS_WEIGHT', '0') == '1'
    if use_class_weight:
        # compute weights from train dataset class counts
        try:
            counts = np.bincount(train_loader.dataset.targets)
            weights = 1.0 / (counts + 1e-6)
            weights = weights / weights.sum() * len(weights)
            class_weights = torch.tensor(weights, dtype=torch.float32, device=device)
            criterion = nn.CrossEntropyLoss(weight=class_weights)
            print(f"Using class-weighted loss: {class_weights}")
        except Exception as e:
            print(f"Could not compute class weights, falling back to unweighted loss: {e}")
            criterion = nn.CrossEntropyLoss()
    else:
        criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Optional LR scheduler (enable via LR_SCHEDULER env var, e.g., 'cosine' or 'step')
    lr_scheduler = os.environ.get('LR_SCHEDULER', '').lower()
    scheduler = None
    if lr_scheduler == 'cosine':
        try:
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, epochs))
            print("Using CosineAnnealingLR scheduler")
        except Exception:
            scheduler = None
    elif lr_scheduler == 'step':
        try:
            scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)
            print("Using StepLR scheduler")
        except Exception:
            scheduler = None

    best_val_acc = 0.0
    MODEL_PATH = MODEL_DIR / 'fruit_classifier.pt'
    best_path = MODEL_DIR / 'fruit_classifier.best.pt'

    log_file = LOG_DIR / 'train_log.csv'
    if not log_file.exists():
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['epoch', 'train_loss', 'val_acc', 'val_correct', 'val_total', 'model_path'])

    for epoch in range(epochs):
        model.train()
        running = 0
        for imgs, labels in train_loader:
            imgs = imgs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running += loss.item()
        avg = running / max(1, len(train_loader))
        print(f"Epoch {epoch+1}/{epochs} train loss: {avg:.4f}")

        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs = imgs.to(device)
                labels = labels.to(device)
                outputs = model(imgs)
                preds = outputs.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        val_acc = correct / total if total > 0 else 0.0
        print(f"Epoch {epoch+1} val acc: {val_acc:.4f} ({correct}/{total})")

        # checkpoint best
        epoch_path = MODEL_DIR / f'fruit_classifier_epoch_{epoch+1}.pt'
        torch.save({'model_state': model.state_dict(), 'classes': classes}, epoch_path)
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({'model_state': model.state_dict(), 'classes': classes}, best_path)
            print(f"New best model saved to {best_path} (val_acc={best_val_acc:.4f})")

        if scheduler is not None:
            try:
                scheduler.step()
            except Exception:
                pass

        # log
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([epoch + 1, f"{avg:.6f}", f"{val_acc:.6f}", correct, total, str(epoch_path)])

    # Save last model as well
    torch.save({'model_state': model.state_dict(), 'classes': classes}, MODEL_PATH)
    print(f"Saved final model to {MODEL_PATH}")
    if best_path.exists():
        print(f"Best model available at {best_path} (val_acc={best_val_acc:.4f})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-3)
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    train(epochs=args.epochs, lr=args.lr, device=device)
