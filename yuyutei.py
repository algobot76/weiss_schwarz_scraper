import pathlib
import shutil

import requests
import yaml
from bs4 import BeautifulSoup

DOWNLOAD_DIR_PREFIX = pathlib.Path("downloads")
DOWNLOAD_IMAGES = True

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

    if DOWNLOAD_IMAGES:
        download_dir = DOWNLOAD_DIR_PREFIX.joinpath(title)
        if download_dir.exists():
            shutil.rmtree(download_dir)
        download_dir.mkdir(parents=True)
        for card in cards:
            id_ = card["id"]
            new_id = id_.replace("/", "-")
            image = card["image"]
            new_image = image.replace("90_126", "front")
            download_path = download_dir.joinpath(f"{new_id}.jpg")
            r = requests.get(new_image, stream=True)
            if r.status_code == 200:
                with open(download_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
