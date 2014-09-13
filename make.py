import zipfile
import os

files = [
    'src/geometry.py',
    'src/geometry.py',
    'strategies/best/MyStrategy.py',
]

with zipfile.ZipFile('strategy.zip', 'w') as out:
    for src_file in filter(lambda f: f.endswith('.py'), os.listdir('src')):
        out.write(os.path.join('src', src_file), src_file)

    strategy_file = 'strategies/best/MyStrategy.py'
    out.write(strategy_file, os.path.basename(strategy_file))
