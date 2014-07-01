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
        ScheduledExecutorService service = Executors.newScheduledThreadPool(4);

        // accept incoming clients connections
        final ArrayList<ObjectOutputStream> clients = new ArrayList<>();
        {
            service.execute(() -> {
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
            });
        }

        // physics updates: steps of 15 ms
        final Ball ball = new Ball(new Vector2f(1f - 0.1f, 0f), new Vector2f(-1f, 1f), 0.1f);
        {
            updates = 0;

            service.scheduleAtFixedRate(() -> {
                ball.update(0.015f);
                ticks++;
                updates++;
            }, 0, 15, TimeUnit.MILLISECONDS);
        }

        // clients updates: steps of 50 ms
        {
            snapshots = 0;

            service.scheduleAtFixedRate(() -> {
                Snapshot snapshot = new Snapshot();
                snapshot.serverTime = System.nanoTime();
                snapshot.ballx = ball.position.x;
                snapshot.bally = ball.position.y;

                for (ObjectOutputStream out : clients) {
                    try {
                        out.writeObject(snapshot);
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
    private static long ticks;
    private static int updates, snapshots;
}
