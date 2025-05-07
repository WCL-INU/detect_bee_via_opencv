# roi를 검출하고, 그 ROI를 기준으로 다른 이미지에서 벌을 검출하는 코드입니다.
# # Otsu's thresholding을 사용하여 벌을 검출합니다.
# 현재 정확도가 그리 높지 않습니다.
# 배경 이미지를 적응형으로 바꿔서 사용하면 더 좋을 것 같습니다. (이동평균이랄까 그런 거요)
# 또한 겹쳐있는 경우에, 별도의 처리 기법이 필요하다. 면적에 따라 분리하는 방법도 있을 것 같습니다.

import os
import cv2
import numpy as np

def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
	"""
	Resize an image while maintaining its aspect ratio.
	"""
	(h, w) = image.shape[:2]

	if width is None and height is None:
		return image

	if width is not None:
		# Calculate height based on aspect ratio
		r = width / float(w)
		dim = (width, int(h * r))
	else:
		# Calculate width based on aspect ratio
		r = height / float(h)
		dim = (int(w * r), height)

	return cv2.resize(image, dim, interpolation=inter)

def preprocess_image(image_path, width=800):
	"""
	Load and preprocess an image by resizing and converting to HSV.
	"""
	img = cv2.imread(image_path)
	img = resize_with_aspect_ratio(img, width=width)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	return img, hsv

def detect_white_panel(hsv):
	"""
	Detect white regions in the image using HSV thresholds.
	"""
	lower_white = np.array([0, 0, 200])
	upper_white = np.array([180, 50, 255])
	mask = cv2.inRange(hsv, lower_white, upper_white)

	# Apply morphological operations to clean up the mask
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
	mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
	mask = cv2.erode(mask, kernel, iterations=2)
	return mask

def find_largest_contour(mask):
	"""
	Find the largest contour in the mask.
	"""
	contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if not contours:
		raise RuntimeError("No white panel found.")
	return max(contours, key=cv2.contourArea)

def process_images(image_dir, roi_coords, background):
	"""
	Process all images in the directory to detect bees.
	"""
	image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
	idx = 0

	while True:
		image_file = image_files[idx]
		image_path = os.path.join(image_dir, image_file)

		# Load and preprocess the target image
		target_img = cv2.imread(image_path)
		target_img = resize_with_aspect_ratio(target_img, width=800)
		just_show = target_img.copy()
		target_img_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

		# Extract ROI from the target image
		x, y, w, h = roi_coords
		target_roi = target_img_gray[y:y+h, x:x+w]
		cv2.rectangle(just_show, (x,y), (x+w, y+h), (0,255,0), 2)

		# Compute the difference between the background and the target ROI
		diff = cv2.absdiff(background, target_roi)

		# Apply morphological filtering
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
		filtered_diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)

		# Apply Otsu's thresholding
		th, otsu_thresh = cv2.threshold(filtered_diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		print("Otsu's threshold value:", th)

		# Detect contours in the thresholded image
		contours, _ = cv2.findContours(otsu_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		if contours and th >= 30:  # Threshold value is heuristic
			for c in contours:
				xx, yy, ww, hh = cv2.boundingRect(c)
				cv2.rectangle(just_show, (x+xx, y+yy), (x+xx+ww, y+yy+hh), (0, 0, 255), 2)
		else:
			print("No bees detected.")

		# Add a title bar with the file name
		bar_height = 50
		black_bar = cv2.copyMakeBorder(just_show, bar_height, 0, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
		font = cv2.FONT_HERSHEY_SIMPLEX
		font_scale = 1
		font_color = (255, 255, 255)
		thickness = 2
		text_size = cv2.getTextSize(image_file, font, font_scale, thickness)[0]
		text_x = (black_bar.shape[1] - text_size[0]) // 2
		text_y = (bar_height + text_size[1]) // 2
		cv2.putText(black_bar, image_file, (text_x, text_y), font, font_scale, font_color, thickness)
		just_show = black_bar

		# Display the results
		cv2.imshow('Detected ROI', just_show)
		# cv2.imshow('Difference', diff)
		# cv2.imshow('Filtered Difference', filtered_diff)
		# cv2.imshow('Otsu Threshold', otsu_thresh)

		# Handle key presses for navigation
		key = cv2.waitKey(0)
		if key == 27:  # Exit on 'Esc' key
			break
		elif key == 97:  # Left arrow key ('a')
			if idx > 0:
				idx -= 1
			else:
				print("Already at the first image.")
		elif key == 100:  # Right arrow key ('d')
			if idx < len(image_files) - 1:
				idx += 1
			else:
				print("Already at the last image.")

	cv2.destroyAllWindows()

# Main execution
if __name__ == "__main__":
	# Load and preprocess the reference image
	img, hsv = preprocess_image('images/image_2025-03-24_08-46-13.jpg')

	# Detect the white panel and extract ROI
	mask = detect_white_panel(hsv)
	largest_contour = find_largest_contour(mask)
	x, y, w, h = cv2.boundingRect(largest_contour)
	roi = img[y:y+h, x:x+w]
	background = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

	# Process images in the directory
	process_images('./images', (x, y, w, h), background)
