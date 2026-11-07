import csv
import sys

from settings import LINE_A, LINE_B

CSV_PATH = "output/tracks.csv"


def side(line, point):
    (x1, y1), (x2, y2) = line
    qx, qy = point
    cross = (x2 - x1) * (qy - y1) - (y2 - y1) * (qx - x1)
    return cross >= 0


def load_rows(csv_path):
    rows = []
    with open(csv_path, newline="") as file:
        for row in csv.DictReader(file):
            rows.append({
                "time": float(row["time"]),
                "track_id": int(row["track_id"]),
                "type": row["type"],
                "x": int(row["x"]),
                "y": int(row["y"]),
            })
    return rows


def find_crossings(rows):
    tracks = {}
    for row in rows:
        tid = row["track_id"]
        point = (row["x"], row["y"])


        if tid not in tracks:
            tracks[tid] = {"type": row["type"], "prev": point, "A": None, "B": None}
            continue

        track = tracks[tid]
        for name, line in (("A", LINE_A), ("B", LINE_B)):
            moved_across = side(line, track["prev"]) != side(line, point)
            if moved_across and track[name] is None:
                track[name] = row["time"]

        track["prev"] = point
    return tracks


def summarise(tracks):
    counts = {}
    wrong_way = {}
    for track in tracks.values():
        if track["A"] is None:
            continue

        kind = track["type"]
        counts[kind] = counts.get(kind, 0) + 1


        if track["B"] is not None and track["B"] < track["A"]:
            wrong_way[kind] = wrong_way.get(kind, 0) + 1
    return counts, wrong_way


def main():
    try:
        rows = load_rows(CSV_PATH)
    except FileNotFoundError:
        sys.exit(f"{CSV_PATH} not found. Run track_dump.py first.")

    tracks = find_crossings(rows)
    counts, wrong_way = summarise(tracks)

    total = sum(counts.values())
    total_wrong = sum(wrong_way.values())
    share = total_wrong / total * 100 if total else 0

    print(f"Vehicles crossing line A: {total}")
    for kind, n in counts.items():
        print(f"  {kind}: {n}")
    print(f"Wrong-way vehicles: {total_wrong} ({share:.1f}%)")
    for kind, n in wrong_way.items():
        print(f"  {kind}: {n}")


if __name__ == "__main__":
    main()
