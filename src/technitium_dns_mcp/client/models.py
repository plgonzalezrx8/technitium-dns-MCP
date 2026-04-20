from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

type EndpointClassification = Literal[
    "readonly",
    "mutation",
    "destructive",
    "admin",
]
type ConfirmationMode = Literal["none", "confirm", "destructive", "critical"]
type ApiScalar = str | int | float | bool
type RequestParam = ApiScalar | None
type RequestParams = Mapping[str, RequestParam]
type UploadFile = tuple[str, bytes, str]
type UploadFiles = Mapping[str, UploadFile]


@dataclass(frozen=True, slots=True)
class ConfirmationPolicy:
    mode: ConfirmationMode = "none"
    acknowledgement: str | None = None

    @property
    def requires_confirmation(self) -> bool:
        return self.mode != "none"


@dataclass(frozen=True, slots=True)
class EndpointMetadata:
    tool_name: str
    api_path: str
    family: str
    classification: EndpointClassification
    required_params: tuple[str, ...] = ()
    optional_params: tuple[str, ...] = ()
    confirmation_policy: ConfirmationPolicy = field(default_factory=ConfirmationPolicy)


@dataclass(frozen=True, slots=True)
class DownloadResponse:
    content: bytes
    content_type: str | None = None
    filename: str | None = None
