# -*- coding: utf-8 -*-
"""Fetch the ACTIVE Firestore security rules of ono-health-gallery.

Auth: OAuth access token passed via env var GTOKEN (never on the command line).
Saves the current rules source to rules_backup.txt (rollback safety) and prints it.
"""
import json
import os
import urllib.request

TOKEN = os.environ["GTOKEN"].strip()
PROJECT = "projects/ono-health-gallery"
API = "https://firebaserules.googleapis.com/v1"

def get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "x-goog-user-project": "ono-health-gallery",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

releases = get(f"{API}/{PROJECT}/releases")
print("== releases ==")
for rel in releases.get("releases", []):
    print(" ", rel["name"], "->", rel["rulesetName"])

fs = [r for r in releases.get("releases", []) if r["name"].endswith("cloud.firestore")]
if not fs:
    raise SystemExit("No cloud.firestore release found!")

ruleset = get(f"{API}/{fs[0]['rulesetName']}")
src = ruleset["source"]["files"][0]["content"]

backup = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules_backup.txt")
with open(backup, "w", encoding="utf-8") as f:
    f.write(src)

print("== active ruleset:", fs[0]["rulesetName"], "==")
print(src)
print("== backup saved to:", backup, "==")
