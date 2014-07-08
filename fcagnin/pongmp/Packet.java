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
    public static byte[] serialize(Packet packet) {
        ByteBuffer byteBuffer = ByteBuffer.allocate( Long.BYTES + packet.balls.size() * (Byte.BYTES + Ball.BYTES) );

        packet.serverTime = System.nanoTime();
        byteBuffer.putLong( packet.serverTime );

        for ( Ball ball : packet.balls.values() ) {
            byteBuffer.put( (byte) 127 );  // ball code
            byteBuffer.put( Ball.serialize( ball ) );
        }

        return byteBuffer.array();
    }

    public static Packet deserialize(byte[] bytes) {
        Packet packet = new Packet();

        ByteBuffer byteBuffer = ByteBuffer.wrap( bytes );

        packet.serverTime = byteBuffer.getLong();
        packet.clientTime = System.nanoTime();

        while ( byteBuffer.hasRemaining() ) {
            byteBuffer.get();  // ball code

            byte[] dst = new byte[Ball.BYTES];
            byteBuffer.get( dst );
            Ball ball = Ball.deserialize( dst );
            packet.balls.put( ball.id, ball );
        }

        return packet;
    }

    ////////////////////////////////

    public long serverTime, clientTime;
    public HashMap<Long, Ball> balls;
}