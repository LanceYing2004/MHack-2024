from flask import Flask, request, jsonify

app = Flask(__name__)

# Your existing function
def your_function(user_input):
    # Process the input and return output
    return f"Processed: Hi viraj, love the haircut. {user_input}"

@app.route('/api', methods=['POST'])
def api():
    data = request.json
    user_input = data.get('input')
    
    # Call your existing function
    output = your_function(user_input)
    
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Make the server accessible on your network
