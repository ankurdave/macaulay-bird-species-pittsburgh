#!/usr/bin/env python3
"""
Allows scraping thumbnails from the Macaulay Library based on a CSV from a search.

For example, here is a search for images of Mourning Dove:
https://search.macaulaylibrary.org/catalog?mediaType=photo&unconfirmed=incl&captive=incl&taxonCode=moudov&view=list
"""

import csv
import requests
import sys
import os
import os.path

csv_to_dir = [
    ('ML__2022-07-12T17-22_moudov_photo.csv', '0_mourning_dove'),
    ('ML__2022-07-12T18-07_rebwoo_photo.csv', '1_red_bellied_woodpecker'),
    ('ML__2022-07-12T18-18_dowwoo_photo.csv', '2_downy_woodpecker'),
    ('ML__2022-07-12T18-28_blujay_photo.csv', '3_blue_jay'),
    ('ML__2022-07-12T18-29_amecro_photo.csv', '4_american_crow'),
    ('ML__2022-07-12T18-30_amerob_photo.csv', '5_american_robin'),
    ('ML__2022-07-12T18-31_tuftit_photo.csv', '6_tufted_titmouse'),
    ('ML__2022-07-12T18-40_carchi_photo.csv', '7_carolina_chickadee'),
    ('ML__2022-07-12T18-41_bkcchi_photo.csv', '8_black_capped_chickadee'),
    ('ML__2022-07-12T18-41_whbnut_photo.csv', '9_white_breasted_nuthatch'),
    ('ML__2022-07-12T18-46_carwre_photo.csv', '10_carolina_wren'),
    ('ML__2022-07-12T18-47_sonspa_photo.csv', '11_song_sparrow'),
    ('ML__2022-07-12T18-47_eastow_photo.csv', '12_eastern_towhee'),
    ('ML__2022-07-12T18-49_chispa_photo.csv', '13_chipping_sparrow_breeding'),
    ('ML__2022-07-12T18-50_chispa_photo.csv', '14_chipping_sparrow_immature_nonbreeding'),
    ('ML__2022-07-12T18-51_slcjun_photo.csv', '15_dark_eyed_junco_slate_colored'),
    ('ML__2022-07-12T18-52_whtspa_photo.csv', '16_white_throated_sparrow'),
    ('ML__2022-07-12T18-54_houspa_photo.csv', '17_house_sparrow_adult_male'),
    ('ML__2022-07-12T18-55_houspa_photo.csv', '18_house_sparrow_female_juvenile'),
    ('ML__2022-07-12T18-57_amegfi_photo.csv', '19_american_goldfinch_breeding_male'),
    ('ML__2022-07-12T18-58_amegfi_photo.csv', '20_american_goldfinch_female_nonbreeding_male'),
    ('ML__2022-07-12T18-59_houfin_photo.csv', '21_house_finch_adult_male'),
    ('ML__2022-07-12T19-00_houfin_photo.csv', '22_house_finch_female_juvenile'),
    ('ML__2022-07-12T19-01_norcar_photo.csv', '23_northern_cardinal_adult_male'),
    ('ML__2022-07-12T19-02_norcar_photo.csv', '24_northern_cardinal_female_juvenile'),
    ('ML__2022-07-12T19-03_comgra_photo.csv', '25_common_grackle'),
    ('ML__2022-07-12T19-03_rewbla_photo.csv', '26_red_winged_blackbird'),
    ('ML__2022-07-12T19-08_eursta_photo.csv', '27_european_starling_nonbreeding'),
    ('ML__2022-07-12T19-06_eursta_photo.csv', '28_european_starling_breeding_adult'),
]

def get_image(ml_catalog_number, output_dir):
    img = f"{output_dir}/{ml_catalog_number}.jpg"
    if os.path.exists(img):
        print(f"{img}: exists")
        return
    url = f"https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{ml_catalog_number}/1200"
    print(f"{img} <- {url}")
    r = requests.get(url, allow_redirects=True)
    open(img, 'wb').write(r.content)


def load_ml_catalog_numbers(search_csv):
    # Keep one image per recordist to avoid duplicates.
    by_recordist = {}
    with open(search_csv, 'r') as f:
        reader = csv.reader(f)
        row_num = 0
        for row in reader:
            if row_num == 0:
                row_num += 1
                continue

            ml_catalog_number = row[0]
            recordist = row[5]
            rating = float(row[40]) if row[40] else 0.0

            if ((recordist in by_recordist and by_recordist[recordist][1] < rating)
                or (recordist not in by_recordist)):
                by_recordist[recordist] = (ml_catalog_number, rating)

            row_num += 1

    sorted_by_rating_desc = sorted(by_recordist.values(), key=lambda pair: pair[1], reverse=True)
    return [ml_catalog_number for (ml_catalog_number, rating) in sorted_by_rating_desc if rating > 0.0]

if __name__ == "__main__":
    for (search_csv, output_dir) in csv_to_dir:
        ml_catalog_numbers = load_ml_catalog_numbers(search_csv)
        os.makedirs(output_dir, exist_ok=True)
        # Take the first 1000 images.
        for cat_num in ml_catalog_numbers[0:1000]:
            get_image(cat_num, output_dir)
