from flask import Flask, request, jsonify
from flask_cors import CORS
from assembler import assemble
from executor import execute

app = Flask(__name__)
CORS(app)   # allows your HTML file to call this from a different port

@app.route('/execute', methods=['POST'])
def run():
    try:
        data = request.get_json()
        code = data['code']
        instructions = assemble(code)
        result = execute(instructions)
        return jsonify({ 'registers': result['registers'], 'log': result['log'], 'error': None })
    except Exception as e:
        return jsonify({ 'registers': None, 'log': [], 'error': str(e) })

if __name__ == '__main__':
    app.run(debug=True, port=5000)