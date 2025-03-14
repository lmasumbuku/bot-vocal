import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère les appels téléphoniques et permet la prise de commande vocale """
    response = VoiceResponse()

    response.say("Bienvenue dans votre restaurant ! Que souhaitez-vous commander ?", 
                 voice='alice', language='fr-FR')

    response.record(timeout=5, transcribe=True, transcribe_callback="/transcription")

    return str(response)

@app.route("/transcription", methods=['POST'])
def transcription():
    """ Récupère la transcription de la commande et renvoie une confirmation """
    transcribed_text = request.form.get("TranscriptionText", "")
    
    response = VoiceResponse()
    
    if transcribed_text:
        response.say(f"Vous avez commandé : {transcribed_text}. Merci !", voice='alice', language='fr-FR')
    else:
        response.say("Je n'ai pas compris votre commande. Merci de réessayer.", voice='alice', language='fr-FR')

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
