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
    """ Teste OpenAI sur Render avec affichage des erreurs détaillées """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Donne-moi une commande typique dans un restaurant"}]
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        return f"Erreur OpenAI détectée : {str(e)}"
    except Exception as e:
        return f"Erreur inconnue : {str(e)}"

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère les appels et demande la commande du client """
    response = VoiceResponse()

    response.say("Bienvenue dans votre restaurant ! Que souhaitez-vous commander ?", 
                 voice='alice', language='fr-FR')

    # 🎙️ Enregistrer l'appel sans transcription (on utilisera OpenAI)
    response.record(
        timeout=10, 
        play_beep=True,  
        max_length=15  # ⏳ Eviter une coupure trop rapide
    )

    response.pause(length=2)
    response.say("Merci pour votre commande. Nous la traitons.", voice='alice', language='fr-FR')

    return str(response)

import requests

def transcrire_avec_openai(audio_url):
    """ 🔍 Télécharge l'audio et l'envoie à OpenAI pour transcription """
    try:
        print(f"🚀 Téléchargement de l'audio depuis Twilio : {audio_url}")

        # 📥 Télécharger l'audio de Twilio
        response = requests.get(audio_url)
        if response.status_code != 200:
            print(f"❌ Erreur lors du téléchargement de l'audio: {response.status_code}")
            return "Erreur de récupération de l'audio."

        # 📂 Sauvegarde temporaire du fichier audio
        audio_path = "audio_twilio.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)

        print("✅ Audio téléchargé avec succès, envoi à OpenAI Whisper...")

        # 📤 Envoyer l'audio à OpenAI Whisper pour transcription
        with open(audio_path, "rb") as audio_file:
            whisper_response = openai.Audio.transcribe("whisper-1", audio_file)

        return whisper_response.get("text", "Je n'ai pas compris votre commande.")
    
    except Exception as e:
        print(f"❌ Erreur transcription OpenAI: {str(e)}")
        return "Erreur lors de la transcription."

@app.route("/transcription", methods=['POST'])
def transcription():
    """ Récupère la transcription et affiche dans les logs """
    transcribed_text = request.form.get("TranscriptionText", "")
    audio_url = request.form.get("RecordingUrl", "")

    print(f"📞 Twilio a envoyé la transcription : {transcribed_text}")
    print(f"🎙️ URL de l'enregistrement : {audio_url}")  

    if not transcribed_text and audio_url:
        print("🚀 Aucun texte reçu de Twilio, transcription via OpenAI Whisper...")
        transcribed_text = transcrire_avec_openai(audio_url)

    # 🔍 Analyser la commande et extraire les plats/quantités
    commande_analysee = analyser_commande(transcribed_text)

    response = VoiceResponse()
    response.say(f"Vous avez commandé : {commande_analysee}. Merci pour votre commande !", 
                 voice='alice', language='fr-FR')

    return str(response)

@app.route("/debug_transcription", methods=['POST'])
def debug_transcription():
    """ Vérifie les données envoyées par Twilio après l'enregistrement """
    print("📩 Données reçues de Twilio :", request.form)
    return "OK"

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
