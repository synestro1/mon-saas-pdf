FROM python:3.9-slim

WORKDIR /app

# Copie des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code et des templates
COPY . .

# Création d'un dossier temporaire pour les uploads si besoin
RUN mkdir -p uploads

EXPOSE 8000

CMD ["python", "app.py"]