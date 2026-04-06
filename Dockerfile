FROM node:20-bookworm

RUN apt-get update && apt-get install -y python3-pip ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY requirements.txt ./
RUN pip install --break-system-packages -r requirements.txt

COPY transcription_server.py ./

RUN mkdir -p dist/public/assets
COPY index.cjs ./dist/index.cjs
COPY index.html ./dist/public/index.html
COPY index-*.css ./dist/public/assets/
COPY index-*.js ./dist/public/assets/

COPY start.sh ./
RUN chmod +x start.sh

EXPOSE 5000
CMD ["./start.sh"]
