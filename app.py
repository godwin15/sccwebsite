from flask import Flask, request, render_template

app = Flask(__name__, template_folder="html/", static_url_path="/static")

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
