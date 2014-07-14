package networld.simulation;

import networld.Utils;

import java.nio.ByteBuffer;


public class World {
    public World() {
        abstractObjects = new AbstractObject[MAX_OBJECTS];
    }

    ////////////////////////////////
    public void update(float dt) {
        for ( AbstractObject abstractObject : abstractObjects ) {
            if ( abstractObject != null ) { abstractObject.update( dt ); }
        }
    }

    public void render() {
        for ( AbstractObject abstractObject : abstractObjects ) {
            if ( abstractObject != null ) { abstractObject.render(); }
        }
    }

    ////////////////////////////////
    public static void serialize(World world, ByteBuffer byteBuffer) {
        for ( AbstractObject abstractObject : world.abstractObjects ) {
            if ( abstractObject instanceof Ball ) {
                byteBuffer.put( CODE_BALL );
                Ball.serialize( (Ball) abstractObject, byteBuffer );
            } else if ( abstractObject instanceof Square ) {
                byteBuffer.put( CODE_SQUARE );
                Square.serialize( (Square) abstractObject, byteBuffer );
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
                    world.abstractObjects[i] = Ball.deserialize( byteBuffer );
                    break;

                case CODE_SQUARE:
                    world.abstractObjects[i] = Square.deserialize( byteBuffer );
                    break;

                case CODE_NULL:
                    break;
            }
        }

        return world;
    }


    public static World createRandom() {
        World world = new World();

        int numObjs = Utils.randomInt( 40, 100 );
        for ( int i = 0; i < numObjs; i++ ) {
            if ( i % 3 == 0 ) {
                world.abstractObjects[i] = Square.createRandom();
            } else {
                world.abstractObjects[i] = Ball.createRandom();
            }
        }

        return world;
    }

    ////////////////////////////////
    public static final int MAX_OBJECTS = 100;
    public static final int BYTES = MAX_OBJECTS * (Byte.BYTES + Ball.BYTES);

    public AbstractObject[] abstractObjects;

    private static final byte CODE_NULL = 0;
    private static final byte CODE_BALL = 1;
    private static final byte CODE_SQUARE = 2;
}
