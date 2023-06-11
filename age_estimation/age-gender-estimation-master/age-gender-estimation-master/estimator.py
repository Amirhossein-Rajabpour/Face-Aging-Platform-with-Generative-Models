from pathlib import Path
import os
import cv2
import dlib
import numpy as np
import argparse
from contextlib import contextmanager
from omegaconf import OmegaConf
from tensorflow.keras.utils import get_file
from tensorflow.keras.models import load_model
from src.factory import get_model


pretrained_model = "https://github.com/yu4u/age-gender-estimation/releases/download/v0.6/EfficientNetB3_224_weights.11-3.44.hdf5"
modhash = '6d7f7b7ced093a8b3ef6399163da6ece'


def get_args():
    parser = argparse.ArgumentParser(description="This script detects faces from web cam input, "
                                                 "and estimates age and gender for the detected faces.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--weight_file", type=str, default=None,
                        help="path to weight file (e.g. weights.28-3.73.hdf5)")
    parser.add_argument("--margin", type=float, default=0.4,
                        help="margin around detected face for age-gender estimation")
    parser.add_argument("--image_dir", type=str, default=None,
                        help="target image directory; if set, images in image_dir are used instead of webcam")
    args = parser.parse_args()
    return args


def yield_images_from_dir(image_dir):
    image_dir = Path(image_dir)

    for image_path in image_dir.glob("*.*"):
        img = cv2.imread(str(image_path), 1)

        if img is not None:
            h, w, _ = img.shape
            r = 640 / max(w, h)
            yield cv2.resize(img, (int(w * r), int(h * r)))


def load_model_from_disk():
    # Check if the model file exists
    if os.path.exists("./pretrained_model/efficientnetb3_notop.h5"):
        model = load_model("./pretrained_model/efficientnetb3_notop.h5")
        print("#### model exists")
        return model
    else:
        print("#### model does not exist!!")
        return None


def save_model_to_disk(model):
    model.save("./pretrained_model/efficientnetb3_notop.h5")


def estimate(image_path, wight_path):
    args = get_args()
    weight_file = wight_path
    margin = args.margin
    image_dir = image_path

    if not weight_file:
        weight_file = get_file("EfficientNetB3_224_weights.11-3.44.hdf5", pretrained_model, cache_subdir="pretrained_models",
                               file_hash=modhash, cache_dir=str(Path(__file__).resolve().parent))

    # for face detection
    detector = dlib.get_frontal_face_detector()

    # load model and weights
    model_name, img_size = Path(weight_file).stem.split("_")[:2]
    img_size = int(img_size)

    cfg = OmegaConf.from_dotlist(
        [f"model.model_name={model_name}", f"model.img_size={img_size}"])

    # Load the model from disk if available
    model = load_model_from_disk()

    if model is None:
        # Model not found on disk, download and save it
        print("#### saving the model...")
        model = get_model(cfg)
        save_model_to_disk(model)

    # model = get_model(cfg)
    model.load_weights(weight_file)

    image_generator = yield_images_from_dir(image_dir)

    for img in image_generator:
        input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_h, img_w, _ = np.shape(input_img)

        # detect faces using dlib detector
        detected = detector(input_img, 1)
        faces = np.empty((len(detected), img_size, img_size, 3))

        if len(detected) > 0:
            for i, d in enumerate(detected):
                x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + \
                    1, d.bottom() + 1, d.width(), d.height()
                xw1 = max(int(x1 - margin * w), 0)
                yw1 = max(int(y1 - margin * h), 0)
                xw2 = min(int(x2 + margin * w), img_w - 1)
                yw2 = min(int(y2 + margin * h), img_h - 1)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
                faces[i] = cv2.resize(
                    img[yw1:yw2 + 1, xw1:xw2 + 1], (img_size, img_size))

            # predict ages and genders of the detected faces
            results = model.predict(faces)
            predicted_genders = results[0]
            ages = np.arange(0, 101).reshape(101, 1)
            predicted_ages = results[1].dot(ages).flatten()

            # print results
            print("ages: ", int(predicted_ages))
            print("gender: ", predicted_genders)
            print("resul is: ", results)

            return int(predicted_ages)
