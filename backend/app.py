# Backend API (Flask sample)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    # ... AI logic here ...
    return jsonify({'fruits': ['apple', 'banana']})

if __name__ == '__main__':
    app.run(debug=True)
