import psycopg2
import http.server
import urllib.parse
import logging
import bcrypt
import time
import os
import subprocess

DATABASE_CONFIG = {
    'database': "ibmclouddb",
    'user': "ibm_cloud_100a9baf_f835_41c3_9b39_057f07271c94",
    'password': "2df8bd56a14f3a406bc76dadeb2c218a40590e8e82649df4be77ecd6ac4da5ef",
    'host': "8f5807ec-5945-4061-bc26-dfcf27a6bdc8.bsbaodss0vb4fikkn2bg.databases.appdomain.cloud",
    'port': "30346"
}

logging.basicConfig(level=logging.INFO)

def connect_db():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        logging.error("Database connection failed: %s", e)
        return None

class MyHandler(http.server.BaseHTTPRequestHandler):
    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read().encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "File Not Found: %s" % file_path)

    def do_GET(self):
        if self.path == '/':
            self.serve_file('index.html', 'text/html')
        elif self.path == '/app':
            self.serve_file('app.py', 'text/html')
        elif self.path == '/style.css':
            self.serve_file('style.css', 'text/css')
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode())

        logging.info("Received POST request with data: %s", post_data)

        if self.path == '/login':
            self.handle_login(post_data)
        elif self.path == '/register':
            self.handle_register(post_data)
        else:
            self.send_error(404)

    def handle_login(self, post_data):
        email = post_data['emailLogin'][0]
        password = post_data['passwordLogin'][0]

        conn = connect_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT password FROM \"user\" WHERE email = %s", (email,))
                    row = cur.fetchone()

                    if row and bcrypt.checkpw(password.encode(), row[0].encode()):
                        self.send_response(302)
                        self.send_header('Location', '/app')
                        self.end_headers()
                        os.system('streamlit run app.py &')  # Run the Streamlit app in the background
                    else:
                        self.send_error_response("Email atau kata sandi salah.", 401)
            except Exception as e:
                self.send_error_response(f"Terjadi kesalahan: {e}", 500)
            finally:
                conn.close()
        else:
            self.send_error_response("Database connection failed.", 500)

    def handle_register(self, post_data):
        idx = int(time.time())
        name = post_data['nama'][0]
        email = post_data['emailRegis'][0]
        password = post_data['passwordRegis'][0]
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        conn = connect_db()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO \"user\" (id, username, email, password) VALUES (%s, %s, %s, %s)", 
                                (idx, name, email, hashed_password))
                    conn.commit()
                    self.send_response(302)
                    self.send_header('Location', '/app')
                    self.end_headers()
                    os.system('streamlit run app.py &')
            except psycopg2.errors.UniqueViolation:
                self.send_error_response("Email sudah terdaftar. Silakan gunakan email lain.", 400)
            except Exception as e:
                self.send_error_response(f"Terjadi kesalahan: {e}", 500)
            finally:
                conn.close()
        else:
            self.send_error_response("Database connection failed.", 500)

    def send_error_response(self, message, status):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"<html><body><p>{message}</p></body></html>".encode())

if __name__ == '__main__':
    server_address = ('', 8080)  # Use a more common port for HTTP
    httpd = http.server.HTTPServer(server_address, MyHandler)
    logging.info('Server running on port 8080...')
    httpd.serve_forever()
