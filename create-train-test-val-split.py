#!/usr/bin/env python3

import os
import tempfile
import shutil
import random
import glob
from sklearn.model_selection import train_test_split
from pathlib import Path

num_files_copied = 0
total_num_files = 0

def copy_to_train_val_or_test_dir(src, train_val_or_test):
    global num_files_copied

    dst = f.replace('/all/', f"/{train_val_or_test}/")
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.link(src, dst)

    num_files_copied += 1
    if num_files_copied % 1000 == 0 or num_files_copied == total_num_files:
        print(f"... Copied {num_files_copied}/{total_num_files}")

if __name__ == '__main__':
    image_files = glob.glob('images/all/**/*.jpg', recursive=True)
    label_files = [f.replace('images/', 'labels/').replace('.jpg', '.txt') for f in image_files]
    train_images, val_images, train_labels, val_labels = train_test_split(
        image_files, label_files, test_size=0.2, random_state=1
    )
    val_images, test_images, val_labels, test_labels = train_test_split(
        val_images, val_labels, test_size=0.5, random_state=1
    )

    total_num_files = (
        len(train_images) + len(train_labels) + len(val_images) + len(val_labels) +
        len(test_images) + len(test_labels)
    )

    for f in train_images + train_labels:
        copy_to_train_val_or_test_dir(f, 'train')
    for f in val_images + val_labels:
        copy_to_train_val_or_test_dir(f, 'val')
    for f in test_images + test_labels:
        copy_to_train_val_or_test_dir(f, 'test')
    print('Done.')
