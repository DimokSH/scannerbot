from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Инициализация множества ключей
my_keys = {'7', '105'}

# Инициализация хранилища для QR-кодов
storage = {}

@app.route('/addKey/', methods=['GET'])
def add_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key in my_keys:
        return jsonify({"message": "key {key} is allredy exist"}), 404
    my_keys.add(key)
    return '', 200

@app.route('/checkKey/', methods=['GET'])
def check_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key in my_keys:
        return '', 200
    return jsonify({"message": f"error checkKey key {key} not found"}), 404

@app.route('/newqr/', methods=['GET'])
def new_qr():
    key = request.args.get('key')
    qr = request.args.get('qr')
    if not key or not qr:
        return jsonify({"message": "Missing key or qr parameter"}), 400
    if key not in my_keys:
        return jsonify({"message": f"error newqr not found {key}"}), 404
    if key not in storage:
        storage[key] = []
    storage[key].append(qr)
    return str(storage[key]), 200

@app.route('/deleteKey/', methods=['GET'])
def delete_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key not in my_keys:
        return jsonify({"message": f"error deleteKey key {key} not found"}), 404
    my_keys.remove(key)
    if key in storage:
        del storage[key]
    return '', 200

@app.route('/getStorage/', methods=['GET'])
def get_storage():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key not in my_keys:
        return jsonify({"message": f"error getStorage key {key} not found"}), 404
    data = storage.get(key, [])
    if key in storage:
        del storage[key]
    return jsonify(data), 200

@app.route('/listKeys', methods=['GET'])
def list_keys():
    return jsonify(list(my_keys)), 200

@app.route('/listStorage', methods=['GET'])
def list_storage():
    return jsonify(storage), 200

@app.route('/', methods=['GET'])
def scan():
    return render_template('index.html')

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify('hello'), 200
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
