import os
from flask import Flask, request

xxxkey=os.environ.get("")

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save('uploads/' + file.filename)
    return 'file uploaded successfully'

if __name__ == '__main__':
    app.run()