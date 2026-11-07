"""Find when each vehicle crosses lines A and B, then count vehicles and wrong-way drivers.

Reads output/tracks.csv (made by track_dump.py) instead of the video,
so it runs in under a second and you can rerun it as often as you like.
"""

import csv
import sys

from settings import LINE_A, LINE_B

CSV_PATH = "output/tracks.csv"


def side(line, point):
    """Return True if the point is on one side of the line (or exactly on it), False if on the other.

    The 2D cross product of (line direction) and (line start -> point) is positive on
    one side, negative on the other and zero on the line. Treating zero as "True"
    means a point landing exactly on the line can't make us miss a crossing.
    """
    (x1, y1), (x2, y2) = line
    qx, qy = point
    cross = (x2 - x1) * (qy - y1) - (y2 - y1) * (qx - x1)
    return cross >= 0


def load_rows(csv_path):
    """Read tracks.csv into a list of dictionaries, turning the text into numbers."""
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
    """Return {track_id: {"type", "prev", "A", "B"}}.

    "prev" is the vehicle's last known point; "A" and "B" are the times it first
    crossed each line, or None if it never did. Rows must be in time order,
    which they are, because track_dump.py writes them frame by frame.
    """
    tracks = {}
    for row in rows:
        tid = row["track_id"]
        point = (row["x"], row["y"])

        # First time we see this vehicle: remember it and wait for its next position.
        if tid not in tracks:
            tracks[tid] = {"type": row["type"], "prev": point, "A": None, "B": None}
            continue

        track = tracks[tid]
        # Check both lines the same way. Each pass gives a name ("A" or "B") and its line.
        for name, line in (("A", LINE_A), ("B", LINE_B)):
            moved_across = side(line, track["prev"]) != side(line, point)
            # Only the FIRST crossing counts, so a car wobbling on the line isn't counted twice.
            if moved_across and track[name] is None:
                track[name] = row["time"]

        track["prev"] = point
    return tracks


def summarise(tracks):
    """Return (vehicles counted at line A by type, wrong-way vehicles by type)."""
    counts = {}
    wrong_way = {}
    for track in tracks.values():
        # Only vehicles that crossed line A are counted. Line A sees traffic in both
        # directions; IDs that only crossed B are usually a vehicle whose ID changed.
        if track["A"] is None:
            continue

        kind = track["type"]
        # counts.get(kind, 0) means "the count so far, or 0 if this type is new".
        counts[kind] = counts.get(kind, 0) + 1

        # Crossed both lines, but B first: going the wrong way.
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
    share = total_wrong / total * 100 if total else 0   # avoid dividing by zero

    print(f"Vehicles crossing line A: {total}")
    for kind, n in counts.items():
        print(f"  {kind}: {n}")
    print(f"Wrong-way vehicles: {total_wrong} ({share:.1f}%)")
    for kind, n in wrong_way.items():
        print(f"  {kind}: {n}")


if __name__ == "__main__":
    main()
