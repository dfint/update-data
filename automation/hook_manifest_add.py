import json
from binascii import crc32
from pathlib import Path
from typing import Any, Iterator, NamedTuple

import toml
from natsort import natsorted

base_dir = Path(__file__).parent.parent  # base directory of the repository

hook_v2_json_path = base_dir / "metadata/hook_v2.json"
hook_v3_json_path = base_dir / "metadata/hook_v3.json"
offsets_toml_path = base_dir / "store/offsets"
store_path = base_dir / "store"
libs_path = store_path / "libs"
hook_base_path = libs_path / "hook"
dfhooks_base_path = libs_path / "dfhooks"

DEFAULT_MIRROR = "https://dfint.github.io"

offsets_base_url = "/update-data/store/offsets/"
hook_download_base_url = "/update-data/store/libs/hook/"
dfhooks_download_base_url = "/update-data/store/libs/dfhooks/"
config_base_url = "/update-data/store/"


class ConfigItem(NamedTuple):
    df_checksum: str
    payload_checksum: int
    hook_lib_url: str
    config_url: str
    offsets_url: str
    dfhooks_url: str
    
    def dict_v2(self) -> dict[str, Any]:
        return {
            "df": self.df_checksum,
            "checksum": self.payload_checksum,
            "lib": DEFAULT_MIRROR + self.hook_lib_url,
            "config": DEFAULT_MIRROR + self.config_url,
            "offsets": DEFAULT_MIRROR + self.offsets_url,
            "dfhooks": DEFAULT_MIRROR + self.dfhooks_url,
        }

    def dict_v3(self) -> dict[str, Any]:
        return {
            "df": self.df_checksum,
            "checksum": self.payload_checksum,
            "lib": self.hook_lib_url,
            "config": self.config_url,
            "offsets": self.offsets_url,
            "dfhooks": self.dfhooks_url,
        }


def add_info_to_manifest(manifest_path: str, config_item: dict[str, Any]) -> None:
    hook_manifest = json.loads(manifest_path.read_text())
    hook_manifest.append(config_item)
    manifest_path.write_text(json.dumps(hook_manifest, indent=2))


def add_maifest_entry(hook_path: str, config_file_name: str, offsets_file_name: str, dfhooks_path: str) -> None:
    res_hook = (hook_base_path / hook_path).read_bytes()
    res_config = (store_path / config_file_name).read_bytes()
    res_offsets = (offsets_toml_path / offsets_file_name).read_bytes()
    res_dfhooks = (dfhooks_base_path / dfhooks_path).read_bytes()

    offsets_data = toml.loads(res_offsets.decode(encoding="utf-8"))
    df_checksum = offsets_data["metadata"]["checksum"]
    payload_checksum = crc32(res_hook + res_config + res_offsets + res_dfhooks)

    config_item = ConfigItem(
        df_checksum,
        payload_checksum,
        hook_download_base_url + hook_path,
        config_base_url + config_file_name,
        offsets_base_url + offsets_file_name,
        dfhooks_download_base_url + dfhooks_path,
    )

    add_info_to_manifest(
        hook_v2_json_path,
        config_item.dict_v2(),
    )

    add_info_to_manifest(
        hook_v3_json_path,
        config_item.dict_v3(),
    )


def get_file_name(url: str) -> str:
    return url.rpartition("/")[2]


def get_existing_df_checksums() -> set[int]:
    json_data = json.loads(hook_v2_json_path.read_text(encoding="utf-8"))
    return {item["df"] for item in json_data}


def get_metadata_entries_from_files() -> Iterator[tuple[int, str]]:
    for file in offsets_toml_path.glob("*.toml"):
        file_data = toml.load(file)
        yield file_data["metadata"]["checksum"], file.name


def main() -> None:
    existing_checksums = get_existing_df_checksums()
    checksum_to_file_map = dict(get_metadata_entries_from_files())
    missing_checksums = set(checksum_to_file_map) - existing_checksums
    missing_files = natsorted(map(checksum_to_file_map.get, missing_checksums))

    print("New entries:", missing_files)
    config = toml.load(base_dir / "automation/hook_manifest_add.toml")

    for file_name in missing_files:
        operating_system = Path(file_name).stem.rpartition("_")[2]
        lib_variant = config[operating_system]
        add_maifest_entry(
            lib_variant["lib"],
            "config.toml",
            file_name,
            lib_variant["dfhooks"]
        )


if __name__ == "__main__":
    main()
