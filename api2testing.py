<<<<<<< HEAD
import requests
import json

# Your IntaSend credentials
public_key = "ISPubKey_test_93fe8cb0-f5f5-4a9f-b460-47b7dff05369"
private_key = "ISSecretKey_test_3c3d2f65-168d-436d-84bc-14df12a7a5eb"

# URL for the payment request endpoint
url = "https://api.intasend.com/v1/payment/collection/request/"

headers = {
    "Authorization": f"Bearer {private_key}",  # Use only the private key here
    "Content-Type": "application/json"
}

# Payment request payload (including phone number)
data = {
    "amount": 1000,
    "currency": "KES",
    "payment_method": "MPESA",
    "callback_url": "https://189c-102-212-236-23.ngrok-free.app",
    "email": "brianshiru563@gmail.com",
    "phone_number": "254112865629"  # Customer's phone number in international format without the "+"
}

# Send the request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Check the response
print(response.json())



from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from post_management import posts_bp
import logging
from forms import UploadForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from forms import DeleteForm
from config import Config
from stk_push import stk_push
from callback import callback_bp  # Blueprint for callback handling
from flask_wtf.csrf import CSRFProtect

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
    'admin': {'password': generate_password_hash('adminpassword'), 'role': 'admin'},
    'user': {'password': generate_password_hash('userpassword'), 'role': 'user'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.role = users[username]['role']

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

# Configuration for file upload
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)


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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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

=======
import requests
import json

# Your IntaSend credentials
public_key = "ISPubKey_test_93fe8cb0-f5f5-4a9f-b460-47b7dff05369"
private_key = "ISSecretKey_test_3c3d2f65-168d-436d-84bc-14df12a7a5eb"

# URL for the payment request endpoint
url = "https://api.intasend.com/v1/payment/collection/request/"

headers = {
    "Authorization": f"Bearer {private_key}",  # Use only the private key here
    "Content-Type": "application/json"
}

# Payment request payload (including phone number)
data = {
    "amount": 1000,
    "currency": "KES",
    "payment_method": "MPESA",
    "callback_url": "https://189c-102-212-236-23.ngrok-free.app",
    "email": "brianshiru563@gmail.com",
    "phone_number": "254112865629"  # Customer's phone number in international format without the "+"
}

# Send the request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Check the response
print(response.json())



from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from post_management import posts_bp
import logging
from forms import UploadForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from forms import DeleteForm
from config import Config
from stk_push import stk_push
from callback import callback_bp  # Blueprint for callback handling
from flask_wtf.csrf import CSRFProtect

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
    'admin': {'password': generate_password_hash('adminpassword'), 'role': 'admin'},
    'user': {'password': generate_password_hash('userpassword'), 'role': 'user'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.role = users[username]['role']

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

# Configuration for file upload
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)


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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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

>>>>>>> f8a00e35b77637d46ca2d4b0b6f40c082d27d19c
