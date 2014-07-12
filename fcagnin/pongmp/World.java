package pongmp;

import pongmp.entities.Ball;

import java.nio.ByteBuffer;
import java.util.HashMap;


public class World {
    public World() {
        balls = new HashMap<>();
    }

    ////////////////////////////////

    public static void serialize(World world, ByteBuffer byteBuffer) {
        for ( Ball ball : world.balls.values() ) {
            byteBuffer.put( (byte) 127 );  // ball code
            Ball.serialize( ball, byteBuffer );
        }
    }

    public static World deserialize(ByteBuffer byteBuffer) {
        World world = new World();

        while ( byteBuffer.hasRemaining() ) {
            byteBuffer.get();  // ball code

            Ball ball = Ball.deserialize( byteBuffer );
            world.balls.put( ball.id, ball );
        }

        return world;
    }

    ////////////////////////////////
    public HashMap<Long, Ball> balls;
}
