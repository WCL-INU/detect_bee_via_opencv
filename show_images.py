import os
import cv2
from dotenv import load_dotenv

load_dotenv()

directory = os.getenv("DIR")

# Directory containing images
image_dir = directory

# List all files in the directory
image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f)) and f.lower().endswith('.jpg') and not f.startswith('.')]
image_files.sort()  # Sort files to maintain order

# Display each image using cv2.imshow
idx = 0
prev_idx = idx  # Initialize previous index to current index
while True:
	image_file = image_files[idx]
	image_path = os.path.join(image_dir, image_file)
	image = cv2.imread(image_path)
	prev_image_path = os.path.join(image_dir, image_files[prev_idx])
	prev_image = cv2.imread(prev_image_path)
	
	if image is not None:
		resized_image = cv2.resize(image, (800, 600))  # Adjust window size

		if prev_image is not None:
			# Calculate the difference between the current and previous images
			diff_image = cv2.absdiff(resized_image, cv2.resize(prev_image, (800, 600)))
			# diff_image = cv2.cvtColor(diff_image, cv2.COLOR_BGR2GRAY)
			# _, diff_image = cv2.threshold(diff_image, 30, 255, cv2.THRESH_BINARY)
			# diff_image = cv2.cvtColor(diff_image, cv2.COLOR_GRAY2BGR)
			# resized_image = cv2.addWeighted(resized_image, 0.7, diff_image, 0.3, 0)
			cv2.imshow('Difference Image', diff_image)
		
		# Add a black bar at the top and put the file name as title
		bar_height = 50
		black_bar = cv2.copyMakeBorder(resized_image, bar_height, 0, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
		font = cv2.FONT_HERSHEY_SIMPLEX
		font_scale = 1
		font_color = (255, 255, 255)
		thickness = 2
		text_size = cv2.getTextSize(image_file, font, font_scale, thickness)[0]
		text_x = (black_bar.shape[1] - text_size[0]) // 2
		text_y = (bar_height + text_size[1]) // 2
		cv2.putText(black_bar, image_file, (text_x, text_y), font, font_scale, font_color, thickness)
		resized_image = black_bar

		cv2.imshow('Image Viewer', resized_image)
		key = cv2.waitKey(0)  # Wait indefinitely for a key press
		prev_idx = idx
		if key == 27 or key == ord('q'):  # Exit on 'Esc' key
			break
		elif key == ord('a'):  # Left arrow key ('a' ASCII code is 97)
			if idx > 0:
				idx -= 1
			else:
				print("Already at the first image.")
			continue
		elif key == ord('d'):  # Right arrow key ('d' ASCII code is 100)
			if idx < len(image_files) - 1:
				idx += 1
			else:
				print("Already at the last image.")
			continue
	else:
		print(f"Could not read image: {image_file}")
cv2.destroyAllWindows()
