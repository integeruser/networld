package networld.simulation;

import networld.Utils;
import org.lwjgl.util.vector.Vector2f;
import org.lwjgl.util.vector.Vector3f;

import java.nio.ByteBuffer;

import static org.lwjgl.opengl.GL11.*;


public class Square extends AbstractObject {
    public Square(Vector2f position, Vector2f velocity, float radius, Vector3f color) {
        this.position = position;
        this.velocity = velocity;
        this.radius = radius;
        this.color = color;
    }

    public Square(Square ball) {
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
        Square startBall = (Square) start;
        Square endBall = (Square) end;

        position.x = startBall.position.x + (1 - ratio) * (endBall.position.x - startBall.position.x);
        position.y = startBall.position.y + (1 - ratio) * (endBall.position.y - startBall.position.y);
    }

    @Override
    public void render() {
        glBegin( GL_LINE_LOOP );
        glColor3f( color.x, color.y, color.z );

        glVertex2d( position.x + radius, position.y + radius );
        glVertex2d( position.x + radius, position.y - radius );
        glVertex2d( position.x - radius, position.y - radius );
        glVertex2d( position.x - radius, position.y + radius );

        glEnd();
    }

    ////////////////////////////////
    public Vector2f position;
    public Vector2f velocity;
    public float radius;
    public Vector3f color;

    ////////////////////////////////
    public static final int BYTES = 2 * Float.BYTES + 2 * Float.BYTES + Float.BYTES + 3 * Float.BYTES;

    public static void serialize(Square ball, ByteBuffer byteBuffer) {
        byteBuffer.putFloat( ball.position.x );
        byteBuffer.putFloat( ball.position.y );

        byteBuffer.putFloat( ball.velocity.x );
        byteBuffer.putFloat( ball.velocity.y );

        byteBuffer.putFloat( ball.radius );

        byteBuffer.putFloat( ball.color.x );
        byteBuffer.putFloat( ball.color.y );
        byteBuffer.putFloat( ball.color.z );
    }

    public static Square deserialize(ByteBuffer byteBuffer) {
        Vector2f position = new Vector2f( byteBuffer.getFloat(), byteBuffer.getFloat() );
        Vector2f velocity = new Vector2f( byteBuffer.getFloat(), byteBuffer.getFloat() );
        float radius = byteBuffer.getFloat();
        Vector3f color = new Vector3f( byteBuffer.getFloat(), byteBuffer.getFloat(), byteBuffer.getFloat() );

        return new Square( position, velocity, radius, color );
    }


    public static Square createRandom() {
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

        return new Square( position, velocity, radius, color );
    }
}
