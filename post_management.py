import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from forms import UploadForm  # Ensure you have a form defined in forms.py or elsewhere



posts_bp = Blueprint('uploads', __name__)
@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))

    form = UploadForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        image = form.image.data

        if not title or not content:
            flash('Title and content are required', 'warning')
            return redirect(url_for('posts.create_post'))
        
        # Save the post content as a .txt file
        post_dir = 'static/uploads'
        if not os.path.exists(post_dir):
            os.makedirs(post_dir)
        
        post_filename = f"{title.replace(' ', '_')}.txt"
        post_file_path = os.path.join(post_dir, post_filename)
        
        with open(post_file_path, 'w') as file_content:
            file_content.write(f"Title: {title}\n\n{content}")
        
        # Save the uploaded image if it exists
        if image:
            image_filename = f"{title.replace(' ', '_')}.jpg"  # Save images as JPG
            image_path = os.path.join(post_dir, image_filename)
            image.save(image_path)

        flash('Post created successfully!', 'success')
        return redirect(url_for('uploads.create_post'))  # Redirect to the view posts page

    return render_template('create_post.html', form=form)

# Route for viewing posts (this will be your gallery page)
@posts_bp.route('/view')
@login_required
def view_posts():
    post_dir = 'static/uploads'
    posts = [f for f in os.listdir(post_dir) if f.endswith('.txt')]
    post_data = []

    # Read content from .txt files to display on the gallery
    for post in posts:
        post_file_path = os.path.join(post_dir, post)
        with open(post_file_path, 'r') as file_content:
            post_data.append(file_content.read())

    # Collect image filenames
    images = [f.replace('.txt', '.jpg') for f in posts if os.path.exists(os.path.join(post_dir, f.replace('.txt', '.jpg')))]

    return render_template('view_posts.html', uploads=posts, post_data=post_data, images=images)



@posts_bp.route('/gallery')
def gallery():
    post_dir = 'static/uploads'
    posts = []
    
    # Loop through the posts (assuming posts are stored with title.txt and title.jpg for images)
    for post in os.listdir(post_dir):
        if post.endswith('.txt'):
            post_file = post
            post_image = post.replace('.txt', '.jpg')
            
            # Read content from .txt file
            with open(os.path.join(post_dir, post_file), 'r') as file_content:
                content = file_content.read()

            # Prepare the post data with content and corresponding image
            posts.append({
                'title': post_file.replace('_', ' ').replace('.txt', ''),
                'content': content,
                'image': post_image if os.path.exists(os.path.join(post_dir, post_image)) else None
            })

    return render_template('gallery.html', posts=posts)
