FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# install deps
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    "uvicorn[standard]==0.29.0" \
    pydantic==2.6.4 \
    python-multipart==0.0.9 \
    pdfminer.six==20231228 \
    Pillow==10.3.0

# write the whole app + demo data
RUN python - <<'PY'
import os, json, textwrap, time
base = "/app/api"
demo = os.path.join(base, "static", "bundles", "demo")
os.makedirs(demo, exist_ok=True)
open(os.path.join(base, "__init__.py"), "w").write("")

main_py = textwrap.dedent("""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time, json, os, re
from io import BytesIO
from PIL import Image

app = FastAPI(title="Ethical Scanner API — clean build")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(__file__)
DEMO_DIR = os.path.join(BASE_DIR, "static", "bundles", "demo")
DATA_DIR = os.path.join(BASE_DIR, "data"); os.makedirs(DATA_DIR, exist_ok=True)

@app.get("/")
def root(): return {"ok": True, "service": "Ethical Scanner API — clean", "ts": int(time.time())}

def _load_json(p): return json.load(open(p))

@app.get("/bundles/demo/manifest.json")
def manifest():
    files = []
    for fn in ["products.json","company_map.json","sanctions_min.json"]:
        p = os.path.join(DEMO_DIR, fn)
        if os.path.exists(p): files.append({"path": fn, "size": os.path.getsize(p)})
    return {"bundle_id":"b_demo","generated_at": int(time.time()), "files": files, "signature": "DEV"}

@app.get("/bundles/demo/{name}")
def bundle_file(name: str):
    p = os.path.join(DEMO_DIR, name)
    if not os.path.exists(p): return {"error":"not found"}
    return _load_json(p)

GTIN13 = re.compile(r"\\b(\\d{13})\\b"); GTIN14 = re.compile(r"\\b(\\d{14})\\b")
@app.post("/v1/receipts/import")
async def receipts_import(text: str = Form("")):
    gtins = set(GTIN13.findall(text)) | set(GTIN14.findall(text))
    return {"ok": True, "gtins": sorted(gtins)}

class URLScanReq(BaseModel): url: str
@app.post("/v1/url-scan")
def url_scan(_: URLScanReq): return {"ok": True, "products": []}

def strip_exif_jpeg(data: bytes) -> bytes:
    im = Image.open(BytesIO(data)); out = BytesIO()
    clean = Image.new(im.mode, im.size); clean.putdata(list(im.getdata()))
    clean.save(out, format='JPEG', quality=90); return out.getvalue()

@app.post("/v1/reports")
async def reports(gtin: str = Form(...), reason: str = Form("user_mismatch"),
                  notes: str = Form(""), ocr_text: str = Form(""),
                  evidence: UploadFile | None = File(None)):
    rid = f"r_{gtin}_{int(time.time())}"
    rec = {"id": rid, "gtin": gtin, "reason": reason, "notes": notes, "ocr_text": ocr_text, "ts": int(time.time())}
    if evidence is not None:
        raw = await evidence.read()
        try: jpg = strip_exif_jpeg(raw)
        except Exception: jpg = raw
        open(os.path.join(DATA_DIR, rid + ".jpg"), "wb").write(jpg)
        rec["evidence_file"] = rid + ".jpg"
    json.dump(rec, open(os.path.join(DATA_DIR, rid + ".json"), "w"))
    return {"ok": True, "id": rid}
""").strip()

open(os.path.join(base, "main.py"), "w").write(main_py)

products = [
    {"gtin":"0123456789012","name":"Demo Pasta","coo":"IT","last_seen":1734300000},
    {"gtin":"00012345678905","name":"Demo Coffee","coo":"BR","last_seen":1734300000},
]
json.dump(products, open(os.path.join(demo, "products.json"), "w"), indent=2)
open(os.path.join(demo, "company_map.json"), "w").write("[]\n")
json.dump({
    "as_of":"2025-08-15",
    "jurisdictions":{"RU":["US","EU","UK","CA","UN"],"IR":["US","EU","UK","CA","UN"],
                     "KP":["US","EU","UK","CA","UN"],"SY":["US","EU","UK","CA","UN"],"CU":["US","CA","UK","EU"]}
}, open(os.path.join(demo, "sanctions_min.json"), "w"), indent=2)
PY

EXPOSE 8000
CMD ["python","-m","uvicorn","api.main:app","--host","0.0.0.0","--port","8000"]
