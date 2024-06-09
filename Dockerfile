# Gunakan base image Python 3.11 slim
FROM python:3.11.9-slim

# Update package manager dan install beberapa paket yang diperlukan
RUN apt-get update && apt-get install -y build-essential \
    && apt-get install -y curl wget git

# Setel direktori kerja di dalam kontainer
WORKDIR /app

# Salin seluruh konten dari direktori saat ini ke dalam direktori /app di dalam kontainer
COPY . .

# Install dependencies yang didefinisikan dalam requirements.txt
RUN pip install -r requirements.txt

# Expose port for the Streamlit app
EXPOSE 8080

# Command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "app.py"]

