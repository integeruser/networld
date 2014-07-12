package pongmp;

import pongmp.entities.Ball;

import java.nio.ByteBuffer;


public class Packet {
    public Packet() {
        serverTime = -1;
        clientTime = -1;
        world = new World();
    }

    ////////////////////////////////
    public int size() {
        return Long.BYTES + world.balls.size() * (Byte.BYTES + Ball.BYTES);
    }

    ////////////////////////////////
    public static void serialize(Packet packet, ByteBuffer byteBuffer) {
        packet.serverTime = System.nanoTime();
        byteBuffer.putLong( packet.serverTime );

        World.serialize( packet.world, byteBuffer );
    }

    public static Packet deserialize(ByteBuffer byteBuffer) {
        Packet packet = new Packet();

        packet.serverTime = byteBuffer.getLong();
        packet.clientTime = System.nanoTime();

        packet.world = World.deserialize( byteBuffer );

        return packet;
    }

    ////////////////////////////////
    public long serverTime, clientTime;
    public World world;
}