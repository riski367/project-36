# Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt first
COPY requirements.txt ./

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy app files
COPY app.py ./
COPY test.py ./
COPY config.yaml ./  

# Expose port for the Streamlit app
EXPOSE 8080

# Command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "app.py"]
