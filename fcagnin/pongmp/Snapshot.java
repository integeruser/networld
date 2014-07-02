package pongmp;

import pongmp.entities.Ball;

import java.io.Serializable;

public class Snapshot implements Serializable {
    public long serverTime, clientTime;
    public Ball ball;
}
