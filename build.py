#!/usr/bin/env python3
"""Genera index.html (cifrato) dal vademecum truck in chiaro.

Uso:
    XILEMA_PIN='****' python3 build.py
    # oppure, senza variabile d'ambiente, lo script chiede il PIN (input nascosto)

Sorgente in chiaro: ../Trk/VADEMECUM-TRUCK.html (fuori da git, contiene netti riservati).
Lo script ne estrae CSS e corpo, li cifra con lo stesso schema di mak-distanziali-xilema
(chiave = PBKDF2-SHA256(PIN, salt, 200k) -> AES-GCM-256) e li inserisce in
index.template.html. Nel repo pubblico finisce solo index.html con il blob cifrato.
Il PIN non viene mai stampato ne' salvato.
"""
import base64, datetime, getpass, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "Trk", "VADEMECUM-TRUCK.html")
TEMPLATE = os.path.join(HERE, "index.template.html")
INDEX = os.path.join(HERE, "index.html")
PBKDF2_ITER = 200_000


def encrypt(plaintext: bytes, pin: str) -> str:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        sys.exit("Manca il pacchetto 'cryptography': pip3 install cryptography")
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, PBKDF2_ITER, dklen=32)
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    b = lambda x: base64.b64encode(x).decode("ascii")
    return b(salt) + "." + b(iv) + "." + b(ct)


def main():
    pin = os.environ.get("XILEMA_PIN") or getpass.getpass("PIN Xilema: ")
    if not pin:
        sys.exit("PIN vuoto: interrompo.")
    with open(SOURCE, encoding="utf-8") as fh:
        src = fh.read()
    css = re.search(r"<style>(.*?)</style>", src, re.S)
    body = re.search(r"<body>(.*?)</body>", src, re.S)
    if not css or not body:
        sys.exit("Sorgente inatteso: <style> o <body> non trovati.")
    if "<script" in body.group(1).lower():
        sys.exit("Il sorgente contiene <script>: non previsto, interrompo.")
    payload = {"css": css.group(1), "body": body.group(1)}
    blob = encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"), pin)
    meta = {"kdf": "PBKDF2-SHA256", "iter": PBKDF2_ITER, "cipher": "AES-GCM"}
    with open(TEMPLATE, encoding="utf-8") as fh:
        tpl = fh.read()
    for token in ("/*DATA_BLOB*/", "/*BUILD_META*/", "/*GENERATO*/"):
        if token not in tpl:
            sys.exit(f"Segnaposto {token} non trovato in index.template.html")
    html = (tpl.replace("/*DATA_BLOB*/", json.dumps(blob))
               .replace("/*BUILD_META*/", json.dumps(meta))
               .replace("/*GENERATO*/", json.dumps(datetime.date.today().isoformat())))
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"index.html scritto: {len(html)//1024} KB, sorgente {len(src)//1024} KB")


if __name__ == "__main__":
    main()
