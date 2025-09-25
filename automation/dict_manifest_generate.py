from pathlib import Path
from pydantic import BaseModel, RootModel
import strictyaml

current_directory = Path(__file__).parent
config_path = current_directory / "dict_manifest_config.yaml"
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


class Config(RootModel):
    root: list[DictManifestConfigEntry]


def load_config() -> Config:
    yaml = strictyaml.load(config_path.read_text())
    return Config.model_validate(yaml.data)


if __name__ == "__main__":
    print(load_config())
