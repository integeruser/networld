package pongmp;

import java.io.Serializable;


public class Snapshot implements Serializable {
    public Snapshot() {
        balls = new byte[0];
    }

    public long serverTime, clientTime;
    public byte[] balls;
}
