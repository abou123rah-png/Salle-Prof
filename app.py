# app.py – Version finale avec le bon modèle et rendu parfait

from flask import Flask, render_template, request, session
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "salle_prof_2025"

# Clé API
genai.configure(api_key="AIzaSyBMoNpET9UyBcGlEVKJ0uCeGzaRy6ChTa8")

# Modèle gratuit 2025
model = genai.GenerativeModel("gemini-2.5-flash")

# Listes
subjects = ['Mathématiques', 'Français', 'Physique-Chimie', 'SVT', 'Histoire-Géographie', 'Anglais', 'Philosophie', 'Espagnol']
levels = ['2nde', '1ère', 'Terminale']
exam_types = ['Devoir Surveillé', 'Composition', "Exercices d'application", 'Quiz rapide']
difficulties = ['Facile', 'Moyen', 'Difficile']

def generate_exam_content(exam_request):
    prompt = f"""
Tu es un professeur expérimenté au Lycée de Thiaroye au Sénégal.
Génère un sujet d'évaluation en {exam_request['subject']} pour {exam_request['level']}.
Type: {exam_request['type']}.
Thème/Chaptre: {exam_request['topic']}.
Difficulté: {exam_request['difficulty']}.
Durée suggérée: {exam_request.get('duration', 'Non spécifiée')}.
    
Le sujet doit être conforme au programme officiel sénégalais.
Structurez le sujet avec un en-tête clair, instructions, et exercices numérotés.
Utilise du Markdown pour le formatage, y compris pour les maths si nécessaire (utilise $$ pour les équations).
Commence directement par le titre du sujet.
"""
    response = model.generate_content(prompt)
    return response.text

def generate_correction_content(exam_content):
    prompt = f"""
Fournis une correction détaillée et complète pour le sujet d'évaluation suivant.
Incluez des explications pas à pas, surtout pour les maths et sciences.
Utilise du Markdown pour le formatage.
    
Sujet:
{examen_content}
"""
    response = model.generate_content(prompt)
    return response.text

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    current_content = session.get('current_content')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'generate_exam':
            exam_request = {
                'subject': request.form['subject'],
                'level': request.form['level'],
                'type': request.form['type'],
                'topic': request.form['topic'],
                'difficulty': request.form['difficulty'],
                'duration': request.form.get('duration', '')
            }

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
                error = f"Erreur : {str(e)}"

        elif action == 'generate_correction' and current_content:
            try:
                correction = generate_correction_content(current_content['examContent'])
                current_content['correctionContent'] = correction
                session['current_content'] = current_content
            except Exception as e:
                error = f"Erreur correction : {str(e)}"

    return render_template('index.html', 
                           error=error,
                           current_content=current_content,
                           subjects=subjects,
                           levels=levels,
                           exam_types=exam_types,
                           difficulties=difficulties)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)