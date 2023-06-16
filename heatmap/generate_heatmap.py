import cv2
import os
import numpy as np

def get_file_names(directory):
    file_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.splitext(file)[0]
            file_names.append(file_path)
    return file_names

# Subtracting the traffic data images with the template image

template_image_path = 'Map_images/map_template.png'
template_image = cv2.imread(template_image_path)

subtract_file_names = get_file_names('Map_images/Original_map_images')

for file_name in subtract_file_names:
    image_path = 'Map_images/Original_map_images/' + file_name + '.png'
    image = cv2.imread(image_path)

    subtracted_image = cv2.subtract(template_image, image)
    subtracted_image = cv2.bitwise_not(subtracted_image)
    cv2.imwrite('Map_images/Subtracted_images/' + file_name + '.png', subtracted_image)

print("STATUS: Subtraction of images complete, Check Subtracted_images directory")


#Blending the subtracted images together to create the a single image of the traffic data

directory_path = 'Map_images/Subtracted_images'

# Initialize an empty list to store the images
image_list = []

# Iterate over the images in the directory
for root, dirs, files in os.walk(directory_path):
    for file in files:
        # Read each image and append it to the list
        image_path = os.path.join(root, file)
        image = cv2.imread(image_path)
        image_list.append(image)

# Check if at least two images are available
if len(image_list) < 2:
    print("Insufficient images for blending.")
    exit()

# Initialize the first image as the base for blending
blended_image = image_list[0]

# Blend the remaining images iteratively
for i in range(1, len(image_list)):
    alpha = 1.0 / (i + 1)  # Calculate the weight for the current image
    beta = 1.0 - alpha     # Calculate the weight for the existing blended image
    blended_image = cv2.addWeighted(blended_image, beta, image_list[i], alpha, 0)

cv2.imwrite('blended.png', blended_image)

print("STATUS: Blending of images complete, check blended.png")

# Isolating the traffic data from the blended image

def remove_blues(image):
    # Convert image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper thresholds for red, orange, and blue colors
    lower_red1 = np.array([0, 100, 100], dtype=np.uint8)
    upper_red1 = np.array([10, 255, 255], dtype=np.uint8)
    lower_red2 = np.array([170, 100, 100], dtype=np.uint8)
    upper_red2 = np.array([180, 255, 255], dtype=np.uint8)
    lower_orange = np.array([10, 100, 100], dtype=np.uint8)
    upper_orange = np.array([25, 255, 255], dtype=np.uint8)

    # Create binary masks for red and orange colors
    mask_red1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    mask_orange = cv2.inRange(hsv_image, lower_orange, upper_orange)

    # Combine the masks to get the final mask (excluding blue)
    mask = cv2.bitwise_or(mask_red1, mask_red2)
    mask = cv2.bitwise_or(mask, mask_orange)

    # # Apply the mask to the original image to remove blues
    rgba_image = cv2.bitwise_and(image, image, mask=mask)

    return rgba_image

# Load the image
image = cv2.imread('blended.png')

# Remove blues and create a transparent background
final_image = remove_blues(image)
cv2.imwrite('traffic_data.png', final_image)

print("STATUS: Isolation of traffic data complete, check traffic_data.png")


# Generating the heatmap using the blended images

def create_heatmap(image):
    # Convert image to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(grayscale, (15, 15), 0)

    # Normalize the blurred image to a range of 0-255
    normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    # Apply a colormap to create the heatmap
    heatmap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)

    return heatmap

# Load the image
image = cv2.imread('traffic_data.png')

# Create the heatmap
heatmap = create_heatmap(image)

cv2.imwrite('heatmap.png', heatmap)

print("STATUS: Heatmap generation complete, check heatmap.png")