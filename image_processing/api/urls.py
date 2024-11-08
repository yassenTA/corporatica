# image_processing/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("upload_image", UploadedImageView.as_view(), name="upload_image"),
    path("batch_upload", BatchUploadView.as_view(), name="batch_upload"),
    path("color_histogram", ColorHistogramView.as_view(), name="color_histogram"),
    path("resize_image", ResizeImageView.as_view(), name="resize_image"),
    path("crop_image", CropImageView.as_view(), name="crop_image"),
    path("convert_image", ConvertImageView.as_view(), name="convert_image"),
]
