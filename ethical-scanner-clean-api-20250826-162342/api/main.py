
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import time, json, os, re
from io import BytesIO
from PIL import Image

app = FastAPI(title="Ethical Scanner API — clean build")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
DEMO_DIR = os.path.join(BASE_DIR, "static", "bundles", "demo")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"ok": True, "service": "Ethical Scanner API — clean", "ts": int(time.time())}

def _load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)

@app.get("/bundles/demo/manifest.json")
def manifest():
    files = []
    for fn in ["products.json","company_map.json","sanctions_min.json"]:
        p = os.path.join(DEMO_DIR, fn)
        if os.path.exists(p):
            files.append({"path": fn, "size": os.path.getsize(p)})
    return {"bundle_id":"b_demo","generated_at": int(time.time()), "files": files, "signature": "DEV"}

@app.get("/bundles/demo/{name}")
def bundle_file(name: str):
    p = os.path.join(DEMO_DIR, name)
    if not os.path.exists(p):
        return {"error":"not found"}
    return _load_json(p)

GTIN13 = re.compile(r"\b(\d{13})\b")
GTIN14 = re.compile(r"\b(\d{14})\b")

@app.post("/v1/receipts/import")
async def receipts_import(text: str = Form("")):
    gtins = set(GTIN13.findall(text)) | set(GTIN14.findall(text))
    return {"ok": True, "gtins": sorted(list(gtins))}

class URLScanReq(BaseModel):
    url: str

@app.post("/v1/url-scan")
def url_scan(_: URLScanReq):
    return {"ok": True, "products": []}

def strip_exif_jpeg(data: bytes) -> bytes:
    im = Image.open(BytesIO(data))
    out = BytesIO()
    clean = Image.new(im.mode, im.size)
    clean.putdata(list(im.getdata()))
    clean.save(out, format='JPEG', quality=90)
    return out.getvalue()

@app.post("/v1/reports")
async def reports(gtin: str = Form(...), reason: str = Form("user_mismatch"),
                  notes: str = Form(""), ocr_text: str = Form(""),
                  evidence: UploadFile | None = File(None)):
    rid = f"r_{gtin}_{int(time.time())}"
    rec = {"id": rid, "gtin": gtin, "reason": reason, "notes": notes, "ocr_text": ocr_text, "ts": int(time.time())}
    if evidence is not None:
        raw = await evidence.read()
        try:
            jpg = strip_exif_jpeg(raw)
        except Exception:
            jpg = raw
        with open(os.path.join(DATA_DIR, rid + ".jpg"), "wb") as f:
            f.write(jpg)
        rec["evidence_file"] = rid + ".jpg"
    with open(os.path.join(DATA_DIR, rid + ".json"), "w") as f:
        json.dump(rec, f)
    return {"ok": True, "id": rid}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000)
