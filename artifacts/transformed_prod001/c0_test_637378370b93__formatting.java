public class Box implements java.io.Serializable {
  public int length;
  public int width;
  public int height;

  public Box() {
    this.length = 0;
    this.width = 0;
    this.height = 0;
  }

  public Box(int l, int w, int h) {
    this.length = l;
    this.width = w;
    this.height = h;
  }

  public void display() {
    System.out.println(
        "Length = " + this.length + ", Width = " + this.width + ", Height = " + this.height);
  }

  public long calculateVolume() {
    return (long) this.length * this.width * this.height;
  }
}

class DemoBox {
  public static void main(String[] args) {
    Box box1 = new Box();
    box1.length = 5;
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
