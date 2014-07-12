package pongmp;

import pongmp.entities.Ball;

import java.nio.ByteBuffer;
import java.util.HashMap;


public class Packet {
    public Packet() {
        serverTime = -1;
        clientTime = -1;
        balls = new HashMap<>();
    }

    ////////////////////////////////
    public int size() {
        return Long.BYTES + balls.size() * (Byte.BYTES + Ball.BYTES);
    }

    ////////////////////////////////
    public static void serialize(Packet packet, ByteBuffer byteBuffer) {
        packet.serverTime = System.nanoTime();
        byteBuffer.putLong( packet.serverTime );

        for ( Ball ball : packet.balls.values() ) {
            byteBuffer.put( (byte) 127 );  // ball code
            Ball.serialize( ball, byteBuffer );
        }
    }

    public static Packet deserialize(ByteBuffer byteBuffer) {
        Packet packet = new Packet();

        packet.serverTime = byteBuffer.getLong();
        packet.clientTime = System.nanoTime();

        while ( byteBuffer.hasRemaining() ) {
            byteBuffer.get();  // ball code

            Ball ball = Ball.deserialize( byteBuffer );
            packet.balls.put( ball.id, ball );
        }

        return packet;
    }

    ////////////////////////////////
    public long serverTime, clientTime;
    public HashMap<Long, Ball> balls;
}