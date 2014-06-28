package pongmp;

import org.lwjgl.util.vector.Vector2f;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;

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
        long prevTime = System.nanoTime();
        while (true) {
            long time = System.nanoTime();
            float dt = (time - prevTime) / 1000000;
            prevTime = time;

            update(dt);
            updateClients();

//            String timeStamp = new SimpleDateFormat("HH:mm:ss").format(Calendar.getInstance().getTime());
//            System.out.println(timeStamp + " dt: " + dt);
            try {
                Thread.sleep(10);
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
