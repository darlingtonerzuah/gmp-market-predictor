from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "GSE Market predictor - Ready to go!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)