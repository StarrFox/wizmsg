from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


@dataclass
class MessageParameter:
    name: str
    type: str


@dataclass
class Message:
    name: str
    description: str
    # param name: MessageParameter
    parameters: dict[str, MessageParameter]


def _get_messages_from_xml(root_element: ElementTree.Element) -> dict[str, Message]:
    messages = {}
    for message_element in root_element:
        if message_element.tag == "_ProtocolInfo":
            continue

        record = message_element[0]

        def _get_record_value(sub_element_name) -> str:
            element = record.find(sub_element_name)

            if element is None:
                raise ValueError(f"{sub_element_name} missing from message entry")

            return element.text

        message_name = _get_record_value("_MsgName")
        message_description = _get_record_value("_MsgDescription")

        parameters = {}
        for parameter_element in record:
            parameter_name = parameter_element.tag
            if parameter_name.startswith("_"):
                continue

            parameter_type = parameter_element.attrib["TYPE"]

            parameters[parameter_name] = MessageParameter(parameter_name, parameter_type)

        messages[message_name] = Message(message_name, message_description, parameters)

    return messages


@dataclass
class Protocol:
    service_id: int
    type: str
    version: int
    description: str
    # message name: Message
    messages: dict[str, Message]

    @classmethod
    def from_xml_file(cls, file_path: str | Path):
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

        return cls(service_id, protocol_type, protocol_version, protocol_description, messages)
