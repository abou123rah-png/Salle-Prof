# README.md - Updated for Flask

# Salle Prof Lycée Thiaroye

Assistant pédagogique intelligent pour les professeurs du Lycée de Thiaroye. Génération de sujets d'évaluation et de corrections conformes au programme sénégalais.

## Run Locally

**Prerequisites:** Python 3.10+, pip

1. Install dependencies:
   `pip install -r requirements.txt`
2. Set the `GEMINI_API_KEY` in `.env` to your Gemini API key
3. Run the app:
   `python app.py`
4. Access at http://localhost:3000

## Notes on Conversion
- Le frontend React a été converti en templates HTML/Jinja avec Flask.
- Les appels API Gemini sont maintenant côté serveur pour plus de sécurité (clé API non exposée).
- Le rendu Markdown et KaTeX se fait via scripts client-side (marked + katex auto-render). Pour un meilleur support math, envisagez de pré-rendre côté serveur avec markdown-it ou similaire.
- Les composants (Header, ExamForm, ResultDisplay) ont été intégrés directement dans le template.
- L'historique et autres fonctionnalités avancées ne sont pas implémentées ; ajoutez-les si needed.
- Pour la production, utilisez Gunicorn/Waitress et un reverse proxy comme Nginx.
- Ajoutez du JS pour le loading states si nécessaire (e.g., via HTMX ou vanilla JS pour AJAX). La version actuelle utilise des submits full-page pour simplicité.