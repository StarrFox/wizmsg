from wizmsg import Protocol


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
    protocol = Protocol.from_string(string_protocol)

    assert protocol.service_id == 20
    assert protocol.type == "FAKE"
    assert protocol.description == "Fake Messages"

    assert protocol.messages.get("MSG_TEST") is not None

    test_message = protocol.messages["MSG_TEST"]

    assert test_message.description == "test if protocol system works"
    assert test_message.name == "MSG_TEST"

    assert test_message.parameters.get("Number") is not None

    test_message_number_parameter = test_message.parameters["Number"]

    assert test_message_number_parameter.name == "Number"
    assert test_message_number_parameter.type == "INT"
