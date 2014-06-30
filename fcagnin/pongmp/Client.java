package pongmp;

import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;
import org.lwjgl.util.vector.Vector2f;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.net.Socket;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

import static org.lwjgl.opengl.GL11.*;

public class Client {
    public static void main(String[] args) throws LWJGLException {
        final Ball ball = new Ball(new Vector2f(1f - 0.1f, 0f), new Vector2f(-1f, 1f), 0.1f);

        // process incoming server snapshots connections
        {
            ScheduledExecutorService service = Executors.newScheduledThreadPool(1);
            service.execute(() -> {
                try {
                    int port = 1337;
                    Socket socket = new Socket("localhost", port);
                    ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

                    while (true) {
                        float[] position = (float[]) in.readObject();
                        ball.position.x = position[0];
                        ball.position.y = position[1];
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                    System.exit(-1);
                } catch (ClassNotFoundException e) {
                    e.printStackTrace();
                    System.exit(-1);
                }
            });
        }

        // create window and start rendering
        {
            Display.setTitle("pongmp");
            Display.setDisplayMode(new DisplayMode(300, 300));
            Display.setResizable(true);
            Display.setVSyncEnabled(true);
            Display.create();

            glViewport(0, 0, Display.getWidth(), Display.getHeight());

            while (!Display.isCloseRequested()) {
                if (Display.wasResized()) {
                    glViewport(0, 0, Display.getWidth(), Display.getHeight());
                }

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
                ball.render();

                Display.update();
            }

            Display.destroy();
        }
    }
}
