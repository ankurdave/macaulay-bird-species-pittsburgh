#!/usr/bin/env python3
"""
Model-assisted labeling for object detection.

Usage: python3 autolabel.py <class> <image_dir>

Example: python3 autolabel.py '0' images/train/0_mourning_dove
"""
import cv2
import numpy as np
import yolov5
import os
import os.path
import sys

# Model is available at https://github.com/ankurdave/bird-models/blob/master/yolov5n-coco-cub2011.onnx.
model_onnx = yolov5.load('/Users/ankur.dave/repos/bird-models/yolov5n-coco-cub2011.onnx')
model_onnx.conf = 0.5

window_name = 'image'
cv2.namedWindow(window_name)

prev_label_files = []

def try_autolabel(image_infile, label_outfile, cls):
    if os.path.exists(label_outfile):
        print(f"{image_infile} is already labeled as {label_outfile}, skipping.")
        return

    stream = cv2.VideoCapture(image_infile)
    if not stream.isOpened():
        print(f"Could not open {image_infile}")
        quit()
    ret, frame_bgr = stream.read()
    if not ret:
        print(f"Could not read {image_infile}")
        quit()
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    img_height, img_width, _ = frame_rgb.shape
    print(f"{image_infile}: {img_width} x {img_height}")

    results = model_onnx(frame_rgb)
    labels, cord = results.xyxyn[0][:, -1].numpy(), results.xyxyn[0][:, :-1].numpy()

    label_coords = []

    n = len(labels)
    for i in range(n):
        row = cord[i]
        x1, y1, x2, y2 = row[0:4]
        label_coords.append(((x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1))

    def draw_label_rectangles(frame_bgr):
        for x_center, y_center, width, height in label_coords:
            bgr = (0, 0, 255)
            cv2.rectangle(frame_bgr, \
                          (int((x_center - width / 2) * img_width), int((y_center - height / 2) * img_height)), \
                          (int((x_center + width / 2) * img_width), int((y_center + height / 2) * img_height)), \
                           bgr, 2)
        cv2.imshow(window_name, frame_bgr)

    print(f"\nLabeling {image_infile} as {cls}...")
    print(f"- Press y/SPC/RET to accept suggested labels.")
    print(f"- Press c to clear labels.")
    print(f"- Click and drag to add a new label.")
    print(f"- Press n to skip this image.")
    print(f"- Press x to delete this image.")
    print(f"- Press u to undo (delete) the most recently saved label file.")
    print(f"- Press q/ESC to quit.")
    print(f"Press a key...")

    upper_left = None
    def select_label_coords(event, x, y, flags, param):
        nonlocal upper_left
        if event == cv2.EVENT_LBUTTONDOWN:
            # Record where the user started dragging.
            upper_left = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            # Show a rectangle around the user's current selection area.
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            bgr = (0, 0, 0)
            cv2.rectangle(frame_bgr, upper_left, (x, y), bgr, 2)
            cv2.imshow(window_name, frame_bgr)
        elif event == cv2.EVENT_LBUTTONUP:
            # Record the user's selection area and show the new labels.
            x1, y1 = upper_left[0] / img_width, upper_left[1] / img_height
            x2, y2 = x / img_width, y / img_height
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            print(f"Selected area: {x_center} {y_center} {width} {height}")
            label_coords.append((x_center, y_center, width, height))
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            draw_label_rectangles(frame_bgr)
        elif event == cv2.EVENT_MOUSEMOVE:
            # Draw crosshairs under the mouse pointer.
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            bgr = (0, 0, 0)
            cv2.line(frame_bgr, (x, 0), (x, img_height), bgr, 2)
            cv2.line(frame_bgr, (0, y), (img_width, y), bgr, 2)
            draw_label_rectangles(frame_bgr)

    cv2.setMouseCallback(window_name, select_label_coords)
    while True:
        tmp_frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        draw_label_rectangles(tmp_frame_bgr)
        user_command = cv2.waitKey(0)
        if user_command == ord('q') or user_command == 27:
            quit()
        elif user_command == ord('y') or user_command == 13 or user_command == 32:
            label_dirname = os.path.dirname(label_outfile)
            try:
                os.makedirs(label_dirname, exist_ok=False)
                print(f"Created directory {label_dirname}.")
            except OSError:
                pass
            print(f"Creating {label_outfile} with labels:")
            with open(label_outfile, 'x') as label_file:
                for x_center, y_center, width, height in label_coords:
                    label_line = f"{cls} {x_center} {y_center} {width} {height}"
                    print(f"  {label_line}")
                    label_file.write(label_line + "\n")
            prev_label_files.append(label_outfile)
            return
        elif user_command == ord('n'):
            print(f"Skipping {image_infile}.")
            return
        elif user_command == ord('x'):
            print(f"Deleting {image_infile}.")
            os.remove(image_infile)
            return
        elif user_command == ord('u'):
            if len(prev_label_files) > 0:
                prev_label_file = prev_label_files.pop()
                os.remove(prev_label_file)
                print(f"Undoing previous label file {prev_label_file}.")
            else:
                print(f"No previous label file to undo.")
        elif user_command == ord('c'):
            print(f"Clearing labels.")
            label_coords = []
        else:
            print(f"Unknown key: {user_command}")


if __name__ == '__main__':
    cls = sys.argv[1]
    image_dir = sys.argv[2]
    image_files = os.listdir(image_dir)
    num_images_processed = 0
    for image_file in image_files:
        image_file_path = os.path.join(image_dir, image_file)
        label_file_path = image_file_path.replace('images', 'labels').replace('.jpg', '.txt')
        print(f"Progress: {num_images_processed} of {len(image_files)}")
        try_autolabel(image_file_path, label_file_path, cls)
        num_images_processed += 1
