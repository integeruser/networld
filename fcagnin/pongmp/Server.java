package pongmp;

import org.lwjgl.util.vector.Vector2f;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;

public class Server {
    public static void main(String[] args) {
        new Server().run();
    }

    ////////////////////////////////
    public Server() {
        ball = new Ball(new Vector2f(1f - 0.1f, 0f), new Vector2f(-1f, 1f), 0.1f);

        clients = new ArrayList<>();
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

    ////////////////////////////////
    private void run() {
        final int tickRate = 66;
        final float dtSec = 1f / tickRate;
        final long dtNano = (long) (1000000000f / tickRate);

        System.out.println("Starting simulation - "
                + "tickRate: " + tickRate + ", "
                + "dt: " + dtNano + ", ");
        new Thread((Runnable) () -> {
            while ( true ) {
                    String timeStamp = new SimpleDateFormat("HH:mm:ss").format(Calendar.getInstance().getTime());
                    System.out.println(timeStamp + " dt: " + dtNano);
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();

        boolean running = true;
        long timeLastUpdate = 0;
        long prevTime = 0, timePassed = 0;

        while (running) {
            long time = System.nanoTime();
            timePassed += time - prevTime;
            prevTime = time;

            if (time > timeLastUpdate + dtNano) {
                update(dtSec);
                updateClients();

                timeLastUpdate = time;
            }

            if (timePassed > 1000) {
                // print statistics

                timePassed = 0;
            }

            try {
                Thread.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void update(float dt) {
        ball.update(dt);
    }


    ////////////////////////////////
    private void updateClients() {
        float[] position = new float[2];
        position[0] = ball.position.x;
        position[1] = ball.position.y;

        for (ObjectOutputStream out : clients) {
            try {
                out.writeObject(position);
                out.flush();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    ////////////////////////////////
    private Ball ball;

    private ArrayList<ObjectOutputStream> clients;
}
