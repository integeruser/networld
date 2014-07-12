package networld.simulation;


public abstract class AbstractObject {
    protected AbstractObject() {
        id = firstFreeId++;
    }

    ////////////////////////////////
    abstract public void update(float dt);

    abstract public void interpolate(AbstractObject start, AbstractObject end, float ratio);

    abstract public void render();

    ////////////////////////////////
    private static long firstFreeId = 0;

    public long id;
}
