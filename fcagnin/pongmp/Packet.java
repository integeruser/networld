package pongmp;

import java.io.Serializable;


public class Packet implements Serializable {
    public Packet() {
        balls = new byte[0];
    }

    public long serverTime, clientTime;
    public byte[] balls;
}
