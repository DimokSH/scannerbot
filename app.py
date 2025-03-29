import os, random

from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask import Flask


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB (adjust as needed)
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

UPLOAD_FOLDER = 'uploads'
# Инициализация множества ключей
myKeys = {'777'}
myKeysParams = {'777': {'dateCreated': datetime.today()}}

# Инициализация хранилища для QR-кодов
storage = {}


def deleteFile(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            print(f"Ошибка: файл {file_path} не существует.")
            return []
        if not os.path.isfile(file_path):
            print(f"Ошибка, это не файл: {file_path} не существует.")
        os.remove(file_path)
    except Exception as e:
        print(f"Ошибка при удалении: {e}")


# удалим из ключей, из myKeysParams и файлы тоже надо удалить
def deleteAllDataByKey(key):
    myKeys.remove(key)  # удалим из ключей
    _ = myKeysParams.pop(key, None)  # удалим из хранилища дат

    # удалим файлы относящиеся к данному ключу
    listFoto = find_files_by_prefix(key)
    for fileName in listFoto:
        deleteFile(fileName)


def find_files_by_prefix(search_prefix):
    # Получаем путь к каталогу запускаемого файла
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, "uploads")

    # Проверка существования каталога uploads
    if not os.path.exists(target_dir):
        print(f"Ошибка: каталог {target_dir} не существует.")
        return []
    if not os.path.isdir(target_dir):
        print(f"Ошибка: {target_dir} не является каталогом.")
        return []

    # Поиск файлов, начинающихся с подстроки
    matching_files = []
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if os.path.isfile(item_path) and item.startswith(search_prefix):
            matching_files.append(item)

    return matching_files


# @app.route('/addKey/', methods=['GET'])
# def add_key():
#     key = request.args.get('key')
#     if not key:
#         return jsonify({"message": "Key parameter is missing"}), 400
#     if key in myKeys:
#         return jsonify({"message": "key {key} is allredy exist"}), 404
#     myKeys.add(key)
#     return '', 200


@app.route('/checkKey/', methods=['GET'])
def check_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key in myKeys:
        return '', 200
    return jsonify({"message": f"error checkKey key {key} not found"}), 404


@app.route('/newqr/', methods=['GET'])
def new_qr():
    key = request.args.get('key')
    qr = request.args.get('qr')
    if not key or not qr:
        return jsonify({"message": "Missing key or qr parameter"}), 400
    if key not in myKeys:
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
    if key not in myKeys:
        return jsonify({"message": f"error deleteKey key {key} not found"}), 404
    myKeys.remove(key)
    if key in storage:
        del storage[key]
    return '', 200


@app.route('/getStorage/', methods=['GET'])
def get_storage():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key not in myKeys:
        return jsonify({"message": f"error getStorage key {key} not found"}), 404
    data = storage.get(key, [])
    if len(data) == 0:
        return jsonify(data), 300
    # удаляем штрихкод из массива штрихкодов
    if key in storage:
        del storage[key]
    print(data)
    return jsonify(data), 200


@app.route('/listKeys', methods=['GET'])
def list_keys():
    return jsonify(list(myKeys)), 200


@app.route('/listStorage', methods=['GET'])
def list_storage():
    return jsonify(storage), 200


@app.route('/listFiles', methods=['GET'])
def listFiles():
    l = []
    for key in myKeys:
        l2 = find_files_by_prefix(key)
        l = [*l, *l2]
    return jsonify(l), 200


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_photo/', methods=['POST'])
def upload_photo():
    key = request.args.get('key')
    print(key)
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key not in myKeys:
        return jsonify({"message": f"error  key {key} not found in storage"}), 400
    print(22222)

    # только одно фото может быть для одного ключа!
    #
    listFiles = find_files_by_prefix(key)
    for fileName in listFiles:
        deleteFile(fileName)

    # Проверка наличия файла
    if 'photo' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['photo']


    # Проверка расширения файла
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400


    # Генерация безопасного имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{key}_{timestamp}.{extension}"

    # Сохранение файла
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    return jsonify({'message': 'File uploaded successfully', 'filename': 'ok'}), 200


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', servAdr=servAdr)


@app.route('/foto', methods=['GET'])
def foto():
    return render_template('foto.html', servAdr=servAdr)


@app.route('/getfoto/', methods=['GET'])
def get_foto():
    key = request.args.get('key')
    if not key:
        return jsonify({"message": "Key parameter is missing"}), 400
    if key not in myKeys:
        return jsonify({"message": f"error  key {key} not found in storage"}), 404

    # только одно фото может быть для одного ключа!
    listFiles = find_files_by_prefix(key)
    if len(listFiles) == 0:
        return jsonify({"message": f"Нет файлов для передачи"}), 404

    filename = listFiles[0]
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.isfile(file_path):
        return jsonify({"message": "File not found"}), 404

    return send_from_directory(UPLOAD_FOLDER, filename)


# @app.route('/', methods=['GET'])
# def home():
#     return jsonify('hello'), 200

@app.route('/generateNewKey', methods=['GET'])
def generateNewKey():
    # удалим старые просроченные ключи - если больше одного дня назад создан
    setCopy = myKeys.copy()
    for key in setCopy:
        daysFromCreation = (datetime.today() - myKeysParams[key]['dateCreated']).days
        if daysFromCreation > 2:
            print(f'удаляем ключ {key} daysGone {daysFromCreation}')
            deleteAllDataByKey(key)

    newKey = '999'
    while newKey not in myKeys:
        newKey = str(random.randint(100, 998))
        if newKey not in myKeys:
            myKeys.add(newKey)
            myKeysParams[newKey] = {'dateCreated': datetime.today()}
            break

    return jsonify({'message': 'new key generated successfully', 'key': newKey}), 200



# generateNewKey()


if __file__ == 'D:\\__Python_projects\\pythonScanner\\app.py':
    servAdr = 'http://127.0.0.1:5000'
else:
    servAdr = 'https://scannerbot.ru'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)



