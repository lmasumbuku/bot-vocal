import os
import openai
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

@app.route("/test_openai", methods=['GET'])
def test_openai():
    """ Teste OpenAI sur Render """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Donne-moi une commande typique dans un restaurant"}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur OpenAI : {str(e)}"

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère les appels et demande la commande du client """
    response = VoiceResponse()

    response.say("Bienvenue dans votre restaurant ! Que souhaitez-vous commander ?", 
                 voice='alice', language='fr-FR')

    # 🎙️ Enregistrer l'appel et activer la transcription
    response.record(timeout=10, transcribe=True, transcribe_callback="/transcription", play_beep=True)

    return str(response)

@app.route("/transcription", methods=['POST'])
def transcription():
    """ Récupère la transcription et affiche dans les logs """
    transcribed_text = request.form.get("TranscriptionText", "")
    audio_url = request.form.get("RecordingUrl", "")

    print(f"📞 Twilio a envoyé la transcription : {transcribed_text}")  # Debug

    if not transcribed_text:
        # Utiliser OpenAI Whisper pour améliorer la transcription
        transcribed_text = transcrire_avec_openai(audio_url)

    # 🔍 Analyser la commande et extraire les plats/quantités
    commande_analysee = analyser_commande(transcribed_text)

    response = VoiceResponse()
    response.say(f"Vous avez commandé : {commande_analysee}. Merci pour votre commande !", 
                 voice='alice', language='fr-FR')

    return str(response)

def transcrire_avec_openai(audio_url):
    """ 🔍 Utilise OpenAI Whisper pour transcrire l'audio """
    if not audio_url:
        return "Je n'ai pas compris votre commande."
    
    response = openai.Audio.transcribe("whisper-1", audio_url)
    return response.get("text", "Je n'ai pas compris votre commande.")

def analyser_commande(texte):
    """ 🔍 Analyse la commande pour extraire les plats et quantités """
    plats_disponibles = ["pizza", "burger", "salade", "sushi", "pâtes", "tacos"]
    quantites = ["un", "deux", "trois", "quatre", "cinq", "six"]

    commande = texte.lower()
    elements_commande = []

    for plat in plats_disponibles:
        if plat in commande:
            quantite = 1  # Valeur par défaut
            for q in quantites:
                if q in commande:
                    quantite = quantites.index(q) + 1
            elements_commande.append(f"{quantite} {plat}(s)")

    return ", ".join(elements_commande) if elements_commande else "Commande non reconnue"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
