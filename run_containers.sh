#!/bin/bash
# Builds and runs the SuperKart backend and frontend as separate Docker containers
# connected through a user-defined Docker network. Run inside the GitHub Codespace:
#   bash run_containers.sh
set -e

NETWORK=superkart-net

# 1. Create the Docker network (ignore the error if it already exists)
docker network create $NETWORK 2>/dev/null || true

# 2. Build the images
docker build -t superkart-backend ./backend_files
docker build -t superkart-frontend ./frontend_files

# 3. Remove old containers if they exist
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true

# 4. Run the backend (Flask API on port 7860)
docker run -d --name superkart-backend --network $NETWORK -p 7860:7860 superkart-backend

# 5. Run the frontend (Streamlit on port 8501); it reaches the backend by container name
docker run -d --name superkart-frontend --network $NETWORK -p 8501:8501 \
  -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
echo "Backend  -> port 7860 (set to Public in the Ports tab for API access from Colab)"
echo "Frontend -> port 8501"
