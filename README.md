# mak-vademecum-truck

Vademecum personale sull'offerta truck (TRK), consultabile da iPhone e iPad.
Pagina single-file, nessuna dipendenza esterna, contenuto cifrato con PIN.

LIVE: https://stefanoserafin.github.io/mak-vademecum-truck/

## Come funziona

- Il documento in chiaro sta fuori da questo repo (`../Trk/VADEMECUM-TRUCK.html`) e non va mai committato: contiene materiale riservato.
- `build.py` ne estrae CSS e corpo, li cifra (PBKDF2-SHA256 200k -> AES-GCM-256) e li inserisce in `index.template.html`, producendo `index.html`.
- Nel browser il PIN decifra il blob con WebCrypto; con «Ricorda su questo dispositivo» il PIN resta nel localStorage di quel dispositivo.
- Stesso schema e stesso PIN di `mak-distanziali-xilema`.

## Disegni e infografiche

Le 25 figure (SVG inline, senza script) sono generate da `../Trk/vademecum_figure.py`, che le inserisce nel documento in chiaro tra marcatori `<!--FIG nome-->`. Lo script è idempotente: si può rilanciare dopo ogni modifica. Resta fuori dal repo perché contiene i dati riservati dei grafici.

## Aggiornare

    python3 ../Trk/vademecum_figure.py   # solo se cambiano le figure

    XILEMA_PIN='****' python3 build.py
    git add index.html && git commit -m "aggiornamento" && git push

## Limite noto

Un PIN numerico corto protegge dalla lettura casuale, non da chi scarica la pagina e prova tutte le combinazioni. Scelta consapevole, per comodità d'uso da telefono.
