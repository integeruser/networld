package networld;

import networld.networking.Packet;
import networld.simulation.World;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.nio.ByteBuffer;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;


public class Server {
    public static void main(String[] args) throws IOException {
        final int port = Integer.parseInt( args[0] );
        Server server = new Server( port );
        server.waitConnection();
        server.start();
    }

    ////////////////////////////////
    public Server(int port) throws SocketException {
        socket = new DatagramSocket( port );

        System.out.println( "Server: created." );
    }

    ////////////////////////////////
    public void waitConnection() throws IOException {
        System.out.println( "Server: waiting for connection..." );

        /* wait for client connection */
        DatagramPacket datagramPacket = new DatagramPacket( new byte[1], 1 );
        socket.receive( datagramPacket );

        clientAddress = datagramPacket.getAddress();
        clientPort = datagramPacket.getPort();

        System.out.println( "Server: " + clientAddress + ":" + clientPort + " connected." );
    }

    public void start() {
        System.out.println( "Server: starting..." );

        /* start physics simulation (fixed-dt = 15ms) */
        final World world = World.createRandom();
        updates = 0;
        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate( () -> {
            world.update( 0.015f );
            updates++;
        }, 0, 15, TimeUnit.MILLISECONDS );

        /* start packet sending (every 50 ms) */
        snapshots = 0;
        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate( () -> {
            /* create a new Packet */
            Packet packet = new Packet();
            packet.world = world;

            /* serialize the Packet into byte[]*/
            ByteBuffer byteBuffer = ByteBuffer.allocate( packet.size() );
            Packet.serialize( packet, byteBuffer );
            byte[] bytes = byteBuffer.array();

            /* delta with the previous Packet */
            byte[] delta = bytes;
            // if ( prevBytes != null ) { delta = Utils.delta( prevBytes, bytes ); }
            prevBytes = bytes;

            /* compress the serialized Packet */
            byte[] compressedDelta = null;
            try {
                compressedDelta = Utils.compress( delta );
            } catch ( IOException e ) {
                e.printStackTrace();
                System.exit( -1 );
            }

            /* send the Packet to client */
            DatagramPacket datagramPacket = new DatagramPacket( compressedDelta, compressedDelta.length,
                    clientAddress, clientPort );
            try {
                socket.send( datagramPacket );
            } catch ( IOException e ) {
                e.printStackTrace();
                System.exit( -1 );
            }

            /* update stats */
            snapshots++;
            packetSizeSum += bytes.length;
            compressedPacketSizeSum += compressedDelta.length;
        }, 0, 50, TimeUnit.MILLISECONDS );

        /* start printing info (every second) */
        Executors.newSingleThreadScheduledExecutor().scheduleAtFixedRate( () -> {
            String timeStamp = new SimpleDateFormat( "HH:mm:ss" ).format( Calendar.getInstance().getTime() );
            System.out.println( timeStamp + " updates/s: " + updates + ", snapshots/s: " + snapshots + ", " +
                    "avg. packet size: " + compressedPacketSizeSum / snapshots + " (uncompressed: " +
                    packetSizeSum / snapshots + ", ratio: " + (float) compressedPacketSizeSum / packetSizeSum
                    + ")" );
            updates = 0;
            snapshots = 0;
            packetSizeSum = 0;
            compressedPacketSizeSum = 0;
        }, 0, 1, TimeUnit.SECONDS );
    }

    ////////////////////////////////
    private final DatagramSocket socket;
    private InetAddress clientAddress;
    private int clientPort;

    private byte[] prevBytes;

    /* settings / stats */
    private int updates, snapshots, packetSizeSum, compressedPacketSizeSum;
}
