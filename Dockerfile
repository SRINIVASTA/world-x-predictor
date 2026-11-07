version: '3.8'

services:
  predictor:
    build: .
    container_name: predictor_instance
    ports:
      - "8509:8501"
    volumes:
      # Mounts the local hidden config file directory right into the workspace
      - ./.streamlit/secrets.toml:/app/.streamlit/secrets.toml:ro
    restart: unless-stopped
