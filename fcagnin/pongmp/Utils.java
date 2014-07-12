package pongmp;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.Inflater;


public class Utils {
    public static void main(String[] args) throws IOException {
        /*
        Ball[] balls = new Ball[100];
        for ( int i = 0; i < balls.length; i++ ) {
            balls[i] = Ball.createRandom();
        }
        ByteBuffer byteBuffer = ByteBuffer.allocate( balls.length * Ball.BYTES );
        for ( Ball b : balls ) {
            byteBuffer.put( Ball.serialize( b ) );
        }
        byte[] game1 = byteBuffer.array();

        for ( int i = 0; i < balls.length; i++ ) {
            if ( i % 2 == 0 ) { balls[i].update( 0.15f * i ); }
        }
        byteBuffer = ByteBuffer.allocate( balls.length * Ball.BYTES );
        for ( Ball b : balls ) {
            byteBuffer.put( Ball.serialize( b ) );
        }
        byte[] game2 = byteBuffer.array();

        byte[] delta = new byte[game1.length];
        for ( int i = 0; i < game1.length; i++ ) {
            delta[i] = (byte) (game1[i] ^ game2[i]);
        }

        for ( int i = 0; i < game1.length; i++ ) {
            if ( (game1[i] ^ delta[i]) != game2[i] ) { System.out.println( "false" ); }
        }
        System.out.println( Arrays.toString( game1 ) );
        System.out.println( Arrays.toString( delta ) );
        System.out.println( Arrays.toString( game2 ) );


        System.out.println( delta.length );
        byte[] comp = c( delta );
        System.out.println( comp.length );
        System.out.println( Arrays.toString( comp ) );

        byte[] dec = d( comp );
        for ( int i = 0; i < dec.length; i++ ) {
            if ( (game1[i] ^ dec[i]) != game2[i] ) { System.out.println( "false" ); }
        }

        System.out.println(compress( delta ).length);*/
    }

    public static byte[] c(byte[] bytes) {
        ByteBuffer byteBuffer = ByteBuffer.allocate( bytes.length );

        int i = 0;
        byte c = 0;
        while ( i < bytes.length ) {
            byte b = bytes[i];
            if ( b == 0 ) {
                c++;
            } else {
                if ( c != 0 ) {
                    byteBuffer.put( (byte) 0 );
                    byteBuffer.put( c );
                    c = 0;
                }
                byteBuffer.put( b );
            }
            i++;
        }

        return Arrays.copyOf( byteBuffer.array(), byteBuffer.position() );
    }

    public static byte[] d(byte[] bytes) {
        ByteBuffer byteBuffer = ByteBuffer.allocate( 10000 );
        int i = 0;
        while ( i < bytes.length ) {
            byte b = bytes[i];
            if ( b == 0 ) {
                i++;
                byte n = bytes[i];
                for ( int j = 0; j < n; j++ ) {
                    byteBuffer.put( (byte) 0 );
                }
            } else {
                byteBuffer.put( b );
            }
            i++;
        }

        return Arrays.copyOf( byteBuffer.array(), byteBuffer.position() );
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

        return output;
    }

    ////////////////////////////////

    public static float randomFloat(float min, float max) {
        return (float) (Math.random() * (max - min) + min);
    }
}
