from flask_cors import cross_origin, CORS
from main import get_token, auth, get_message_history
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import json
import time
import os
from vk_cloud import access_token, send_image, getText
from flask import Flask, flash, request, redirect, url_for
from with_history import send_with_doc
from sql import upload_data, load_data, update_data
import ast
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'C:/Users/User1/PycharmProjects/Task4/download-files'
ALLOWED_EXTENSIONS_IMAGE = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS_DOC = set(['doc', 'docx'])


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
response = get_token(auth)
lock = asyncio.Lock()
cors = CORS(app, resources={r"*": {"origins": "*"}})

if response != 1:
    giga_token = response.json()['access_token']
    expires_at = response.json()['expires_at']


@app.route('/api/send-message', methods=['POST', 'GET'])
async def give_greeting():
    if round(time.time()*1000) >= expires_at:
        async with lock:
            refresh()
    request_data = request.form  # Получаем JSON из тела запроса
    history = json.loads(request_data.get('history'))
    if history is None or len(history) == 0:
        conversation_history = None
    else:
        conversation_history = history
    response, conversation_history = await get_message_history(giga_token, conversation_history)
    response_data = response.json()
    return json.dumps(response_data['choices'][0]['message'])
async def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE
async def allowed_file_doc(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_DOC
@app.route('/api/send-file', methods = ['POST'])
async def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part

        # if user does not select file, browser also
        # submit a empty part without filename
        user_id, chat_id = int(request.form['user_id']), int(request.form['chat_id'])
        question = request.form['question']
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and (await allowed_image(file.filename) or await allowed_file_doc(file.filename)):
                if await allowed_image(file.filename):
                    file_to_txt = await send_image(file, access_token)
                elif await allowed_file_doc(file.filename):
                    file_to_txt = await getText(file)
                chat_history = []
                chat_history = str(chat_history)
                answer_AI, chat_history = await send_with_doc(file_to_txt, question, chat_history)
                chat_history = str(chat_history)
                upload_data(user_id, file_to_txt, chat_history, chat_id)
                return answer_AI
        else:
            file_to_txt, chat_history = load_data(user_id, chat_id)
            answer_AI, chat_history = await send_with_doc(file_to_txt, question, chat_history)
            chat_history = str(chat_history)
            update_data(user_id, chat_history, chat_id)
            return answer_AI

            #filename = 'image.jpg'
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
def refresh():
    global giga_token, expires_at
    response = get_token(auth)
    if response != 1:
        giga_token = response.json()['access_token']
        expires_at = response.json()['expires_at']
    return


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4567)