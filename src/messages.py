from enum import Enum

import entities as e
import networking as n


class ServerOperations(Enum):
    NOP            = 0x01
    GAMESTATE      = 0x02
    SERVER_COMMAND = 0x05
    DOWNLOAD       = 0x06
    SNAPSHOT       = 0x07

class ServerMessage():
    def __init__(self):
        self.last_cmsg_received_seq = -1
        self.op = -1
        self.server_time = -1
        self.last_frame_num = -1
        self.entities = None

    @staticmethod
    def frombytes(b):
        smsg = ServerMessage()
        smsg.last_cmsg_received_seq = b.r_int(b)
        smsg.op = b.r_byte(b)
        return smsg

    @staticmethod
    def tobytes(smsg):
        packet = bytearray()
        n.w_int(packet, smsg.last_cmsg_received_seq)
        n.w_byte(packet, smsg.op.value)

        if smsg.op == ServerOperations.SNAPSHOT:
            n.w_float(packet, smsg.server_time)
            n.w_int(packet, smsg.last_frame_num)

            for entity in smsg.entities:
                msg = e.Entity.new(entity)
                packet.extend(msg)

            n.w_short(packet, 0x3FF)
        elif smsg.op == ServerOperations.NOP:
            pass
        else:
            raise NotImplementedError

        n.w_byte(packet, 0x08)
        return packet



class ClientMessage():
    def __init__(self):
        self.server_id = -1
        self.last_smsg_received_seq = -1

    @staticmethod
    def frombytes(b):
        cmsg = ClientMessage()
        cmsg.server_id = b.r_int(b)
        cmsg.last_smsg_received_seq = b.r_int(b)
        return cmsg

    @staticmethod
    def tobytes(cmsg):
        packet = bytearray()
        n.w_int(packet, cmsg.server_id)
        n.w_int(packet, cmsg.last_smsg_received_seq)
        n.w_byte(packet, 0x05)
        return packet
