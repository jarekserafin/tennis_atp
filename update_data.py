"""Download Jeff Sackmann's ATP data using only the Python standard library."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REPOSITORY = "Aneeshers/tennis-sackmann-archive"
DATA_DIR = Path(__file__).resolve().parent / "data"
CORRECTIONS_FILE = Path(__file__).resolve().parent / "player_corrections.json"
ANNUAL_MATCH = re.compile(r"atp_matches_\d{4}\.csv")
CORE_FILE = re.compile(r"atp_rankings_(?:\d{2}s|current)\.csv")
REFERENCE_FILES = {"atp_players.csv", "matches_data_dictionary.txt", "UPSTREAM_README.md"}


def request(url):
    return urlopen(Request(url, headers={"User-Agent": "tennis-atp-data-updater"}), timeout=60)


def fetch_json(url):
    with request(url) as response:
        return json.load(response)


def blob_hash(path):
    """Calculate the Git blob hash used by GitHub, without requiring Git."""
    digest = hashlib.sha1(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_files(tree, include_all=False):
    files = {}
    for entry in tree:
        if entry["type"] != "blob":
            continue
        path = entry["path"]
        if path == "LICENSE":
            files["LICENSE"] = entry
        elif path.startswith("atp/"):
            name = path.removeprefix("atp/")
            if "/" in name:
                continue
            if (ANNUAL_MATCH.fullmatch(name) or CORE_FILE.fullmatch(name)
                    or name in REFERENCE_FILES
                    or (include_all and name.startswith("atp_matches_") and name.endswith(".csv"))):
                files[name] = entry
    required = REFERENCE_FILES | {"atp_rankings_current.csv", "LICENSE"}
    if required - files.keys() or not any(ANNUAL_MATCH.fullmatch(name) for name in files):
        raise ValueError("Archiwum nie zawiera oczekiwanych plików ATP. Dane nie zostały zmienione.")
    return dict(sorted(files.items()))


def validate_csv(path):
    if path.suffix != ".csv":
        return
    if path.name == "atp_players.csv":
        required = {"player_id", "name_first", "name_last", "dob", "hand", "height", "wikidata_id"}
    elif path.name.startswith("atp_rankings_"):
        required = {"ranking_date", "rank", "player", "points"}
    elif ANNUAL_MATCH.fullmatch(path.name):
        required = {"tourney_date", "winner_id", "loser_id", "surface", "minutes",
                    "winner_hand", "winner_ht", "winner_age", "loser_age",
                    "w_ace", "l_ace", "w_df", "l_df", "w_1stIn", "l_1stIn"}
    else:
        required = {"tourney_date"}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = csv.reader(stream)
        header = next(rows, [])
        if required - set(header) or next(rows, None) is None:
            raise ValueError(f"Niepoprawny lub pusty CSV: {path.name}")


def apply_player_corrections(path, corrections):
    """Apply project corrections after checking the original source file."""
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames
        rows = list(reader)
    missing = set(corrections)
    for row in rows:
        player_id = row["player_id"]
        if player_id not in corrections:
            continue
        for column, value in corrections[player_id].items():
            if column not in columns or column == "player_id":
                raise ValueError(f"Niepoprawna kolumna korekty: {column}")
            row[column] = str(value)
        missing.discard(player_id)
    if missing:
        raise ValueError(f"Brak zawodników wymagających korekty: {sorted(missing)}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def synchronize(data_dir, files, commit, check=False, corrections=None):
    corrections = corrections or {}
    try:
        previous = json.loads((data_dir / ".sackmann-source.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}

    def is_current(name, entry):
        path = data_dir / name
        if not path.is_file():
            return False
        local_hash = blob_hash(path)
        if name == "atp_players.csv" and corrections:
            return (previous.get("files", {}).get(name) == entry["sha"]
                    and previous.get("local_files", {}).get(name) == local_hash
                    and previous.get("player_corrections") == corrections)
        return local_hash == entry["sha"]

    changed = [name for name, entry in files.items() if not is_current(name, entry)]
    print(f"Pliki: {len(files)}, do pobrania: {len(changed)}, bez zmian: {len(files) - len(changed)}", flush=True)
    if check:
        for name in changed:
            print(f"  {name}")
        return changed

    data_dir.mkdir(parents=True, exist_ok=True)
    # Download and validate the entire update before replacing any existing file.
    with tempfile.TemporaryDirectory(prefix=".sackmann-download-", dir=data_dir) as directory:
        staged = Path(directory)
        for index, name in enumerate(changed, 1):
            print(f"[{index}/{len(changed)}] {name}", flush=True)
            url = f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/{quote(files[name]['path'])}"
            target = staged / name
            with request(url) as response, target.open("wb") as stream:
                shutil.copyfileobj(response, stream)
            if blob_hash(target) != files[name]["sha"]:
                raise ValueError(f"Błąd integralności pliku: {name}. Dane nie zostały zmienione.")
            validate_csv(target)
            if name == "atp_players.csv" and corrections:
                apply_player_corrections(target, corrections)
        for name in changed:
            (staged / name).replace(data_dir / name)
        manifest = {
            "repository": REPOSITORY,
            "commit": commit,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "files": {name: entry["sha"] for name, entry in files.items()},
            "local_files": {name: blob_hash(data_dir / name) for name in files},
            "player_corrections": corrections,
        }
        metadata = staged / ".sackmann-source.json"
        metadata.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        metadata.replace(data_dir / metadata.name)
    return changed


def print_coverage(data_dir, files):
    annual = sorted(name for name in files if ANNUAL_MATCH.fullmatch(name))
    for name, column in [(annual[-1], "tourney_date"), ("atp_rankings_current.csv", "ranking_date")]:
        with (data_dir / name).open(encoding="utf-8-sig", newline="") as stream:
            latest = max(row[column] for row in csv.DictReader(stream))
        print(f"{name}: ostatnia data w danych {latest[:4]}-{latest[4:6]}-{latest[6:8]}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pobierz lub zaktualizuj dane ATP Jeffa Sackmanna.")
    parser.add_argument("--check", action="store_true", help="Sprawdź zmiany bez zapisywania plików.")
    parser.add_argument("--all", action="store_true", dest="include_all",
                        help="Pobierz również debel, Futures, kwalifikacje/Challengery i mecze amatorskie.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Katalog docelowy (domyślnie data/ obok skryptu).")
    args = parser.parse_args(argv)
    try:
        revision = fetch_json(f"https://api.github.com/repos/{REPOSITORY}/commits/main")
        commit = revision["sha"]
        print(f"Źródło: {REPOSITORY}\nCommit: {commit}\nData commitu: {revision['commit']['committer']['date']}", flush=True)
        print("Archiwum zawiera kopię danych Sackmanna z czerwca 2026; nie jest bieżącym źródłem ATP.", flush=True)
        tree = fetch_json(f"https://api.github.com/repos/{REPOSITORY}/git/trees/{commit}?recursive=1")
        if tree.get("truncated"):
            raise ValueError("Niepełna lista plików GitHub. Dane nie zostały zmienione.")
        files = selected_files(tree["tree"], args.include_all)
        corrections = json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))
        synchronize(args.data_dir.resolve(), files, commit, args.check, corrections)
        if not args.check:
            print_coverage(args.data_dir.resolve(), files)
            print(f"Gotowe. Dane zapisane w {args.data_dir.resolve()}")
        return 0
    except (OSError, URLError, ValueError, KeyError) as error:
        print(f"Błąd aktualizacji: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
