import json
import glob
import os

def main():
    # Alle JSON-Dateien im aktuellen Verzeichnis finden
    json_files = glob.glob("output/*.json")

    if not json_files:
        print("there are no json files.")
        return

    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"failed to read {file}: unhealthy JSON.")
            continue

        modified = False

        # Fall 1: Liste von Objekten
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                url = item.get("url", "").strip()
                content = item.get("content", "")
                if "Quelle:" not in content:
                    item["content"] = content.strip() + f"\n\nsource: {url}"
                    modified = True

        # Fall 2: Einzelnes JSON-Objekt
        elif isinstance(data, dict):
            url = data.get("url", "").strip()
            content = data.get("content", "")
            if "Quelle:" not in content:
                data["content"] = content.strip() + f"\n\nsource: {url}"
                modified = True

        else:
            print(f" file {file} has no json.")
            continue

        if modified:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"changed file: {file}")
        else:
            print(f"no changes: {file}")

if __name__ == "__main__":
    main()