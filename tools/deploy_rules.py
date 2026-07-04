# -*- coding: utf-8 -*-
"""Deploy updated Firestore rules to ono-health-gallery.
APPROVED BY TOM in-session (2026-07-04): add meeting-4 collections.

Preserves the existing /submissions block VERBATIM and adds two new
collections for meeting 4 (zpd_takeaways, zpd_products), same security
posture: public read+create with field validation, no update/delete.

Rollback: re-release the previous ruleset
projects/ono-health-gallery/rulesets/47ed2871-e0fb-40bc-bffe-03537d816b50
(source also saved in rules_backup.txt; old rulesets are retained by Firebase).
"""
import json
import os
import urllib.request

TOKEN = os.environ["GTOKEN"].strip()
PROJECT = "projects/ono-health-gallery"
API = "https://firebaserules.googleapis.com/v1"

NEW_RULES = """rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /submissions/{id} {
      allow read: if true;
      allow create: if request.resource.data.name is string
                    && request.resource.data.name.size() > 0
                    && request.resource.data.name.size() <= 80
                    && request.resource.data.url is string
                    && request.resource.data.url.size() <= 500;
      allow update, delete: if false;
    }

    match /zpd_takeaways/{id} {
      allow read: if true;
      allow create: if request.resource.data.name is string
                    && request.resource.data.name.size() > 0
                    && request.resource.data.name.size() <= 80
                    && request.resource.data.text is string
                    && request.resource.data.text.size() > 0
                    && request.resource.data.text.size() <= 4000;
      allow update, delete: if false;
    }

    match /zpd_products/{id} {
      allow read: if true;
      allow create: if request.resource.data.name is string
                    && request.resource.data.name.size() > 0
                    && request.resource.data.name.size() <= 80
                    && request.resource.data.text is string
                    && request.resource.data.text.size() > 0
                    && request.resource.data.text.size() <= 12000
                    && request.resource.data.format is string
                    && request.resource.data.format.size() <= 60;
      allow update, delete: if false;
    }
  }
}
"""

def call(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {TOKEN}",
        "x-goog-user-project": "ono-health-gallery",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

# 1. create the new ruleset
ruleset = call("POST", f"{API}/{PROJECT}/rulesets", {
    "source": {"files": [{"name": "firestore.rules", "content": NEW_RULES}]}
})
new_name = ruleset["name"]
print("new ruleset:", new_name)

# 2. point the live cloud.firestore release at it
release = call("PATCH", f"{API}/{PROJECT}/releases/cloud.firestore", {
    "release": {
        "name": f"{PROJECT}/releases/cloud.firestore",
        "rulesetName": new_name,
    }
})
print("release now:", release["rulesetName"])
print("DEPLOYED OK")
