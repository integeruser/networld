package networld;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Random;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.Inflater;


public class Utils {
    public static byte[] delta(byte[] from, byte[] to) {
        assert from != null && to != null;
        assert from.length == to.length;

        byte[] res = new byte[from.length];
        for ( int i = 0; i < res.length; i++ ) {
            res[i] = (byte) (from[i] ^ to[i]);
        }

        return res;
    }

    public static byte[] reconstruct(byte[] from, byte[] delta) {
        assert from != null && delta != null;
        assert from.length == delta.length;

        byte[] res = new byte[from.length];
        for ( int i = 0; i < res.length; i++ ) {
            res[i] = (byte) (from[i] ^ delta[i]);
        }

        return res;
    }

    ////////////////////////////////
    public static byte[] compress(byte[] input) throws IOException {
        Deflater deflater = new Deflater();
        deflater.setInput( input );
        deflater.finish();

        byte[] buffer = new byte[1024];
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream( input.length );
        while ( !deflater.finished() ) {
            int count = deflater.deflate( buffer );
            outputStream.write( buffer, 0, count );
        }
        outputStream.close();

        return outputStream.toByteArray();
    }

    public static byte[] decompress(byte[] input) throws IOException, DataFormatException {
        Inflater inflater = new Inflater();
        inflater.setInput( input );

        byte[] buffer = new byte[1024];
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream( input.length );
        while ( !inflater.finished() ) {
            int count = inflater.inflate( buffer );
            outputStream.write( buffer, 0, count );
        }
        outputStream.close();

        inflater.end();

        return outputStream.toByteArray();
    }

    ////////////////////////////////
    public static Random random = new Random();

    public static int randomInt(int min, int max) {
        return random.nextInt( (max - min) + 1 ) + min;
    }

    public static float randomFloat(float min, float max) {
        return random.nextFloat() * (max - min) + min;
    }
}
