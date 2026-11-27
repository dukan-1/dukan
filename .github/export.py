# One-off: copy the website's public catalogue and item photos (pub/cat, pimg/*) into this branch.
import json, urllib.request, base64, os, re
P = "https://firestore.googleapis.com/v1/projects/dukan-ff682/databases/(default)/documents/"
def get(path):
    with urllib.request.urlopen(P + path, timeout=30) as r:
        return json.load(r)
def val(v):
    if "mapValue" in v: return {k: val(x) for k, x in v["mapValue"].get("fields", {}).items()}
    if "arrayValue" in v: return [val(x) for x in v["arrayValue"].get("values", [])]
    for k in ("stringValue", "booleanValue"):
        if k in v: return v[k]
    if "integerValue" in v: return int(v["integerValue"])
    if "doubleValue" in v: return float(v["doubleValue"])
    return None
os.makedirs("media-export/img", exist_ok=True)
cat = {k: val(x) for k, x in get("pub/cat").get("fields", {}).items()}
info = {k: val(x) for k, x in get("pub/info").get("fields", {}).items()}
json.dump({"cat": cat, "info": info}, open("media-export/cat.json", "w"), ensure_ascii=False)
items = (cat.get("p") or {})
n = 0
for pid, e in items.items():
    if not isinstance(e, dict) or not e.get("iv"): continue
    try:
        d = {k: val(x) for k, x in get("pimg/" + pid).get("fields", {}).items()}
    except Exception as ex:
        print("skip", pid, ex); continue
    src = d.get("d") or ""
    m = re.match(r"data:image/(jpeg|png|webp);base64,(.+)", src)
    if m:
        open("media-export/img/%s.%s" % (pid, "jpg" if m.group(1) == "jpeg" else m.group(1)), "wb").write(base64.b64decode(m.group(2)))
    elif d.get("u"):
        try:
            with urllib.request.urlopen(d["u"], timeout=30) as r:
                open("media-export/img/%s.jpg" % pid, "wb").write(r.read())
        except Exception as ex:
            print("url skip", pid, ex); continue
    n += 1
print("items", len(items), "photos", n)
