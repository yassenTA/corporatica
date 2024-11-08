# image_processing/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..models import UploadedImage
from .serializer import UploadedImageSerializer
from PIL import Image
import os
import io
from .utils import generate_color_histogram, save_histogram_plot
from django.http import FileResponse
from .utils import resize_image, crop_image, convert_image_format
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class UploadedImageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = UploadedImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BatchUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist("images")
        images = []
        for file in files:
            image = UploadedImage(image=file)
            image.save()
            images.append(UploadedImageSerializer(image).data)
        return Response(images, status=status.HTTP_201_CREATED)


class ColorHistogramView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):

        try:
            image = UploadedImage.objects.get(id=request.query_params.get("image_id"))
            histogram_data = generate_color_histogram(image.image.path)
            histogram_plot = save_histogram_plot(histogram_data)
            return FileResponse(histogram_plot, content_type="image/png")
        except UploadedImage.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ResizeImageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        width = int(request.data.get("width"))
        height = int(request.data.get("height"))
        try:
            image = UploadedImage.objects.get(id=request.data.get("image_id"))
            resized_image = resize_image(image.image.path, width, height)
            buffer = io.BytesIO()
            resized_image.save(buffer, format="PNG")
            buffer.seek(0)
            return FileResponse(buffer, content_type="image/png")
        except UploadedImage.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CropImageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        left = int(request.data.get("left"))
        top = int(request.data.get("top"))
        right = int(request.data.get("right"))
        bottom = int(request.data.get("bottom"))
        try:
            image = UploadedImage.objects.get(id=request.data.get("image_id"))
            cropped_image = crop_image(image.image.path, left, top, right, bottom)
            buffer = io.BytesIO()
            cropped_image.save(buffer, format="PNG")
            buffer.seek(0)
            return FileResponse(buffer, content_type="image/png")
        except UploadedImage.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ConvertImageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        format = request.data.get("format", "JPEG").upper()
        try:
            image = UploadedImage.objects.get(id=request.data.get("image_id"))
            buffer = convert_image_format(image.image.path, format)
            return FileResponse(buffer, content_type=f"image/{format.lower()}")
        except UploadedImage.DoesNotExist:
            return Response(
                {"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND
            )
