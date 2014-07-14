package networld.simulation;

import networld.Utils;

import java.nio.ByteBuffer;


public class World {
    public World() {
        balls = new Ball[MAX_OBJECTS];
    }

    ////////////////////////////////
    public void update(float dt) {
        for ( Ball ball : balls ) {
            if ( ball != null ) { ball.update( dt ); }
        }
    }

    public void render() {
        for ( Ball ball : balls ) {
            if ( ball != null ) { ball.render(); }
        }
    }

    ////////////////////////////////
    public static void serialize(World world, ByteBuffer byteBuffer) {
        for ( Ball ball : world.balls ) {
            if ( ball instanceof Ball ) {
                byteBuffer.put( CODE_BALL );
                Ball.serialize( ball, byteBuffer );
            } else {
                byteBuffer.put( CODE_NULL );
            }
        }
    }

    public static World deserialize(ByteBuffer byteBuffer) {
        World world = new World();

        for ( int i = 0; i < MAX_OBJECTS; i++ ) {
            byte code = byteBuffer.get();
            switch ( code ) {
                case CODE_BALL:
                    world.balls[i] = Ball.deserialize( byteBuffer );
                    break;

                default:
            }
        }

        return world;
    }


    public static World createRandom() {
        World world = new World();

        int numObjs = Utils.randomInt( 20, 100 );
        for ( int i = 0; i < numObjs; i++ ) {
            Ball ball = Ball.createRandom();
            world.balls[i] = ball;
        }

        return world;
    }

    ////////////////////////////////
    public static final int MAX_OBJECTS = 100;
    public static final int BYTES = MAX_OBJECTS * (Byte.BYTES + Ball.BYTES);

    public Ball[] balls;

    private static final byte CODE_NULL = 0;
    private static final byte CODE_BALL = 127;
}
