from dataclasses import dataclass
from dataclass_wizard.v0 import YAMLWizard

from .media_file_data import MediaFileData


@dataclass
class MediaFilesYamlFile(YAMLWizard):
    """
    MediaFilesYamlFile - data model for mediascan_files.yml file output by mediascan cmd/scanfiles

    """

    files: list[MediaFileData]
