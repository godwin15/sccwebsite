import os
from flask import Flask, request, render_template,send_from_directory

app = Flask(__name__, template_folder="html/", static_url_path="/static")
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
