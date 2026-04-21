import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Map;

public class Main {
    private static final int DEFAULT_PORT = 8080;
    
    public static void main(String[] args) throws IOException {
        int port = Integer.parseInt(System.getenv().getOrDefault("PORT", String.valueOf(DEFAULT_PORT)));
        String serviceName = System.getenv().getOrDefault("SERVICE_NAME", "java-api");
        String dbHost = System.getenv().getOrDefault("DB_HOST", "database");
        
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        
        server.createContext("/health", new HealthHandler(serviceName, dbHost));
        server.createContext("/api", new ApiHandler(serviceName, dbHost));
        
        server.setExecutor(null);
        server.start();
        
        System.out.println("Java service listening on port " + port);
    }
    
    static class HealthHandler implements HttpHandler {
        private final String serviceName;
        private final String dbHost;
        
        public HealthHandler(String serviceName, String dbHost) {
            this.serviceName = serviceName;
            this.dbHost = dbHost;
        }
        
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            Map<String, Object> response = new HashMap<>();
            response.put("message", "OK");
            response.put("service", serviceName);
            response.put("language", "Java");
            response.put("version", "21");
            response.put("db_host", dbHost);
            
            sendResponse(exchange, response);
        }
    }
    
    static class ApiHandler implements HttpHandler {
        private final String serviceName;
        private final String dbHost;
        
        public ApiHandler(String serviceName, String dbHost) {
            this.serviceName = serviceName;
            this.dbHost = dbHost;
        }
        
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Hello from Java service!");
            response.put("service", serviceName);
            response.put("language", "Java");
            response.put("version", "21");
            response.put("db_host", dbHost);
            
            sendResponse(exchange, response);
        }
    }
    
    private static void sendResponse(HttpExchange exchange, Map<String, Object> response) throws IOException {
        String json = mapToJson(response);
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(200, json.getBytes().length);
        OutputStream os = exchange.getResponseBody();
        os.write(json.getBytes());
        os.close();
    }
    
    private static String mapToJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (!first) sb.append(",");
            first = false;
            sb.append("\"").append(entry.getKey()).append("\":");
            Object value = entry.getValue();
            if (value instanceof String) {
                sb.append("\"").append(value).append("\"");
            } else {
                sb.append(value);
            }
        }
        sb.append("}");
        return sb.toString();
    }
}
