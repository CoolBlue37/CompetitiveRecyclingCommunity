from pathlib import Path
from collections import Counter, defaultdict
from ultralytics import YOLO

WEIGHTS = "runs/classify/train-6/weights/best.pt"   # your trained weights
TEST_DIR = Path("trashnet")                       # folder with cardboard/, glass/, metal/, paper/, plastic/, trash/

def norm(s):
    return s.lower().replace(" ", "").replace("_", "")

# TrashNet folder -> model class name(s) that count as correct (compared after norm())
CORRECT = {
    "cardboard": {"cardboard"},
    "glass":     {"glass"},
    "metal":     {"metal"},
    "paper":     {"paper"},
    "plastic":   {"plastic"},
    "trash":     {"miscellaneoustrash"},   # adjust to match your class names
}
# CORRECT = {
#     "cardboard": {"Cardboard"},
#     "glass":     {"Glass"},
#     "metal":     {"Metal"},
#     "paper":     {"Paper"},
#     "plastic":   {"Plastic"},
#     "trash":     {"Textile Trash", "Miscellaneous Trash"},
#     "organic":   {"Food Organics, Vegetation"},
# }

def main():
    model = YOLO(WEIGHTS)
    print("model classes:", model.names)

    total, correct = Counter(), Counter()
    confused = defaultdict(Counter)

    for cls_dir in sorted(d for d in TEST_DIR.iterdir() if d.is_dir()):
        truth = norm(cls_dir.name)
        if truth not in CORRECT:
            print("skipping unknown folder:", cls_dir.name)
            continue
        imgs = [p for p in cls_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]

        for r in model.predict(imgs, stream=True, batch=8, verbose=False):
            pred = norm(r.names[r.probs.top1])
            total[truth] += 1
            confused[truth][pred] += 1
            if pred in CORRECT[truth]:
                correct[truth] += 1

    print()
    for t in total:
        print(f"{t:10s} {correct[t]}/{total[t]} = {correct[t]/total[t]:.0%}   top guesses: {confused[t].most_common(3)}")
    print(f"\noverall: {sum(correct.values())}/{sum(total.values())} = {sum(correct.values())/sum(total.values()):.0%}")

if __name__ == "__main__":
    main()