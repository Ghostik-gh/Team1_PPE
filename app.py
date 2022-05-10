import os
import shutil
from flask import Flask, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
from Yolov5_DeepSort_Pytorch.track import start
import Yolov5_DeepSort_Pytorch.track
from threading import Thread
from time import sleep
# import database

# import sys
# _PATH = 'C:\msys64\mingw64\bin'
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + _PATH)

'''
Для начала следует установить сам gstreamer в систему.

[Для Linux Ubuntu]
Чтобы установить gstreamer в систему запустите в терминале:

>> sudo apt install libgstreamer1.0-0 gstreamer1.0-plugins-{base,good,bad,ugly} gstreamer1.0-tools python3-gi gir1.2-gstreamer-1.0
>> sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
'''

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib


app = Flask(__name__)

# Папка для сохранения загруженных файлов
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# conn_data = ()
# db = database.Database((conn_data))


@app.route('/', methods=['POST'])
def upload_file_POST():
    # loading_flag = False

    ###########################################################################
    # Удаляет все папки чтобы запущенный ран сохранился в 
    # Yolov5_DeepSort_Pytorch\runs\track\weights\best_osnet_ibn_x1_0_MSMT17
    delete_folder = './Yolov5_DeepSort_Pytorch/runs/track/weights/'
    delete_folders = os.listdir(delete_folder)
    for g in delete_folders:
        try:
            shutil.rmtree(delete_folder + g)
            print(f'[INFO] "{g}" from "{delete_folder}" was deleted!')
        except:
            pass

    ###########################################################################
    # Сохраняет файл в UPLOAD_FOLDER
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    filename = secure_filename(file.filename)
    filepath = f"{app.config['UPLOAD_FOLDER']}/{filename}"
    file.save(filepath)

    ###########################################################################
    return redirect(url_for('loading', file = filename))


@app.route('/', methods=['GET'])
def upload_file_GET():
    return render_template('index.html')


@app.route('/load/<file>', methods=['GET', 'POST'])
def loading(file):
    # @after_this_request
    # def after_request(responce):
    #     # Запускает Треккинг видео
    #     # Переносим файл в static
    #     return responce
    return redirect(url_for('download', file = file))
    # return render_template('loading.html')


@app.route('/download/<file>', methods=['GET', 'POST'])
def download(file):
    filepath = f"{app.config['UPLOAD_FOLDER']}/{file}"
    data = start(filepath)
    # db.push(data, 'small', 'xdxdxdxdxdxd')

    ###########################################################################
    # Данный кусок кода удаляет загруженный исходный файл из /uploads
    try:
        delete_folder = './uploads/'
        delete_files = os.listdir(delete_folder)
        for n in delete_files:
            os.remove(delete_folder + n)
            print(f'[INFO] Source file "{n}" from "{delete_folder}" was deleted.')
    except:
        print("[O-ops!] Failed to delete source file.")

    ###########################################################################
    # Переносим размеченный файл в /static
    try:
        file_source = './Yolov5_DeepSort_Pytorch/runs/track/weights/best_osnet_ibn_x1_0_MSMT17/'
        file_destination = './static/'
        get_files = os.listdir(file_source)    
        for g in get_files:
            shutil.move(file_source + g, file_destination)
            print(f'[INFO] {g} from "{file_source}" transfered by "{file_destination}" and ready for using!')
    except:
        print("[O-ops!] Output file already exists.")

    ###########################################################################
    # И удаляем папку откуда взяли файл
    try:
        delete_folder = 'Yolov5_DeepSort_Pytorch/runs/track/weights/'
        delete_files = os.listdir(delete_folder)
        for n in delete_files:
            print(f'[INFO] Folder "{n}" was deleted from "{delete_folder}".')
            shutil.rmtree(delete_folder + n)
    except:
        print("[O-ops!] Failed delete.")

    ###########################################################################
    # Gstreamer here   
    # В данном куске кода лишь пример использования gstreamer'a 
    Gst.init()

    main_loop = GLib.MainLoop()
    thread = Thread(target=main_loop.run)
    thread.start()
    pipeline = Gst.parse_launch("v4l2src ! decodebin ! videoconvert ! autovideosink")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass

    pipeline.set_state(Gst.State.NULL)
    main_loop.quit()

    ###########################################################################
    return render_template('videoplayer.html', filename=file)


if __name__ == "__main__":
    app.run(debug=True,  port=5000)
