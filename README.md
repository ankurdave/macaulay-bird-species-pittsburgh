See `bird_classes.py` for the meaning of each class id.

Use a [pretrained YOLOv5 model](https://github.com/ankurdave/bird-models) or train your own as follows:

```python
# Datasets
# ========
mkdir bird-datasets
pushd bird-datasets

# Clone this repo and run `python3 download_images.py && python3 create-train-test-val-split.py`,
# or download a pre-created version using
# `aws s3 cp s3://macaulay-bird-species-pittsburgh/macaulay.tar.gz . && tar xzf macaulay.tar.gz`.

# Edit macaulay/macaulay-bird-species-pittsburgh.yaml and set the path to bird-datasets.

# Optional: Download the NABirds dataset (creation instructions TODO) using
# `aws s3 cp s3://macaulay-bird-species-pittsburgh/nabirds_yolov5.tar.gz . && tar xzf nabirds_yolov5.tar.gz`.

popd

# Start from pretrained model (optional)
# ======================================
mkdir bird-models
curl -o bird-models/yolov5n-birds-pittsburgh.pt -L https://github.com/ankurdave/bird-models/raw/master/yolov5n-birds-pittsburgh.pt

# Training
# ========
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip3 install -r requirements.txt
python3 train.py --data ../bird-datasets/macaulay/macaulay-bird-species-pittsburgh.yaml --weights ../bird-models/yolov5n-birds-pittsburgh.pt --cfg yolov5n.yaml --cache disk
```

To add more labels to this dataset:

1. Search for a single bird species on eBird. Download a CSV of the search results.
2. Edit `scrape-macaulay-search-csv.py` to add the CSV to `csv_to_dir`, then run that script to download the images.
3. Run `python3 autolabel.py <class_id> images/all/<dir>/` to label the new images with model assist. For example, to label images of Mourning Doves: `python3 autolabel.py '0' images/all/0_mourning_dove/`
