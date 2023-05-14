# English Tutor Chatbot

This is a simple chatbot project that helps users learn English. The chatbot uses OpenAI's GPT-3.5-turbo model for generating responses, Google Text-to-Speech for audio output, and speech recognition for audio input. It features a web interface built with Flask, where users can interact with the chatbot using text or audio.

## Features

- Text-based chat interface
- Audio input and output support
- User authentication and login system
- Conversation history management

## Installation

1. Clone the repository:

```
git clone https://github.com/MoeXD2/english-tutor-chatbot.git
```

2. Navigate to the project directory:

```
cd english-tutor-chatbot
```

3. Install the required dependencies:

```
pip install -r requirements.txt
```

4. Replace `YOUR_USERNAME` and `PASSWORD` in the `login()` function in the `app.py` file with your desired username and password.

5. Create a `keys` directory in the project root and place your OpenAI API key in a file named `api_key.txt` inside the `keys` directory.

## Usage

1. Run the Flask app:

```
python app.py
```

2. Open a web browser and navigate to `http://localhost:5000/login`.

3. Log in using the username and password you set in the `app.py` file.

4. Start interacting with the chatbot using text or audio input.

## Dependencies

- Flask
- Flask-Session
- openai
- gtts
- pydub
- moviepy
- SpeechRecognition
