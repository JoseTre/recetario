import sys
sys.path.append('/opt/miniconda3/lib/python3.12/site-packages')
import os
import cv2
import numpy as np

output_folder = "smart_cropped_recipes"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir('.'):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        print(f"Processing: {filename}")
        
        # 1. Load image
        img = cv2.imread(filename)
        if img is None:
            continue
            
        # 2. Pre-process to find the edges of the card
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Threshold adjusted to 130 to handle real-world natural shadows
        _, thresh = cv2.threshold(blurred, 130, 255, cv2.THRESH_BINARY)
        
        # 3. Find the contours (shapes) in the image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            print(f"  Skipping {filename}: No distinct shape boundaries found.")
            continue
            
        # Get the largest detected shape (which should be the index card)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 4. Find the minimum bounding rotated rectangle around the card
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.int64(box)
        
        # 5. Extract angle and dimensions for straightening
        (x, y), (w, h), angle = rect
        
        # OpenCV rotation angle logic adjustments
        if angle < -45:
            angle = 90 + angle
            w, h = h, w
            
        # 6. Straighten the image (Deskew)
        center = (int(x), int(y))
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_img = cv2.warpAffine(img, rotation_matrix, (img.shape[1], img.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # 7. Crop out the straightened card cleanly
        crop_x = max(0, int(x - w / 2))
        crop_y = max(0, int(y - h / 2))
        crop_w = int(w)
        crop_h = int(h)
        
        cropped_img = rotated_img[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
        
        # 8. Save the final clean image
        if cropped_img.size > 0:
            cv2.imwrite(os.path.join(output_folder, filename), cropped_img)
        else:
            print(f"  Error processing geometry on {filename}")

print("\nAll done! Check your straightened files inside the 'smart_cropped_recipes' folder.")
