package pongmp;

import pongmp.entities.Ball;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.Inflater;


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

        try {
            return compress( byteBuffer.array() );
        } catch ( IOException e ) {
            e.printStackTrace();
            return null;
        }
    }

    public static Packet deserialize(byte[] bytes) {
        Packet packet = new Packet();

        ByteBuffer byteBuffer = null;
        try {
            byteBuffer = ByteBuffer.wrap( decompress( bytes ) );
        } catch ( IOException e ) {
            e.printStackTrace();
            return null;
        } catch ( DataFormatException e ) {
            e.printStackTrace();
            return null;
        }

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


    public static byte[] compress(byte[] data) throws IOException {
        Deflater deflater = new Deflater();
        deflater.setInput( data );

        ByteArrayOutputStream outputStream = new ByteArrayOutputStream( data.length );

        deflater.finish();
        byte[] buffer = new byte[1024];
        while ( !deflater.finished() ) {
            int count = deflater.deflate( buffer ); // returns the generated code... index
            outputStream.write( buffer, 0, count );
        }
        outputStream.close();
        byte[] output = outputStream.toByteArray();

        //        LOG.debug("Original: " + data.length / 1024 + " Kb");
        //        LOG.debug("Compressed: " + output.length / 1024 + " Kb");
        return output;
    }

    public static byte[] decompress(byte[] data) throws IOException, DataFormatException {
        Inflater inflater = new Inflater();
        inflater.setInput( data );

        ByteArrayOutputStream outputStream = new ByteArrayOutputStream( data.length );
        byte[] buffer = new byte[1024];
        while ( !inflater.finished() ) {
            int count = inflater.inflate( buffer );
            outputStream.write( buffer, 0, count );
        }
        outputStream.close();
        byte[] output = outputStream.toByteArray();

        //        LOG.debug("Original: " + data.length);
        //        LOG.debug("Compressed: " + output.length);
        return output;
    }

    ////////////////////////////////

    public long serverTime, clientTime;
    public HashMap<Long, Ball> balls;
}