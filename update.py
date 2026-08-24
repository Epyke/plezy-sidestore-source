import json
import urllib.request
import datetime

UPSTREAM_REPO = "edde746/plezy"
JSON_PATH = "apps.json"

url = f"https://api.github.com/repos/{UPSTREAM_REPO}/releases/latest"
req = urllib.request.Request(url, headers={"User-Agent": "SideStore-Source-Bot"})

with urllib.request.urlopen(req) as response:
    release_data = json.loads(response.read().decode())

tag = release_data["tag_name"].lstrip("v")
published_at = release_data.get(
    "published_at", 
    datetime.datetime.now(datetime.timezone.utc).isoformat()
)[:10]
body = release_data.get("body", "Bug fixes and improvements.")


ipa_asset = None
for asset in release_data.get("assets", []):
    if asset["name"].endswith(".ipa"):
        ipa_asset = asset
        break

if not ipa_asset:
    print("No .ipa found in latest release.")
    exit(0)

with open(JSON_PATH, "r") as f:
    source_data = json.load(f)

app = source_data["apps"][0]

existing_versions = [v["version"] for v in app.get("versions", [])]
if tag in existing_versions:
    print(f"Version {tag} is already up to date.")
    exit(0)

new_version = {
    "version": tag,
    "date": published_at,
    "localizedDescription": body[:250] if body else "Update release.",
    "downloadURL": ipa_asset["browser_download_url"],
    "size": ipa_asset["size"]
}

app["versions"].insert(0, new_version)

with open(JSON_PATH, "w") as f:
    json.dump(source_data, f, indent=2)

print(f"Successfully added version {tag} to {JSON_PATH}!")