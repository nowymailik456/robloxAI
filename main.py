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
            response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['IMAGE']
                )
            )
            
            image_data_bytes = None
            for part in response.candidates[0].content.parts:
                if part.inline_data.data:
                    image_data_bytes = part.inline_data.data
                    break # Znaleźliśmy dane obrazu, przerywamy pętlę
            
            if not image_data_bytes:
                return jsonify({"status": "ERROR", "text": "Nie udało się wygenerować obrazu."}), 500
            
            print(f"Przetwarzam obraz na mozaikę o wymiarach {MOSAIC_SIZE[0]}x{MOSAIC_SIZE[1]}...")
            
            image_to_process = Image.open(io.BytesIO(image_data_bytes))
    
            resized_image = image_to_process.resize(MOSAIC_SIZE, Image.Resampling.LANCZOS)
    
            pixel_data = list(resized_image.getdata())
            flat_pixel_list = []
            for r, g, b in pixel_data:
                flat_pixel_list.extend([r, g, b])
    
            return jsonify({
                "status": "SUCCESS",
                "width": MOSAIC_SIZE[0],
                "height": MOSAIC_SIZE[1],
                "pixel

        except Exception as e:
            # Jeśli cokolwiek pójdzie nie tak z Google AI, zobaczymy błąd w logach
            print(f"Wystąpił błąd podczas komunikacji z Google AI: {e}")
            return jsonify({"status": "ERROR", "text": "Wystąpił błąd po stronie serwera."}), 500
    else:
        # Odpowiedź, jeśli ktoś wejdzie na stronę bez parametru
        return jsonify({"status": "OK", "text": "Serwer działa. Dodaj parametr ?txt=... do adresu URL."})
