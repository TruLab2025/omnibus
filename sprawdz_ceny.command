#!/bash
cd "$(dirname "$0")"
echo "Sprawdzam aktualne ceny produktów..."
python3 cron.py
echo ""
echo "Gotowe! Możesz teraz zamknąć to okno."
read -p "Naciśnij Enter, aby wyjść..."
