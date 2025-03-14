import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère les appels et enregistre la commande du client """
    response = VoiceResponse()

    response.say("Bienvenue dans votre restaurant ! Que souhaitez-vous commander ?", 
                 voice='alice', language='fr-FR')

    # 🎙️ Enregistrer la voix du client et la transcrire
    response.record(timeout=5, transcribe=True, transcribe_callback="/transcription")

    return str(response)

@app.route("/transcription", methods=['POST'])
def transcription():
    """ Récupère la transcription et analyse la commande """
    transcribed_text = request.form.get("TranscriptionText", "")

    response = VoiceResponse()

    if transcribed_text:
        # 🔍 Analyse de la commande
        commande_analysee = analyser_commande(transcribed_text)
        
        response.say(f"Vous avez commandé : {commande_analysee}. Merci pour votre commande !", 
                     voice='alice', language='fr-FR')
    else:
        response.say("Je n'ai pas compris votre commande. Merci de réessayer.", voice='alice', language='fr-FR')

    return str(response)

def analyser_commande(texte):
    """ 🔍 Analyse la commande pour extraire les plats et quantités """
    plats_disponibles = ["pizza", "burger", "salade", "sushi", "pâtes"]
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
    app.run(debug=True)
