import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.api_core.exceptions import ResourceExhausted

app = Flask(__name__)

# Fetching keys from 9 separate environment variables
def get_all_keys():
    keys = []
    for i in range(1, 10):
        key = os.getenv(f"API_KEY_{i}")
        if key:
            keys.append(key)
    return keys

current_key_index = 0

def get_client():
    keys = get_all_keys()
    # Cycle through the list of keys we just found
    return genai.Client(api_key=keys[current_key_index % len(keys)])

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
        # Rotate to the next key if current one hits limit
        keys = get_all_keys()
        if keys:
            current_key_index = (current_key_index + 1) % len(keys)
        return jsonify({"answer": "Switching servers, please try your request again in a second."})

if __name__ == '__main__':
    app.run()
