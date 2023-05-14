import os, openai, base64, json
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_session import Session
from gtts import gTTS
from tempfile import TemporaryDirectory
import speech_recognition as sr
from moviepy.editor import AudioFileClip
from pydub import AudioSegment

conversation_history = []

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

openai.api_key = open("keys/api_key.txt", 'r').read()


@app.route("/")
def home():
   if not session.get('logged_in'):
      return redirect(url_for('login'))
   return render_template("index.html", conversation_histories = session.get('conversation_histories', []))


@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']

      if username == 'YOUR_USERNAME' and password == 'PASSWORD':
         session['logged_in'] = True
         return redirect(url_for('home'))
      else:
         return render_template('login.html', error="Invalid credentials")
   return render_template('login.html')


@app.route('/logout')
def logout():
   session.pop('logged_in', None)
   return redirect(url_for('login'))


def get_chatgpt_response(conversation_history):
   messages = [
      {"role": "system", "content": "You are a helpful assistant that helps users learn English. Please speak in a clear and simple tone, help them correct their mistakes, and guide them on how to improve their speaking skills. When responding, keep your messages short and to the point. Remember to help them correct any mistakes in their sentences."}
   ]
   
   messages.extend(conversation_history)
   
   try:
      response = openai.ChatCompletion.create(
         model = "gpt-3.5-turbo",
         messages = messages,
         temperature = 0.5,
         max_tokens = 1000,
         frequency_penalty = 0,
         presence_penalty = 0,
      )
      result = response['choices'][0]['message']['content'].strip()
   except Exception as e:
      print(e)
      result = f"Error: Unable to process the request. {str(e)}"
   
   return result


def text_to_speech(text):
   with TemporaryDirectory() as temp_dir:
      tts = gTTS(text, lang="en")
      audio_file_path = os.path.join(temp_dir, "output.mp3")
      tts.save(audio_file_path)
      with open(audio_file_path, "rb") as audio_file:
         audio_data = audio_file.read()
   return base64.b64encode(audio_data).decode("utf-8")


@app.route("/", methods = ["POST"])
def chat():
   if request.method == "POST":
      prompt = request.form["prompt"]
      conversation_history = json.loads(request.form.get("history"))

      conversation_history.append({"role": "user", "content": prompt})
      response_text = get_chatgpt_response(conversation_history)

      audio_data = text_to_speech(response_text)
      conversation_history.append({"role": "assistant", "content": response_text})

      return jsonify({"response_text": response_text, "audio_data": audio_data, "history": conversation_history})
   
   return render_template("index.html", conversation_histories = session.get('conversation_histories', []))

@app.route("/history")
def history():
   return render_template("history.html", conversation_histories=session.get('conversation_histories', []))


@app.route("/send-audio", methods=["POST"])
def send_audio():
   if request.method == "POST":
      try:
         conversation_history = json.loads(request.values.get("history")) or []
      except TypeError:
         pass

      audio_data = request.files["audio"]

      # Save the received audio file
      temp_webm_path = "audio/temp_audio_file.webm"
      temp_mp3_path = "audio/temp_audio_file.mp3"
      with open(temp_webm_path, "wb") as f:
         f.write(audio_data.read())
         
      # Convert WebM to MP3 using Pydub
      webm_audio = AudioSegment.from_file(temp_webm_path, format = "webm")
      webm_audio.export(temp_mp3_path, format = "mp3")

      # Load the WebM audio file using moviepy
      webm_audio = AudioFileClip(temp_mp3_path)

      # Export the audio as a WAV file
      temp_wav_path = "audio/temp_audio_file.wav"
      webm_audio.write_audiofile(temp_wav_path, codec='pcm_s16le')

      # Process the audio using speech_recognition
      recognizer = sr.Recognizer()
      with sr.AudioFile(temp_wav_path) as source:
         audio = recognizer.record(source)

      # Recognize the speech
      text = recognizer.recognize_google(audio)

      # Add the user's message to the conversation history
      conversation_history.append({"role": "user", "content": text})

      # Generate the response
      response_text = get_chatgpt_response(conversation_history)

      # Add the ChatGPT's response to the conversation history
      conversation_history.append({"role": "assistant", "content": response_text})

      audio_data = text_to_speech(response_text)

      # Remove temporary files
      try:
         os.remove(temp_webm_path)
         os.remove(temp_wav_path)
         os.remove(temp_mp3_path)
      except FileNotFoundError:
         pass

      return jsonify({"response_text": response_text, "audio_data": audio_data, "history": conversation_history, "user_text": text})

   return render_template("index.html", conversation_histories=session.get('conversation_histories', []))


@app.route("/delete-history", methods=["POST"])
def delete_history():
   session['conversation_histories'] = []
   session.modified = True
   return redirect(url_for("history"))


@app.route("/save-history", methods=["POST"])
def save_history():
   conversation_history = request.json.get('conversation_history')
   if 'conversation_histories' not in session:
      session['conversation_histories'] = []

   session['conversation_histories'].append(conversation_history)
   session.modified = True
   return jsonify({"success": True})


if __name__ == "__main__":
   app.run(debug = True)