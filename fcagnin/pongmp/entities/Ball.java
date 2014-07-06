package pongmp.entities;

import org.lwjgl.util.vector.Vector2f;

import java.nio.ByteBuffer;

import static org.lwjgl.opengl.GL11.*;


public class Ball extends AbstractObject {
    public Ball() {
        position = new Vector2f();
        velocity = new Vector2f();
        radius = 0;
    }

    public Ball(Vector2f position, Vector2f velocity, float radius) {
        this.position = position;
        this.velocity = velocity;
        this.radius = radius;
    }

    public Ball(Ball ball) {
        position = new Vector2f( ball.position );
        velocity = new Vector2f( ball.velocity );
        radius = ball.radius;
    }


    ////////////////////////////////
    @Override
    public void update(float dt) {
        position.x = position.x + dt * velocity.x;
        position.y = position.y + dt * velocity.y;

        if ( position.x - radius < -1 ) {
            position.x = radius - 1;
            velocity.x = -velocity.x;
        }
        if ( position.x + radius > 1 ) {
            position.x = 1 - radius;
            velocity.x = -velocity.x;
        }
        if ( position.y - radius < -1 ) {
            position.y = radius - 1;
            velocity.y = -velocity.y;
        }
        if ( position.y + radius > 1 ) {
            position.y = 1 - radius;
            velocity.y = -velocity.y;
        }
    }

    @Override
    public void interpolate(AbstractObject start, AbstractObject end, float ratio) {
        Ball startBall = (Ball) start;
        Ball endBall = (Ball) end;

        position.x = startBall.position.x + (1 - ratio) * (endBall.position.x - startBall.position.x);
        position.y = startBall.position.y + (1 - ratio) * (endBall.position.y - startBall.position.y);
    }

    @Override
    public void render() {
        glBegin( GL_LINE_LOOP );

        for ( int i = 0; i <= 300; i++ ) {
            double angle = 2 * Math.PI * i / 300;
            glVertex2d( position.x + radius * Math.cos( angle ), position.y + radius * Math.sin( angle ) );
        }

        glEnd();
    }


    ////////////////////////////////
    public Vector2f position;
    public Vector2f velocity;
    public float radius;


    ////////////////////////////////
    public static byte[] serialize(Ball ball) {
        ByteBuffer byteBuffer = ByteBuffer.allocate( Long.BYTES + 2 * Float.BYTES + 2 * Float.BYTES + Float.BYTES );

        byteBuffer.putLong( ball.id );

        byteBuffer.putFloat( ball.position.x );
        byteBuffer.putFloat( ball.position.y );

        byteBuffer.putFloat( ball.velocity.x );
        byteBuffer.putFloat( ball.velocity.y );

        byteBuffer.putFloat( ball.radius );

        return byteBuffer.array();
    }

    public static Ball deserialize(byte[] bytes) {
        ByteBuffer byteBuffer = ByteBuffer.wrap( bytes )/*.order(ByteOrder.LITTLE_ENDIAN)*/;

        long id = byteBuffer.getLong();
        Vector2f position = new Vector2f( byteBuffer.getFloat(), byteBuffer.getFloat() );
        Vector2f velocity = new Vector2f( byteBuffer.getFloat(), byteBuffer.getFloat() );
        float radius = byteBuffer.getFloat();

        Ball ball = new Ball( position, velocity, radius );
        ball.id = id;
        return ball;
    }
}
