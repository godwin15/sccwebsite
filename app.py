import os
from flask import Flask, request, render_template,send_from_directory, redirect, url_for, flash
import stripe
import boto3
from flask_mail import Mail, Message
import configparser
import re
import traceback


app = Flask(__name__, template_folder="html/", static_url_path="/static")
app.secret_key = os.urandom(16)

config = configparser.ConfigParser()
config.read('.env')

public_key = config['ENV']['PUBLIC_KEY']
stripe.api_key = config['ENV']['STRIPE_KEY']

# Configure Amazon S3 credentials
BUCKET_NAME = 'supernaturalpics'
S3_BUCKET_NAME = config['ENV']['S3_BUCKET_NAME']
AWS_ACCESS_KEY_ID = config['ENV']['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['ENV']['AWS_SECRET_ACCESS_KEY']

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config['ENV']['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = config['ENV']['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = config['ENV']['MAIL_USERNAME']

mail = Mail(app)


# Helper function to generate signed URLs for the PDF files
def generate_signed_url(file, page=1):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    signed_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': S3_BUCKET_NAME,
            'Key': file,
            'ResponseContentDisposition': 'inline',
            'Range': f'bytes={page*1024}-',  # Start from the specified page
        },
        ExpiresIn=3600  # URL expiration time in seconds
    )
    return signed_url

# Helper function to generate signed URLs for the PDF files
def generate_first_page_url(file, bucket):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    signed_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': file, 'ResponseContentDisposition': 'inline',},
        ExpiresIn=3600  # URL expiration time in seconds
    )
    return signed_url


def get_files_from_s3():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # get the list of pdf files
        response_pdf = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix='', Delimiter='/')
        pdf_files = [obj['Key'] for obj in response_pdf['Contents'] if obj['Key'].endswith('.pdf')]
        
        # get the list of jpg files
        response_jpg = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='', Delimiter='/')
        jpg_files = [obj['Key'] for obj in response_jpg['Contents'] if obj['Key'].endswith('.png')]
        
        file_details = []
        for pdf_file in pdf_files:
            signed_url = generate_signed_url(pdf_file)

            # generate the symbol jpg file for each pdf
            # let's assume that each pdf file has a corresponding jpg file with the same name but different extension
            base_name = os.path.splitext(pdf_file)[0]
            jpg_file = f'{base_name}.png'
            if jpg_file in jpg_files:
                symbol_url = generate_first_page_url(jpg_file, bucket=BUCKET_NAME)
            else:
                symbol_url = None  # default symbol if no corresponding jpg found

            file_details.append({
                'file': pdf_file,
                'signed_url': signed_url,
                'symbol': symbol_url,
            })

        return file_details

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def validate_email(email):
    #validation logic
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/home')
@app.route('/')
def home():
    file_details = get_files_from_s3()
    return render_template('index.html', title='Supernatural Community Church', file_details=file_details)

@app.route('/about')
def about():
    return render_template('about.html', title='about SCC')

@app.route('/give-online')
def offering():
    return render_template('offering.html', public_key=public_key, title='Give to SCC')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html', title='Thank you')

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
            return redirect(url_for('home')) 
        except Exception as e:
            print("Error sending email:", e)
            traceback.print_exc()
            flash("Oops! Something went wrong. Please try again later.")
            return redirect(url_for('home')) 
    else:
        flash("Invalid email address. Please provide a valid email.")
        return redirect(url_for('home')) 

# Index route to display the uploaded PDF files
@app.route('/materials')
def materials():
    file_details = get_files_from_s3()
    return render_template('materials.html', file_details=file_details, title='Resources')

if __name__ == '__main__':
    app.run(debug=True)
