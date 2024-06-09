# Base Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy app files
COPY app.py ./
COPY test.py ./
COPY config.yaml ./  
COPY fruit\ model ./

# Expose port for the Streamlit app
EXPOSE 8080

# Command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "app.py"]
