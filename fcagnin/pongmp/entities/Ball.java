package pongmp.entities;

import org.lwjgl.util.vector.Vector2f;
import org.lwjgl.util.vector.Vector3f;
import pongmp.Utils;

import java.nio.ByteBuffer;

import static org.lwjgl.opengl.GL11.*;


public class Ball extends AbstractObject {
    public Ball() {
        position = new Vector2f();
        velocity = new Vector2f();
        radius = 0;
        color = new Vector3f( 255f, 255f, 255f );
    }

    public Ball(Vector2f position, Vector2f velocity, float radius, Vector3f color) {
        this.position = position;
        this.velocity = velocity;
        this.radius = radius;
        this.color = color;
    }

    public Ball(Ball ball) {
        id = ball.id;

        position = new Vector2f( ball.position );
        velocity = new Vector2f( ball.velocity );
        radius = ball.radius;
        color = new Vector3f( ball.color );
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
        glColor3f( color.x, color.y, color.z );

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
    public Vector3f color;


    ////////////////////////////////
    public static final int BYTES = Long.BYTES + 2 * Float.BYTES + 2 * Float.BYTES + Float.BYTES + 3 * Float.BYTES;

    public static byte[] serialize(Ball ball) {
        ByteBuffer byteBuffer = ByteBuffer.allocate( BYTES );

        byteBuffer.putLong( ball.id );

        byteBuffer.putFloat( ball.position.x );
        byteBuffer.putFloat( ball.position.y );

        byteBuffer.putFloat( ball.velocity.x );
        byteBuffer.putFloat( ball.velocity.y );

        byteBuffer.putFloat( ball.radius );

        byteBuffer.putFloat( ball.color.x );
        byteBuffer.putFloat( ball.color.y );
        byteBuffer.putFloat( ball.color.z );

        return byteBuffer.array();
    }

    public static Ball deserialize(byte[] bytes) {
        ByteBuffer byteBuffer = ByteBuffer.wrap( bytes );

        long id = byteBuffer.getLong();
        Vector2f position = new Vector2f( byteBuffer.getFloat(), byteBuffer.getFloat() );
        Vector2f velocity = new Vector2f( byteBuffer.getFloat(), byteBuffer.getFloat() );
        float radius = byteBuffer.getFloat();
        Vector3f color = new Vector3f( byteBuffer.getFloat(), byteBuffer.getFloat(), byteBuffer.getFloat() );

        Ball ball = new Ball( position, velocity, radius, color );
        ball.id = id;
        return ball;
    }


    public static Ball createRandom() {
        float radius = Utils.randomFloat( 0.05f, 0.15f );
        Vector2f position = new Vector2f(
                Utils.randomFloat( -1 + radius, 1 - radius ),
                Utils.randomFloat( -1 + radius, 1 - radius ) );
        Vector2f velocity = new Vector2f(
                (Math.random() < 0.5 ? -1 : 1) * Utils.randomFloat( 0.1f, 1f ),
                (Math.random() < 0.5 ? -1 : 1) * Utils.randomFloat( 0.1f, 1f ) );
        Vector3f color = new Vector3f(
                Utils.randomFloat( 0f, 1f ),
                Utils.randomFloat( 0f, 1f ),
                Utils.randomFloat( 0f, 1f ) );
        return new Ball( position, velocity, radius, color );
    }
}
