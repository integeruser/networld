from enum import Enum

import entities as e
import networking as n


class ServerOperations(Enum):
    NOP = 0x01
    GAMESTATE = 0x02
    SERVER_COMMAND = 0x05
    DOWNLOAD = 0x06
    SNAPSHOT = 0x07


class ServerMessage():
    EOF = 0x08

    def __init__(self):
        self.id = -1
        self.last_cmsg_received = -1
        self.op = None

    @staticmethod
    def frombytes(b):
        smsg = ServerMessage()
        smsg.id = n.r_int(b)
        smsg.last_cmsg_received = n.r_int(b)
        smsg.op = ServerOperations(n.r_byte(b))

        if smsg.op == ServerOperations.SNAPSHOT:
            smsg.server_time = n.r_float(b)
            smsg.frame_count = n.r_int(b)
            smsg.world_len = n.r_int(b)
            smsg.world = n.r_blob(b, smsg.world_len)
            smsg.n_entities = n.r_int(b)
        elif smsg.op == ServerOperations.NOP:
            pass
        else:
            raise NotImplementedError

        assert n.r_byte(b) == ServerMessage.EOF
        return smsg

    @staticmethod
    def tobytes(smsg):
        packet = bytearray()
        n.w_int(packet, smsg.id)
        n.w_int(packet, smsg.last_cmsg_received)
        n.w_byte(packet, smsg.op.value)

        if smsg.op == ServerOperations.SNAPSHOT:
            n.w_float(packet, smsg.server_time)
            n.w_int(packet, smsg.frame_count)
            n.w_int(packet, smsg.world_len)
            n.w_blob(packet, smsg.world)
            n.w_int(packet, smsg.n_entities)
        elif smsg.op == ServerOperations.NOP:
            pass
        else:
            raise NotImplementedError

        n.w_byte(packet, ServerMessage.EOF)
        return packet


class ClientMessage():
    EOF = 0x05

    def __init__(self):
        self.id = -1
        self.last_smsg_received = -1

    @staticmethod
    def frombytes(b):
        cmsg = ClientMessage()
        cmsg.id = n.r_int(b)
        cmsg.last_smsg_received = n.r_int(b)
        assert n.r_byte(b) == ClientMessage.EOF
        return cmsg

    @staticmethod
    def tobytes(cmsg):
        packet = bytearray()
        n.w_int(packet, cmsg.id)
        n.w_int(packet, cmsg.last_smsg_received)
        n.w_byte(packet, ClientMessage.EOF)
        return packet
