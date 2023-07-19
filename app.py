import os
from flask import Flask, request, render_template,send_from_directory, redirect, url_for, flash
import stripe
import boto3
from PyPDF2 import PdfReader
from io import BytesIO
from flask_mail import Mail, Message
import configparser
import re
import traceback


app = Flask(__name__, template_folder="html/", static_url_path="/static")
app.secret_key = os.urandom(16)

config = configparser.ConfigParser()
config.read('.env')

public_key = "-"
stripe.api_key = "-"

# Configure Amazon S3 credentials
S3_BUCKET_NAME = '-'
AWS_ACCESS_KEY_ID = '-'
AWS_SECRET_ACCESS_KEY = '-'

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USERNAME'] = config['ENV']['MAIL_USERNAME']
#app.config['MAIL_PASSWORD'] = config['ENV']['MAIL_PASSWORD']
#app.config['MAIL_DEFAULT_SENDER'] = config['ENV']['MAIL_USERNAME']

mail = Mail(app)

# Helper function to generate signed URLs for the PDF files
def generate_signed_url(file):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    signed_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': file},
        ExpiresIn=3600  # URL expiration time in seconds
    )
    return signed_url

# Helper function to retrieve the list of PDF files from Amazon S3
def get_pdf_files_from_s3():
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix='', Delimiter='/')
    files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
    file_details = []
    for file in files:
        signed_url = generate_signed_url(file)
        obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=file)
        pdf_data = obj['Body'].read()
        pdf_file = BytesIO(pdf_data)
        pdf_reader = PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        print("Metadata for file:", file)
        print(metadata)  # Print the metadata dictionary
        title = metadata.get('/x-amz-meta-title', metadata.get('/Title', file))
        message = metadata.get('/x-amz-meta-message', '')
        file_details.append({
            'file': file,
            'title': title,
            'message': message,
            'signed_url': signed_url
        })
    return file_details

def validate_email(email):
    #validation logic
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email)

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

@app.route('/offering')
def offering():
    return render_template('offering.html', public_key=public_key)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/get-involved')
def get_involved():
    return render_template("join_us.html")

@app.route('/payment', methods=['POST'])
def payment():

    #CUSTOMER INFO
    amount = request.form['amount']
    amount=int(float(amount) * 100)
    customer = stripe.Customer.create(email =request.form['stripeEmail'], source=request.form['stripeToken'])
    #PAYMENT INFO
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount, # 19.99
        currency='usd',
        description='Donation'
    )
    return redirect(url_for('thankyou'))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    amount = request.json['amount']

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': amount,
                'product_data': {
                    'name': 'Donation',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.url_root + 'thankyou',
        cancel_url=request.url_root,
    )

    return {'id': session.id}

@app.route('/process_email', methods=['POST'])
def process_email():
    email = request.form.get('email')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')

    if validate_email(email):
        try:
            # Send the email using Flask-Mail
            msg = Message("New Subscription", recipients=["godwinsilayo100@gmail.com"])
            msg.body = f"{firstName} {lastName} with Emaail: {email} has joined our mailing list \n\n Thank you"
            mail.send(msg)
            flash("Thank you for subscribing! We have sent you a confirmation email.")
            return redirect(url_for('about')) 
        except Exception as e:
            print("Error sending email:", e)
            traceback.print_exc()
            flash("Oops! Something went wrong. Please try again later.")
            return redirect(url_for('about')) 
    else:
        flash("Invalid email address. Please provide a valid email.")
        return redirect(url_for('get-involved')) 

# Index route to display the uploaded PDF files
@app.route('/materials')
def materials():
    file_details = get_pdf_files_from_s3()
    return render_template('materials.html', file_details=file_details)

if __name__ == '__main__':
    app.run(debug=True)
