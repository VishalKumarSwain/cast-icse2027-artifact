public class Box implements java.io.Serializable {
    public int length_renamed;
    public int width;
    public int height;

    public Box() {
        this.length_renamed = 0;
        this.width = 0;
        this.height = 0;
    }

    public Box(int l, int w, int h) {
        this.length_renamed = l;
        this.width = w;
        this.height = h;
    }

    public void display() {
        System.out.println("Length = " + this.length_renamed + ", Width = " + this.width + ", Height = " + this.height);
    }

    public long calculateVolume() {
        return (long) this.length_renamed * this.width * this.height;
    }
}

class DemoBox {
    public static void main(String[] args) {
        Box box1 = new Box();
        box1.length_renamed = 5;
        box1.width = 6;
        box1.height = 7;
        box1.display();
        System.out.println("Box1 Volume = " + box1.calculateVolume());

        int len = 10;
        int width = 20;
        int height = 30;
        Box box2 = new Box(len, width, height);
        box2.display();
        System.out.println("Box2 Volume = " + box2.calculateVolume());
    }
}
