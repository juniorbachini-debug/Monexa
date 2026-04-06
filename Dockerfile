FROM node:20-slim

# Install Python for transcription sidecar
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Node dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Python dependencies
COPY requirements.txt ./
RUN python3 -m pip install --break-system-packages -r requirements.txt

# Copy built app + Python scripts
COPY dist/ ./dist/
COPY transcription_server.py transcribe_audio.py ./
COPY finance.db* ./

# Start script launches both servers
COPY start.sh ./
RUN chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"]
