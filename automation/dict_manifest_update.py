import binascii
import json
from pathlib import Path

from utils import get_from_url

repository_root = Path(__file__).parent.parent
DEFAULT_MIRROR = "https://dfint.github.io"


def update_v1_dict_manifest():
    print("Updating checksums for dict manifest v1:")
    dict_json_path = repository_root / "metadata/dict.json"
    manifest = json.loads(dict_json_path.read_text(encoding="utf-8"))

    for i, item in enumerate(manifest):
        try:
            data = (
                get_from_url(item["csv"])
                + get_from_url(item["font"])
                + get_from_url(item["encoding"])
            )
            checksum = binascii.crc32(data)
        except Exception as ex:
            print(f"Failed on recalculation {item['language']}:\n", ex)
        else:
            if item.get("checksum") != checksum:
                manifest[i]["checksum"] = checksum

    dict_json_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def update_v3_dict_manifest():
    print("Updating checksums for dict manifest v3:")
    dict_json_path = repository_root / "metadata/dict_v3.json"
    manifest = json.loads(dict_json_path.read_text(encoding="utf-8"))

    for i, item in enumerate(manifest):
        try:
            data = (
                get_from_url(DEFAULT_MIRROR + item["csv"])
                + get_from_url(DEFAULT_MIRROR + item["font"])
                + get_from_url(DEFAULT_MIRROR + item["encoding"])
            )
            checksum = binascii.crc32(data)
        except Exception as ex:
            print(f"Failed on recalculation {item['language']}:\n", ex)
        else:
            if item.get("checksum") != checksum:
                manifest[i]["checksum"] = checksum

    dict_json_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    update_v1_dict_manifest()
    update_v3_dict_manifest()


if __name__ == "__main__":
    main()
