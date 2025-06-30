import cv2
import numpy as np
import glob
import os
import random
import matplotlib.pyplot as plt

# Path to the folder containing images
folder = 'images_device_106'
image_paths = glob.glob(os.path.join(folder, '*.*'))

if not image_paths:
    print("No images found in the folder.")
    exit()

# Randomly sample up to 100 images
sample_size = min(100, len(image_paths))
sampled_paths = random.sample(image_paths, sample_size)

# Read the first image to get size
first_img = cv2.imread(sampled_paths[0])
if first_img is None:
    print("First image could not be read.")
    exit()
first_img = cv2.cvtColor(first_img, cv2.COLOR_BGR2RGB)
h, w, c = first_img.shape

# Initialize accumulator
accumulator = np.zeros((h, w, c), dtype=np.float64)
count = 0

for path in sampled_paths:
    img = cv2.imread(path)
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (w, h))
        accumulator += img
        count += 1

if count == 0:
    print("No valid images found in the folder.")
    exit()

# Compute average image
avg_img = (accumulator / count).astype(np.uint8)

# Show the average image
plt.imshow(avg_img)
# plt.title('Average Image')
# plt.axis('off')
plt.show()

# Save the average image
output_path = os.path.join(folder, 'average_image.jpg')
cv2.imwrite(output_path, cv2.cvtColor(avg_img, cv2.COLOR_RGB2BGR))
