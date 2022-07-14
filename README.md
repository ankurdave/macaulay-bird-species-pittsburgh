Class ids:

```
class_id_to_name_and_nabirds_id = {
    '0': ('529', 'Mourning Dove'),
    '1': ('553', 'Red-bellied Woodpecker'),
    '2': ('559', 'Downy Woodpecker'),
    '3': ('950', 'Blue Jay'),
    '4': ('957', 'American Crow'),
    '5': ('753', 'American Robin (Adult)'),
    '6': ('819', 'Tufted Titmouse'),
    '7': ('811', 'Carolina Chickadee'),
    '8': ('812', 'Black-capped Chickadee'),
    '9': ('824', 'White-breasted Nuthatch'),
    '10': ('830', 'Carolina Wren'),
    '11': ('902', 'Song Sparrow'),
    '12': ('889', 'Eastern Towhee'),
    '13': ('769', 'Chipping Sparrow (Breeding)'),
    '14': ('976', 'Chipping Sparrow (Immature/nonbreeding adult)'),
    '15': ('746', 'Dark-eyed Junco (Slate-colored)'),
    '16': ('764', 'White-throated Sparrow (White-striped)'),
    '17': ('796', 'House Sparrow (Male)'),
    '18': ('1003', 'House Sparrow (Female/Juvenile)'),
    '19': ('794', 'American Goldfinch (Breeding Male)'),
    '20': ('1001', 'American Goldfinch (Female/Nonbreeding Male)'),
    '21': ('790', 'House Finch (Adult Male)'),
    '22': ('997', 'House Finch (Female/immature)'),
    '23': ('772', 'Northern Cardinal (Adult Male)'),
    '24': ('979', 'Northern Cardinal (Female/Juvenile)'),
    '25': ('912', 'Common Grackle'),
    # "Red-Winged Blackbird (Female)" is omitted to avoid confusion with female sparrows/finches.
    '26': ('780', 'Red-winged Blackbird (Male)',
    '27': ('856', 'European Starling (Nonbreeding Adult)'),
    '28': ('748', 'European Starling (Breeding Adult)'),
}
```

Train with YOLOv5:

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
