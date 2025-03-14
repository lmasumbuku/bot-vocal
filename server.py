import os
import openai
from flask import Flask

# Charger la clé API depuis les variables d’environnement Render
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/test_openai", methods=['GET'])
def test_openai():
    """ Teste OpenAI sur Render """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Dis-moi une commande classique dans un restaurant"}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur OpenAI : {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
