from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import os

def predict_image(image):  # now accepts PIL Image directly
    # Use custom object scope to handle the incompatible 'groups' parameter
    from tensorflow.keras.models import load_model
    import tensorflow as tf
    
    # Custom loader to handle the groups parameter
    def load_model_with_custom_objects():
        # Define a custom DepthwiseConv2D layer loader
        def custom_objects_handler():
            import tensorflow as tf
            
            class CustomDepthwiseConv2D(tf.keras.layers.DepthwiseConv2D):
                def __init__(self, **kwargs):
                    # Remove the 'groups' parameter if it exists
                    if 'groups' in kwargs:
                        kwargs.pop('groups')
                    super(CustomDepthwiseConv2D, self).__init__(**kwargs)
            
            return {
                'DepthwiseConv2D': CustomDepthwiseConv2D
            }
        
        # Load the model with custom objects
        with tf.keras.utils.custom_object_scope(custom_objects_handler()):
            return load_model("keras_model.h5", compile=False)
    
    # Load the model with custom object handling
    try:
        model = load_model_with_custom_objects()
    except Exception as e:
        print(f"Failed to load model with custom handler: {e}")
        # As a fallback, try with tf.keras directly
        try:
            from tensorflow import keras
            model = keras.models.load_model("keras_model.h5", compile=False)
        except Exception as e:
            print(f"Failed to load model with tf.keras: {e}")
            raise e
    
    # Load class names
    class_names = open("labels.txt", "r").readlines()
    
    # Process the PIL Image directly
    if image.mode != 'RGB':
        image = image.convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    image_array = np.asarray(image).astype(np.float32)
    normalized = (image_array / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    
    # Make prediction
    prediction = model.predict(data)
    index = np.argmax(prediction)
    return class_names[index].strip(), float(prediction[0][index])
