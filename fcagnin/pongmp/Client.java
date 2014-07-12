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
import java.util.zip.DataFormatException;

import static org.lwjgl.opengl.GL11.*;


public class Client {
    public static void main(String[] args) throws LWJGLException, InterruptedException {
        Server.main( null ); // temporary

        final ConcurrentLinkedQueue<Packet> snapshots = new ConcurrentLinkedQueue<>();
        final HashMap<Long, Ball> balls = new HashMap<>();

        ScheduledExecutorService service = Executors.newScheduledThreadPool( 1 );

        // process incoming server snapshots connections
        {
            service.execute( () -> {
                try {
                    int port = 1337;
                    Socket socket = new Socket( "localhost", port );
                    ObjectInputStream in = new ObjectInputStream( socket.getInputStream() );

                    Packet lastPacket = new Packet();
                    while ( true ) {
                        byte[] bytes = (byte[]) in.readObject();
                        byte[] decompressedBytes = Utils.decompress( bytes );
                        ByteBuffer byteBuffer = ByteBuffer.wrap( decompressedBytes );
                        Packet packet = Packet.deserialize( byteBuffer );

                        // reject late packets
                        if ( lastPacket.serverTime < packet.serverTime ) {
                            snapshots.add( packet );
                            lastPacket = packet;
                        }
                    }
                } catch ( IOException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                } catch ( ClassNotFoundException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                } catch ( DataFormatException e ) {
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

            Packet startPacket = new Packet(), endPacket = null;
            while ( !Display.isCloseRequested() ) {
                if ( Display.wasResized() ) { glViewport( 0, 0, Display.getWidth(), Display.getHeight() ); }

                final long interpTime = 100000000;
                long renderingTime = System.nanoTime() - interpTime;

                for ( long i : startPacket.world.balls.keySet() ) {
                    if ( !balls.containsKey( i ) ) {
                        balls.put( i, new Ball( startPacket.world.balls.get( i ) ) );
                    }
                }

                if ( endPacket == null ) { endPacket = snapshots.poll(); }
                while ( endPacket != null && endPacket.clientTime < renderingTime ) {
                    startPacket = endPacket;
                    endPacket = snapshots.poll();
                }

                if ( endPacket != null ) {
                    // update position: interpolate between snapshots
                    long startTime = startPacket.clientTime;
                    long endTime = endPacket.clientTime;
                    float timeBetweenSnapshots = endTime - startTime;

                    float ratio = (endTime - renderingTime) / timeBetweenSnapshots;

                    for ( long i : balls.keySet() ) {
                        balls.get( i ).interpolate( startPacket.world.balls.get( i ), endPacket.world.balls.get( i ),
                                ratio );
                    }
                } else { System.out.println( "endPacket null" ); }

                // render
                glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
                for ( Ball ball : balls.values() ) { ball.render(); }

                Display.update();
            }

            Display.destroy();
            System.exit( -1 );
        }
    }
}
