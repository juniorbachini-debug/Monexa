#!/bin/bash
# Start Python transcription sidecar in background
python3 transcription_server.py &

# Wait for it to be ready
sleep 2

# Start Node.js Express server (main app)
NODE_ENV=production node dist/index.cjs
