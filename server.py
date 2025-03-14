import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

@app.route("/voice", methods=['POST'])
def voice():
    """ Gère l'appel et propose un menu interactif avec DTMF """
    response = VoiceResponse()

    gather = Gather(input="dtmf", num_digits=1, action="/menu_choice")
    gather.say("Bienvenue ! Pour commander, appuyez sur 1 pour une pizza, 2 pour un burger, 3 pour une salade.")
    
    response.append(gather)
    response.say("Nous n'avons pas reçu votre choix. Merci de réessayer.")
    
    return str(response)

@app.route("/menu_choice", methods=['POST'])
def menu_choice():
    """ Vérifie le choix du menu et demande la quantité """
    response = VoiceResponse()
    digits = request.form.get("Digits")

    menu = {
        "1": "pizza",
        "2": "burger",
        "3": "salade"
    }

    if digits in menu:
        choix = menu[digits]
        gather = Gather(input="dtmf", num_digits=1, action=f"/quantity?item={choix}")
        gather.say(f"Vous avez choisi {choix}. Combien en voulez-vous ? Appuyez sur un chiffre entre 1 et 6.")
        response.append(gather)
    else:
        response.say("Option invalide. Merci de réessayer.")
        response.redirect("/voice")

    return str(response)

@app.route("/quantity", methods=['POST'])
def quantity():
    """ Récupère la quantité et confirme la commande """
    response = VoiceResponse()
    item = request.args.get("item", "produit")
    digits = request.form.get("Digits")

    quantites = {
        "1": "un",
        "2": "deux",
        "3": "trois",
        "4": "quatre",
        "5": "cinq",
        "6": "six"
    }

    if digits in quantites:
        quantite = quantites[digits]
        response.say(f"Vous avez commandé {quantite} {item}(s). Merci pour votre commande !")
    else:
        response.say("Quantité invalide. Merci de réessayer.")
        response.redirect(f"/menu_choice")

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
