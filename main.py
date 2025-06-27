import os
from flask import Flask, request, jsonify
from PIL import Image
import io
from google import genai
from google.genai import types

app = Flask(__name__)

api_key = os.environ.get('api_key') 
client = genai.Client(api_key=api_key)

def image_to_pixel_data(image, scale_percentage=25):
    """Konwertuje obrazek na dane pixeli"""
    width, height = image.size
    new_width = max(1, int(width * scale_percentage / 100))
    new_height = max(1, int(height * scale_percentage / 100))
    
    resized_image = image.resize((new_width, new_height))
    pixels = resized_image.load()
    
    data = []
    for y in range(new_height):
        for x in range(new_width):
            r, g, b = pixels[x, y][:3]
            data.append({
                "r": r,
                "g": g, 
                "b": b,
                "x": x,
                "y": y
            })
    
    return {
        "pixels": data,
        "width": new_width,
        "height": new_height
    }

@app.route('/', methods=['GET'])
def home():
    if "txt" in request.args:
        txt = request.args.get('txt')
        scale = int(request.args.get('scale', 25))
        
        if not txt:
            return jsonify({"status": "ERROR", "text": "Parametr 'txt' nie może być pusty."}), 400

        if not api_key:
            return jsonify({"status": "ERROR", "text": "Błąd serwera: Klucz API nie jest skonfigurowany."}), 500

        try:
            # TYLKO GENEROWANIE OBRAZÓW
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=txt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image = Image.open(io.BytesIO(part.inline_data.data))
                    pixel_data = image_to_pixel_data(image, scale)
                    
                    return jsonify({
                        "status": "OK",
                        "data": pixel_data
                    })
            
            # Jeśli nie znaleziono obrazu w odpowiedzi
            return jsonify({"status": "ERROR", "text": "Nie udało się wygenerować obrazu."}), 500

        except Exception as e:
            print(f"Wystąpił błąd: {e}")
            return jsonify({"status": "ERROR", "text": "Wystąpił błąd podczas generowania obrazu."}), 500
    
    return jsonify({"status": "OK", "text": "Serwer gotowy do generowania obrazów. Dodaj parametr ?txt=... do adresu URL."})

if __name__ == '__main__':
    app.run(debug=True)
