from flask import Flask
from database import crear_base

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Crear base al iniciar
crear_base()

@app.route("/")
def home():
    return "<h1>Sistema de Calibraciones v2</h1>"

if __name__ == "__main__":
    app.run(debug=True)