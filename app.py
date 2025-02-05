from flask import Flask, render_template, redirect, request, flash, session, url_for
from config import *
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_session import Session
import os
import cv2
import numpy as np
import mediapipe as mp
from werkzeug.utils import secure_filename

# Initialize extensions
mysql = MySQL()
bcrypt = Bcrypt()
sess = Session()  # Renamed Session to avoid conflicts

def create_app():
    # Initialize the Flask app
    app = Flask(__name__)

    # Set up the app configurations
    app.config['MYSQL_HOST'] = MYSQL_HOST
    app.config['MYSQL_USER'] = MYSQL_USER
    app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
    app.config['MYSQL_DB'] = MYSQL_DB
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SESSION_TYPE'] = SESSION_TYPE
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Initialize extensions with the app
    mysql.init_app(app)
    bcrypt.init_app(app)
    sess.init_app(app)  # Use the renamed Session instance

    # Register the Blueprint for auth routes
    from auth import auth_bp  # Import here to avoid circular import
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Define the root route
    @app.route('/')
    def index():
        if 'user_id' in session:  # If the user is logged in, redirect them to home
            return redirect('/home')
        return render_template('index.html')  # Show the landing page if not logged in

    # Profile route
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))  # Redirect to login if not logged in

        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()

        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            profile_picture = request.files.get('profile_picture')

            if profile_picture and profile_picture.filename:
                picture_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profile', profile_picture.filename)
                profile_picture.save(picture_path)
            else:
                picture_path = user['profile_picture']  # Keep old profile picture if no new one is uploaded
    
            if password:
                password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                cur = mysql.connection.cursor()
                cur.execute("UPDATE users SET username = %s, email = %s, password_hash = %s, profile_picture = %s WHERE id = %s", 
                            (username, email, password_hash, picture_path, user_id))
            else:
                cur = mysql.connection.cursor()
                cur.execute("UPDATE users SET username = %s, email = %s, profile_picture = %s WHERE id = %s", 
                            (username, email, picture_path, user_id))
   
            mysql.connection.commit()
            cur.close()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))

        return render_template('profile.html', user=user)

    # Home route
    @app.route('/home', methods=['GET', 'POST'])
    def home():
        if 'user_id' not in session:  # Redirect to login if the user is not logged in
            return redirect(url_for('auth.login'))

        user_id = session['user_id']  # Retrieve user ID from session
        username = session['username']  # Retrieve username from session

        if request.method == 'POST':
            # Handle file upload for outfit image
            file = request.files.get('outfit_image')
            if file and file.filename:
                # Ensure the 'outfits' directory exists before saving
                outfit_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'outfits')
                os.makedirs(outfit_folder, exist_ok=True)  # Create folder if not exists
            


                # Use secure_filename to sanitize the file name
                filename = secure_filename(file.filename)
            
                # Define full file path within the static folder
                filename = os.path.join('uploads', 'outfits', filename)  # Save relative path
                filename = filename.replace("\\", "/")
            
                # Save the file in the correct folder
                file.save(os.path.join(os.getcwd(), 'static', filename))

                # Save path to database (store relative path to the file)
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO wardrobe (user_id, outfit_image) VALUES (%s, %s)", (user_id, filename))
                mysql.connection.commit()
                cur.close()
                flash("Outfit uploaded successfully!", "success")

        # Fetch user wardrobe items
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM wardrobe WHERE user_id = %s", (user_id,))
        wardrobe_items = cur.fetchall()
        cur.close()

        return render_template('home.html', wardrobe_items=wardrobe_items)
                

    # Logout route
    @app.route('/logout')
    def logout():
        session.clear()  # Clear session on logout
        flash("Logged out successfully!", "info")
        return redirect(url_for('auth.login'))  # Redirect to login page after logout


    # Initialize MediaPipe Pose model
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils


    def remove_background(image):
        """ Removes background using GrabCut, refines mask, and smoothens edges for better blending. """

        mask = np.zeros(image.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        rect = (10, 10, image.shape[1] - 10, image.shape[0] - 10)
        cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    
        # Apply morphological operations to refine mask
        kernel = np.ones((5, 5), np.uint8)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)  # Closes small holes
    
        # Further smooth mask edges
        mask2 = cv2.GaussianBlur(mask2, (15, 15), 5)  # Large blur for feathering

        # Use bilateral filtering to preserve outfit details while smoothing
        image_filtered = cv2.bilateralFilter(image, 15, 75, 75)

        # Create final outfit with soft edges
        result = image_filtered * mask2[:, :, np.newaxis]  

        return result


    # Virtual Try-On route
    @app.route('/try_on', methods=['GET', 'POST'])
    def try_on():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        # Retrieve uploaded images
        user_image = request.files.get('user_image')
        outfit_image = request.files.get('outfit_image')

        if user_image and outfit_image and user_image.filename and outfit_image.filename:
            # Define paths for saving images
            base_upload_path = os.path.join(os.getcwd(), 'static', 'uploads')
            user_upload_path = os.path.join(base_upload_path, 'user')
            outfit_upload_path = os.path.join(base_upload_path, 'outfit')
            result_upload_path = os.path.join(base_upload_path, 'result')

            # Ensure all directories exist
            os.makedirs(user_upload_path, exist_ok=True)
            os.makedirs(outfit_upload_path, exist_ok=True)
            os.makedirs(result_upload_path, exist_ok=True)

            # Save uploaded images
            user_image_path = os.path.join(user_upload_path, user_image.filename)
            outfit_image_path = os.path.join(outfit_upload_path, outfit_image.filename)
            user_image.save(user_image_path)
            outfit_image.save(outfit_image_path)

            # Read the images using OpenCV
            user_img = cv2.imread(user_image_path)
            outfit_img = cv2.imread(outfit_image_path)

            # Ensure both images are in the correct format
            if user_img is None or outfit_img is None:
                flash("Error reading images. Please upload valid images.", "danger")
                return redirect(url_for('home'))

            # Convert the user image to RGB for pose processing
            user_img_rgb = cv2.cvtColor(user_img, cv2.COLOR_BGR2RGB)

            # Get the pose landmarks for the user image
            results = pose.process(user_img_rgb)
            if results.pose_landmarks:
                # Extract key points (shoulders, hips, etc.)
                landmarks = results.pose_landmarks.landmark

                # Get coordinates of important body parts
                shoulder_left = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y)
                shoulder_right = (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
                hip_left = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y)
                hip_right = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y)

                # Compute bounding box for outfit resizing
                width = int(abs(shoulder_left[0] - shoulder_right[0]) * user_img.shape[1] * 1.6)  # Increased scaling factor
                height = int(abs(hip_left[1] - shoulder_left[1]) * user_img.shape[0] * 1.3)  # Increased vertical scaling

                if width <= 0 or height <= 0:
                    flash("Invalid dimensions for the outfit overlay.", "danger")
                    return redirect(url_for('home'))

                # Remove background from outfit image
                outfit_cleaned = remove_background(outfit_img)

                # Resize the outfit image to fit the calculated bounding box
                outfit_resized = cv2.resize(outfit_cleaned, (int(width), int(height)))

                # Calculate offset for positioning the outfit (centered around the shoulders)
                x_offset = int((shoulder_left[0] + shoulder_right[0]) / 2 * user_img.shape[1]) - width // 2
                y_offset = int(shoulder_left[1] * user_img.shape[0]) - int(height * 0.16)  # Adjust vertical position

                # Ensure outfit image fits within bounds of the user image
                x1, x2 = max(0, x_offset), min(user_img.shape[1], x_offset + width)
                y1, y2 = max(0, y_offset), min(user_img.shape[0], y_offset + height)

                outfit_resized = outfit_resized[:y2 - y1, :x2 - x1]

                # Create a binary mask for the outfit image (assuming alpha channel exists for transparency)
                gray_outfit = cv2.cvtColor(outfit_resized, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray_outfit, 10, 255, cv2.THRESH_BINARY)

                # Ensure the mask and outfit image are resized to match the user image
                mask_resized = cv2.resize(mask, (outfit_resized.shape[1], outfit_resized.shape[0]), interpolation=cv2.INTER_NEAREST)
                mask_inv_resized = cv2.bitwise_not(mask_resized)

                # Ensure the types are compatible (CV_8U)
                outfit_resized = outfit_resized.astype(np.uint8)
                mask_resized = mask_resized.astype(np.uint8)
                mask_inv_resized = mask_inv_resized.astype(np.uint8)


                # Extract outfit foreground
                outfit_fg = cv2.bitwise_and(outfit_resized, outfit_resized, mask=mask_resized)

                # Extract user image background
                user_bg = user_img[y1:y2, x1:x2]
                user_bg = cv2.bitwise_and(user_bg, user_bg, mask=mask_inv_resized)

                # Merge the images (overlay outfit on the user)
                result_img = user_img.copy()
                result_img[y1:y2, x1:x2] = cv2.add(user_bg, outfit_fg)

                # Save result image
                result_image_filename = "result_image.jpg"
                result_image_path = os.path.join(result_upload_path, result_image_filename)
                cv2.imwrite(result_image_path, result_img)

                # Pass the image paths to the template
                flash("Virtual Try-On successful!", "success")
                return render_template('try_on_result.html',
                       user_image_path=f'uploads/user/{user_image.filename}',
                       outfit_image_path=f'uploads/outfit/{outfit_image.filename}',
                       result_image_path=f'uploads/result/{result_image_filename}')

            else:
                flash("Pose landmarks not detected. Try again with a clearer image.", "danger")
                return redirect(url_for('home'))

        flash("Please upload both images for the try-on.", "danger")
        return redirect(url_for('home'))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
