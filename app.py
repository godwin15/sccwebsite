from flask import Flask, request, render_template

app = Flask(__name__, template_folder="html/", static_url_path="/static")

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/joinus')
def joinus_page():
    return render_template('join_us.html')

if __name__ == '__main__':
    app.run(debug=True)
