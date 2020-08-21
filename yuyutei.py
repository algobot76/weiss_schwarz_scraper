import json
import os
import pathlib
import shutil
from urllib.parse import urlparse

import requests
import yaml
from PIL import Image
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_DIR_PREFIX = pathlib.Path("downloads")
DOWNLOAD_IMAGES = os.getenv("DOWNLOAD_IMAGES")
if DOWNLOAD_IMAGES == "True":
    DOWNLOAD_IMAGES = True
else:
    DOWNLOAD_IMAGES = False
TTS_EXPORT = os.getenv("TTS_EXPORT")
if TTS_EXPORT == "True":
    TTS_EXPORT = True
else:
    TTS_EXPORT = False

IMAGE_URL_PREFIX = "https://yuyu-tei.jp/card_image/ws/front"

with open("urls.yaml", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

urls = data["urls"]


def main():
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

        for card in cards:
            image = card["image"]
            segments = urlparse(image).path.split("/")
            series = segments[-2]
            file_name = segments[-1]
            card["image"] = f"{IMAGE_URL_PREFIX}/{series}/{file_name}"

        print(f"Got {len(cards)} cards.")

        download_dir = DOWNLOAD_DIR_PREFIX.joinpath(title)
        if DOWNLOAD_IMAGES or TTS_EXPORT:
            if download_dir.exists():
                shutil.rmtree(download_dir)
            download_dir.mkdir(parents=True)

        if TTS_EXPORT:
            for card in cards:
                name = card["name"]
                url = card["image"]
                tts_obj = get_tts_dict(name, url)
                new_file_name = f"{name}.json"
                file_path = download_dir.joinpath(new_file_name)
                print(f"Exporting TTS file for {name}.")
                with open(file_path, "w") as f:
                    json.dump(tts_obj, f)
                print(f"TTS file for {name} has been exported.")

        if DOWNLOAD_IMAGES:
            print("Downloading images.")
            for card in cards:
                name = card["name"]
                download_url = card["image"]
                file_name = f"{name}.png"
                download_path = download_dir.joinpath(file_name)

                print(f"Downloading {name}.")
                r = requests.get(download_url, stream=True)
                if r.status_code == 200:
                    img = Image.open(r.raw)
                    img.thumbnail((256, 256))
                    img.save(download_path)
                    print(f"{name} has been downloaded.")
                else:
                    print(f"Failed to download {name}.")


def get_tts_dict(name, url):
    return {
        "SaveName": "",
        "GameMode": "",
        "Date": "",
        "Gravity": 0.5,
        "PlayArea": 0.5,
        "GameType": "",
        "GameComplexity": "",
        "Tags": [],
        "Table": "",
        "Sky": "",
        "Note": "",
        "Rules": "",
        "TabStates": {},
        "ObjectStates": [
            {
                "Name": "CardCustom",
                "Transform": {
                    "posX": -3.16292953,
                    "posY": 1.76476943,
                    "posZ": -3.37939978,
                    "rotX": 1.20715467E-05,
                    "rotY": 179.985962,
                    "rotZ": -7.070623E-07,
                    "scaleX": 1.0,
                    "scaleY": 1.0,
                    "scaleZ": 1.0
                },
                "Nickname": name,
                "Description": "",
                "GMNotes": "",
                "ColorDiffuse": {
                    "r": 0.713235259,
                    "g": 0.713235259,
                    "b": 0.713235259
                },
                "Locked": False,
                "Grid": True,
                "Snap": True,
                "IgnoreFoW": False,
                "MeasureMovement": False,
                "DragSelectable": True,
                "Autoraise": True,
                "Sticky": True,
                "Tooltip": True,
                "GridProjection": False,
                "HideWhenFaceDown": True,
                "Hands": True,
                "CardID": 400,
                "SidewaysCard": False,
                "CustomDeck": {
                    "4": {
                        "FaceURL": url,
                        "BackURL": "http://cloud-3.steamusercontent.com/ugc/1486704590715727248/BB5BB72B1091745CC51B26AFE3108671519FAF9E/",
                        "NumWidth": 1,
                        "NumHeight": 1,
                        "BackIsHidden": True,
                        "UniqueBack": False,
                        "Type": 0
                    }
                },
                "LuaScript": "",
                "LuaScriptState": "",
                "XmlUI": "",
                "GUID": ""
            }
        ],
        "LuaScript": "",
        "LuaScriptState": "",
        "XmlUI": "",
        "VersionNumber": ""
    }


if __name__ == "__main__":
    main()
