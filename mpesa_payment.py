<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from post_management import posts_bp
import logging
from forms import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from forms import DeleteForm
from forms import RegisterForm
from config import Config
from stk_push import stk_push
from callback import callback_bp  # Blueprint for callback handling
from flask_wtf.csrf import CSRFProtect
from flask import request, redirect, url_for, flash

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




def format_phone_number(phone):
    # Ensure the number starts with '254' (Kenya country code) and is 12 digits long
    if phone.startswith('07'):
        return '254' + phone[1:]  # Convert '07XXXXXXXX' to '2547XXXXXXXX'
    elif phone.startswith('+'):
        return phone[1:]  # Remove the leading '+' from international format
    elif phone.startswith('254'):
        return phone  # Phone number is already in the correct format
    else:
        return None  # Invalid format

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        amount = request.form.get('amount')
        payment_type = request.form.get('payment_type')

        # Format the phone number
        formatted_phone = format_phone_number(phone_number)
        if not formatted_phone:
            flash('Invalid phone number format', 'error')
            return redirect(url_for('checkout'))

        # Call stk_push function with formatted phone number
        result = stk_push(amount, formatted_phone)
        if 'errorMessage' in result:
            flash(result['errorMessage'], 'error')
            return redirect(url_for('checkout'))

        # Handle success or failure of the payment request
        if result.get('ResponseCode') == '0':
            flash('Payment request sent successfully!', 'success')
        else:
            flash('Payment request failed.', 'error')

    return render_template('checkout.html')



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
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    flash('Invalid file type')
    return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Configuration for Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    return render_template('index.html', gallery_images=image_files)

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

@app.route('/donation')
def donation():
    return render_template('donation.html')

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


import requests
import base64
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from requests.auth import HTTPBasicAuth
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Initialize CSRF protection



# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to your Flask secret key
csrf = CSRFProtect(app)
# Load M-Pesa credentials from environment variables
MPESA_CONSUMER_KEY = "BbrhGBweVcx1vZg8v3SutFEYCX97dZ0JQ684BAfzAqvzTZgC"
MPESA_CONSUMER_SECRET = "lBnUt3tv1735v46lVaE5WaT7sRLN4UTI4wdrt81VlDUAsOwTC6UAo7KZh9WLcCBL"
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
MPESA_CALLBACK_URL = " https://mydomain.com/path"

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


from datetime import datetime
import pytz

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
    
    
    shortcode = "174379"  # Your business shortcode
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
        "AccountReference": "Test123",
        "TransactionDesc": "Payment for testing",
        "Timestamp": timestamp,
        "Password": password  # Use the generated password
    }

    response = requests.post(api_url, json=payload, headers=headers)
    
    return response.json()


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

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
        if phone_number.startswith('07'):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
=======
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from post_management import posts_bp
import logging
from forms import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from forms import DeleteForm
from forms import RegisterForm
from config import Config
from stk_push import stk_push
from callback import callback_bp  # Blueprint for callback handling
from flask_wtf.csrf import CSRFProtect
from flask import request, redirect, url_for, flash

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




def format_phone_number(phone):
    # Ensure the number starts with '254' (Kenya country code) and is 12 digits long
    if phone.startswith('07'):
        return '254' + phone[1:]  # Convert '07XXXXXXXX' to '2547XXXXXXXX'
    elif phone.startswith('+'):
        return phone[1:]  # Remove the leading '+' from international format
    elif phone.startswith('254'):
        return phone  # Phone number is already in the correct format
    else:
        return None  # Invalid format

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        amount = request.form.get('amount')
        payment_type = request.form.get('payment_type')

        # Format the phone number
        formatted_phone = format_phone_number(phone_number)
        if not formatted_phone:
            flash('Invalid phone number format', 'error')
            return redirect(url_for('checkout'))

        # Call stk_push function with formatted phone number
        result = stk_push(amount, formatted_phone)
        if 'errorMessage' in result:
            flash(result['errorMessage'], 'error')
            return redirect(url_for('checkout'))

        # Handle success or failure of the payment request
        if result.get('ResponseCode') == '0':
            flash('Payment request sent successfully!', 'success')
        else:
            flash('Payment request failed.', 'error')

    return render_template('checkout.html')



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
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    flash('Invalid file type')
    return redirect(request.url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Configuration for Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    return render_template('index.html', gallery_images=image_files)

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

@app.route('/donation')
def donation():
    return render_template('donation.html')

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


import requests
import base64
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from requests.auth import HTTPBasicAuth
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Initialize CSRF protection



# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to your Flask secret key
csrf = CSRFProtect(app)
# Load M-Pesa credentials from environment variables
MPESA_CONSUMER_KEY = "BbrhGBweVcx1vZg8v3SutFEYCX97dZ0JQ684BAfzAqvzTZgC"
MPESA_CONSUMER_SECRET = "lBnUt3tv1735v46lVaE5WaT7sRLN4UTI4wdrt81VlDUAsOwTC6UAo7KZh9WLcCBL"
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
MPESA_CALLBACK_URL = " https://mydomain.com/path"

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


from datetime import datetime
import pytz

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
    
    
    shortcode = "174379"  # Your business shortcode
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
        "AccountReference": "Test123",
        "TransactionDesc": "Payment for testing",
        "Timestamp": timestamp,
        "Password": password  # Use the generated password
    }

    response = requests.post(api_url, json=payload, headers=headers)
    
    return response.json()


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

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
        if phone_number.startswith('07'):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
>>>>>>> f8a00e35b77637d46ca2d4b0b6f40c082d27d19c
