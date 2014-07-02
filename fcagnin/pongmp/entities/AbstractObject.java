package pongmp.entities;

public abstract class AbstractObject {
    abstract public void update(float dt);
    abstract public void interp(AbstractObject start, AbstractObject end, float ratio);
    abstract public void render();
}
