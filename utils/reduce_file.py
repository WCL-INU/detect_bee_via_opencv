import os
from datetime import datetime, timedelta
import re
from PIL import Image

directory = ""

# Create a dictionary to track files by (date, hour, minute)
file_time_map = {}

# Pre-scan directory to group files by (YYYYMMDD, HH, MM)
for filename in os.listdir(directory):
    match = re.search(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z', filename)
    if match:
        key = (match.group(1), match.group(2), match.group(3), match.group(4), match.group(5))  # (YYYY, MM, DD, HH, MM)
        file_time_map.setdefault(key, []).append(filename)

# Print file pairs with same (date, hour, minute)
for key, files in file_time_map.items():
    for file in files:
        if re.search('thumb.jpg', file):
            print("find thumb file. delete it.")
            filepath = os.path.join(directory, file)
            try:
                os.remove(filepath)
            except Exception as e:
                print(e)

for key, files in file_time_map.items():
    if len(files) > 1:
        print(f"Files with same date/hour/minute {key}: {files}")

print("now, compare file's time and capture time.")

for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if not os.path.isfile(filepath):
        continue
    
    # Extract original image information (width, height, format)
    try:
        with Image.open(filepath) as img:
            width, height = img.size
            img_format = img.format
            print(f"    Width: {width}, Height: {height}, Format: {img_format}")

            # Try to extract original capture time from EXIF data
            exif_data = img._getexif()
            capture_datetime = None
            if exif_data:
                # 36867 is DateTimeOriginal, 306 is DateTime
                for tag in [36867, 306]:
                    if tag in exif_data:
                        capture_datetime = exif_data[tag]
                        break
            if capture_datetime:
                print(f"    Original Capture Time (EXIF): {capture_datetime}")
            else:
                print("    Original Capture Time (EXIF): Not found")
    except Exception as e:
        print(f"    Could not open image: {e}")
    
    if capture_datetime:
        # Extract date and time from filename using regex (format: YYYY:MM:DD HH:MM:SS)
        match = re.search(r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z', filename)
        if not match:
            print("    Date and Time in Filename: Not found")
        
        filename_datetime = f"{match.group(1)}:{match.group(2)}:{match.group(3)} {match.group(4)}:{match.group(5)}:{match.group(6)}"
        print(f"    Date and Time in Filename: {filename_datetime}")
        
        # Convert both datetimes to Python datetime objects for comparison
        try:
            exif_dt = datetime.strptime(capture_datetime, "%Y:%m:%d %H:%M:%S")
            file_dt = datetime.strptime(filename_datetime, "%Y:%m:%d %H:%M:%S")
            print(f"    EXIF datetime object: {exif_dt}")
            print(f"    Filename datetime object: {file_dt}")
        except Exception as e:
            print(f"    Error parsing datetimes: {e}")
        
        # Compare datetimes
        # Allow up to 1 second difference between exif_dt and file_dt or exif_dt and file_dt + 9 hours
        if abs((exif_dt - file_dt).total_seconds()) == 0:
            continue
        elif abs((exif_dt - file_dt).total_seconds()) == 1:
            # Check if a file with the EXIF datetime already exists
            potential_new_filename = re.sub(
                r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z',
                exif_dt.strftime('%Y%m%dT%H%M%SZ'),
                filename
            )
            potential_new_filepath = os.path.join(directory, potential_new_filename)
            if os.path.exists(potential_new_filepath):
                try:
                    os.remove(filepath)
                    print(f"    Removed duplicate file: {filename}")
                except Exception as e:
                    print(f"    Error removing file: {e}")
            else:
                try:
                    os.rename(filepath, potential_new_filepath)
                    print(f"    Renamed file to: {potential_new_filename}")
                except Exception as e:
                    print(f"    Error renaming file: {e}")
        elif abs((exif_dt - (file_dt + timedelta(hours=9))).total_seconds()) <= 1:
            # Replace filename datetime with exif_dt (keep format)
            try:
                new_filename = re.sub(
                    r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z',
                    exif_dt.strftime('%Y%m%dT%H%M%SZ'),
                    filename
                )
                new_filepath = os.path.join(directory, new_filename)
                os.rename(filepath, new_filepath)
                print(f"    Renamed file to: {new_filename}")
            except Exception as e:
                print(f"    Error renaming file: {e}, removing file.")
            try:
                os.remove(filepath)
            except Exception as remove_e:
                print(f"    Error removing file: {remove_e}")
        else:
            continue
