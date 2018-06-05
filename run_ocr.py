from flask import Flask, render_template, send_file, request, make_response, stream_with_context, send_file
import json, os
from utils_ocr import exec_stream_fj, exec_stream_zj
import io
import pandas as pd

import pyexcel

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.getcwd()

html = '''
    <!DOCTYPE html>
        <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/4.0.0-beta/css/bootstrap.min.css"
          integrity="sha384-/Y6pD6FV/Vv2HJnA6t+vslU6fwYXjCFtcEpHbNJ0lyAFsXTsjBbfaDjzALeQsN6M" crossorigin="anonymous">
    <title>Upload File</title>
    
    <h1>文件上传</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file class=btn-primary>
         <input type=submit value=上传>
    </form>
    '''


@app.route('/upzj', methods=['POST'])
def uploadzj():
    file = request.files['file']
    # app.logger.info(file.filename)
    if file:
        filename = file.filename
        app.logger.info(filename)
        data_xml = pyexcel.get_records(file_type="xlsx", file_content=file)
        # app.logger.info(data_xml)
        result = exec_stream_zj(data_xml)
        return json.dumps(result)


@app.route('/upfj', methods=['POST'])
def uploadfj():
    file = request.files['file']
    # app.logger.info(file.filename)
    if file:
        filename = file.filename
        app.logger.info(filename)
        data_xml = pyexcel.get_records(file_type="xlsx", file_content=file)
        # app.logger.info(data_xml)
        result = exec_stream_fj(data_xml)
        return json.dumps(result)


@app.route('/download', methods=['GET'])
def download():
    # with open("buf_img_dxp.jpg", "rb") as f:
    #     content = f.read()
    # response = make_response(content)
    response = make_response(send_file("buf_img_dxp.jpg"))

    response.headers['Content-Disposition'] = 'attachment; filename={}'.format("response.jpg")
    return response


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        print(request.form)
        file = request.files['file']

        if file:
            filename = file.filename
            app.logger.info(filename)
            # 方法一
            # csvfile = io.BufferedReader(file.stream)
            # c = pd.read_excel(csvfile)
            # app.logger.info(c)

            # 方法二   参考pyexcel-xls文档
            # data_xml = pyexcel.get_records(file_type="xlsx", file_content=file)
            # app.logger.info(data_xml)
            # result = exec_stream_fj(data_xml)
            # return json.dumps(result)
            return json.dumps("hello,upload")
    return html


@app.route('/queryfj')
def queryfj():
    name = "福建税务局发票查询系统"
    return render_template('showfj.html', user=name)


@app.route('/queryzj')
def query_zj():
    name = "浙江税务局发票查询系统"
    return render_template('showzj.html', user=name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8899, debug=True, threaded=True)
