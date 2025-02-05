# Virtual Wardrobe Project (Developed by Divyansh Jain and Mahak Gupta)

This project is a **Virtual Wardrobe** application that allows users to create a virtual wardrobe by uploading outfits and trying them on virtually. The system uses machine learning techniques to align outfits onto the user's body for a realistic virtual try-on experience.

## Features

- **User Authentication**: Users can sign up and log in to manage their wardrobe.
- **Virtual Try-On**: Users can upload their user image and outfit images for a virtual try-on experience.
- **Wardrobe Management**: Users can upload outfits to their wardrobe, which are stored locally.
- **Profile Management**: Users can update their profile details, including username, email, password, and profile picture.
- **Logout**: Users can log out, clearing the session.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (with animations)
- **Database**: MySQL
- **Machine Learning**: TensorFlow, OpenCV, MediaPipe
- **Authentication**: bcrypt for password hashing
- **Version Control**: Git, GitHub

### Key Files

1. **`app.py`**: The main application file where Flask routes and app configurations are defined.
2. **`auth.py`**: Contains user authentication routes (login, signup, logout).
3. **`virtual_try_on.py`**: Contains the virtual try-on functionality.
4. **`helpers.py`**: Contains utility functions for image processing and data handling.
5. **`static/`**: Contains static files like CSS, JavaScript, and images.
6. **`templates/`**: Contains HTML templates for each page (login, signup, profile, home, etc.).


Future Enhancements
Improve the virtual try-on system using AI techniques like OpenPose or DensePose for better outfit alignment.
Add cloud storage for outfit image uploads.
Enhance UI/UX with advanced animations and transitions.


### Prerequisites

1. Install Python 3.8 or above.
2. Install MySQL on your local machine and set up a database for the project.

### Install Dependencies

1. Clone the repository:

```bash
git clone https://github.com/your-username/virtual-wardrobe.git
cd virtual-wardrobe

Create a virtual environment and activate it:
python3 -m venv venv
source venv/bin/activate  # For Windows, use venv\Scripts\activate
