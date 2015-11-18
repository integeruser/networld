package networld;

import networld.networking.Packet;
import networld.simulation.Ball;
import networld.simulation.Square;
import networld.simulation.World;
import org.lwjgl.LWJGLException;
import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;

import javax.swing.*;
import java.awt.*;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.zip.DataFormatException;

import static org.lwjgl.opengl.GL11.*;


public class Client {
    public static void main(String[] args) throws IOException, LWJGLException {
        if ( args.length == 3 ) {
            /* start client */
            final int clientPort = Integer.parseInt( args[0] );
            final InetAddress serverAddress = InetAddress.getByName( args[1] );
            final int serverPort = Integer.parseInt( args[2] );
            Client client = new Client( clientPort, serverAddress, serverPort );
            client.start();
        } else {
            /* start server on localhost at the specified port */
            final InetAddress serverAddress = InetAddress.getByName( "127.0.0.1" );
            final int serverPort = 1337;
            Executors.newSingleThreadExecutor().execute( () -> {
                try {
                    Server server = new Server( serverPort );
                    server.waitConnection();  // blocking
                    server.start();
                } catch ( SocketException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                } catch ( IOException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                }
            } );

            /* start client */
            final int clientPort = 1338;
            Client client = new Client( clientPort, serverAddress, serverPort );
            client.start();
        }

        System.exit( 0 );  // kill all threads
    }

    ////////////////////////////////
    public Client(int port, InetAddress serverAddress, int serverPort) throws LWJGLException, SocketException {
        /* initialize settings */
        int displayWidth = 400, displayHeight = 400;
        vsynced = true;

        /* create console (before creating Display to not get window focus */
        console = new Console();
        Point consoleLocation = console.getLocation();
        console.setLocation( consoleLocation.x + displayWidth / 2 + console.getWidth() / 2, consoleLocation.y );

        /* create LWJGL window */
        Display.setTitle( "networld" );
        Display.setDisplayMode( new DisplayMode( displayWidth, displayHeight ) );
        Display.setVSyncEnabled( vsynced );
        Display.create();

        /* create socket */
        socket = new DatagramSocket( port );
        this.serverAddress = serverAddress;
        this.serverPort = serverPort;

        /* initialize others variables */
        snapshots = new ConcurrentLinkedQueue<>();
        world = new World();

        System.out.println( "Client: created." );
    }

    ////////////////////////////////
    public void start() throws IOException {
        System.out.println( "Client: starting..." );

        /* send request to server to initialize communications */
        socket.send( new DatagramPacket( new byte[1], 1, serverAddress, serverPort ) );

        /* start receiving packets */
        Executors.newSingleThreadExecutor().execute( () -> {
            byte[] buf = new byte[8192];
            DatagramPacket datagramPacket = new DatagramPacket( buf, buf.length );

            Packet lastPacket = new Packet();
            while ( true ) {
                /* receive packet from server */
                try {
                    socket.receive( datagramPacket );
                } catch ( IOException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                }

                byte[] bytes = Arrays.copyOf( datagramPacket.getData(), datagramPacket.getLength() );

                /* decompress the serialized Packet */
                byte[] decompressedBytes = null;
                try {
                    decompressedBytes = Utils.decompress( bytes );
                } catch ( IOException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                } catch ( DataFormatException e ) {
                    e.printStackTrace();
                    System.exit( -1 );
                }

                /* reconstruct the correct Packet with the previous Packet */
                byte[] reconstructed = decompressedBytes;
                // if ( prevBytes != null ) { reconstructed = Utils.reconstruct( prevBytes, decompressedBytes ); }
                prevBytes = reconstructed;

                /* deserialize the received Packet */
                ByteBuffer byteBuffer = ByteBuffer.wrap( reconstructed );
                Packet packet = Packet.deserialize( byteBuffer );

                /* add the received Packet to the queue */
                if ( lastPacket.serverTime < packet.serverTime ) {
                    snapshots.add( packet );
                    lastPacket = packet;
                }
            }
        } );

        /* start rendering (main loop) */
        final long interpTime = 100000000;
        Packet startPacket = new Packet(), endPacket = null;
        while ( !Display.isCloseRequested() ) {
            long time = System.nanoTime();
            long renderingTime = time - interpTime;

            /* update World based on Packets */
            if ( endPacket == null ) { endPacket = snapshots.poll(); }
            while ( endPacket != null && endPacket.clientTime < renderingTime ) {
                startPacket = endPacket;

                /* add new objects to World */
                for ( int i = 0; i < World.MAX_OBJECTS; i++ ) {
                    if ( startPacket.world.abstractObjects[i] != null ) {
                        if ( world.abstractObjects[i] == null ) {
                            if ( startPacket.world.abstractObjects[i] instanceof Ball ) {
                                world.abstractObjects[i] = new Ball( (Ball) startPacket.world.abstractObjects[i] );
                            } else if ( startPacket.world.abstractObjects[i] instanceof Square ) {
                                world.abstractObjects[i] = new Square( (Square) startPacket.world.abstractObjects[i] );
                            } else {
                                System.out.println( "unrecognized object" );
                            }
                        }
                    }
                }

                endPacket = snapshots.poll();
            }

            if ( endPacket != null ) {
                /* update position: interpolate between snapshots */
                long startTime = startPacket.clientTime;
                long endTime = endPacket.clientTime;
                float timeBetweenSnapshots = endTime - startTime;

                float ratio = (endTime - renderingTime) / timeBetweenSnapshots;

                for ( int i = 0; i < World.MAX_OBJECTS; i++ ) {
                    if ( world.abstractObjects[i] != null ) {
                        world.abstractObjects[i].interpolate(
                                startPacket.world.abstractObjects[i],
                                endPacket.world.abstractObjects[i],
                                ratio );
                    }
                }
            } else {
                System.out.println( "endPacket null" );
            }

            /* adjust viewport */
            if ( Display.wasResized() ) { glViewport( 0, 0, Display.getWidth(), Display.getHeight() ); }

            /* render World */
            glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
            world.render();

            /* update stats */
            loops++;
            cumLoopTime += System.nanoTime() - time;

            /* update LWJGL window and sync framerate */
            Display.update();
            Display.sync( 60 );
        }

        Display.destroy();
    }

    ////////////////////////////////
    private final DatagramSocket socket;
    private final InetAddress serverAddress;
    private final int serverPort;

    private final ConcurrentLinkedQueue<Packet> snapshots;
    private final World world;

    private byte[] prevBytes;

    /* settings / stats */
    private boolean vsynced;
    private long loops, cumLoopTime;

    ////////////////////////////////
    private final Console console;

    private class Console extends JFrame {
        private Console() {
            super( "networld-console" );

            JPanel consolePanel = new JPanel() {
                @Override
                public void paintComponent(Graphics g) {
                    super.paintComponents( g );

                    g.setColor( Color.BLACK );
                    g.fillRect( 0, 1, getWidth(), getHeight() );

                    g.setColor( Color.WHITE );
                    g.drawString( "loops/s: " + loops, 5, 15 );
                    g.drawString( "avg. loop time: " + String.format( "%.2f", cumLoopTime / (1000000f * loops) ), 5,
                            30 );

                    g.setColor( vsynced ? Color.GREEN : Color.RED );
                    g.drawString( "vsynced: " + vsynced, 5, 45 );

                    loops = 0;
                    cumLoopTime = 0;
                }
            };
            consolePanel.setPreferredSize( new Dimension( 300, 100 ) );

            ScheduledExecutorService service = Executors.newScheduledThreadPool( 1 );
            service.scheduleAtFixedRate( (Runnable) consolePanel::repaint, 0, 1, TimeUnit.SECONDS );

            getContentPane().add( consolePanel );

            setDefaultCloseOperation( WindowConstants.EXIT_ON_CLOSE );
            pack();
            setLocationRelativeTo( null );
            setVisible( true );
        }
    }
}
