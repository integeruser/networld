package pongmp;

public class Utils {
    public static float randomFloat(float min, float max) {
        return (float) (Math.random() * (max - min) + max);
    }
}
