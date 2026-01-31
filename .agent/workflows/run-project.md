---
description: Uruchom projekt Price Tracker PoC
---

// turbo-all

1. **Uruchom Backend (FastAPI)**  
Uruchamia serwer na porcie 8000.
```bash
cd /Users/trulab/.gemini/antigravity/scratch/price-checker-poc && python3 app.py
```

2. **Otwórz Interfejs w Safari**  
Otwiera stronę główną w przeglądarce.
```bash
open -a Safari /Users/trulab/.gemini/antigravity/scratch/price-checker-poc/frontend.html
```

3. **Sprawdź Ceny (Cron)**  
Ręczne uruchomienie skryptu sprawdzającego ceny.
```bash
cd /Users/trulab/.gemini/antigravity/scratch/price-checker-poc && python3 cron.py
```
