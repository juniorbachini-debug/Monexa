FROM node:20-bookworm

# Python 3 já vem pré-instalado nessa imagem. Só instalar pip.
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Node dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Python dependencies
COPY requirements.txt ./
RUN pip install --break-system-packages -r requirements.txt

# Copy built app + Python scripts
COPY dist/ ./dist/
COPY transcription_server.py transcribe_audio.py ./

# Start script launches both servers
COPY start.sh ./
RUN chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"]
