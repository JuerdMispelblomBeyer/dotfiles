#!/usr/bin/env python3
import re
from pathlib import Path
import shutil

APPS_DIR = Path.home() / ".local/share/applications"

APP_ID_RE = re.compile(r"--app-id=([a-z0-9]+)")
PROFILE_RE = re.compile(r"Profile_[0-9]+")

def main():
    for f in APPS_DIR.glob("msedge-*.desktop"):
        text = f.read_text(encoding="utf-8", errors="replace")

        app_id_match = APP_ID_RE.search(text)
        profile_match = PROFILE_RE.search(f.name)

        if not app_id_match or not profile_match:
            continue

        app_id = app_id_match.group(1)
        profile = profile_match.group(0)

        # Wayland app_id observed: msedge-_APPID-Profile_X
        correct_name = f"msedge-_{app_id}-{profile}.desktop"
        correct_path = f.with_name(correct_name)

        if f.name == correct_name:
            continue

        backup = f.with_suffix(f.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(f, backup)

        print(f"✔ Renaming {f.name}")
        print(f"    → {correct_name}")

        f.rename(correct_path)

    print("\nDone.")
    print("Log out and back in, then re-pin apps to the dock.")

if __name__ == "__main__":
    main()