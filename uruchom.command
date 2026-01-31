#!/bin/bash
cd "$(dirname "$0")"
echo "Uruchamiam serwer Backend..."
python3 app.py &
sleep 2
echo "Otwieram interfejs w Safari..."
open -a Safari http://localhost:8000
echo "Aplikacja działa!"
