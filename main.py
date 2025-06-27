from google import genai
import os
from flask import Flask, request, jsonify


app = Flask(__name__)

my_secret = os.environ['api_key']

client = genai.Client(api_key=my_secret)



@app.route('/', methods=['GET'])
def home():
  if "txt" in request.args:
    txt = request.args['txt']
    response = ""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=txt,
        )
    except:
      return jsonify({"status": "ERROR", "text": "Invalid cookies"})
    return jsonify({"status": "OK", "text": response})
  else:
    return jsonify({"status": "OK", "text": ""})


app.run(debug=False,port=3000,host="0.0.0.0")
