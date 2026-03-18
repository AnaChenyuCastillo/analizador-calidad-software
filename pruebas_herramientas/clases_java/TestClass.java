package pruebas_herramientas.clases_java;


public class TestClass {
    private int value;

    public TestClass(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public void increment() {
        value++;
    }

    public void reset() {
        value = 0;
    }
}
