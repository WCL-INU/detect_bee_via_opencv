import os
import cv2

# Directory containing images
image_dir = './images'

# List all files in the directory
image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

# Display each image using cv2.imshow
idx = 0
while True:
	image_file = image_files[idx]
	image_path = os.path.join(image_dir, image_file)
	image = cv2.imread(image_path)
	if image is not None:
		resized_image = cv2.resize(image, (800, 600))  # Adjust window size
		
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
		if key == 27:  # Exit on 'Esc' key
			break
		elif key == 97:  # Left arrow key ('a' ASCII code is 97)
			if idx > 0:
				idx -= 1
			else:
				print("Already at the first image.")
			continue
		elif key == 100:  # Right arrow key ('d' ASCII code is 100)
			if idx < len(image_files) - 1:
				idx += 1
			else:
				print("Already at the last image.")
			continue
	else:
		print(f"Could not read image: {image_file}")
cv2.destroyAllWindows()
