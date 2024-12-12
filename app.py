# Imports
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_from_directory, jsonify
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user, current_user
)
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from dotenv import load_dotenv
from datetime import datetime
import pytz
import os
import requests
import base64
import logging

# Importing custom modules
from forms import LoginForm, RegisterForm, DeleteForm
from post_management import posts_bp

# Initialize Flask app
app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.register_blueprint(posts_bp, url_prefix='/posts')
load_dotenv()

# Load configuration from environment variables
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Flask-WTF CSRF Protection
csrf = CSRFProtect(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




# Dummy user storage with hashed password and roles
users = {
    'admin': {'password': generate_password_hash('admin'), 'role': 'admin'},
    'user': {'password': generate_password_hash('user'), 'role': 'user'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.role = users[username]['role']

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = users.get(username)
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(username)
            login_user(user_obj)
            return redirect(url_for('admin_dashboard'))  # Or user dashboard depending on role
        else:
            flash('Invalid username or password')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if username in users:
            flash('Username already exists. Please choose another one.')
        else:
            # Add the new user to the dictionary with hashed password
            users[username] = {
                'password': generate_password_hash(password),
                'role': 'user'  # Default role is 'user'
            }
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None



# Configuration for file upload
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']





# Load M-Pesa credentials from environment variables
MPESA_CONSUMER_KEY = "BbrhGBweVcx1vZg8v3SutFEYCX97dZ0JQ684BAfzAqvzTZgC"
MPESA_CONSUMER_SECRET = "lBnUt3tv1735v46lVaE5WaT7sRLN4UTI4wdrt81VlDUAsOwTC6UAo7KZh9WLcCBL"
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
MPESA_CALLBACK_URL = "https://eaaf-102-212-236-151.ngrok-free.app/"

def get_access_token(consumer_key, consumer_secret):
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    key_secret = f"{consumer_key}:{consumer_secret}"
    b64_encoded = base64.b64encode(key_secret.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_encoded}"
    }

    print(f"Requesting access token with headers: {headers}")  # Debug info
    response = requests.get(api_url, headers=headers)

    print(f"Response Code: {response.status_code}")  # Debug info
    print(f"Response Body: {response.text}")  # Debug info
    print(f"Response Body: {response.text}")  # Debug info
    print(f"Consumer Key: {consumer_key}")  # Debug info
    print(f"Consumer Secret: {consumer_secret}")  # Debug info

    if response.status_code == 200:
        json_response = response.json()
        access_token = json_response['access_token']
        return access_token
    else:
        return None




# Get current UTC time in the required format
utc_now = datetime.now(pytz.utc)
timestamp = utc_now.strftime('%Y%m%d%H%M%S')
print(timestamp)



import base64
from datetime import datetime
import pytz

def generate_password(shortcode, passkey):
    # Get current UTC time in the required format
    utc_now = datetime.now(pytz.utc)
    timestamp = utc_now.strftime('%Y%m%d%H%M%S')
    
    # Concatenate shortcode, passkey, and timestamp
    password_string = f"{shortcode}{passkey}{timestamp}"
    
    # Encode in Base64
    password = base64.b64encode(password_string.encode()).decode()
    
    return password, timestamp


def stk_push(amount, phone_number):
    # Get access token
    access_token = get_access_token(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET)
    if not access_token:
        return {'errorMessage': 'Failed to get access token'}

    # Prepare your STK Push request payload and headers
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    
    shortcode = "7409567"  # Your business shortcode
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # Your passkey
    
    # Generate password and timestamp
    password, timestamp = generate_password(shortcode, passkey)
    
    payload = {
        "BusinessShortCode": shortcode,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://mydomain.com/path",
        "AccountReference": "7409567",
        "TransactionDesc": "gci machakos",
        "Timestamp": timestamp,
        "Password": password  # Use the generated password
    }

    response = requests.post(api_url, json=payload, headers=headers)
    
    return response.json()




class CheckoutForm(FlaskForm):
    phone = StringField('Phone Number', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Pay Now')
 


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        phone_number = form.phone.data
        amount = form.amount.data

        # Format phone number
        if phone_number.startswith('07')+phone_number.startswith('01'):
            phone_number.startswith('01')
            phone_number = '254' + phone_number[1:] 
            
            

        # Call stk_push function with formatted phone number
        result = stk_push(amount, phone_number)
        
        # Handle the result
        if 'errorMessage' in result:
            flash(result['errorMessage'], 'error')
        elif result.get('ResponseCode') == '0':
            flash('Payment request sent successfully!', 'success')
        else:
            flash('Payment request failed.', 'error')

        return redirect(url_for('checkout'))

    return render_template('checkout.html', form=form)





@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('admin_dashboard'))
    flash('Invalid file type')
    return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Configuration for Flask-Mail
mail = Mail(app)

# forms.py


class SubscribeForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')

@app.route('/')
def index():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    form = SubscribeForm()  # Initialize the form
    return render_template('index.html', gallery_images=image_files, form=form)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():  # Validate the form data
        email = form.email.data
        
        msg = Message('New Subscription', 
                      sender=app.config['MAIL_DEFAULT_SENDER'], 
                      recipients=[app.config['MAIL_DEFAULT_SENDER']])
        msg.body = f'New subscriber: {email}'
        
        try:
            mail.send(msg)
            flash('You have subscribed successfully!', 'success')
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            flash('Failed to send subscription email. Please try again later.', 'error')
        
        return redirect(url_for('index'))
    
    flash('Invalid email address. Please try again.', 'error')
    return redirect(url_for('index'))
@app.route('/gallery')
def gallery():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    is_admin = current_user.is_authenticated and current_user.role == 'admin'
    return render_template('gallery.html', gallery_images=image_files, is_admin=is_admin)

@app.route('/delete_post/<filename>', methods=['POST'])
@login_required
def delete_post(filename):
    if current_user.role != 'admin':
        flash('Unauthorized action')
        return redirect(url_for('index'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('Post deleted successfully!', 'success')
    else:
        flash('Post not found', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/process_donation', methods=['POST'])
def process_donation():
    name = request.form['name']
    email = request.form['email']
    amount = request.form['amount']
    payment_method = request.form['payment_method']

    # Process donation based on payment method
    if payment_method == 'paypal':
        # Redirect to PayPal donation link (you can integrate PayPal API here)
        flash('Redirecting to PayPal...')
        return redirect(url_for('donate'))
    
    elif payment_method == 'mpesa':
        # Process M-Pesa payment (You can integrate M-Pesa API here)
        flash('Processing M-Pesa payment...')
        return redirect(url_for('donate'))

    flash('Thank you for your donation!')
    return redirect(url_for('donate'))



@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/giving')
def giving():
    return render_template('giving.html')

@app.route('/donate')
def donation():
    return render_template('donate.html')

@app.route('/submit_form', methods=['POST'])
@csrf.exempt  # If you're using CSRF tokens in forms, remove this line
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    msg = Message('New Contact Form Submission',
              sender=app.config['MAIL_DEFAULT_SENDER'],  # Ensure sender is set
              recipients=[app.config['MAIL_DEFAULT_SENDER']])
    msg.body = f'Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}'
    
    try:
        mail.send(msg)
        flash('Message sent successfully!', 'success')
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        flash('Failed to send message. Please try again later.', 'error')

    return redirect(url_for('contact'))


@app.route('/Subscribe', methods=['POST'])
def Subscribe():
    email = request.form.get('email')  # Get the email from the form

    msg = Message('New Newsletter Subscription',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[app.config['MAIL_DEFAULT_SENDER']])
    msg.body = f'A user has subscribed to the newsletter with the email: {email}'

    try:
        mail.send(msg)
        response = {'message': 'You have successfully subscribed to the newsletter!'}
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        response = {'message': 'Failed to subscribe. Please try again later.'}

    return jsonify(response)  # Return the response as JSON

@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('index'))

    form = DeleteForm()  # Create an instance of DeleteForm

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid file type', 'error')

    # Get all image files from the upload folder
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]

    # Fetch recent content data
    recent_content = [
        {"id": idx, "title": file, "date": "2024-08-10", "status": "Active", "image_url": file}
        for idx, file in enumerate(image_files)
    ]

    latest_content_count = len(image_files)
    
    return render_template('admin_dashboard.html', recent_content=recent_content, latest_content_count=latest_content_count, form=form)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=3000, debug=True)