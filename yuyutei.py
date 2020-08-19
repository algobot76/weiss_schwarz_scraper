import os
import pathlib
import shutil
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_DIR_PREFIX = pathlib.Path("downloads")
DOWNLOAD_IMAGES = os.getenv("DOWNLOAD_IMAGES", False)
if DOWNLOAD_IMAGES == "True":
    DOWNLOAD_IMAGES = True

IMAGE_URL_PREFIX = "https://yuyu-tei.jp/card_image/ws/front"

with open("urls.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

urls = data["urls"]

for title, url in urls.items():
    print(f"Title: {title}")
    print(f"URL: {url}")

    r = requests.get(url)
    if r.status_code != 200:
        print(f"Failed to get cards for the title {title}.")
        continue
    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "html.parser")
    card_units = soup.find_all("li", class_="card_unit")

    cards = []
    for card_unit in card_units:
        id_ = card_unit.find("p", class_="id").get_text().strip()
        name = card_unit.find("p", class_="name").get_text()
        image = card_unit.find("p", class_="image").img["src"]
        cards.append(dict(id=id_, name=name, image=image))
    print(f"Got {len(cards)} cards.")

    if DOWNLOAD_IMAGES:
        download_dir = DOWNLOAD_DIR_PREFIX.joinpath(title)
        if download_dir.exists():
            shutil.rmtree(download_dir)
        download_dir.mkdir(parents=True)
        for card in cards:
            name = card["name"]
            image = card["image"]
            segments = urlparse(image).path.split("/")
            series = segments[-2]
            file_name = segments[-1]
            download_url = f"{IMAGE_URL_PREFIX}/{series}/{file_name}"
            download_path = download_dir.joinpath(file_name)

            print(f"Downloading {name}.")
            r = requests.get(download_url, stream=True)
            if r.status_code == 200:
                with open(download_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                print(f"{name} has been downloaded.")
            else:
                print(f"Failed to download {name}.")
