from fastapi.testclient import TestClient
from vision_api import app

client = TestClient(app)

print('GET /vision/health')
r = client.get('/vision/health')
print(r.status_code, r.json())

print('\nPOST /vision/predict (1x1 PNG)')
# 1x1 PNG
png = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
import base64
im = base64.b64decode(png)
files = {'file': ('test.png', im, 'image/png')}
r = client.post('/vision/predict', files=files)
print(r.status_code)
print(r.json())
