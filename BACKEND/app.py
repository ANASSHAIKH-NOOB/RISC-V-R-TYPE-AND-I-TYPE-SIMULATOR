from flask import Flask, request, jsonify
from flask_cors import CORS
from assembler import assemble
from executor import execute

app = Flask(__name__)
CORS(app)  # allows your HTML (on a different port) to call this

@app.route('/execute', methods=['POST'])
def run():
    try:
        data     = request.get_json()
        code     = data['code']
        instrs   = assemble(code)
        result   = execute(instrs)
        return jsonify({
            'registers': result['registers'],
            'log':       result['log'],
            'binary':    [{'source': i['source'], 'binary': i['binary'], 'address': i['address']} for i in instrs],
            'error':     None
        })
    except Exception as e:
        return jsonify({'registers': None, 'log': [], 'binary': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)