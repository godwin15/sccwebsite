import os
from flask import Flask, request, render_template,send_from_directory

app = Flask(__name__, template_folder="html/", static_url_path="/static")
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/joinus')
def joinus_page():
    return render_template('join_us.html')

@app.route('/materials')
def materials():
    return render_template('materials.html')

if __name__ == '__main__':
    app.run(debug=True)
