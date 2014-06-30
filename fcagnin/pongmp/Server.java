package pongmp;

import org.lwjgl.util.vector.Vector2f;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Server {
    public static void main(String[] args) throws InterruptedException {
        ScheduledExecutorService service = Executors.newScheduledThreadPool(1);

        final ArrayList<ObjectOutputStream> clients = new ArrayList<>();
        final Ball ball = new Ball(new Vector2f(1f - 0.1f, 0f), new Vector2f(-1f, 1f), 0.1f);

        // listen and accept client connections
        {
            new Thread((Runnable) () -> {
                int port = 1337;
                try (ServerSocket serverSocket = new ServerSocket(port)) {
                    System.out.println("Listening on port " + port);

                    while (true) {
                        Socket clientSocket = serverSocket.accept();
                        clients.add(new ObjectOutputStream(clientSocket.getOutputStream()));
                        System.out.println("Client added to queue");
                    }
                } catch (IOException e) {
                    System.err.println("Could not listen on port " + port);
                    System.exit(-1);
                }
            }).start();
        }

        // physics update: steps of 15 ms
        {
            updates = 0;

            service.scheduleAtFixedRate(() -> {
                ball.update(0.015f);
                updates++;
            }, 0, 15, TimeUnit.MILLISECONDS);
        }

        // clients update: steps of 50 ms
        {
            snapshots = 0;

            service.scheduleAtFixedRate(() -> {
                float[] position = new float[2];
                position[0] = ball.position.x;
                position[1] = ball.position.y;

                for (ObjectOutputStream out : clients) {
                    try {
                        out.writeObject(position);
                        out.flush();
                    } catch (IOException e) {
                        e.printStackTrace();
                        System.exit(-1);
                    }
                }

                snapshots++;
            }, 0, 50, TimeUnit.MILLISECONDS);
        }

        // print info
        {
            service.scheduleAtFixedRate(() -> {
                String timeStamp = new SimpleDateFormat("HH:mm:ss").format(Calendar.getInstance().getTime());
                System.out.println(timeStamp + " updates/s: " + updates + ", snapshots/s: " + snapshots);
                updates = 0;
                snapshots = 0;
            }, 0, 1, TimeUnit.SECONDS);
        }
    }

    ////////////////////////////////
    private static int updates, snapshots;
}
