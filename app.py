import os
from flask import Flask, request, render_template
from pypdf import PdfReader
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

# --- CONFIGURATION DEVOPS ---

# 1. Compteur : Combien de fichiers ont été uploadés ?
UPLOAD_COUNT = Counter('pdf_uploads_total', 'Total number of uploaded PDFs')

# 2. Histogramme : Combien de temps ça prend pour traiter un fichier ? (Performance)
PROCESS_TIME = Histogram('pdf_processing_seconds', 'Time spent processing PDF')

# 3. Compteur d'erreurs : Combien de fichiers ont planté ?
ERROR_COUNT = Counter('pdf_errors_total', 'Total number of failed PDF processings')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = time.time() # On lance le chrono
        
        file = request.files['file']
        if file.filename == '':
            return "Aucun fichier sélectionné", 400

        if file:
            try:
                # Incrémenter le compteur DevOps
                UPLOAD_COUNT.inc()

                # Analyse du PDF
                reader = PdfReader(file)
                num_pages = len(reader.pages)
                file_size = len(file.read()) / 1024  # Taille en Ko
                
                # On arrête le chrono et on l'envoie au monitoring
                PROCESS_TIME.observe(time.time() - start_time)

                return render_template('index.html', 
                                     filename=file.filename, 
                                     pages=num_pages, 
                                     size=round(file_size, 2),
                                     info="Analyse réussie avec succès !")
            except Exception as e:
                ERROR_COUNT.inc() # On note l'erreur pour le monitoring
                return f"Erreur lors de la lecture du PDF : {str(e)}", 500

    return render_template('index.html')

# Endpoint pour Prometheus (le monitoring viendra lire ici)
@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    # On écoute sur 0.0.0.0 pour Docker
    app.run(host='0.0.0.0', port=8000)