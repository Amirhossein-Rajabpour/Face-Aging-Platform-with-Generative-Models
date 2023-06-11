from pathlib import Path
import cv2
import dlib
import numpy as np
import argparse
from contextlib import contextmanager
from wide_resnet import WideResNet
from keras.utils.data_utils import get_file

pretrained_model = "https://github.com/yu4u/age-gender-estimation/releases/download/v0.5/weights.28-3.73.hdf5"
modhash = 'fbe63257a054c1c5466cfd7bf14646d6'

TARGET_SUFFIX = '_fake_B'
TARGET_SUFFIX_REPLACE = '_real_A'

def get_args():
    parser = argparse.ArgumentParser(description="This script detects faces from web cam input, "
                                                 "and estimates age and gender for the detected faces.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--weight_file", type=str, default=None,
                        help="path to weight file (e.g. weights.28-3.73.hdf5)")
    parser.add_argument("--depth", type=int, default=16,
                        help="depth of network")
    parser.add_argument("--width", type=int, default=8,
                        help="width of network")
    parser.add_argument("--margin", type=float, default=0.4,
                        help="margin around detected face for age-gender estimation")
    parser.add_argument("--image_dir", type=str, default=None,
                        help="target image directory; if set, images in image_dir are used instead of webcam")
    args = parser.parse_args()
    return args


def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
               font_scale=0.8, thickness=1):
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x, y = point
    cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)


@contextmanager
def video_capture(*args, **kwargs):
    cap = cv2.VideoCapture(*args, **kwargs)
    try:
        yield cap
    finally:
        cap.release()


def yield_images():
    # capture video
    with video_capture(0) as cap:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            # get video frame
            ret, img = cap.read()

            if not ret:
                raise RuntimeError("Failed to capture image")

            yield img


def yield_images_from_dir(image_dir):
    image_dir = Path(image_dir)

    for image_path in image_dir.glob("*.*"):
        if TARGET_SUFFIX in str(image_path):
            img = cv2.imread(str(image_path), 1)
            img2 = cv2.imread(str(image_path).replace(TARGET_SUFFIX, TARGET_SUFFIX_REPLACE), 1)

            if img is not None:
                h, w, _ = img.shape
                r = 640 / max(w, h)
                h2, w2, _ = img2.shape
                r2 = 640 / max(w2, h2)
                yield cv2.resize(img, (int(w * r), int(h * r))), cv2.resize(img2, (int(w2 * r2), int(h2 * r2))), str(image_path)


def predict_age(img, detector, margin, img_size, model):
    input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_h, img_w, _ = np.shape(input_img)

    # detect faces using dlib detector
    detected = detector(input_img, 1)
    faces = np.empty((len(detected), img_size, img_size, 3))

    predicted_age = None
    if len(detected) > 0:
        for i, d in enumerate(detected):
            x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
            xw1 = max(int(x1 - margin * w), 0)
            yw1 = max(int(y1 - margin * h), 0)
            xw2 = min(int(x2 + margin * w), img_w - 1)
            yw2 = min(int(y2 + margin * h), img_h - 1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
            faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

        # predict ages and genders of the detected faces
        results = model.predict(faces)
        predicted_genders = results[0]
        ages = np.arange(0, 101).reshape(101, 1)
        predicted_ages = results[1].dot(ages).flatten()
        predicted_age = float(predicted_ages.tolist()[0])
    return predicted_age


def main():
    args = get_args()
    depth = args.depth
    k = args.width
    weight_file = args.weight_file
    margin = args.margin
    image_dir = args.image_dir

    if not weight_file:
        weight_file = get_file("weights.28-3.73.hdf5", pretrained_model, cache_subdir="pretrained_models",
                               file_hash=modhash, cache_dir=Path(__file__).resolve().parent)

    # for face detection
    detector = dlib.get_frontal_face_detector()

    # load model and weights
    img_size = 64
    model = WideResNet(img_size, depth=depth, k=k)()
    model.load_weights(weight_file)

    image_generator = yield_images_from_dir(image_dir) if image_dir else yield_images()

    age_diffs = []
    excluded_images = []

    for generated_image, original_image, filename in image_generator:
        generated_age = predict_age(generated_image, detector, margin, img_size, model)
        original_age = predict_age(original_image, detector, margin, img_size, model)
        if generated_age == None or original_age == None:
            excluded_images.append(filename)
        else:
            age_diff = generated_age - original_age
            if age_diff < 0:
                age_diff = 0  # we should not see negative, treat all negative as model didn't do anything.
            age_diffs.append(age_diff)
    print('Max Age Progression: {:.2f}'.format(max(age_diffs)))
    print('Avg Age Progression: {:.2f}'.format(sum(age_diffs) / len(age_diffs)))
    print('10+ Age Progression: {:.2f}%'.format(len([x for x in age_diffs if x >= 10]) / len(age_diffs) * 100))
    print('15+ Age Progression: {:.2f}%'.format(len([x for x in age_diffs if x >= 15]) / len(age_diffs) * 100))
    print('20+ Age Progression: {:.2f}%'.format(len([x for x in age_diffs if x >= 20]) / len(age_diffs) * 100))
    print('Skipped images: {:d} out of {:d}'.format(len(excluded_images), len(age_diffs)))


if __name__ == '__main__':
    main()
