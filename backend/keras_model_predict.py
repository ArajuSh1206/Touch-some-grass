from PIL import Image, ImageOps
import numpy as np
import os
import tensorflow as tf 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model once at import time
def load_model_with_custom_objects():
    class CustomDepthwiseConv2D(tf.keras.layers.DepthwiseConv2D):
        def __init__(self, **kwargs):
            kwargs.pop('groups', None)
            super(CustomDepthwiseConv2D, self).__init__(**kwargs)

    with tf.keras.utils.custom_object_scope({'DepthwiseConv2D': CustomDepthwiseConv2D}):
        return tf.keras.models.load_model(os.path.join(BASE_DIR, "keras_model.h5"), compile=False)

try:
    model = load_model_with_custom_objects()
except Exception as e:
    print(f"Failed to load model with custom handler: {e}")
    model = tf.keras.models.load_model(os.path.join(BASE_DIR, "keras_model.h5"), compile=False)

# Load labels once too
class_names = open(os.path.join(BASE_DIR, "labels.txt"), "r").readlines()

def predict_image(image):
    # Process the PIL Image directly
    if image.mode != 'RGB':
        image = image.convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    image_array = np.asarray(image).astype(np.float32)
    normalized = (image_array / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized

    print(f"Input shape: {data.shape}, dtype: {data.dtype}, min: {data.min()}, max: {data.max()}")

    try:
        prediction = model.predict(data)
    except Exception as e:
        print(f"Error during model prediction: {e}")
        raise

    index = np.argmax(prediction)
    return class_names[index].strip(), float(prediction[0][index])
