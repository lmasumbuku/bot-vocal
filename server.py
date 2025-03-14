import os
import openai
import requests
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/test", methods=['GET'])
def test():
    """ Vérification si le serveur fonctionne """
    return "✅ Le serveur Render fonctionne !"

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère les appels et demande la commande du client """
    response = VoiceResponse()

    response.say("Bienvenue dans votre restaurant ! Que souhaitez-vous commander ?", 
                 voice='alice', language='fr-FR')

    # 🎙️ Enregistrer l'appel sans transcription (on utilisera OpenAI Whisper)
    response.record(
        timeout=10, 
        play_beep=True,  
        max_length=15  # ⏳ Eviter une coupure trop rapide
    )

    response.pause(length=2)
    response.say("Merci pour votre commande. Nous la traitons.", voice='alice', language='fr-FR')

    return str(response)

@app.route("/transcription", methods=['POST'])
def transcription():
    """ Récupère l'audio et l'envoie à OpenAI pour transcription """
    audio_url = request.form.get("RecordingUrl", "")

    print(f"🎙️ URL de l'enregistrement reçu : {audio_url}")

    if not audio_url:
        print("❌ Aucun enregistrement reçu de Twilio !")
        return "Erreur : Pas d'URL d'enregistrement reçue."

    # 📥 Télécharger l'audio
    audio_path = "audio_twilio.mp3"
    response = requests.get(audio_url, allow_redirects=True)

    if response.status_code == 200:
        with open(audio_path, "wb") as f:
            f.write(response.content)
        print("✅ Audio téléchargé avec succès !")
    else:
        print(f"❌ Erreur lors du téléchargement : {response.status_code}")
        return "Erreur de récupération de l'audio."

    # 📤 Envoyer l'audio à OpenAI pour transcription
    transcribed_text = transcrire_avec_openai(audio_path)

    print(f"✅ Transcription OpenAI : {transcribed_text}")

    response = VoiceResponse()
    response.say(f"Vous avez commandé : {transcribed_text}. Merci pour votre commande !", 
                 voice='alice', language='fr-FR')

    return str(response)

def transcrire_avec_openai(audio_path):
    """ 🔍 Envoie l'audio téléchargé à OpenAI Whisper pour transcription """
    try:
        print("🚀 Envoi de l'audio à OpenAI Whisper...")

        with open(audio_path, "rb") as audio_file:
            whisper_response = openai.Audio.transcribe("whisper-1", audio_file)

        print(f"✅ Réponse OpenAI : {whisper_response.get('text')}")
        return whisper_response.get("text", "Je n'ai pas compris votre commande.")

    except Exception as e:
        print(f"❌ Erreur OpenAI Whisper : {str(e)}")
        return "Erreur lors de la transcription."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
