import os
from flask import Flask, request, jsonify
import google.generativeai as genai

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# --- Konfiguracja Klucza API ---
# Bezpiecznie pobieramy klucz API ze zmiennych środowiskowych na Renderze
# Używamy .get(), aby aplikacja nie wywaliła się, jeśli klucza nie ma
api_key = os.environ.get('api_key') 

# Sprawdzamy, czy klucz API został znaleziony i konfigurujemy bibliotekę Google
if api_key:
    genai.configure(api_key=api_key)
else:
    # Ten komunikat zobaczysz w logach na Renderze, jeśli zapomnisz dodać klucza
    print("BŁĄD KRYTYCZNY: Zmienna środowiskowa 'API_KEY' nie jest ustawiona!")


# --- Główny punkt wejścia do API ---
@app.route('/', methods=['GET'])
def home():
    # Sprawdzamy, czy w adresie URL jest parametr "txt"
    if "txt" in request.args:
        txt = request.args.get('txt')
        
        # Zabezpieczenie na wypadek pustego parametru
        if not txt:
            return jsonify({"status": "ERROR", "text": "Parametr 'txt' nie może być pusty."}), 400

        # Sprawdzamy, czy klucz API został poprawnie załadowany
        if not api_key:
            return jsonify({"status": "ERROR", "text": "Błąd serwera: Klucz API nie jest skonfigurowany."}), 500

        try:
            # Tworzymy model, używając poprawnej i aktualnej nazwy
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            # Generujemy odpowiedź - to jest skomplikowany obiekt
            response_object = model.generate_content(txt)
            
            # =======================================================
            # === NAJWAŻNIEJSZA ZMIANA JEST TUTAJ ===
            # Wyciągamy samą treść tekstową z obiektu odpowiedzi
            generated_text = response_object.text
            # =======================================================
            
            # Zwracamy do Robloxa już tylko prosty tekst
            return jsonify({"status": "OK", "text": generated_text})

        except Exception as e:
            # Jeśli cokolwiek pójdzie nie tak z Google AI, zobaczymy błąd w logach
            print(f"Wystąpił błąd podczas komunikacji z Google AI: {e}")
            return jsonify({"status": "ERROR", "text": "Wystąpił błąd po stronie serwera."}), 500
    else:
        # Odpowiedź, jeśli ktoś wejdzie na stronę bez parametru
        return jsonify({"status": "OK", "text": "Serwer działa. Dodaj parametr ?txt=... do adresu URL."})
