import json
import hashlib

from datetime import datetime
from pathlib import Path
from sqlmodel import Session, delete, select
from model import Attraction, DataVersion


BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR / "data" / "taipei-attractions.json"

# Helper function for parsing "imgurls"
def _parse_images(img_data, img_host):

    img_list = []
    for pic in img_data.split("/imgs/"):
        if pic != "":
            img_list.append(f"{img_host}/imgs/{pic}")
    return img_list


# Helper function for parsing "MRT"
def _parse_mrts(mrt_data):

    mrt_list = []
    if not mrt_data:
        return mrt_list
    for mrt in mrt_data.split("、"):
        if mrt != "":
            mrt_list.append(mrt)
    return mrt_list


# Load Taipei attractions data from JSON file
def load_attractions_if_updated(session: Session):
    
    current_hash = hashlib.md5(JSON_PATH.read_bytes()).hexdigest()

    stat = select(DataVersion).where(DataVersion.filename == JSON_PATH.name)
    version = session.exec(stat).first()

    if version and version.filehash == current_hash:
        print(f"{JSON_PATH.name} is up to date. Skipping reload.")
        return
    
    print(f"{JSON_PATH.name} has been updated. Reloading attraction data...")


    with JSON_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    img_host = data["img_host"]

    # Delete all data in Attractions table and reload the latest data
    session.exec(delete(Attraction))

    for item in data["list"]:
        attraction = Attraction(
            attr_id = item["_id"],
            name = item["name"],
            category = item["CAT"],
            address = item["address"],
            mrt = _parse_mrts(item["MRT"]),
            description = item["description"],
            transport = item["direction"],
            lat = float(item["latitude"]),
            lng = float(item["longitude"]),
            images = _parse_images(item["imgurls"], img_host)
        )
        session.add(attraction)

 
    # Update file hash
    if version:
        version.filehash = current_hash
        session.add(version)
    else:
        session.add(DataVersion(filename=JSON_PATH.name, filehash=current_hash))
 
    session.commit()
    
    print(f"Loaded {len(data['list'])} attraction records.")
        