import os
import openai
import requests
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/test", methods=['GET'])
def test():
    """ Vérification si le serveur fonctionne """
    return "✅ Le serveur Render fonctionne !"

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère les appels et enregistre la commande du client """
    response = VoiceResponse()

    response.say("Bienvenue ! Que souhaitez-vous commander ?", voice='alice', language='fr-FR')

    # 🎙️ Enregistrer la voix sans transcription Twilio
    response.record(
        timeout=10,
        play_beep=True,
        max_length=15
    )

    response.say("Merci pour votre commande. Nous la traitons.", voice='alice', language='fr-FR')

    return str(response)

@app.route("/transcription", methods=['POST'])
def transcription():
    """ Télécharge l'audio de Twilio et le transcrit avec OpenAI Whisper """
    audio_url = request.form.get("RecordingUrl", "")
    print(f"🎙️ URL de l'enregistrement reçu : {audio_url}")

    if not audio_url:
        print("❌ Aucun enregistrement reçu !")
        return "Erreur : Aucun enregistrement."

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

    # 📤 Envoyer l'audio à OpenAI Whisper
    transcribed_text = transcrire_avec_openai(audio_path)
    print(f"✅ Transcription OpenAI : {transcribed_text}")

    # 🔍 Analyse et réponse
    commande_analysee = analyser_commande(transcribed_text)
    print(f"✅ Commande analysée : {commande_analysee}")

    response = VoiceResponse()
    response.say(f"Vous avez commandé : {commande_analysee}. Merci pour votre commande !", 
                 voice='alice', language='fr-FR')

    return str(response)

def transcrire_avec_openai(audio_path):
    """ 🔍 Envoie l'audio téléchargé à OpenAI Whisper """
    try:
        print("🚀 Envoi de l'audio à OpenAI Whisper...")

        with open(audio_path, "rb") as audio_file:
            whisper_response = openai.Audio.transcribe("whisper-1", audio_file)

        print(f"✅ Réponse OpenAI : {whisper_response.get('text')}")
        return whisper_response.get("text", "Je n'ai pas compris votre commande.")

    except Exception as e:
        print(f"❌ Erreur OpenAI Whisper : {str(e)}")
        return "Erreur lors de la transcription."

def analyser_commande(texte):
    """ 🔍 Analyse la commande et détecte les plats et quantités """
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
