from wizmsg import ProtocolDefinition


string_protocol = """
<FakeMessages>
    <_ProtocolInfo>
        <RECORD>
          <ServiceID TYPE="UBYT">20</ServiceID>
          <ProtocolType TYPE="STR">FAKE</ProtocolType>
          <ProtocolVersion TYPE="INT">1</ProtocolVersion>
          <ProtocolDescription TYPE="STR">Fake Messages</ProtocolDescription>
        </RECORD>
    </_ProtocolInfo>
    <MSG_TEST>
        <RECORD>
            <_MsgName TYPE="STR" NOXFER="TRUE">MSG_TEST</_MsgName>
            <_MsgDescription TYPE="STR" NOXFER="TRUE">test if protocol system works</_MsgDescription>
            <_MsgHandler TYPE="STR" NOXFER="TRUE"></_MsgHandler>
            <_MsgAccessLvl TYPE="UBYT" NOXFER="TRUE">0</_MsgAccessLvl>
            <Number TYPE="INT"></Number>
        </RECORD>
    </MSG_TEST>
</FakeMessages>
"""


def test_load_protocol_from_string():
    protocol = ProtocolDefinition.from_string(string_protocol)

    assert protocol.service_id == 20
    assert protocol.type == "FAKE"
    assert protocol.description == "Fake Messages"

    # TODO: fix
    assert protocol.messages.get(1) is not None

    test_message = protocol.messages["MSG_TEST"]

    assert test_message.description == "test if protocol system works"
    assert test_message.name == "MSG_TEST"

    assert test_message.parameters.get("Number") is not None

    test_message_number_parameter = test_message.parameters["Number"]

    assert test_message_number_parameter.name == "Number"
    assert test_message_number_parameter.type == "INT"


def test_load_protocol_from_file():
    # TODO: replace with manual definition (include dupes)
    protocol = ProtocolDefinition.from_xml_file("/home/starr/PycharmProjects/wizmsg/message_files/GameMessages.xml")

    assert protocol.description == "Game Messages"

    protocol = ProtocolDefinition.from_xml_file("/home/starr/PycharmProjects/wizmsg/message_files/LoginMessages.xml")
    protocol = ProtocolDefinition.from_xml_file("/home/starr/PycharmProjects/wizmsg/message_files/PatchMessages.xml")
    protocol = ProtocolDefinition.from_xml_file("/home/starr/PycharmProjects/wizmsg/message_files/PetMessages.xml")
    protocol = ProtocolDefinition.from_xml_file(
        "/home/starr/PycharmProjects/wizmsg/message_files/ScriptDebuggerMessages.xml"
    )
    protocol = ProtocolDefinition.from_xml_file("/home/starr/PycharmProjects/wizmsg/message_files/WizardMessages.xml")


