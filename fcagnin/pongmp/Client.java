package pongmp;

import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;
import org.lwjgl.util.vector.Vector2f;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.net.Socket;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

import static org.lwjgl.opengl.GL11.*;

public class Client {
    public static void main(String[] args) throws LWJGLException, InterruptedException {
        final ConcurrentLinkedQueue<Snapshot> snapshots = new ConcurrentLinkedQueue<>();
        final Ball ball = new Ball(new Vector2f(1f - 0.1f, 0f), new Vector2f(-1f, 1f), 0.1f);

        ScheduledExecutorService service = Executors.newScheduledThreadPool(1);

        // process incoming server snapshots connections
        {
            service.execute(() -> {
                try {
                    int port = 1337;
                    Socket socket = new Socket("localhost", port);
                    ObjectInputStream in = new ObjectInputStream(socket.getInputStream());

                    Snapshot lastSnapshot = new Snapshot();
                    lastSnapshot.serverTime = 0;
                    while (true) {
                        Snapshot snapshot = (Snapshot) in.readObject();
                        // reject late packets
                        if (lastSnapshot.serverTime < snapshot.serverTime) {
                            snapshot.clientTime = System.nanoTime();
                            snapshots.add(snapshot);

                            lastSnapshot = snapshot;
                        }
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

            Snapshot startSnapshot = new Snapshot(), endSnapshot = null;
            while (!Display.isCloseRequested()) {
                if (Display.wasResized()) {
                    glViewport(0, 0, Display.getWidth(), Display.getHeight());
                }

                final long interpTime = 100000000;
                long renderingTime = System.nanoTime() - interpTime;
                if (endSnapshot == null) {
                    endSnapshot = snapshots.poll();
                }
                while (endSnapshot != null && endSnapshot.clientTime < renderingTime) {
                    startSnapshot = endSnapshot;
                    endSnapshot = snapshots.poll();
                }

                if (endSnapshot != null) {
                    // update position: interpolate between snapshots
                    long startTime = startSnapshot.clientTime;
                    long endTime = endSnapshot.clientTime;
                    float timeBetweenSnapshots = endTime - startTime;

                    ball.position.x = startSnapshot.ball.position.x + (1 - ((endTime - renderingTime) / timeBetweenSnapshots)) * (endSnapshot.ball.position.x - startSnapshot.ball.position.x);
                    ball.position.y = startSnapshot.ball.position.y + (1 - ((endTime - renderingTime) / timeBetweenSnapshots)) * (endSnapshot.ball.position.y - startSnapshot.ball.position.y);
                } else {
                    System.out.println("null");
                }

                // render
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
                ball.render();

                Display.update();
            }

            Display.destroy();
            System.exit(-1);
        }
    }
}
