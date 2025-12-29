import os
import json
import requests
import base64
import gzip
import io

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, dest_path):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {dest_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    ensure_dir("mapfiles")
    ensure_dir("asset/text")
    ensure_dir("audfiles")
    ensure_dir("midifiles")
    ensure_dir("covfiles")
    ensure_dir("iconfiles")
    ensure_dir("eventbanner")

    with open('b64.txt', 'r') as f:
        b64_data = f.read()

    binary_data = base64.b64decode(b64_data)

    with gzip.open(io.BytesIO(binary_data), 'rt', encoding='utf-8') as gz:
        json_data = gz.read()

    json_data = json.loads(json_data)

    tracks = json_data['tracks']
    print("downloading audios and thumbnails...")

    for track in tracks:
        for key in ['audioFileName', 'audioPreviewFileName']:
            file_name = track.get(key, "")
            if file_name:
                dest_path = os.path.join("audfiles", file_name)
                if not os.path.exists(dest_path):
                    url = f"https://d1h9358u1aon5f.cloudfront.net/audfiles/{file_name}"
                    download_file(url, dest_path)

        for key in ['midiFileName']:
            file_name = track.get(key, "")
            if file_name:
                if file_name != "NULL":
                    dest_path = os.path.join("midifiles", file_name)
                    if not os.path.exists(dest_path):
                        url = f"https://d1h9358u1aon5f.cloudfront.net/midifiles/{file_name}"
                        download_file(url, dest_path)
            

        for key in ['coverFileName', 'blurredCoverFileName', 'thumbnailFileName']:
            file_name = track.get(key, "")
            if file_name:
                dest_path = os.path.join("covfiles", file_name)
                if not os.path.exists(dest_path):
                    url = f"https://d1h9358u1aon5f.cloudfront.net/covfiles/{file_name}"
                    download_file(url, dest_path)

    maps = json_data['maps']
    print("downloading maps...")

    for map in maps:
        for key in ["mapFileName"]:
            file_name = map.get(key, "")
            if file_name:
                dest_path = os.path.join("mapfiles", file_name)
                if not os.path.exists(dest_path):
                    url = f"https://d1h9358u1aon5f.cloudfront.net/mapfiles/{file_name}"
                    download_file(url, dest_path)

    event_banners = json_data['eventBanners']
    print("downloading event banners...")
    for banner in event_banners:
        for key in ["fileName"]:
            file_name = banner.get(key, "")
            if file_name:
                dest_path = os.path.join("eventbanner", file_name)
                if not os.path.exists(dest_path):
                    url = f"https://d1h9358u1aon5f.cloudfront.net/eventbanner/{file_name}"
                    download_file(url, dest_path)

    pack_icon_atlas = json_data['packIconAtlasFilename']
    localization_entry = json_data['localizationEntryFilename']
    print("Downloading misc...")

    if pack_icon_atlas:
        dest_path = os.path.join("iconfiles", pack_icon_atlas)
        if not os.path.exists(dest_path):
            url = f"https://d1h9358u1aon5f.cloudfront.net/iconfiles/{pack_icon_atlas}"
            download_file(url, dest_path)

    if localization_entry:
        dest_path = os.path.join("asset/text", localization_entry)
        if not os.path.exists(dest_path):
            url = f"https://d1h9358u1aon5f.cloudfront.net/asset/text/{localization_entry}"
            download_file(url, dest_path)

if __name__ == "__main__":
    main()