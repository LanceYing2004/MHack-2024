from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)


# Function to call the Ollama model API
def get_ollama_response(prompt):
    url = 'http://localhost:11434/api/generate'  # Ollama API URL
    headers = {'Content-Type': 'application/json'}
    body = {
        "model": "llama3",
        "prompt": prompt,
        "stream" : False
    }
    # curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d "{ \"model\": \"llama3\", \"prompt\": \"Why is the sky blue?\", \"stream\": false }"

    # Make the request to the Ollama API
    response = requests.post(url, headers=headers, json=body)

    print(response.text)  # Print the raw response for debugging
    return response.text


@app.route('/api', methods=['POST'])
def api():
    data = request.json
    user_input = data.get('input')

    # Get the response from the Ollama model
    output = get_ollama_response(user_input)

    return jsonify(output)  # Return the output JSON


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# python -m web_api run --host=0.0.0.0 --port=5000

#  * Running on all addresses (0.0.0.0)
#  * Running on http://127.0.0.1:5000
#  * Running on http://35.0.128.189:5000
#   Press CTRL+C to quit
