"""Validate track YAML against the current mediascan model."""

from dataclasses import fields
from datetime import datetime
from math import isfinite
from typing import TypeGuard, cast

import yaml

from mediascan.types.mediafile.mediafile_acoustid_data import (
    MediaFileAcoustIDData,
    MediaFileAcoustIDRecording,
    MediaFileAcoustIDResult,
)
from mediascan.types.mediafile.mediafile_data import MediaFileData
from mediascan.types.mediafile.mediafile_fpcalc_data import MediaFileFpCalcData
from mediascan.types.track.streaming.streaming_data import StreamingData
from mediascan.types.track.track_data import TrackData
from mediascan.types.track.track_id_data import TrackIdData
from mediascan.types.track.track_yaml_file import TrackYamlFile


def camel_case(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.title() for part in rest)


CORE_FIELDS = {field.name for field in fields(TrackData)}
ID_FIELDS = {camel_case(field.name) for field in fields(TrackIdData)}
STREAMING_FIELDS = {camel_case(field.name) for field in fields(StreamingData)}
MEDIAFILE_FIELDS = {camel_case(field.name) for field in fields(MediaFileData)}
FPCALC_FIELDS = {camel_case(field.name) for field in fields(MediaFileFpCalcData)}
ACOUSTID_FIELDS = {camel_case(field.name) for field in fields(MediaFileAcoustIDData)}
RESULT_FIELDS = {camel_case(field.name) for field in fields(MediaFileAcoustIDResult)}
RECORDING_FIELDS = {camel_case(field.name) for field in fields(MediaFileAcoustIDRecording)}


class _YamlLoader(yaml.SafeLoader):
    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[object, object]:
        mapping = cast(dict[object, object], super().construct_mapping(node, deep=deep))
        keys: set[str] = set()
        for key_node, _ in node.value:
            key: object = self.construct_object(key_node, deep=deep)
            if isinstance(key, str):
                if key in keys:
                    raise ValueError(f"Duplicate YAML field '{key}'")
                keys.add(key)
        return mapping


def is_mapping(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in cast(dict[object, object], value))


def is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def load_document(content: str) -> dict[str, object]:
    document: object = yaml.load(content, Loader=_YamlLoader)
    if not is_mapping(document):
        raise ValueError("Expected a track YAML mapping")
    return document


def is_number(value: object) -> bool:
    return type(value) is int or (type(value) is float and isfinite(value))


def validate_acoustid_data(value: object, field_path: str) -> None:
    if not is_mapping(value) or value.keys() != ACOUSTID_FIELDS:
        raise ValueError(f"{field_path} must contain exactly results and status")
    if not isinstance(value["status"], str):
        raise ValueError(f"{field_path}.status must be a string")
    results = value["results"]
    if not is_list(results):
        raise ValueError(f"{field_path}.results must be a list")
    for index, result in enumerate(results):
        result_path = f"{field_path}.results[{index}]"
        if not is_mapping(result) or result.keys() != RESULT_FIELDS:
            raise ValueError(f"{result_path} must contain exactly id, recordings, and score")
        if not isinstance(result["id"], str):
            raise ValueError(f"{result_path}.id must be a string")
        if not is_number(result["score"]):
            raise ValueError(f"{result_path}.score must be a number")
        recordings = result["recordings"]
        if not is_list(recordings):
            raise ValueError(f"{result_path}.recordings must be a list")
        for recording_index, recording in enumerate(recordings):
            recording_path = f"{result_path}.recordings[{recording_index}]"
            if not is_mapping(recording) or recording.keys() - RECORDING_FIELDS:
                raise ValueError(f"{recording_path} must contain only supported recording fields")
            if not isinstance(recording.get("id"), str):
                raise ValueError(f"{recording_path}.id must be a string")
            for key, item in recording.items():
                if item is None and key != "id":
                    continue
                if key == "length":
                    valid = type(item) is int
                elif key == "video":
                    valid = type(item) is bool
                elif key == "isrcs":
                    valid = is_list(item) and all(isinstance(isrc, str) for isrc in item)
                else:
                    valid = isinstance(item, str)
                if not valid:
                    raise ValueError(f"{recording_path}.{key} has an invalid type")


def validate_track_yaml_content(content: str) -> dict[str, object]:
    """Enforce the camelCase mediascan schema before saving or skipping."""
    document = load_document(content)
    if document.keys() - {"trackData", "trackIdData", "mediaFileData"}:
        raise ValueError("Unexpected track YAML fields")
    core = document.get("trackData")
    if not is_mapping(core) or core.keys() != CORE_FIELDS:
        raise ValueError("trackData must contain exactly the six core metadata fields")
    for key, value in core.items():
        if key == "year":
            if type(value) is not int:
                raise ValueError("trackData.year must be an integer")
        elif not isinstance(value, str) or not value.strip():
            raise ValueError(f"trackData.{key} must be a non-empty string")
    identifiers = document.get("trackIdData")
    if identifiers is not None:
        if not is_mapping(identifiers) or identifiers.keys() - ID_FIELDS:
            raise ValueError("trackIdData must contain only supported identifier fields")
        streaming_data = identifiers.get("streamingData")
        if streaming_data is not None:
            if not is_list(streaming_data):
                raise ValueError("trackIdData.streamingData must be a list")
            for streaming_index, streaming in enumerate(streaming_data):
                field_path = f"trackIdData.streamingData[{streaming_index}]"
                if not is_mapping(streaming) or streaming.keys() - STREAMING_FIELDS:
                    raise ValueError(f"{field_path} must contain only supported streaming fields")
                for required in ("streamingService", "trackUrl", "trackId"):
                    value = streaming.get(required)
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError(f"{field_path}.{required} must be a non-empty string")
                if "apiData" not in streaming:
                    raise ValueError(f"{field_path}.apiData is required")
                isrc = streaming.get("isrc")
                if isrc is not None and not isinstance(isrc, str):
                    raise ValueError(f"{field_path}.isrc must be a string or null")
    mediafiles = document.get("mediaFileData")
    if mediafiles is not None:
        if not is_list(mediafiles):
            raise ValueError("mediaFileData must be a list")
        for index, mediafile in enumerate(mediafiles):
            field_path = f"mediaFileData[{index}]"
            if not is_mapping(mediafile) or mediafile.keys() - MEDIAFILE_FIELDS:
                raise ValueError(f"{field_path} must contain only supported media-file fields")
            for key, value in mediafile.items():
                value_path = f"{field_path}.{key}"
                if key == "fpcalcData":
                    if value is not None:
                        if not is_mapping(value) or value.keys() - FPCALC_FIELDS:
                            raise ValueError(f"{value_path} must be a fingerprint mapping or null")
                        duration = value.get("duration")
                        fingerprint = value.get("fingerprint")
                        if duration is not None and not is_number(duration):
                            raise ValueError(f"{value_path}.duration must be a number or null")
                        if fingerprint is not None and not isinstance(fingerprint, str):
                            raise ValueError(f"{value_path}.fingerprint must be a string or null")
                    continue
                if key == "acoustidData":
                    if value is not None:
                        validate_acoustid_data(value, value_path)
                    continue
                if key == "duration":
                    if value is not None and not is_number(value):
                        raise ValueError(f"{value_path} must be a number or null")
                    continue
                if key == "modTime":
                    if value is not None:
                        if isinstance(value, str):
                            try:
                                datetime.fromisoformat(value.replace("Z", "+00:00"))
                            except ValueError as error:
                                raise ValueError(f"{value_path} must be a timestamp or null") from error
                            if "T" not in value and " " not in value:
                                raise ValueError(f"{value_path} must be a timestamp or null")
                        elif not isinstance(value, datetime):
                            raise ValueError(f"{value_path} must be a timestamp or null")
                    continue
                expected_type = int if key in {"size", "year"} else str
                if value is not None and (
                    not isinstance(value, expected_type) or (expected_type is int and isinstance(value, bool))
                ):
                    raise ValueError(f"{value_path} must be a {expected_type.__name__} or null")
    loaded: object = getattr(TrackYamlFile, "from_yaml")(content)
    if not isinstance(loaded, TrackYamlFile):
        raise ValueError("Expected a TrackYamlFile")
    return document
