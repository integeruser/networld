package pongmp;

import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;
import org.lwjgl.util.vector.Vector2f;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.net.Socket;

import static org.lwjgl.opengl.GL11.*;

public class Client {
    public static void main(String[] args) {
        new Client(300, 300).run();
    }


    ////////////////////////////////
    public Client(int width, int height) {
        try {
            Display.setTitle("pongmp");
            Display.setDisplayMode(new DisplayMode(width, height));
            Display.setResizable(true);
            Display.setVSyncEnabled(true);
            Display.create();
        } catch (LWJGLException e) {
            e.printStackTrace();
        }

        ball = new Ball(new Vector2f(1f - 0.1f, 0f), new Vector2f(-1f, 1f), 0.1f);

        new Thread((Runnable) () -> {
            try {
                int port = 1337;
                Socket socket = new Socket("localhost", port);
                ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

                while (true) {
                    float[] position = (float[]) in.readObject();
                    ball.position.x = position[0];
                    ball.position.y = position[1];
//                    System.out.println("Update received");
                }
            } catch (IOException e) {
                e.printStackTrace();
            } catch (ClassNotFoundException e) {
                e.printStackTrace();
            }
        }).start();
    }


    ////////////////////////////////
    private void run() {
        glViewport(0, 0, Display.getWidth(), Display.getHeight());

        long prevTime = System.nanoTime();
        while (!Display.isCloseRequested()) {
            if (Display.wasResized()) {
                glViewport(0, 0, Display.getWidth(), Display.getHeight());
            }

            long time = System.nanoTime();
            float dt = (time - prevTime) / 1000000;
            prevTime = time;

            render();
            Display.update();
        }

        Display.destroy();
    }

    private void render() {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        ball.render();
    }

    ////////////////////////////////
    private Ball ball;
}
