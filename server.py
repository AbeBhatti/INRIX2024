from flask import Flask, request, jsonify
from flask_cors import CORS
from amberSearch import amberSearch

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/ai')
def ai():
    carMake = request.args.get('carMake')
    carModel = request.args.get('carModel')
    carColor = request.args.get('carColor')
    return jsonify(amberSearch(carMake, carModel, carColor))
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)