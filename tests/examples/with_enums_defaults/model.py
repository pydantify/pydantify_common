from __future__ import annotations

from enum import Enum
from typing import Annotated, ClassVar

from pydantic import AliasChoices, ConfigDict, Field, RootModel

from pydantify_common.model import XMLPydantifyModel

NS = "http://example.com/ns/yang/demo"


class StateEnum(Enum):
    up = "up"
    down = "down"


class StateType(RootModel[StateEnum]):
    root: StateEnum


class StateLeaf(RootModel[StateType]):
    root: StateType


class SessionListEntry(XMLPydantifyModel):
    """A single monitor session, mirroring YANG-generated leaf wrappers."""

    model_config = ConfigDict(populate_by_name=True)
    namespace: ClassVar[str] = NS
    prefix: ClassVar[str] = "demo"

    id: Annotated[
        int,
        Field(
            serialization_alias="demo:id",
            validation_alias=AliasChoices("demo:id", "id"),
        ),
    ]
    config_state: Annotated[
        StateLeaf | None,
        Field(
            serialization_alias="demo:configState",
            validation_alias=AliasChoices(
                "demo:configState", "config_state", "configState"
            ),
        ),
    ] = None
    allow_sharing: Annotated[
        bool | None,
        Field(
            serialization_alias="demo:allowSharing",
            validation_alias=AliasChoices(
                "demo:allowSharing", "allow_sharing", "allowSharing"
            ),
        ),
    ] = False
    mtu: Annotated[
        int | None,
        Field(
            serialization_alias="demo:mtu",
            validation_alias=AliasChoices("demo:mtu", "mtu"),
        ),
    ] = 10240
    description: Annotated[
        str | None,
        Field(
            serialization_alias="demo:description",
            validation_alias=AliasChoices("demo:description", "description"),
        ),
    ] = None


class SessionsContainer(XMLPydantifyModel):
    model_config = ConfigDict(populate_by_name=True)
    namespace: ClassVar[str] = NS
    prefix: ClassVar[str] = "demo"

    session_list: Annotated[
        list[SessionListEntry],
        Field(
            default_factory=list,
            serialization_alias="demo:Session-list",
            validation_alias=AliasChoices("demo:Session-list", "session_list"),
        ),
    ]


class Model(XMLPydantifyModel):
    model_config = ConfigDict(populate_by_name=True)
    namespace: ClassVar[str] = NS
    prefix: ClassVar[str] = "demo"

    sessions: Annotated[
        SessionsContainer,
        Field(
            serialization_alias="demo:sessions",
            validation_alias=AliasChoices("demo:sessions", "sessions"),
        ),
    ]
