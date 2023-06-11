from flask import Flask, request, jsonify
import subprocess
import base64
import os
from PIL import Image
from io import BytesIO
import estimator
app = Flask(__name__)


def get(request, key):
    return request.get_json().get(key)


def deserialise_img(img_str):
    img = base64.b64decode(img_str.split(",")[-1])
    img = Image.open(BytesIO(img))
    img = img.convert('RGB')
    return img


def encode_pil_image(pil_image):
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG')
    img_str = "data:image/png;base64," + \
        base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str


@app.route('/')
def hello_world():
    return 'Welcome to Age Estimation!'


@app.route('/age_estimation', methods=['POST'])
def manipulate():

    img = get(request, 'img')
    img = deserialise_img(img)

    # save the image to a file in a specified directory
    save_dir = './image/'
    filename = 'image.jpg'
    img.save(os.path.join(save_dir, filename))

    # # Run a command and get the output
    # full_command = "python demo.py --image_dir ./image --weight_file ./pretrained_model/EfficientNetB3_224_weights.11-3.44.hdf5"
    # edited_command = full_command.split(" ")

    # # output is a single number indicating the age of the input
    # output = subprocess.check_output(edited_command)

    # print("#### output: ", edited_command)

    # Second way to call the estimation API
    image_path = "./image"
    wight_path = "./pretrained_model/EfficientNetB3_224_weights.11-3.44.hdf5"
    age = estimator.estimate(image_path, wight_path)

    print("#### predicted age returned: ", age)

    # return jsonify(age=output)
    return jsonify(age=age)


if __name__ == '__main__':
    print('Running Flask app...')
    app.run(host='0.0.0.0', port=5050)
