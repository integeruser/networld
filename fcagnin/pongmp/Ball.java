package pongmp;


import org.lwjgl.util.vector.Vector2f;

import java.io.Serializable;

import static org.lwjgl.opengl.GL11.*;

public class Ball implements Serializable {
    public Ball(Vector2f position, Vector2f velocity, float radius) {
        this.position = position;
        this.velocity = velocity;
        this.radius = radius;
    }

    public Ball(Ball ball) {
        this.position = new Vector2f(ball.position);
        this.velocity = new Vector2f(ball.velocity);
        this.radius = ball.radius;
    }


    ////////////////////////////////
    public void update(float dt) {
        position.x = position.x + dt * velocity.x;
        position.y = position.y + dt * velocity.y;

        if (position.x - radius < -1) {
            position.x = radius - 1;
            velocity.x = -velocity.x;
        }
        if (position.x + radius > 1) {
            position.x = 1 - radius;
            velocity.x = -velocity.x;
        }
        if (position.y - radius < -1) {
            position.y = radius - 1;
            velocity.y = -velocity.y;
        }
        if (position.y + radius > 1) {
            position.y = 1 - radius;
            velocity.y = -velocity.y;
        }
    }

    public void render() {
        glBegin(GL_LINE_LOOP);

        for (int i = 0; i <= 300; i++) {
            double angle = 2 * Math.PI * i / 300;
            glVertex2d(position.x + radius * Math.cos(angle), position.y + radius * Math.sin(angle));
        }

        glEnd();
    }


    ////////////////////////////////
    public Vector2f position;
    public Vector2f velocity;
    public float radius;
}
