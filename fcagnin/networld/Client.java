package networld;

import networld.networking.Packet;
import networld.simulation.Ball;
import networld.simulation.Square;
import networld.simulation.World;
import org.lwjgl.LWJGLException;
import org.lwjgl.input.Keyboard;
import org.lwjgl.opengl.Display;
import org.lwjgl.opengl.DisplayMode;

import javax.swing.*;
import java.awt.*;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.concurrent.*;
import java.util.zip.DataFormatException;

import static org.lwjgl.opengl.GL11.*;


public class Client {
    public static void main(String[] args) throws LWJGLException, InterruptedException {
        Server.main( null );  // temporary

        Client client = new Client( 400, 400 );
        client.start();

        System.exit( 0 );  // temporary: kill all threads
    }

    ////////////////////////////////
    public Client(int displayWidth, int displayHeight) throws LWJGLException {
        vsync = true;

        // create console before Display to not get window focus
        console = new Console();
        Point consoleLocation = console.getLocation();
        // move console adjacent to Display
        console.setLocation( consoleLocation.x + displayWidth / 2 + console.getWidth() / 2, consoleLocation.y );

        Display.setTitle( "networld" );
        Display.setDisplayMode( new DisplayMode( displayWidth, displayHeight ) );
        Display.setVSyncEnabled( vsync );
        Display.create();

        snapshots = new ConcurrentLinkedQueue<>();
        world = new World();
    }

    ////////////////////////////////
    public void start() {
        ExecutorService service = Executors.newFixedThreadPool( 2 );
        service.submit( () -> {
            try {
                int port = 1337;
                Socket socket = new Socket( "localhost", port );
                ObjectInputStream in = new ObjectInputStream( socket.getInputStream() );

                Packet lastPacket = new Packet();
                while ( true ) {
                    byte[] bytes = (byte[]) in.readObject();
                    byte[] decompressedBytes = Utils.decompress( bytes );

                    byte[] orig = decompressedBytes;
                    if ( prevBytes != null ) { orig = Utils.reconstruct( prevBytes, decompressedBytes ); }

                    prevBytes = orig;

                    ByteBuffer byteBuffer = ByteBuffer.wrap( orig );
                    Packet packet = Packet.deserialize( byteBuffer );

                    // reject late packets
                    if ( lastPacket.serverTime < packet.serverTime ) {
                        snapshots.add( packet );
                        lastPacket = packet;
                    }
                }
            } catch ( IOException | ClassNotFoundException | DataFormatException e ) {
                e.printStackTrace();
                System.exit( -1 );
            }
        } );


        Packet startPacket = new Packet(), endPacket = null;
        while ( !Display.isCloseRequested() ) {
            long time = System.nanoTime();

            processInput();

            final long interpTime = 100000000;
            long renderingTime = System.nanoTime() - interpTime;

            for ( int i = 0; i < World.MAX_OBJECTS; i++ ) {
                if ( startPacket.world.abstractObjects[i] != null ) {
                    if ( world.abstractObjects[i] == null ) {
                        if ( startPacket.world.abstractObjects[i] instanceof Ball ) {
                            world.abstractObjects[i] = new Ball( (Ball) startPacket.world.abstractObjects[i] );
                        } else if ( startPacket.world.abstractObjects[i] instanceof Square ) {
                            world.abstractObjects[i] = new Square( (Square) startPacket.world
                                    .abstractObjects[i] );
                        } else {
                            System.out.println( "unrecognized object" );
                        }
                    }
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

                for ( int i = 0; i < World.MAX_OBJECTS; i++ ) {
                    if ( world.abstractObjects[i] != null ) {
                        world.abstractObjects[i].interpolate(
                                startPacket.world.abstractObjects[i],
                                endPacket.world.abstractObjects[i],
                                ratio );
                    }
                }
            } else { System.out.println( "endPacket null" ); }

            if ( Display.wasResized() ) { glViewport( 0, 0, Display.getWidth(), Display.getHeight() ); }

            glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
            world.render();
            Display.update();

            loops++;
            cumLoopTime += System.nanoTime() - time;

            Display.sync( 60 );
        }

        Display.destroy();
    }

    private void processInput() {
        while ( Keyboard.next() ) {
            if ( Keyboard.getEventKeyState() ) {
                if ( Keyboard.getEventKey() == Keyboard.KEY_V ) {
                    vsync = !vsync;
                    Display.setVSyncEnabled( vsync );
                    System.out.println( " V PRESSED" );
                }
            }
        }
    }

    ////////////////////////////////
    private final Console console;

    private final ConcurrentLinkedQueue<Packet> snapshots;
    private final World world;

    private byte[] prevBytes;

    // stats / settings
    private boolean vsync;
    private long loops, cumLoopTime;

    ////////////////////////////////
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
                    g.drawString( "loops/s.: " + loops, 5, 15 );
                    g.drawString( "avg. loop time: " + cumLoopTime / (1000000f * loops), 5, 45 );
                    g.drawString( "vsync: " + vsync, 5, 30 );

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
