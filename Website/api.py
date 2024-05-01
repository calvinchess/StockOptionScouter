from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import subprocess
import Test

app = Flask(__name__)
CORS(app)

@app.route('/date', methods=['GET'])
def get_date():
    date = datetime.strftime(datetime.now(), "%m %d, %Y")
    return jsonify({'date': date})

@app.route('/date', methods=['GET'])
def get_date():
    date = datetime.strftime(datetime.now(), "%m %d, %Y")
    return jsonify({'date': date})

if __name__ == '__main__':
    app.run()