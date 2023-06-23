from wizmsg import ProtocolDefinition
from wizmsg.network import MessageData, Processor

TEST_PROTOCOL = """<?xml version="1.0" ?>
<TestProtocol>
  <_ProtocolInfo>
    <RECORD>
      <ServiceID TYPE="UBYT">1</ServiceID>
      <ProtocolType TYPE="STR">TEST</ProtocolType>
      <ProtocolVersion TYPE="INT">1</ProtocolVersion>
      <ProtocolDescription TYPE="STR">Testing wizmsg</ProtocolDescription>
    </RECORD>
  </_ProtocolInfo>

  <MSG_PERSON>
    <RECORD>
      <_MsgName TYPE="STR" NOXFER="TRUE">MSG_PERSON</_MsgName>
      <_MsgDescription TYPE="STR" NOXFER="TRUE">:dead:</_MsgDescription>
      <_MsgHandler TYPE="STR" NOXFER="TRUE">crate::person_handler</_MsgHandler>
      <Name TYPE="STR"></Name>
      <Age TYPE="UBYT"></Age>
    </RECORD>
  </MSG_PERSON>
</TestProtocol>
"""


def test_load_protocol_from_string():
    protocol = ProtocolDefinition.from_string(TEST_PROTOCOL)

    assert protocol.service_id == 1
    assert protocol.type == "TEST"
    assert protocol.description == "Testing wizmsg"

    assert protocol.messages.get(1) is not None

    test_message = protocol.messages[1]

    assert test_message.description == ":dead:"
    assert test_message.name == "MSG_PERSON"

    assert test_message.parameters.get("Name") is not None
    assert test_message.parameters.get("Age") is not None

    test_message_number_parameter = test_message.parameters["Age"]

    assert test_message_number_parameter.name == "Age"
    assert test_message_number_parameter.type == "UBYT"


def test_processing():
    processor = Processor()
    processor.load_protocol_from_string(TEST_PROTOCOL)

    message = MessageData(1, 1, "MSG_PERSON", {"Name": "Edgar Allan Poe", "Age": 40})

    raw = processor.prepare_frame(message)
    assert raw == b'\r\xf0\x1b\x00\x00\x00\x00\x00\x01\x01\x12\x00\x0f\x00Edgar Allan Poe(\x00'

    message2 = processor.process_frame(raw)
    assert message == message2
