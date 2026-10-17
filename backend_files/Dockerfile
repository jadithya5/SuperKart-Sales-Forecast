# Use a minimal base image with the same Python version used for training
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Install the Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code and the serialized model
COPY . .

# The Flask API listens on port 7860
EXPOSE 7860

# Start the Flask app with gunicorn (4 workers) on port 7860
# "app:superkart_api" -> module app.py, Flask instance superkart_api
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
