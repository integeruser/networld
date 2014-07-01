package pongmp;

import java.io.Serializable;

public class Snapshot implements Serializable {
    public long serverTime, clientTime;
    public float ballx, bally;
}
