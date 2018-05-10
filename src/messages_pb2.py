# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messages.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='messages.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x0emessages.proto\">\n\x06Packet\x12\x0b\n\x03seq\x18\x01 \x01(\r\x12\x0b\n\x03\x61\x63k\x18\x02 \x01(\r\x12\x1a\n\x08messages\x18\x03 \x03(\x0b\x32\x08.Message\"C\n\x07Message\x12\x0b\n\x03seq\x18\x01 \x01(\r\x12\x0b\n\x03\x61\x63k\x18\x02 \x01(\r\x12\x10\n\x08reliable\x18\x03 \x01(\x08\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\"^\n\rServerMessage\x12\x1f\n\x02op\x18\x02 \x01(\x0e\x32\x13.ServerMessage.Type\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"\x1e\n\x04Type\x12\x08\n\x04NOOP\x10\x00\x12\x0c\n\x08SNAPSHOT\x10\x01\"\xc8\x01\n\rClientMessage\x12(\n\x08\x63ommands\x18\x01 \x03(\x0b\x32\x16.ClientMessage.Command\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x1a\x7f\n\x07\x43ommand\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\t\"W\n\x04Type\x12\x1c\n\x18SIM_DELETE_RANDOM_ENTITY\x10\x00\x12\x1b\n\x17SIM_SPAWN_RANDOM_ENTITY\x10\x01\x12\x14\n\x10SIM_TOGGLE_PAUSE\x10\x02\x62\x06proto3')
)



_SERVERMESSAGE_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='ServerMessage.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NOOP', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SNAPSHOT', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=215,
  serialized_end=245,
)
_sym_db.RegisterEnumDescriptor(_SERVERMESSAGE_TYPE)

_CLIENTMESSAGE_COMMAND_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='ClientMessage.Command.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SIM_DELETE_RANDOM_ENTITY', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SIM_SPAWN_RANDOM_ENTITY', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SIM_TOGGLE_PAUSE', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=361,
  serialized_end=448,
)
_sym_db.RegisterEnumDescriptor(_CLIENTMESSAGE_COMMAND_TYPE)


_PACKET = _descriptor.Descriptor(
  name='Packet',
  full_name='Packet',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='seq', full_name='Packet.seq', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ack', full_name='Packet.ack', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='messages', full_name='Packet.messages', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=80,
)


_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='seq', full_name='Message.seq', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ack', full_name='Message.ack', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reliable', full_name='Message.reliable', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='Message.data', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=82,
  serialized_end=149,
)


_SERVERMESSAGE = _descriptor.Descriptor(
  name='ServerMessage',
  full_name='ServerMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='op', full_name='ServerMessage.op', index=0,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='ServerMessage.data', index=1,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SERVERMESSAGE_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=151,
  serialized_end=245,
)


_CLIENTMESSAGE_COMMAND = _descriptor.Descriptor(
  name='Command',
  full_name='ClientMessage.Command',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ClientMessage.Command.id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='command', full_name='ClientMessage.Command.command', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CLIENTMESSAGE_COMMAND_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=321,
  serialized_end=448,
)

_CLIENTMESSAGE = _descriptor.Descriptor(
  name='ClientMessage',
  full_name='ClientMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='commands', full_name='ClientMessage.commands', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='ClientMessage.data', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_CLIENTMESSAGE_COMMAND, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=248,
  serialized_end=448,
)

_PACKET.fields_by_name['messages'].message_type = _MESSAGE
_SERVERMESSAGE.fields_by_name['op'].enum_type = _SERVERMESSAGE_TYPE
_SERVERMESSAGE_TYPE.containing_type = _SERVERMESSAGE
_CLIENTMESSAGE_COMMAND.containing_type = _CLIENTMESSAGE
_CLIENTMESSAGE_COMMAND_TYPE.containing_type = _CLIENTMESSAGE_COMMAND
_CLIENTMESSAGE.fields_by_name['commands'].message_type = _CLIENTMESSAGE_COMMAND
DESCRIPTOR.message_types_by_name['Packet'] = _PACKET
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['ServerMessage'] = _SERVERMESSAGE
DESCRIPTOR.message_types_by_name['ClientMessage'] = _CLIENTMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Packet = _reflection.GeneratedProtocolMessageType('Packet', (_message.Message,), dict(
  DESCRIPTOR = _PACKET,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:Packet)
  ))
_sym_db.RegisterMessage(Packet)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:Message)
  ))
_sym_db.RegisterMessage(Message)

ServerMessage = _reflection.GeneratedProtocolMessageType('ServerMessage', (_message.Message,), dict(
  DESCRIPTOR = _SERVERMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:ServerMessage)
  ))
_sym_db.RegisterMessage(ServerMessage)

ClientMessage = _reflection.GeneratedProtocolMessageType('ClientMessage', (_message.Message,), dict(

  Command = _reflection.GeneratedProtocolMessageType('Command', (_message.Message,), dict(
    DESCRIPTOR = _CLIENTMESSAGE_COMMAND,
    __module__ = 'messages_pb2'
    # @@protoc_insertion_point(class_scope:ClientMessage.Command)
    ))
  ,
  DESCRIPTOR = _CLIENTMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:ClientMessage)
  ))
_sym_db.RegisterMessage(ClientMessage)
_sym_db.RegisterMessage(ClientMessage.Command)


# @@protoc_insertion_point(module_scope)
