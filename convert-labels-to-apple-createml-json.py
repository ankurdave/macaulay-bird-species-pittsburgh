import glob
import json
import os
from PIL import Image
from bird_classes import class_id_to_name_and_nabirds_id

if __name__ == '__main__':
    for d in ['train', 'val', 'test']:
        image_dir = os.path.join('images', d)
        label_dir = os.path.join('labels', d)
        out_file = os.path.join(image_dir, f"apple-createml-{d}.json")

        label_files = glob.glob(
            os.path.join(label_dir, os.path.join('**', '*.txt')),
            recursive=True,
        )
        num_files_read = 0
        labels = []
        for label_file_path in label_files:
            label_file = os.path.relpath(label_file_path, start=label_dir)

            image_file = label_file.replace('.txt', '.jpg')
            image_file_path = os.path.join(image_dir, image_file)

            im = Image.open(image_file_path)
            im_width, im_height = im.size

            with open(label_file_path, 'r') as f:
                labels_for_image = []
                for line in f:
                    fields = line.strip().split()
                    class_id = fields[0]
                    x_center, y_center, width, height = [float(field) for field in fields[1:]]
                    _, class_name = class_id_to_name_and_nabirds_id[class_id]
                    labels_for_image.append({
                        'label': class_name,
                        'coordinates': {
                            'x': float(x_center * im_width),
                            'y': float(y_center * im_height),
                            'width': int(im_width),
                            'height': int(im_height),
                        }
                    })
                labels.append({
                    'image': image_file,
                    'annotations': labels_for_image,
                })

            num_files_read += 1
            if num_files_read % 1000 == 0 or num_files_read == len(label_files):
                print(f"... Read {num_files_read}/{len(label_files)}")

        with open(out_file, 'w') as f:
            json.dump(labels, f, indent=2)
        print(f"Wrote {out_file}. You can now import {image_dir} into Apple Create ML.")
