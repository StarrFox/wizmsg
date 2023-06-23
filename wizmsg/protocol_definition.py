from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Union
from xml.etree import ElementTree

from loguru import logger


@dataclass
class MessageDefinitionParameter:
    name: str
    type: str


@dataclass
class MessageDefinition:
    order: int
    name: str
    description: str
    parameters: dict[str, MessageDefinitionParameter]


def _get_messages_from_xml(
    root_element: ElementTree.Element,
) -> dict[Union[int, str], MessageDefinition]:
    messages = {}
    for message_element in root_element:
        if message_element.tag == "_ProtocolInfo":
            continue

        record = message_element[0]

        def _get_record_value(
            sub_element_name, *, allow_missing: bool = False, as_int: bool = False
        ) -> int | str | None:
            element = record.find(sub_element_name)

            if element is None:
                if allow_missing:
                    return None

                raise ValueError(f"{sub_element_name} missing from message entry")

            if as_int:
                # TODO: what should happen here if element.text is None
                return int(element.text)

            return element.text

        # this MsgName is actually incorrect; doesn't match the tag name which is used for sorting
        # message_name = _get_record_value("_MsgName")
        message_name = message_element.tag

        # ignore duplicates
        if messages.get(message_name):
            logger.debug(f"ignoring duplicate message {message_name}")
            continue

        message_description = _get_record_value("_MsgDescription")
        message_order = _get_record_value("_MsgOrder", allow_missing=True, as_int=True)

        parameters = {}
        for parameter_element in record:
            parameter_name = parameter_element.tag
            if parameter_name.startswith("_"):
                continue

            # TODO: sometimes this isn't provided, mainly to troll
            try:
                parameter_type = parameter_element.attrib["TYPE"]
            except KeyError:
                if parameter_name == "GlobalID":
                    logger.debug(
                        f"Missing TYPE for param {parameter_name} on message {message_name}"
                    )
                    parameter_type = "GID"

                else:
                    raise RuntimeError(
                        f"Unhandled TYPE for param {parameter_name} of message {message_name}"
                    )

            parameters[parameter_name] = MessageDefinitionParameter(
                parameter_name, parameter_type
            )

        messages[message_name] = MessageDefinition(
            message_order, message_name, message_description, parameters
        )

    message_defs = list(messages.values())

    # order: message
    sorted_messages = {}

    for message in message_defs:
        if message.order is not None:
            in_message_order = True
            break
    else:
        in_message_order = False

    if in_message_order:
        # if message.order use that
        message_defs = sorted(message_defs, key=lambda m: m.order)
    else:
        # if no message.order use name to sort
        message_defs = sorted(message_defs, key=lambda m: m.name)

    # message order starts at 1
    for idx, message in enumerate(message_defs, start=1):
        # sanity check
        if message.order is not None and message.order != idx:
            raise RuntimeError(
                f"index and message order mismatch {message.order=} {idx=}"
            )

        message.order = idx
        sorted_messages[idx] = message

    sorted_messages.update(messages)

    # TODO: find out why messages are sorted wrong sometimes i.e. 182 in GameMessages
    return sorted_messages


@dataclass
class ProtocolDefinition:
    service_id: int
    type: str
    version: int
    description: str
    # message id: MessageDefinition
    messages: dict[int, MessageDefinition]

    @classmethod
    def from_string(cls, protocol_string: str | StringIO):
        if isinstance(protocol_string, str):
            protocol_string = StringIO(protocol_string)

        return cls.from_xml_file(protocol_string)

    @classmethod
    def from_xml_file(cls, file_path: str | Path | StringIO):
        if isinstance(file_path, str):
            file_path = Path(file_path)

        tree = ElementTree.parse(file_path)
        root_element = tree.getroot()

        protocol_info = root_element.find("_ProtocolInfo")

        if protocol_info is None:
            raise ValueError(f"Invalid protocol definition in xml file {file_path}")

        protocol_info_record = protocol_info[0]

        def _get_record_value(name) -> str:
            element = protocol_info_record.find(name)

            if element is None:
                raise ValueError(f"{name} missing from protocol info entry")

            return element.text

        service_id = int(_get_record_value("ServiceID"))
        protocol_type = _get_record_value("ProtocolType")
        protocol_version = int(_get_record_value("ProtocolVersion"))
        protocol_description = _get_record_value("ProtocolDescription")

        messages = _get_messages_from_xml(root_element)

        return cls(
            service_id, protocol_type, protocol_version, protocol_description, messages
        )


if __name__ == "__main__":
    definition = ProtocolDefinition.from_xml_file(
        "/home/starr/PycharmProjects/wizmsg/message_files/GameMessages.xml"
    )

    for order, message in definition.messages.items():
        print(f"{order}: {message.name}")
