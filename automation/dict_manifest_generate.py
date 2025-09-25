import binascii
import json
from pathlib import Path
from pydantic import BaseModel, RootModel
import strictyaml

from utils import get_from_url

current_directory = Path(__file__).parent
config_path = current_directory / "dict_manifest_config.yaml"
repo_root = current_directory.parent
org = "dfint"
current_repo = "update-data"
DEFAULT_MIRROR = "https://dfint.github.io"


class FileInfo(BaseModel):
    name: str
    repo: str
    branch: str = "main"
    path: str


class DictManifestConfigEntry(BaseModel):
    language: str
    code: str | None = None
    files: list[FileInfo]
    checksum: int | None = None


class Config(RootModel):
    root: list[DictManifestConfigEntry]


def load_config() -> Config:
    yaml = strictyaml.load(config_path.read_text())
    return Config.model_validate(yaml.data)


def get_file_data(file: FileInfo) -> bytes:
    if file.repo == current_repo:
        return (repo_root / file.path).read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{org}/{file.repo}/refs/heads/{file.branch}/{file.path}"
        return get_from_url(url)


def calculate_checksums(config: Config) -> None:
    for entry in config.root:
        data = b""
        for file in entry.files:
            file_data = get_file_data(file)
            data += file_data

        entry.checksum = binascii.crc32(data)


def write_dict_manifest_v1(config: Config) -> None:
    manifest_data = []
    for entry in config.root:
        language_info = {
            "language": entry.language,
        }

        if entry.code:
            language_info["code"] = entry.code

        for file in entry.files:
            language_info[file.name] = f"{DEFAULT_MIRROR}/{file.repo}/{file.path}"

        language_info["checksum"] = entry.checksum
        manifest_data.append(language_info)

    dict_json_path = repo_root / "metadata/dict.json"
    dict_json_path.write_text(
        json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def write_dict_manifest_v3(config: Config) -> None:
    manifest_data = []
    for entry in config.root:
        language_info = {
            "language": entry.language,
        }

        if entry.code:
            language_info["code"] = entry.code

        for file in entry.files:
            language_info[file.name] = f"/{file.repo}/{file.path}"

        language_info["checksum"] = entry.checksum
        manifest_data.append(language_info)

    dict_json_path = repo_root / "metadata/dict_v3.json"
    dict_json_path.write_text(
        json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> None:
    print("Loading config...")
    config = load_config()
    print("Calculating checksums...")
    calculate_checksums(config)
    print("Writing dict manifest v1...")
    write_dict_manifest_v1(config)
    print("Writing dict manifest v3...")
    write_dict_manifest_v3(config)
    print("Done.")


if __name__ == "__main__":
    main()
