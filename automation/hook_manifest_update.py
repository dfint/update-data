import binascii
import json
from pathlib import Path

from utils import get_from_url

repo_root = Path(__file__).parent.parent
DEFAULT_MIRROR = "https://dfint.github.io"


def recalculate_v2_manifest():
    print("Recalculating checksums for manifest v2:")
    path = repo_root / "metadata/hook_v2.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))

    for item in manifest:
        print(f"Recalculating checksum for {item["df"]=}...")
        try:
            data = (
                get_from_url(item["lib"])
                + get_from_url(item["config"])
                + get_from_url(item["offsets"])
                + get_from_url(item["dfhooks"])
            )
            checksum = binascii.crc32(data)
            item["checksum"] = checksum
        except Exception:
            print(f"Failed on recalculation {item["df"]=}")
            raise

    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def recalculate_v3_manifest():
    print("Recalculating checksums for manifest v3:")
    path = repo_root / "metadata/hook_v3.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))

    for item in manifest:
        print(f"Recalculating checksum for {item["df"]=}...")
        try:
            data = (
                get_from_url(DEFAULT_MIRROR + item["lib"])
                + get_from_url(DEFAULT_MIRROR + item["config"])
                + get_from_url(DEFAULT_MIRROR + item["offsets"])
                + get_from_url(DEFAULT_MIRROR + item["dfhooks"])
            )
            checksum = binascii.crc32(data)
            item["checksum"] = checksum
        except Exception:
            print(f"Failed on recalculation {item["df"]=}")
            raise

    path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    recalculate_v2_manifest()
    recalculate_v3_manifest()


if __name__ == "__main__":
    main()
