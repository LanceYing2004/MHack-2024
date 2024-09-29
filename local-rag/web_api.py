from flask import Flask, request, jsonify
import requests
from localrag import process_user_call


 

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def api():
    data = request.json
    user_input = data.get('input')

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Call the process_user_call function from ollama_processor
    try:
        response = process_user_call(user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)






# python -m web_api run --host=0.0.0.0 --port=5000

#  * Running on all addresses (0.0.0.0)
#  * Running on http://127.0.0.1:5000
#  * Running on http://35.0.128.189:5000
#   Press CTRL+C to quit
