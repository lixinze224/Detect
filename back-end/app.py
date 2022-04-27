import datetime
import logging as rel_log
import os
import shutil
from datetime import timedelta
from flask import *
# from tools.inference import Detector
from tools.NohInference import NohDetector
from tools.CrowdetInference import CrowdetDetector
import core.main

UPLOAD_FOLDER = r'./uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

werkzeug_logger = rel_log.getLogger('werkzeug')
werkzeug_logger.setLevel(rel_log.ERROR)

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

model = CrowdetDetector()
crowdetmodel = CrowdetDetector()
nohmodel = NohDetector()
# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#路由 根据url映射到hello world函数上
@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))

#和前端axios 的POST对应
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    #print(request.files) dataform传输
    file = request.files['file']
    print(datetime.datetime.now(), file.filename)
    if file and allowed_file(file.filename):
        src_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(src_path)
        shutil.copy(src_path, './tmp/ct')
        image_path = os.path.join('./tmp/ct', file.filename)
        pid, image_info = core.main.c_main(
            image_path, model, file.filename.rsplit('.', 1)[1])
        print(datetime.datetime.now(), "OK")
        return jsonify({'status': 1,
                        'image_url': 'http://127.0.0.1:5003/tmp/ct/' + pid,
                        'draw_url': 'http://127.0.0.1:5003/tmp/draw/' + pid,
                        'image_info': image_info})
    
    return jsonify({'status': 0})
@app.route('/net', methods=['GET', 'POST'])
def net():
    # print(request.method) json传输 
    global model
    print(request.json)
    if request.json['data'] == '2':
        model = nohmodel
    elif request.json['data'] == '1':
        model = crowdetmodel
    str = "OK"
    model.print_name()
    return str
@app.route("/download", methods=['GET'])
def download_file():
    # 下载测试文件需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


# show photo 数据类型为path
@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    if request.method == 'GET':
        if not file is None:
            image_data = open(f'tmp/{file}', "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response


if __name__ == '__main__':
    files = [
        'uploads', 'tmp/ct', 'tmp/draw',
        'tmp/image', 'tmp/mask', 'tmp/uploads'
    ]
    for ff in files:
        if not os.path.exists(ff):
            os.makedirs(ff)
    with app.app_context():
        # model = CrowdetDetector()
        model.print_name()
    app.run(host='127.0.0.1', port=5003, debug=True)
