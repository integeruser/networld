package pongmp;

import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;
import pongmp.entities.Ball;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

import static org.lwjgl.opengl.GL11.*;


public class Client {
    public static void main(String[] args) throws LWJGLException, InterruptedException {
        final ConcurrentLinkedQueue<Snapshot> snapshots = new ConcurrentLinkedQueue<>();
        final HashMap<Long, Ball> balls = new HashMap<>();

        ScheduledExecutorService service = Executors.newScheduledThreadPool( 1 );

        // process incoming server snapshots connections
        {
            service.execute( () -> {
                try {
                    int port = 1337;
                    Socket socket = new Socket( "localhost", port );
                    ObjectInputStream in = new ObjectInputStream( socket.getInputStream() );

                    Snapshot lastSnapshot = new Snapshot();
                    lastSnapshot.serverTime = 0;
                    while ( true ) {
                        Snapshot snapshot = (Snapshot) in.readObject();
                        // reject late packets
                        if ( lastSnapshot.serverTime < snapshot.serverTime ) {
                            snapshot.clientTime = System.nanoTime();
                            snapshots.add( snapshot );

                            lastSnapshot = snapshot;
                        }
                    }
                } catch ( IOException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                } catch ( ClassNotFoundException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                }
            } );
        }

        // create window and start rendering
        {
            Display.setTitle( "pongmp" );
            Display.setDisplayMode( new DisplayMode( 300, 300 ) );
            Display.setResizable( true );
            Display.setVSyncEnabled( true );
            Display.create();

            glViewport( 0, 0, Display.getWidth(), Display.getHeight() );

            Snapshot startSnapshot = new Snapshot(), endSnapshot = null;
            while ( !Display.isCloseRequested() ) {
                if ( Display.wasResized() ) { glViewport( 0, 0, Display.getWidth(), Display.getHeight() ); }

                final long interpTime = 100000000;
                long renderingTime = System.nanoTime() - interpTime;


                HashMap<Long, Ball> prevBalls, nextBalls;
                prevBalls = deserialize( startSnapshot.balls );
                for ( long i : prevBalls.keySet() ) {
                    if ( !balls.containsKey( i ) ) {
                        balls.put( i, new Ball( prevBalls.get( i ) ) );
                    }
                }

                if ( endSnapshot == null ) { endSnapshot = snapshots.poll(); }
                while ( endSnapshot != null && endSnapshot.clientTime < renderingTime ) {
                    startSnapshot = endSnapshot;
                    prevBalls = deserialize( startSnapshot.balls );
                    endSnapshot = snapshots.poll();
                }

                if ( endSnapshot != null ) {
                    nextBalls = deserialize( endSnapshot.balls );

                    // update position: interpolate between snapshots
                    long startTime = startSnapshot.clientTime;
                    long endTime = endSnapshot.clientTime;
                    float timeBetweenSnapshots = endTime - startTime;

                    float ratio = (endTime - renderingTime) / timeBetweenSnapshots;

                    for ( long i : balls.keySet() ) {
                        balls.get( i ).interpolate(
                                prevBalls.get( i ),
                                nextBalls.get( i ),
                                ratio );
                    }
                } else { System.out.println( "endSnapshot null" ); }

                // render
                glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
                for ( Ball ball : balls.values() ) {
                    ball.render();
                }

                Display.update();
            }

            Display.destroy();
            System.exit( -1 );
        }
    }

    private static HashMap<Long, Ball> deserialize(byte[] bytes) {
        HashMap<Long, Ball> map = new HashMap<>();

        ByteBuffer byteBuffer = ByteBuffer.wrap( bytes );
        while ( byteBuffer.hasRemaining() ) {
            byte ballCode = byteBuffer.get();
            byte[] dst = new byte[Ball.BYTES];
            byteBuffer.get( dst );
            Ball ball = Ball.deserialize( dst );
            map.put( ball.id, ball );
        }

        return map;
    }
}
