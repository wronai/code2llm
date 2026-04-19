// Java - valid code (demo)

public class Order {
    private int id;
    private String item;

    public Order(int id, String item) {
        this.id = id;
        this.item = item;
    }

    public int getId() { return id; }
    public String getItem() { return item; }
}

class OrderService {
    private java.util.List<Order> orders = new java.util.ArrayList<>();

    public void addOrder(Order order) {
        orders.add(order);
    }

    public Order getOrder(int id) {
        for (Order order : orders) {
            if (order.getId() == id) {
                return order;
            }
        }
        return null;
    }

    public void processOrders() {
        for (Order order : orders) {
            System.out.println("Order: " + order.getItem());
        }
    }

    public static void main(String[] args) {
        OrderService service = new OrderService();
        service.addOrder(new Order(1, "Widget"));

        Order order = service.getOrder(1);
        if (order != null) {
            System.out.println("Found: " + order.getItem());
        }
    }
}
