# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "toml",
#     "natsort",
# ]
# ///
import json
from binascii import crc32
from pathlib import Path
from typing import Any, Iterator, NamedTuple

import toml
from natsort import natsorted

from utils import get_from_url

base_dir = Path(__file__).parent.parent  # base directory of the repository

hook_json_path = base_dir / "metadata/hook_v2.json"
offsets_toml_path = base_dir / "store/offsets"
config_path = base_dir / "store"

offsets_base_url = "https://raw.githubusercontent.com/dfint/update-data/main/store/offsets/"
lib_download_base_url = "https://github.com/dfint/df-steam-hook-rs/releases/download/"
dfhooks_download_base_url = "https://github.com/DFHack/dfhooks/releases/download/"
config_base_url = "https://raw.githubusercontent.com/dfint/update-data/main/store/"


class ConfigItem(NamedTuple):
    df_checksum: str
    payload_checksum: int
    hook_lib_url: str
    config_url: str
    offsets_url: str
    dfhooks_url: str
    
    def dict(self) -> dict[str, Any]:
        return {
            "df": self.df_checksum,
            "checksum": self.payload_checksum,
            "lib": self.hook_lib_url,
            "config": self.config_url,
            "offsets": self.offsets_url,
            "dfhooks": self.dfhooks_url,
        }


def add_info_to_manifest(manifest_path: str, config_item: ConfigItem) -> None:
    hook_manifest = json.loads(manifest_path.read_text())
    hook_manifest.append(config_item.dict())
    manifest_path.write_text(json.dumps(hook_manifest, indent=2))


def main(hook_lib_url: str, config_file_name: str, offsets_file_name: str, dfhooks_url: str) -> None:
    res_hook = get_from_url(hook_lib_url)
    res_config = (config_path / config_file_name).read_bytes()
    res_offsets = (offsets_toml_path / offsets_file_name).read_bytes()
    res_dfhooks = get_from_url(dfhooks_url)

    offsets_data = toml.loads(res_offsets.decode(encoding="utf-8"))
    df_checksum = offsets_data["metadata"]["checksum"]
    payload_checksum = crc32(res_hook + res_config + res_offsets + res_dfhooks)

    add_info_to_manifest(
        hook_json_path,
        ConfigItem(
            df_checksum,
            payload_checksum,
            hook_lib_url,
            config_base_url + config_file_name,
            offsets_base_url + offsets_file_name,
            dfhooks_url,
        )
    )


def get_file_name(url: str) -> str:
    return url.rpartition("/")[2]


class MetadataEntryKey(NamedTuple):
    file_name: str
    df_checksum: int


def get_existing_metadata_entries() -> set[MetadataEntryKey]:
    json_data = json.loads(hook_json_path.read_text(encoding="utf-8"))
    return {MetadataEntryKey(get_file_name(item["offsets"]), item["df"]) for item in json_data}


def get_metadata_entries_from_files() -> Iterator[MetadataEntryKey]:
    for file in offsets_toml_path.glob("*.toml"):
        file_data = toml.load(file)
        yield MetadataEntryKey(file.name, file_data["metadata"]["checksum"])


def autoadd() -> None:
    json_data = hook_json_path.read_text(encoding="utf-8")
    existing = get_existing_metadata_entries()
    in_files = set(get_metadata_entries_from_files())
    missing_entries = natsorted(in_files - existing)
    
    print("New entries:", missing_entries)
    config = toml.load(base_dir / "automation/hook_manifest_add.toml")

    for file_name, _ in missing_entries:
        operating_system = Path(file_name).stem.rpartition("_")[2]
        lib_variant = config[operating_system]
        main(
            lib_download_base_url + lib_variant["lib"],
            "config.toml",
            file_name,
            dfhooks_download_base_url + lib_variant["dfhooks"]
        )


if __name__ == "__main__":
    autoadd()
