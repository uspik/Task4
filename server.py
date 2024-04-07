from flask import Flask
from main import get_token, auth, get_message_history
app = Flask(__name__)

@app.route('/send_to_GigaChat/<message>')
def give_greeting(message):
    response = get_token(auth)
    if response != 1:
        giga_token = response.json()['access_token']
        conversation_history = []
        response, conversation_history = get_message_history(giga_token, message, conversation_history)
        response_data = response.json()
        return response_data['choices'][0]['message']['content']

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4567)