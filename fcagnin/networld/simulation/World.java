package networld.simulation;

import networld.Utils;

import java.nio.ByteBuffer;
import java.util.HashMap;


public class World {
    public World() {
        balls = new HashMap<>();
    }

    ////////////////////////////////
    public void update(float dt) {
        for ( Ball ball : balls.values() ) { ball.update( dt ); }
    }

    public void render() {
        for ( Ball ball : balls.values() ) { ball.render(); }
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


    public static World createRandom() {
        World world = new World();

        int numObjs = Utils.randomInt( 20, 100 );
        for ( int i = 0; i < numObjs; i++ ) {
            Ball ball = Ball.createRandom();
            world.balls.put( ball.id, ball );
        }

        return world;
    }

    ////////////////////////////////
    public HashMap<Long, Ball> balls;
}
