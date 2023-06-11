from flask import Flask, request, jsonify
import subprocess
import base64
import os
import numpy as np
from PIL import Image
from io import BytesIO
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
    return 'Welcome to CycleGAN!'


@app.route('/cyclegan_aging', methods=['POST'])
def manipulate():

    # Take the input image
    img = get(request, 'img')
    img = deserialise_img(img)

    # Take the desired aging type
    type_input = get(request, 'type')

    # save the image to a file in a specified directory
    save_dir_A = './datasets/y2o/testA/'
    save_dir_B = './datasets/y2o/testB/'

    filename = 'image.jpg'
    img.save(os.path.join(save_dir_A, filename))
    img.save(os.path.join(save_dir_B, filename))

    # Run the command and get the output for one side
    # full_command_one_side = "python test.py --dataroot ./datasets/y2o/testA --name aging_cyclegan --model test --dataset_mode single --no_dropout --gpu_ids -1"
    # edited_command = full_command_one_side.split(" ")

    # Run the command and get the output for both sides
    full_command_both_sides = "python test.py --dataroot ./datasets/y2o/ --name aging_cyclegan --model cycle_gan --no_dropout --gpu_ids -1"
    edited_command = full_command_both_sides.split(" ")
    output = subprocess.check_output(edited_command)

    # Load the image using PIL
    if type_input == "old":
        print("#### make older")
        result_img = open(
            './results/aging_cyclegan/test_latest/images/image_fake_B.png', 'rb')
    else:
        print("#### make younger")
        result_img = open(
            './results/aging_cyclegan/test_latest/images/image_fake_A.png', 'rb')
    res_img = Image.open(result_img)

    return jsonify(img=encode_pil_image(res_img))


if __name__ == '__main__':
    print('Running Flask app...')
    app.run(host='0.0.0.0', port=5050)
