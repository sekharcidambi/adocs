# Network Server Components

## Overview

The Apache OFBiz framework provides a robust set of network server components that enable distributed computing, inter-service communication, and external system integration. These components form the backbone of OFBiz's network architecture, facilitating secure and efficient data exchange across various protocols and communication channels.

## Architecture Overview

OFBiz network server components are built on a modular architecture that supports multiple communication protocols and patterns:

- **Service Engine Integration**: Direct integration with OFBiz's service engine for seamless business logic execution
- **Multi-Protocol Support**: HTTP/HTTPS, RMI, JMS, and custom protocol implementations
- **Security Layer**: Built-in authentication, authorization, and encryption capabilities
- **Load Balancing**: Support for distributed deployments and load distribution
- **Connection Pooling**: Efficient resource management for high-throughput scenarios

## Core Components

### 1. HTTP/HTTPS Server Components

The HTTP server components provide web-based communication capabilities for both REST and SOAP services.

#### Configuration

```xml
<!-- framework/webapp/config/url.properties -->
<web-app>
    <servlet>
        <servlet-name>ControlServlet</servlet-name>
        <servlet-class>org.apache.ofbiz.webapp.control.ControlServlet</servlet-class>
        <init-param>
            <param-name>allowedPaths</param-name>
            <param-value>/control,/select,/index.html,/index.jsp,/default.html,/default.jsp,/images</param-value>
        </init-param>
    </servlet>
</web-app>
```

#### Implementation Example

```java
// Custom HTTP request handler
public class NetworkRequestHandler implements RequestHandler {
    
    private static final String MODULE = NetworkRequestHandler.class.getName();
    
    @Override
    public void init(ServletContext context) throws RequestHandlerException {
        // Initialize network components
        NetworkServerManager.getInstance().initialize();
    }
    
    @Override
    public void handleRequest(HttpServletRequest request, 
                            HttpServletResponse response) 
                            throws RequestHandlerException {
        
        String serviceName = request.getParameter("SERVICE");
        Map<String, Object> serviceContext = new HashMap<>();
        
        try {
            // Extract parameters and build service context
            Enumeration<String> paramNames = request.getParameterNames();
            while (paramNames.hasMoreElements()) {
                String paramName = paramNames.nextElement();
                serviceContext.put(paramName, request.getParameter(paramName));
            }
            
            // Execute service through network layer
            Map<String, Object> result = NetworkServiceDispatcher
                .runSync(serviceName, serviceContext);
            
            // Handle response
            response.setContentType("application/json");
            response.getWriter().write(JSON.from(result).toString());
            
        } catch (Exception e) {
            Debug.logError(e, "Error in network request handling", MODULE);
            throw new RequestHandlerException(e.getMessage());
        }
    }
}
```

### 2. RMI Server Components

Remote Method Invocation (RMI) components enable distributed service calls across JVM boundaries.

#### RMI Service Registry

```java
public class OFBizRMIServiceRegistry {
    
    private static final String MODULE = OFBizRMIServiceRegistry.class.getName();
    private Registry registry;
    private int port;
    
    public void startRegistry(int port) throws RemoteException {
        this.port = port;
        
        try {
            // Create and start RMI registry
            registry = LocateRegistry.createRegistry(port);
            
            // Register core services
            registerCoreServices();
            
            Debug.logInfo("RMI Registry started on port: " + port, MODULE);
            
        } catch (RemoteException e) {
            Debug.logError(e, "Failed to start RMI registry", MODULE);
            throw e;
        }
    }
    
    private void registerCoreServices() throws RemoteException {
        // Register entity engine service
        EntityEngineService entityService = new EntityEngineServiceImpl();
        registry.rebind("EntityEngineService", entityService);
        
        // Register service dispatcher
        ServiceDispatcherRemote serviceDispatcher = new ServiceDispatcherImpl();
        registry.rebind("ServiceDispatcher", serviceDispatcher);
        
        Debug.logInfo("Core RMI services registered", MODULE);
    }
}
```

#### RMI Client Implementation

```java
public class RMIServiceClient {
    
    private static final String MODULE = RMIServiceClient.class.getName();
    private String serverHost;
    private int serverPort;
    
    public RMIServiceClient(String host, int port) {
        this.serverHost = host;
        this.serverPort = port;
    }
    
    public Map<String, Object> invokeRemoteService(String serviceName, 
                                                 Map<String, Object> context) {
        try {
            Registry registry = LocateRegistry.getRegistry(serverHost, serverPort);
            ServiceDispatcherRemote dispatcher = 
                (ServiceDispatcherRemote) registry.lookup("ServiceDispatcher");
            
            return dispatcher.runSync(serviceName, context);
            
        } catch (Exception e) {
            Debug.logError(e, "RMI service invocation failed", MODULE);
            return ServiceUtil.returnError("Remote service call failed: " + e.getMessage());
        }
    }
}
```

### 3. JMS Message Server Components

Java Message Service (JMS) components provide asynchronous messaging capabilities for enterprise integration.

#### JMS Configuration

```xml
<!-- framework/service/config/serviceengine.xml -->
<service-config>
    <service-engine name="jms" class="org.apache.ofbiz.service.jms.JmsServiceEngine">
        <parameter name="send-mode" value="all"/>
        <parameter name="connection-factory-jndi" value="java:comp/env/jms/ConnectionFactory"/>
        <parameter name="queue-jndi" value="java:comp/env/jms/ServiceQueue"/>
        <parameter name="topic-jndi" value="java:comp/env/jms/ServiceTopic"/>
    </service-engine>
</service-config>
```

#### JMS Message Producer

```java
public class OFBizJMSProducer {
    
    private static final String MODULE = OFBizJMSProducer.class.getName();
    private ConnectionFactory connectionFactory;
    private Queue serviceQueue;
    private Topic serviceTopic;
    
    public void initialize() throws JMSException {
        try {
            InitialContext ctx = new InitialContext();
            connectionFactory = (ConnectionFactory) ctx.lookup("java:comp/env/jms/ConnectionFactory");
            serviceQueue = (Queue) ctx.lookup("java:comp/env/jms/ServiceQueue");
            serviceTopic = (Topic) ctx.lookup("java:comp/env/jms/ServiceTopic");
            
        } catch (NamingException e) {
            Debug.logError(e, "JMS initialization failed", MODULE);
            throw new JMSException("Failed to initialize JMS components");
        }
    }
    
    public void sendServiceMessage(String serviceName, Map<String, Object> context, 
                                 boolean persistent) throws JMSException {
        Connection connection = null;
        Session session = null;
        
        try {
            connection = connectionFactory.createConnection();
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
            
            MessageProducer producer = session.createProducer(serviceQueue);
            
            // Create service message
            ObjectMessage message = session.createObjectMessage();
            message.setStringProperty("serviceName", serviceName);
            message.setObject((Serializable) context);
            
            if (persistent) {
                producer.setDeliveryMode(DeliveryMode.PERSISTENT);
            }
            
            producer.send(message);
            Debug.logInfo("Service message sent: " + serviceName, MODULE);
            
        } finally {
            if (session != null) session.close();
            if (connection != null) connection.close();
        }
    }
}
```

#### JMS Message Consumer

```java
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destination", 
                            propertyValue = "java:comp/env/jms/ServiceQueue"),
    @ActivationConfigProperty(propertyName = "destinationType", 
                            propertyValue = "javax.jms.Queue")
})
public class ServiceMessageConsumer implements MessageListener {
    
    private static final String MODULE = ServiceMessageConsumer.class.getName();
    
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof ObjectMessage) {
                ObjectMessage objMessage = (ObjectMessage) message;
                String serviceName = objMessage.getStringProperty("serviceName");
                Map<String, Object> context = (Map<String, Object>) objMessage.getObject();
                
                // Execute service asynchronously
                LocalDispatcher dispatcher = ServiceContainer.getLocalDispatcher(
                    "default", DelegatorFactory.getDelegator("default"));
                
                dispatcher.runAsync(serviceName, context);
                
                Debug.logInfo("Processed async service: " + serviceName, MODULE);
            }
            
        } catch (Exception e) {
            Debug.logError(e, "Error processing JMS message", MODULE);
        }
    }
}
```

## Security Implementation

### SSL/TLS Configuration

```java
public class NetworkSecurityManager {
    
    private static final String MODULE = NetworkSecurityManager.class.getName();
    
    public SSLContext createSSLContext() throws Exception {
        // Load keystore
        KeyStore keyStore = KeyStore.getInstance("JKS");
        String keystorePath = UtilProperties.getPropertyValue("security", 
                                                            "keystore.path");
        String keystorePassword = UtilProperties.getPropertyValue("security", 
                                                                "keystore.password");
        
        try (FileInputStream fis = new FileInputStream(keystorePath)) {
            keyStore.load(fis, keystorePassword.toCharArray());
        }
        
        // Initialize key manager
        KeyManagerFactory kmf = KeyManagerFactory.getInstance(
            KeyManagerFactory.getDefaultAlgorithm());
        kmf.init(keyStore, keystorePassword.toCharArray());
        
        // Initialize trust manager
        TrustManagerFactory tmf = TrustManagerFactory.getInstance(
            TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(keyStore);
        
        // Create SSL context
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), 
                       new SecureRandom());
        
        return sslContext;
    }
}
```

### Authentication and Authorization

```java
public class NetworkAuthenticationHandler {
    
    private static final String MODULE = NetworkAuthenticationHandler.class.getName();
    
    public boolean authenticateRequest(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");
        
        if (UtilValidate.isEmpty(authHeader)) {
            return false;
        }
        
        try {
            // Extract credentials
            String[] credentials = extractCredentials(authHeader);
            String username = credentials[0];
            String password = credentials[1];
            
            // Validate against user login
            Delegator delegator = DelegatorFactory.getDelegator("default");
            GenericValue userLogin = EntityQuery.use(delegator)
                .from("UserLogin")
                .where("userLoginId", username)
                .queryOne();
            
            if (userLogin != null) {
                String hashedPassword = HashCrypt.cryptUTF8(
                    LoginServices.getHashType(), null, password);
                return hashedPassword.equals(userLogin.getString("currentPassword"));
            }
            
        } catch (Exception e) {
            Debug.logError(e, "Authentication error", MODULE);
        }
        
        return false;
    }
    
    private String[] extractCredentials(String authHeader) {
        // Basic authentication implementation
        if (authHeader.startsWith("Basic ")) {
            String encodedCredentials = authHeader.substring(6);
            String decodedCredentials = new String(
                Base64.getDecoder().decode(encodedCredentials));
            return decodedCredentials.split(":", 2);
        }
        
        throw new IllegalArgumentException("Unsupported authentication method");
    }
}
```

## Performance Optimization

### Connection Pooling

```java
public class NetworkConnectionPool {
    
    private static final String MODULE = NetworkConnectionPool.class.getName();
    private final Map<String, ObjectPool<Connection>> connectionPools;
    
    public NetworkConnectionPool() {
        this.connectionPools = new ConcurrentHashMap<>();
    }
    
    public void createPool(String poolName, String serverUrl, 
                          int maxConnections, int maxIdle) {
        
        GenericObjectPoolConfig<Connection> config = new GenericObjectPoolConfig<>();
        config.setMaxTotal(maxConnections);
        config.setMaxIdle(maxIdle);
        config.setMinIdle(1);
        config.setTestOnBorrow(true);
        config.setTestOnReturn(true);
        
        ConnectionFactory factory = new NetworkConnectionFactory(serverUrl);
        ObjectPool<Connection> pool = new GenericObjectPool<>(factory, config);
        
        connectionPools.put(poolName, pool);
        Debug.logInfo("Created connection pool: " + poolName, MODULE);
    }
    
    public Connection borrowConnection(String poolName) throws Exception {
        ObjectPool<Connection> pool = connectionPools.get(poolName);
        if (pool != null) {
            return pool.borrowObject();
        }
        throw new IllegalArgumentException("Pool not found: " + poolName);
    }
    
    public void returnConnection(String poolName, Connection connection) {
        ObjectPool<Connection> pool = connectionPools.get(poolName);
        if (pool != null) {
            try {
                pool.returnObject(connection);
            } catch (Exception e) {
                Debug.logError(e, "Error returning connection to pool", MODULE);
            }
        }
    }
}
```

### Load Balancing

```java
public class NetworkLoadBalancer {
    
    private static final String MODULE = NetworkLoadBalancer.class.getName();
    private final List<ServerNode> serverNodes;
    private final AtomicInteger currentIndex;
    private final LoadBalancingStrategy strategy;
    
    public NetworkLoadBalancer(LoadBalancingStrategy strategy) {
        this.serverNodes = new ArrayList<>();
        this.currentIndex = new AtomicInteger(0);
        this.strategy = strategy;
    }
    
    public ServerNode selectServer() {
        switch (strategy) {
            case ROUND_ROBIN:
                return roundRobinSelection();
            case LEAST_CONNECTIONS:
                return leastConnectionsSelection();
            case WEIGHTED_RANDOM:
                return weightedRandomSelection();
            default:
                return roundRobinSelection();
        }
    }
    
    private ServerNode roundRobinSelection() {
        if (serverNodes.isEmpty()) {
            return null;
        }
        
        int index = currentIndex.getAndIncrement() % serverNodes.size();
        return serverNodes.get(index);
    }
    
    private ServerNode leastConnectionsSelection() {
        return serverNodes.stream()
            .filter(ServerNode::isHealthy)
            .min(Comparator.comparingInt(ServerNode::getActiveConnections))
            .orElse(null);
    }
    
    public enum LoadBalancingStrategy {
        ROUND_ROBIN,
        LEAST_CONNECTIONS,
        WEIGHTED_RANDOM
    }
}
```

## Monitoring and Health Checks

### Network Health Monitor

```java
public class NetworkHealthMonitor {
    
    private static final String MODULE = NetworkHealthMonitor.class.getName();
    private final 