# image_processing/utils.py
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import io


def generate_color_histogram(image_path):
    image = Image.open(image_path)
    colors = ("red", "green", "blue")
    channels = image.split()
    histogram_data = []

    for channel, color in zip(channels, colors):
        histogram, _ = np.histogram(channel, bins=256, range=(0, 256))
        histogram_data.append((color, histogram))

    return histogram_data


def save_histogram_plot(histogram_data):
    plt.figure()
    for color, hist in histogram_data:
        plt.plot(hist, color=color)
    plt.xlim([0, 256])
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf


# image_processing/utils.py (continuation)
def resize_image(image_path, width, height):
    image = Image.open(image_path)
    resized_image = image.resize((width, height))
    return resized_image


def crop_image(image_path, left, top, right, bottom):
    image = Image.open(image_path)
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image


def convert_image_format(image_path, format="JPEG"):
    image = Image.open(image_path)
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer
