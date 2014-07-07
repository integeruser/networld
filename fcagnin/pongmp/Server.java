package pongmp;

import pongmp.entities.Ball;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.HashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;


public class Server {
    public static void main(String[] args) throws InterruptedException {
        ScheduledExecutorService service = Executors.newScheduledThreadPool( 4 );

        // accept incoming clients connections
        final ArrayList<ObjectOutputStream> clients = new ArrayList<>();
        {
            service.execute( () -> {
                int port = 1337;
                try ( ServerSocket serverSocket = new ServerSocket( port ) ) {
                    System.out.println( "Listening on port " + port );

                    while ( true ) {
                        Socket clientSocket = serverSocket.accept();
                        clients.add( new ObjectOutputStream( clientSocket.getOutputStream() ) );
                        paused = false;
                        System.out.println( "Client added to queue" );
                    }
                } catch ( IOException e ) {
                    System.err.println( "Could not listen on port " + port );
                    System.exit( -1 );
                }
            } );
        }

        // physics updates: steps of 15 ms
        final HashMap<Long, Ball> balls = new HashMap<>();

        for ( int i = 0; i < 10; i++ ) {
            Ball ball = Ball.createRandom();
            balls.put( ball.id, ball );
        }

        {
            updates = 0;

            service.scheduleAtFixedRate( () -> {
                if ( !paused ) {
                    for ( Ball ball : balls.values() ) { ball.update( 0.015f ); }
                    ticks++;
                    updates++;
                }
            }, 0, 15, TimeUnit.MILLISECONDS );
        }

        // clients updates: steps of 50 ms
        {
            snapshots = 0;

            service.scheduleAtFixedRate( () -> {
                if ( !paused ) {
                    Snapshot snapshot = new Snapshot();
                    snapshot.serverTime = System.nanoTime();

                    // serialization
                    byte ballCode = 127;

                    int ballsSize = balls.size() * (Byte.BYTES + Ball.BYTES);
                    snapshot.balls = new byte[ballsSize];

                    int ballsIndex = 0;
                    for ( Ball ball : balls.values() ) {
                        snapshot.balls[ballsIndex] = ballCode;
                        ballsIndex += Byte.BYTES;
                        System.arraycopy( Ball.serialize( ball ), 0, snapshot.balls, ballsIndex, Ball.BYTES );
                        ballsIndex += Ball.BYTES;
                    }

                    ArrayList<ObjectOutputStream> clientsToRemove = new ArrayList<>();
                    for ( ObjectOutputStream out : clients ) {
                        try {
                            out.writeObject( snapshot );
                            out.flush();
                        } catch ( IOException e ) {
                            clientsToRemove.add( out );
                        }
                    }
                    for ( ObjectOutputStream out : clientsToRemove ) {
                        clients.remove( out );
                        System.out.println( "Client removed from queue" );
                    }
                    if ( clients.isEmpty() ) { paused = true; }

                    snapshots++;
                }
            }, 0, 50, TimeUnit.MILLISECONDS );
        }

        // print info
        {
            service.scheduleAtFixedRate( () -> {
                if ( !paused ) {
                    String timeStamp = new SimpleDateFormat( "HH:mm:ss" ).format( Calendar.getInstance().getTime() );
                    System.out.println( timeStamp + " updates/s: " + updates + ", snapshots/s: " + snapshots );
                    updates = 0;
                    snapshots = 0;
                }
            }, 0, 1, TimeUnit.SECONDS );
        }
    }

    ////////////////////////////////
    private static long ticks;
    private static int updates, snapshots;
    private static boolean paused;
}
