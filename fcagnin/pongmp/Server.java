package pongmp;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
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
        final World world = World.createRandom();
        {
            updates = 0;

            service.scheduleAtFixedRate( () -> {
                if ( !paused ) {
                    world.update( 0.015f );
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
                    Packet packet = new Packet();
                    packet.world = world;

                    ByteBuffer byteBuffer = ByteBuffer.allocate( packet.size() );

                    Packet.serialize( packet, byteBuffer );
                    byte[] bytes = byteBuffer.array();
                    byte[] compressedBytes = bytes;
                    try {
                        compressedBytes = Utils.compress( bytes );
                    } catch ( IOException e ) {
                        e.printStackTrace();
                        System.exit( -1 );
                    }

                    packetSizeSum += bytes.length;
                    compressedPacketSizeSum += compressedBytes.length;

                    ArrayList<ObjectOutputStream> clientsToRemove = new ArrayList<>();
                    for ( ObjectOutputStream out : clients ) {
                        try {
                            out.writeObject( compressedBytes );
                            out.flush();
                        } catch ( IOException e ) {
                            clientsToRemove.add( out );
                        }
                    }
                    for ( ObjectOutputStream out : clientsToRemove ) {
                        clients.remove( out );
                        System.out.println( "Client removed from queue" );

                        System.exit( 223 ); // temporary
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
                    System.out.println( timeStamp + " updates/s: " + updates + ", snapshots/s: " + snapshots + ", " +
                            "avg. packet size: " + compressedPacketSizeSum / snapshots + " (uncompressed: " +
                            packetSizeSum / snapshots + ", ratio: " + (float) compressedPacketSizeSum / packetSizeSum
                            + ")" );
                    updates = 0;
                    snapshots = 0;
                    packetSizeSum = 0;
                    compressedPacketSizeSum = 0;
                }
            }, 0, 1, TimeUnit.SECONDS );
        }
    }

    ////////////////////////////////
    private static long ticks;
    private static int updates, snapshots, packetSizeSum, compressedPacketSizeSum;
    private static boolean paused = true;
}
