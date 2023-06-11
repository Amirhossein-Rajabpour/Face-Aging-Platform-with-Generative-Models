from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
import requests
import json
import asyncio
import threading


def hello_glow(request):
    return HttpResponse('Hello from Glow model!')


def main_page(request):
    return render(request, "main.html")


def estimate_age(encoded_image):
    # Send a POST request to the Estimate Age Flask server to estimate the age of the input face
    url_estimate = "http://estimate_age_container:5050/age_estimation"
    data_estimate = {
        "img": encoded_image,
    }

    try:
        response_estimate = requests.post(url_estimate, json=data_estimate)
        response_estimate = json.loads(response_estimate.text)
        age = response_estimate['age']

        return age

    except json.JSONDecodeError as e:
        print(f"********JSONDecodeError: {e}")

    except Exception as e:
        print(f"********Error: {e}")


# Send a POST request to the Glow Flask server
def request_glow(dict, encoded_image, alpha, type):
    url_glow = "http://glow_container:5050/api/aging"
    data_glow = {
        "img": encoded_image,
        "alpha": float(alpha),
        "type": type
    }

    try:
        response_glow = requests.post(url_glow, json=data_glow)
        response_glow = json.loads(response_glow.text)
        img_data_glow = response_glow['img'][0]
        dict["glow"] = img_data_glow
        # return img_data_glow

    except json.JSONDecodeError as e:
        print(f"********JSONDecodeError: {e}")

    except Exception as e:
        print(f"********Error: {e}")


# Send a POST request to the CycleGAN Flask server
def request_cyclegan(dict, encoded_image, type):

    # Send a POST request to the Glow Flask server to align the input face
    url_align_face = "http://glow_container:5050/api/align_encode"
    data_align_face = {
        "img": encoded_image,
    }

    try:
        response_align_face = requests.post(
            url_align_face, json=data_align_face)
        response_align_face = json.loads(response_align_face.text)
        aligned_face = response_align_face['img'][0]

        dict["align"] = aligned_face

    except json.JSONDecodeError as e:
        print(f"********JSONDecodeError: {e}")

    except Exception as e:
        print(f"********Error: {e}")

    url_cyclegan = "http://cyclegan_container:5050/cyclegan_aging"
    data_cyclegan = {
        "img": encoded_image,
        "type": type
    }

    try:
        response_cyclegan = requests.post(url_cyclegan, json=data_cyclegan)
        response_cyclegan = json.loads(response_cyclegan.text)
        img_data_cyclegan = response_cyclegan['img']
        dict["cyclegan"] = img_data_cyclegan
        # return img_data_cyclegan

    except json.JSONDecodeError as e:
        print(f"********JSONDecodeError: {e}")

    except Exception as e:
        print(f"********Error: {e}")


@csrf_exempt
def input_glow(request):
    alpha = request.POST.get("alpha")
    img_b64 = request.POST.get("img")

    img_b64 = img_b64[1:-1]

    context = {
        "alpha": alpha,
        "img": img_b64
    }

    return render(request, "results.html", context=context)
    # return HttpResponse(f"image with alpha {alpha} uploaded!")


def process_image(request):
    if request.method == 'POST':

        # Take the option. Make the face older or younger
        selected_aging_type = request.POST.get("dropdown-option")
        print("Selected type is: ", selected_aging_type)

        # Take the image and value of alpha from view
        image_file = request.FILES['image']
        alpha = request.POST.get("alpha")

        # Serialize the image as a base64-encoded string
        encoded_image = "data:image/png;base64," + \
            base64.b64encode(image_file.read()).decode('utf-8')

        # Create a dictionary to store the results
        results = {}

        # Estimate the age of the input face
        main_age = estimate_age(encoded_image)

        # Create two threads and pass in the dictionary as an argument
        t1 = threading.Thread(target=request_glow, args=(
            results, encoded_image, alpha, selected_aging_type))
        t2 = threading.Thread(target=request_cyclegan,
                              args=(results, encoded_image, selected_aging_type))

        # Start the threads
        t1.start()
        t2.start()

        # Wait for the threads to finish
        t1.join()
        t2.join()

        # Estimate ages of output faces
        glow_age = estimate_age(results["glow"])
        cyclegan_age = estimate_age(results["cyclegan"])

        # Send the results to the view
        context = {
            "alpha": alpha,
            "aligned_face": results["align"],
            "img_glow": results["glow"],
            "img_cyclegan": results["cyclegan"],
            "main_age": main_age,
            "glow_age": glow_age,
            "cyclegan_age": cyclegan_age,
            "dif_glow": abs(int(glow_age) - int(main_age)),
            "dif_cyclegan": abs(int(cyclegan_age) - int(main_age))
        }

        # context = {
        #     "alpha": alpha,
        #     "aligned_face": encoded_image,
        #     "img_glow": encoded_image,
        #     "img_cyclegan": encoded_image,
        # }

        return render(request, "results.html", context=context)

    # Return a 400 Bad Request response if the request is invalid
    return JsonResponse({'error': 'Invalid request'}, status=400)
