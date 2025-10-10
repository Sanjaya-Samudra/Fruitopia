"""Orchestrate multiple training experiments and pick the best model.

Usage: run with the project's venv python
python ml/experiments/run_experiments.py
"""
import subprocess
import json
from pathlib import Path
import shutil
import datetime
import os
import sys

BASE = Path(__file__).resolve().parents[2]
ML_DIR = BASE / 'ml'
MODEL_DIR = ML_DIR / 'models'
EXP_ROOT = ML_DIR / 'experiments'
LOG_DIR = ML_DIR / 'logs'
EXP_ROOT.mkdir(parents=True, exist_ok=True)

timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
out_root = EXP_ROOT / timestamp
out_root.mkdir(parents=True, exist_ok=True)

orig_model = MODEL_DIR / 'fruit_classifier.pt'
backup_dir = out_root / 'backup'
backup_dir.mkdir(parents=True, exist_ok=True)
if orig_model.exists():
    shutil.copy2(orig_model, backup_dir / 'fruit_classifier.pt')

# experiment definitions
EXPERIMENTS = [
    {'name': 'baseline-8', 'env': {'AUGMENT_LEVEL': 'baseline', 'CLASS_WEIGHT': '0', 'LR_SCHEDULER': ''}},
    {'name': 'aug-strong-8', 'env': {'AUGMENT_LEVEL': 'strong', 'CLASS_WEIGHT': '0', 'LR_SCHEDULER': ''}},
    {'name': 'class-weighted-8', 'env': {'AUGMENT_LEVEL': 'baseline', 'CLASS_WEIGHT': '1', 'LR_SCHEDULER': ''}},
    {'name': 'aug-weighted-8', 'env': {'AUGMENT_LEVEL': 'strong', 'CLASS_WEIGHT': '1', 'LR_SCHEDULER': ''}},
    {'name': 'lr-schedule-8', 'env': {'AUGMENT_LEVEL': 'baseline', 'CLASS_WEIGHT': '0', 'LR_SCHEDULER': 'cosine'}},
]

PY = sys.executable

results = []

for exp in EXPERIMENTS:
    name = exp['name']
    run_dir = out_root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoints = run_dir / 'checkpoints'
    checkpoints.mkdir(parents=True, exist_ok=True)

    # set EXP_MODEL_DIR so train writes models into this run folder
    env = os.environ.copy()
    env.update(exp['env'])
    env['EXP_MODEL_DIR'] = str(checkpoints)

    run_config = {'name': name, 'env': exp['env'], 'epochs': 8}
    with open(run_dir / 'run_config.json', 'w', encoding='utf-8') as f:
        json.dump(run_config, f, indent=2)

    print(f"Running experiment {name} -> {run_dir}")
    cmd = [PY, str(ML_DIR / 'train.py'), '--epochs', '8']
    proc = subprocess.run(cmd, env=env, cwd=str(BASE))
    if proc.returncode != 0:
        print(f"Experiment {name} failed (exit {proc.returncode}), skipping evaluation")
        results.append({'name': name, 'status': 'failed'})
        continue

    # copy train log and best model into run folder if present
    # evaluate: point evaluate.py at the run's best model
    best_model = checkpoints / 'fruit_classifier.best.pt'
    if not best_model.exists():
        # try the final model
        final_model = checkpoints / 'fruit_classifier.pt'
        if final_model.exists():
            best_model = final_model

    if best_model.exists():
        shutil.copy2(best_model, run_dir / best_model.name)
        # run evaluation using the copied model by temporarily swapping ml/models/fruit_classifier.pt
        temp_target = MODEL_DIR / 'fruit_classifier.pt'
        # backup current model in MODEL_DIR
        temp_backup = run_dir / 'model_dir_backup'
        temp_backup.mkdir(parents=True, exist_ok=True)
        if temp_target.exists():
            shutil.copy2(temp_target, temp_backup / 'fruit_classifier.pt')
        shutil.copy2(best_model, temp_target)
        # run evaluation
        eval_proc = subprocess.run([PY, str(ML_DIR / 'evaluate.py')], cwd=str(BASE))
        # move logs produced to run_dir
        for fname in ('classification_report.csv', 'confusion_matrix.png'):
            p = LOG_DIR / fname
            if p.exists():
                shutil.copy2(p, run_dir / fname)
        # restore model
        if (temp_backup / 'fruit_classifier.pt').exists():
            shutil.copy2(temp_backup / 'fruit_classifier.pt', temp_target)
    else:
        print(f"No model found for run {name}")

    results.append({'name': name, 'status': 'ok', 'run_dir': str(run_dir)})

# select best model by inspecting classification_report.csv for min per-class f1
import csv
best_run = None
best_min_f1 = -1.0

for r in results:
    if r.get('status') != 'ok':
        continue
    run_dir = Path(r['run_dir'])
    report = run_dir / 'classification_report.csv'
    if not report.exists():
        continue
    min_f1 = None
    with open(report, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            try:
                f1 = float(row[3])
            except Exception:
                continue
            if min_f1 is None or f1 < min_f1:
                min_f1 = f1
    if min_f1 is None:
        continue
    print(f"Run {r['name']} min f1: {min_f1}")
    if best_run is None or min_f1 > best_min_f1:
        best_min_f1 = min_f1
        best_run = r

if best_run:
    print(f"Best run selected: {best_run['name']} (min_f1={best_min_f1})")
    # copy its best model to ml/models/fruit_classifier.pt (backup already created)
    selected_run_dir = Path(best_run['run_dir'])
    for candidate in ('fruit_classifier.best.pt', 'fruit_classifier.pt'):
        p = selected_run_dir / candidate
        if p.exists():
            shutil.copy2(p, MODEL_DIR / 'fruit_classifier.pt')
            shutil.copy2(p, out_root / ('selected_' + candidate))
            break
    print(f"Selected model copied to {MODEL_DIR / 'fruit_classifier.pt'}")

    # also copy the selected run artifacts into top-level for quick inspection
    shutil.copytree(selected_run_dir, out_root / 'best_run', dirs_exist_ok=True)

print('Experiments finished. Artifacts: ', out_root)
print('Results summary:')
for r in results:
    print(r)
