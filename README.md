# Omnibus Price Tracker 🛒🔔

Nowoczesne narzędzie do śledzenia cen produktów w sklepach internetowych. Aplikacja monitoruje ceny w tle, wysyła powiadomienia e-mail (HTML) oraz udostępnia wygodny dashboard do zarządzania listą życzeń.

![Screenshot](https://via.placeholder.com/800x400?text=Omnibus+Dashboard+Preview)

## ✨ Możliwości

*   **HTML Dashboard**: Przejrzysty interfejs w przeglądarce (`localhost:8000`).
*   **Śledzenie Cen**: Automatyczne sprawdzanie cen w regularnych odstępach czasu (Cron).
*   **Alerty E-mail**: Stylowe powiadomienia HTML ze zdjęciem produktu i linkiem do sklepu.
*   **Inteligentne Statusy**:
    *   🟢 **KUPUJ**: Dynamiczny przycisk zakupu, gdy cena spadnie.
    *   🟡 **OBSERWUJ**: Śledzenie stabilnych cen.
    *   🔴 **CZEKAJ**: Ostrzeżenie przed podwyżkami.
*   **Zarządzanie**: Dodawanie i usuwanie produktów jednym kliknięciem.

## 🚀 Instalacja

1.  **Sklonuj repozytorium**:
    ```bash
    git clone https://github.com/TruLab2025/omnibus.git
    cd omnibus
    ```

2.  **Stwórz wirtualne środowisko (opcjonalnie, ale zalecane)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Zainstaluj zależności**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Jeśli nie masz pliku requirements.txt, zainstaluj ręcznie: `pip install fastapi uvicorn requests beautifulsoup4 python-dotenv`)*

4.  **Skonfiguruj zmienne środowiskowe**:
    Utwórz plik `.env` na podstawie `.env.template` i uzupełnij dane SMTP (np. Gmail App Password):
    ```ini
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=twoj@gmail.com
    SMTP_PASSWORD=twoje-haslo-aplikacji
    SMTP_FROM=Omnibus Alert <twoj@gmail.com>
    ```

## 🎮 Uruchomienie

### Sposób 1: Szybki Start (macOS)
Kliknij dwukrotnie w plik `uruchom.command` w folderze projektu. Uruchomi to serwer i otworzy przeglądarkę.

### Sposób 2: Terminal
Uruchom serwer API:
```bash
python3 app.py
```
Aplikacja będzie dostępna pod adresem: [http://localhost:8000](http://localhost:8000)

## 🛠️ Technologie
*   **Backend**: Python, FastAPI
*   **Frontend**: HTML5, CSS3, Vanilla JS
*   **Scraping**: BeautifulSoup4
*   **Baza danych**: JSON (lokalny plik `tracked.json`)

---
*Projekt stworzony w celach edukacyjnych (PoC).*
