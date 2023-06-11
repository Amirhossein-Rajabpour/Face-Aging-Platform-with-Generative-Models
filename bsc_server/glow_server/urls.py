from django.urls import path
from glow_server.views import *

urlpatterns = [
    path("glow/", hello_glow),
    path("get_img_user/", input_glow),
    path("main/", main_page),
    path("submit_form/", process_image),
]
