import random, shutil
from pathlib import Path
import splitfolders

random.seed(42)
OUT, CAP = Path("data_all"), 1000

SOURCES = [
    ("RealWaste/Cardboard", "cardboard", 400), ("RealWaste/Glass", "glass", 400),
    ("RealWaste/Metal", "metal", 400),         ("RealWaste/Paper", "paper", 400),
    ("RealWaste/Plastic", "plastic", 400),
    ("RealWaste/Miscellaneous Trash", "trash", 400),
    ("RealWaste/Textile Trash", "trash", 400),
    ("RealWaste/Food Organics", "organic", 400),
    ("RealWaste/Vegetation", "organic", 400)
]

by_class = {}
for folder, cls, n in SOURCES:
    files = [p for p in Path(folder).glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    random.shuffle(files)
    by_class.setdefault(cls, []).extend((f, folder.split("/")[0]) for f in files[:n])

for cls, items in by_class.items():
    random.shuffle(items)
    (OUT / cls).mkdir(parents=True, exist_ok=True)
    for f, src in items[:CAP]:
        shutil.copy(f, OUT / cls / f"{src}_{f.name}")
    print(cls, min(len(items), CAP))

splitfolders.ratio("data_all", output="data", seed=42, ratio=(0.8, 0.2))