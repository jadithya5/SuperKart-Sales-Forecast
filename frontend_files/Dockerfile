# Use a minimal base image with Python 3.11 installed
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the Streamlit app
COPY . .

# Streamlit runs on port 8501
EXPOSE 8501

# Start the Streamlit app, listening on all interfaces
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
