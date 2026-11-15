import random, shutil
from pathlib import Path

random.seed(42)
OUT, CAP = Path("data_all"), 350

# (source folder, your class, max images from this source)
SOURCES = [
    ("TrashNet/cardboard", "cardboard", 400), ("TrashNet/glass", "glass", 400),
    ("TrashNet/metal", "metal", 400),         ("TrashNet/paper", "paper", 400),
    ("TrashNet/plastic", "plastic", 400),     ("TrashNet/trash", "trash", 400),
    ("RealWaste/Cardboard", "cardboard", 100), ("RealWaste/Glass", "glass", 100),
    ("RealWaste/Metal", "metal", 100),         ("RealWaste/Paper", "paper", 100),
    ("RealWaste/Plastic", "plastic", 100),
    ("RealWaste/Miscellaneous Trash", "trash", 300),
    ("RealWaste/Textile Trash", "trash", 150),
    ("RealWaste/Food Organics", "organic", 350),
    # ("mine/empty", "empty", 100),   # your own photos: add these per class too
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

# print(len(by_class.items()))