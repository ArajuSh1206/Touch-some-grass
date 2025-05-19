from flask import Flask, render_template, request, jsonify
import random
from PIL import Image, ImageOps
from backend.keras_model_predict import predict_image
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Fun messages
GRASS_MESSAGES = [
    "Good job! It's grass!",
    "You've finally touched some grass!",
    "Great job! Looking green and clean.",
    "Looks green and clean – that's grass alright!"
]

NO_GRASS_MESSAGES = [
    "Boo! That's not grass.",
    "Not a grass.You can't fool me!",
    "Nice try. That's definitely not grass.",
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
        # Load image directly from memory
        img = Image.open(file.stream)
        img.load()

        # Predict using your model
        prediction, _ = predict_image(img)

        # Choose a fun message
        message = random.choice(GRASS_MESSAGES if prediction.lower() == "grass" else NO_GRASS_MESSAGES)

        return jsonify({
            'prediction': prediction,
            'message': message
        })

    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({'error': f"Error analyzing image: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Grass Classifier application...")
    try:
        if not os.path.exists('keras_model.h5'):
            print("Warning: keras_model.h5 not found.")
        if not os.path.exists('labels.txt'):
            print("Warning: labels.txt not found.")

        app.run(debug=True)
    except Exception as e:
        print(f"Exception encountered: {str(e)}")
