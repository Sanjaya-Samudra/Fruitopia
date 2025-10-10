import torch
from pathlib import Path
print('Python executable:', __import__('sys').executable)
try:
    print('torch version:', torch.__version__)
except Exception as e:
    print('torch import error:', repr(e))

MODEL_PATH = Path(__file__).resolve().parents[1] / 'ml' / 'models' / 'fruit_classifier.pt'
print('model path:', MODEL_PATH)
if not MODEL_PATH.exists():
    print('model file missing')
    raise SystemExit(2)

try:
    data = torch.load(str(MODEL_PATH), map_location='cpu')
    print('checkpoint keys:', list(data.keys()))
    classes = data.get('classes')
    print('classes:', type(classes), 'len=', len(classes) if classes else 0)
    # try to construct mobilenet and load
    from torchvision import models
    import torch.nn as nn
    model = models.mobilenet_v2(pretrained=False)
    model.classifier[1] = nn.Linear(model.last_channel, len(classes))
    model.load_state_dict(data['model_state'])
    print('model load OK')
except Exception as e:
    import traceback
    print('error while loading checkpoint:')
    traceback.print_exc()
    raise
