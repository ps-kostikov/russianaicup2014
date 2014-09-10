import zipfile
import os

files = [
    'src/geometry.py',
    'strategies/best/MyStrategy.py',
]

with zipfile.ZipFile('strategy.zip', 'w') as out:
    for f in files:
        out.write(f, os.path.basename(f))
