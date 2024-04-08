from flask import Flask, request
from main import get_token, auth, get_message_history
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import json
app = Flask(__name__)
response = get_token(auth)
lock = asyncio.Lock()

if response != 1:
    giga_token = response.json()['access_token']

@app.route('/send_to_GigaChat/<message>', methods=['POST'])
async def give_greeting(message):
    conversation_history = str(request.data, "utf-8")
    response, conversation_history = await get_message_history(giga_token, message, json.loads(conversation_history.replace("\n", "")))
    response_data = response.json()
    return response_data['choices'][0]['message']['content']

async def refresh():
    global giga_token
    async with lock:
        response = get_token(auth)
        if response != 1:
            giga_token = response.json()['access_token']

if __name__ == "__main__":
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.start()
    scheduler.add_job(refresh, 'interval', minutes=29)
    app.run(host='0.0.0.0', port=4567)