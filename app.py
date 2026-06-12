import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.api_core.exceptions import ResourceExhausted

app = Flask(__name__)

# Reads the long string of keys from Render's Environment Variables
API_KEYS = os.getenv("GEMINI_API_KEYS").split(",")
current_key_index = 0

def get_client():
    return genai.Client(api_key=API_KEYS[current_key_index])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    global current_key_index
    user_query = request.json.get('query')
    
    try:
        client = get_client()
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=user_query,
            config={"tools": [{"google_search_retrieval": {}}]}
        )
        return jsonify({"answer": response.text})
    
    except (ResourceExhausted, Exception):
        # Automatically moves to the next key if a limit is reached
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        return jsonify({"answer": "Switching API keys... please try your request again in a second."})

if __name__ == '__main__':
    app.run()
