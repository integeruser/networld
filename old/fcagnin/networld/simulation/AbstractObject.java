package networld.simulation;


public abstract class AbstractObject {
    abstract public void update(float dt);

    abstract public void interpolate(AbstractObject start, AbstractObject end, float ratio);

    abstract public void render();
}
