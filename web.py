from flask import Flask, render_template, request, jsonify
import os
import random
from werkzeug.utils import secure_filename
from keras_model_predict import predict_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Fun messages
GRASS_MESSAGES = [
    "Good job! It's grass!",
    "You've finally touched some grass!",
    "Great job! I see you.",
    "Looks green and clean – that's grass alright!"
]

NO_GRASS_MESSAGES = [
    "Boo! That's not grass.",
    "You can't fool me!",
    "That's definitely not grass.",
    "Try again – that ain't it!"
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No image data received'}), 400

    file = request.files['file']
    
    try:
        filename = secure_filename(file.filename or 'webcam.jpg')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        prediction, confidence_value = predict_image(filepath)
        confidence = f"{confidence_value:.2%}"

        # Pick a fun message based on the prediction
        if prediction.lower() == "grass":
            message = random.choice(GRASS_MESSAGES)
        else:
            message = random.choice(NO_GRASS_MESSAGES)

        return jsonify({
            'prediction': prediction,
            'confidence': confidence,
            'message': message  # This is the new key for fun feedback
        })

    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({'error': f"Error analyzing image: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Grass Classifier application...")
    try:
        os.makedirs('static/js', exist_ok=True)

        if not os.path.exists('keras_model.h5'):
            print("Warning: keras_model.h5 not found.")

        if not os.path.exists('labels.txt'):
            print("Warning: labels.txt not found.")

        app.run(debug=True)
    except Exception as e:
        print(f"Exception encountered: {str(e)}")
