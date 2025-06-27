import os
from flask import Flask, request, jsonify
from PIL import Image
import io
from google import genai
from google.genai import types

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
MOSAIC_SIZE = 1024
# --- Konfiguracja Klucza API ---
# Bezpiecznie pobieramy klucz API ze zmiennych środowiskowych na Renderze
# Używamy .get(), aby aplikacja nie wywaliła się, jeśli klucza nie ma
api_key = os.environ.get('api_key') 

client = genai.Client(api_key=api_key)


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
            contents=txt,
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            if not response.candidates or not response.candidates[0].content.parts:
                return jsonify({"status": "ERROR", "text": "Nie udało się wygenerować obrazu (brak kandydatów)."}), 500
    
            image_part = response.candidates[0].content.parts[0]
            if 'image' not in image_part.mime_type:
                 return jsonify({"status": "ERROR", "text": "Odpowiedź AI nie zawierała obrazu."}), 500
    
            image_data_bytes = image_part.inline_data.data
            
            print(f"Przetwarzam obraz na mozaikę o wymiarach {MOSAIC_SIZE[0]}x{MOSAIC_SIZE[1]}...")
            
            image_to_process = Image.open(io.BytesIO(image_data_bytes))
            image_in_rgb = image_to_process.convert('RGB')
            
            resized_image = image_in_rgb.resize(MOSAIC_SIZE, Image.Resampling.LANCZOS)
            
            pixel_data = list(resized_image.getdata())
            
            flat_pixel_list_rgba = []
            # KLUCZOWA ZMIANA: Dodajemy kanał Alfa (A) do każdego piksela
            # Roblox EditableImage wymaga formatu RGBA (4 wartości na piksel)
            for r, g, b in pixel_data:
                flat_pixel_list_rgba.extend([r, g, b, 255]) # 255 = w pełni nieprzezroczysty
            
            return jsonify({
                "status": "SUCCESS",
                "width": MOSAIC_SIZE[0],
                "height": MOSAIC_SIZE[1],
                "pixels": flat_pixel_list_rgba # Wysyłamy listę RGBA
            })

        except Exception as e:
            # Jeśli cokolwiek pójdzie nie tak z Google AI, zobaczymy błąd w logach
            print(f"Wystąpił błąd podczas komunikacji z Google AI: {e}")
            return jsonify({"status": "ERROR", "text": "Wystąpił błąd po stronie serwera."}), 500
    else:
        # Odpowiedź, jeśli ktoś wejdzie na stronę bez parametru
        return jsonify({"status": "OK", "text": "Serwer działa. Dodaj parametr ?txt=... do adresu URL."})
