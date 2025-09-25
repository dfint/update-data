import binascii
from pathlib import Path
from pydantic import BaseModel, RootModel
import strictyaml

from utils import get_from_url

current_directory = Path(__file__).parent
config_path = current_directory / "dict_manifest_config.yaml"
repo_root = current_directory.parent
org = "dfint"
current_repo = "update-data"


class FileInfo(BaseModel):
    name: str
    repo: str
    branch: str = "main"
    path: str


class DictManifestConfigEntry(BaseModel):
    language: str
    code: str
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
        data = b''
        for file in entry.files:
            file_data = get_file_data(file)
            data += file_data

        entry.checksum = binascii.crc32(data)


def main() -> None:
    config = load_config()
    calculate_checksums(config)
    for row in config.root:
        print(row.language, row.code, row.checksum)


if __name__ == "__main__":
    main()
