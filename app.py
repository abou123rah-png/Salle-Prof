# app.py – Salle des Profs Numérique – Lycée Thiaroye
# Créé par Doro Cissé, professeur de Physique-Chimie

from flask import Flask, render_template, request, session
from datetime import datetime
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret_local_temporaire_2025")

# === RÉCUPÉRATION DE LA CLÉ (obligatoire avant tout) ===
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Protection supplémentaire : on bloque l'ancienne clé fuitée même si quelqu'un l'a encore en local
if gemini_api_key and "BuFz1TQsoDwL9pGjq5YBXHexUM9uOnx6Q" in gemini_api_key:
    gemini_api_key = None
    API_ERROR_MESSAGE = (
        "<strong>Ancienne clé détectée et bloquée automatiquement pour ta sécurité !</strong><br><br>"
        "Tu utilises encore l'ancienne clé qui a fuité sur GitHub.<br>"
        "Remplace-la par la nouvelle que tu viens de créer dans Render → Environment."
    )
else:
    API_ERROR_MESSAGE = None

# === VÉRIFICATION INTELLIGENTE DE LA NOUVELLE CLÉ ===
if not gemini_api_key:
    API_ERROR_MESSAGE = (
        "La clé API Gemini est manquante. "
        "Ajoute <code>GEMINI_API_KEY=ta_clé_ici</code> dans le fichier <code>.env</code> en local, "
        "ou dans l'onglet <strong>Environment</strong> sur Render."
    )
else:
    try:
        genai.configure(api_key=gemini_api_key)
        
        # Modèle stable : Gemini 2.5 Flash (fonctionne parfaitement en décembre 2025)
        model = genai.GenerativeModel("gemini-2.5-flash")
        model.generate_content("Test silencieux – ignore ce message.")  # Juste pour vérifier
        
    except Exception as e:
        error_str = str(e).lower()
        if "leaked" in error_str or "reported as leaked" in error_str or "403" in error_str:
            API_ERROR_MESSAGE = (
                "Ta clé API Gemini a été désactivée par Google car elle a été exposée publiquement (fuite).<br><br>"
                "<strong>Actions :</strong><br>"
                "1. Crée une <u>nouvelle clé</u> ici → <a href='https://aistudio.google.com/app/apikey' target='_blank' class='underline text-blue-600'>Google AI Studio</a><br>"
                "2. Colle-la dans Render → Environment → GEMINI_API_KEY<br>"
                "3. Redeploy<br><br>"
                "L'ancienne clé ne pourra jamais être réactivée."
            )
        elif "quota" in error_str:
            API_ERROR_MESSAGE = "Quota Gemini dépassé. Attends demain ou crée un nouveau projet Google."
        elif "billing" in error_str:
            API_ERROR_MESSAGE = "Facturation non activée sur le projet lié à cette clé."
        elif "not found" in error_str or "404" in error_str:
            API_ERROR_MESSAGE = (
                "Modèle non trouvé (erreur 404). C'est un bug temporaire de Google.<br><br>"
                "<strong>Solution :</strong><br>"
                "1. Essaie de relancer l'app dans 5 minutes (Google met à jour souvent).<br>"
                "2. Ou change le modèle dans app.py en 'gemini-1.5-flash' et relance.<br>"
                "3. Si ça persiste, dis-moi l'erreur exacte."
            )
        else:
            API_ERROR_MESSAGE = f"Erreur de connexion Gemini : {str(e)}"

# Si tout est bon → on crée le modèle une seule fois
if not API_ERROR_MESSAGE:
    model = genai.GenerativeModel("gemini-2.5-flash")

# === Listes officielles ===
subjects = ['Mathématiques', 'Français', 'Physique-Chimie', 'SVT', 'Histoire-Géographie', 'Anglais', 'Philosophie', 'Espagnol']
levels = ['2nde', '1ère', 'Terminale']
exam_types = ['Devoir Surveillé', 'Composition', "Exercices d'application", 'Quiz rapide']
difficulties = ['Facile', 'Moyen', 'Difficile']


def generate_exam_content(exam_request):
    prompt = f"""
Tu es un professeur expérimenté au Lycée de Thiaroye au Sénégal.
Génère un sujet d'évaluation en {exam_request['subject']} pour {exam_request['level']}.
Type: {exam_request['type']}.
Thème/Chapitre: {exam_request['topic']}.
Difficulté: {exam_request['difficulty']}.
Durée suggérée: {exam_request.get('duration', 'Non spécifiée')}.

Le sujet doit respecter strictement le programme officiel sénégalais.
Structure claire : en-tête officiel, consignes, exercices numérotés.
Utilise du Markdown pur, avec $$ pour les formules mathématiques (KaTeX).
Commence directement par le titre du sujet (ex: LYCÉE THIAROYE – COMPOSITION DE MATHÉMATIQUES – TERMINALE).
"""
    response = model.generate_content(prompt)
    return response.text


def generate_correction_content(exam_content):
    prompt = f"""
Fournis une correction complète, détaillée et pédagogique du sujet suivant :

{exam_content}

Structure la correction avec :
- Numéro de l'exercice
- Barème suggéré
- Solution complète avec toutes les étapes
- Remarques éventuelles pour les élèves

Utilise du Markdown et $$ pour les formules.
"""
    response = model.generate_content(prompt)
    return response.text


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    current_content = session.get('current_content')

    if API_ERROR_MESSAGE:
        return render_template(
            "index.html",
            api_error=API_ERROR_MESSAGE,
            subjects=subjects,
            levels=levels,
            exam_types=exam_types,
            difficulties=difficulties
        )

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'generate_exam':
            exam_request = {
                'subject': request.form['subject'],
                'level': request.form['level'],
                'type': request.form['type'],
                'topic': request.form['topic'].strip(),
                'difficulty': request.form['difficulty'],
                'duration': request.form.get('duration', '').strip()
            }

            if not exam_request['topic']:
                error = "Le thème/chapitre est obligatoire."
            else:
                try:
                    exam_text = generate_exam_content(exam_request)
                    new_content = {
                        'id': str(int(datetime.now().timestamp())),
                        'request': exam_request,
                        'examContent': exam_text,
                        'createdAt': datetime.now().strftime("%d/%m/%Y à %H:%M")
                    }
                    session['current_content'] = new_content
                    current_content = new_content
                except Exception as e:
                    error = f"Erreur lors de la génération du sujet : {str(e)}"

        elif action == 'generate_correction' and current_content:
            try:
                correction = generate_correction_content(current_content['examContent'])
                current_content['correctionContent'] = correction
                session['current_content'] = current_content
            except Exception as e:
                error = f"Erreur lors de la génération de la correction : {str(e)}"

    return render_template(
        "index.html",
        error=error,
        current_content=current_content,
        subjects=subjects,
        levels=levels,
        exam_types=exam_types,
        difficulties=difficulties
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 3000)))