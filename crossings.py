import csv
import sys
from statistics import mean, median

from settings import LINE_A, LINE_B, DISTANCE_M, WHO_LIMIT_KMH, SPEED_LIMIT_KMH


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

    distance_m = ask_distance(DISTANCE_M)
    speeds, excluded = compute_speeds(tracks, distance_m)
    summary = summarise_speeds(speeds)
    print(f"Speeds measured: {len(speeds)} ({excluded} readings excluded as impossible)")
    if summary["average"] is None:
        print("  No speeds measured.")
    else:
        over_who_share = summary["over_who"] / len(speeds) * 100
        print(f"  Average: {summary['average']:.1f} km/h, median: {summary['median']:.1f} km/h")
        print(f"  Faster than {WHO_LIMIT_KMH} km/h (WHO): {summary['over_who']} ({over_who_share:.1f}%)")
        if summary["over_limit"] is not None:
            print(f"  Speeding (over the {SPEED_LIMIT_KMH} km/h limit): {summary['over_limit']}")


def ask_distance(default):
    answer = input(f"Distance between line A and line B in metres [{default}]: ").strip()
    if answer == "":
        return default
    try:
        distance = float(answer)
    except ValueError:
        sys.exit("Distance must be a number, e.g. 25 or 25.5")
    if distance <= 0:
        sys.exit("Distance must be more than 0.")
    return distance


def compute_speeds(tracks, distance_m):
    excluded = 0
    speeds = []
    for track in tracks.values():
        if track["A"] is not None and track["B"] is not None:
            time = abs(track["B"] - track["A"])
        else:
            continue
        if time == 0:
            continue
        speed = round(distance_m/ time * 3.6, 1)
        if 3 <= speed <= 120:
            speeds.append(speed)
        else:
            excluded += 1
    return speeds, excluded


def summarise_speeds(speeds):
    if not speeds:
        return {"average": None, "median": None, "over_who": 0, "over_limit": None}

    over_who = 0
    for speed in speeds:
        if speed > WHO_LIMIT_KMH:
            over_who += 1


    over_limit = None
    if SPEED_LIMIT_KMH is not None:
        over_limit = 0
        for speed in speeds:
            if speed > SPEED_LIMIT_KMH:
                over_limit += 1

    return {
        "average": mean(speeds),
        "median": median(speeds),
        "over_who": over_who,
        "over_limit": over_limit,
    }



if __name__ == "__main__":
    main()
