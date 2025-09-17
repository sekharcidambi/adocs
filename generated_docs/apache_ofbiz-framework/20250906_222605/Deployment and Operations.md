# Deployment and Operations

This section provides comprehensive guidance for deploying, optimizing, and maintaining Apache OFBiz in production environments. OFBiz is a complex enterprise framework that requires careful consideration of deployment strategies, performance tuning, and ongoing operational practices.

## Production Deployment

### Prerequisites and Environment Setup

Before deploying OFBiz to production, ensure your environment meets the following requirements:

#### System Requirements
- **Java**: OpenJDK 11 or higher (recommended: OpenJDK 17)
- **Memory**: Minimum 4GB RAM (recommended: 8GB+ for production)
- **Storage**: At least 10GB free space for application and logs
- **Operating System**: Linux (recommended), Windows, or macOS

#### Database Configuration

OFBiz supports multiple database systems. Configure your production database:

```properties
# framework/entity/config/entityengine.xml
<datasource name="localderby"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="derby"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    join-style="ansi-no-parenthesis"
    result-fetch-size="50">
    
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    
    <inline-jdbc
        jdbc-driver="org.apache.derby.jdbc.EmbeddedDriver"
        jdbc-uri="jdbc:derby:runtime/data/derby/ofbiz;create=true"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

For PostgreSQL production setup:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    join-style="ansi"
    result-fetch-size="50">
    
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="5"
        pool-maxsize="50"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

### Build and Packaging

#### Creating Production Build

Generate a production-ready build with optimized settings:

```bash
# Clean and build the framework
./gradlew cleanAll loadAll

# Create a distribution package
./gradlew createOfbizBackup

# Build without demo data for production
./gradlew "ofbiz --load-data readers=seed,seed-initial,ext"
```

#### Configuration for Production

Update key configuration files for production deployment:

**framework/base/config/ofbiz-containers.xml**:
```xml
<container name="catalina-container" 
    loaders="main,rmi,test" 
    class="org.apache.ofbiz.catalina.container.CatalinaContainer">
    <property name="delegator-name" value="default"/>
    <property name="use-naming" value="false"/>
    <property name="debug" value="0"/>
    <property name="catalina-runtime-home" value="runtime/catalina"/>
    <property name="apps-context-reloadable" value="false"/>
    <property name="apps-cross-context" value="false"/>
    <property name="apps-distributable" value="false"/>
    <property name="enable-request-dump" value="false"/>
</container>
```

**framework/webapp/config/url.properties**:
```properties
# HTTPS Configuration
port.https.enabled=Y
port.https=8443
default.https.port=8443
force.https.host=your-domain.com

# Security headers
strict-transport-security=max-age=31536000; includeSubDomains
x-frame-options=SAMEORIGIN
x-content-type-options=nosniff
```

### Deployment Strategies

#### Docker Deployment

Create a production Dockerfile:

```dockerfile
FROM openjdk:17-jdk-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Create ofbiz user
RUN useradd -m -s /bin/bash ofbiz

# Set working directory
WORKDIR /opt/ofbiz

# Copy OFBiz files
COPY --chown=ofbiz:ofbiz . .

# Set permissions
RUN chmod +x gradlew

# Switch to ofbiz user
USER ofbiz

# Expose ports
EXPOSE 8080 8443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/webtools/control/main || exit 1

# Start OFBiz
CMD ["./gradlew", "ofbiz"]
```

**docker-compose.yml** for production:

```yaml
version: '3.8'

services:
  ofbiz:
    build: .
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - JAVA_OPTS=-Xms2g -Xmx4g -XX:+UseG1GC
    volumes:
      - ofbiz_data:/opt/ofbiz/runtime
      - ofbiz_logs:/opt/ofbiz/runtime/logs
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: ofbiz
      POSTGRES_USER: ofbiz
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ofbiz
    restart: unless-stopped

volumes:
  ofbiz_data:
  ofbiz_logs:
  postgres_data:
```

#### Traditional Server Deployment

For traditional server deployment, create systemd service:

```ini
# /etc/systemd/system/ofbiz.service
[Unit]
Description=Apache OFBiz ERP System
After=network.target

[Service]
Type=forking
User=ofbiz
Group=ofbiz
WorkingDirectory=/opt/ofbiz
ExecStart=/opt/ofbiz/gradlew ofbizBackground
ExecStop=/opt/ofbiz/gradlew "ofbiz --shutdown"
Restart=always
RestartSec=10

Environment=JAVA_OPTS=-Xms2g -Xmx4g -XX:+UseG1GC -XX:+UseStringDeduplication

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable ofbiz
sudo systemctl start ofbiz
sudo systemctl status ofbiz
```

### SSL/TLS Configuration

Configure HTTPS for production security:

**framework/base/config/ofbiz-containers.xml**:
```xml
<property name="https-keystore" value="framework/base/config/ofbizssl.jks"/>
<property name="https-keystore-type" value="JKS"/>
<property name="https-keystore-pass" value="changeit"/>
<property name="https-key-alias" value="ofbiz"/>
```

Generate SSL certificate:

```bash
# Generate keystore
keytool -genkey -alias ofbiz -keyalg RSA -keystore framework/base/config/ofbizssl.jks

# Import CA certificate (if using CA-signed certificate)
keytool -import -alias root -keystore framework/base/config/ofbizssl.jks -trustcacerts -file ca-cert.crt
```

## Performance Optimization

### JVM Tuning

Optimize JVM settings for production workloads:

```bash
# Set in gradle.properties or environment
export JAVA_OPTS="-server \
  -Xms4g \
  -Xmx8g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UseStringDeduplication \
  -XX:+OptimizeStringConcat \
  -XX:+UseCompressedOops \
  -XX:+UseCompressedClassPointers \
  -Djava.awt.headless=true \
  -Dfile.encoding=UTF-8 \
  -Duser.timezone=UTC"
```

### Database Optimization

#### Connection Pool Tuning

Optimize database connection pools in `entityengine.xml`:

```xml
<inline-jdbc
    jdbc-driver="org.postgresql.Driver"
    jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz?prepareThreshold=3&amp;preparedStatementCacheQueries=256&amp;preparedStatementCacheSizeMiB=5"
    jdbc-username="ofbiz"
    jdbc-password="ofbiz"
    isolation-level="ReadCommitted"
    pool-minsize="10"
    pool-maxsize="100"
    pool-sleeptime="300000"
    pool-lifetime="600000"
    pool-deadlock-maxwait="300000"
    pool-deadlock-retrywait="10000"
    time-between-eviction-runs-millis="600000"/>
```

#### Entity Engine Cache Configuration

Configure entity caching in `cache.properties`:

```properties
# Entity cache settings
cache.entity.default.maxSize=10000
cache.entity.default.expireTime=3600000
cache.entity.default.useSoftReference=true

# Specific entity cache tuning
cache.entity.Party.maxSize=50000
cache.entity.Product.maxSize=100000
cache.entity.ProductStore.maxSize=1000
```

### Application-Level Optimizations

#### Service Engine Tuning

Optimize service execution in `serviceengine.xml`:

```xml
<service-engine name="main">
    <thread-pool send-to-pool="pool"
                 purge-job-days="4"
                 failed-retry-min="3"
                 ttl="120000"
                 jobs="100"
                 min-threads="5"
                 max-threads="15"
                 poll-enabled="true"
                 poll-db-millis="30000">
        <run-from-pool name="pool"/>
    </thread-pool>
</service-engine>
```

#### Widget and Screen Optimization

Enable screen widget caching:

```xml
<!-- framework/widget/config/widget.properties -->
<property name="widget.screen.cache" value="true"/>
<property name="widget.form.cache" value="true"/>
<property name="widget.menu.cache" value="true"/>
<property name="widget.tree.cache" value="true"/>
```

### Web Server Optimization

#### Nginx Reverse Proxy Configuration

Configure Nginx for optimal performance:

```nginx
upstream ofbiz_backend {
    server 127.0.0.1:8080 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8081 max_fails=3 fail_timeout=30s backup;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;

    # Static file caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        proxy_pass http://ofbiz_backend;
    }

    location / {
        proxy_pass http://ofbiz_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
}
```

## Monitoring and Maintenance

### Application Monitoring

#### Health Check Endpoints

Implement custom health check services:

```java
// In a custom service file
public static Map<String, Object> systemHealthCheck(DispatchContext dctx, Map<String, ? extends Object> context) {
    Map<String, Object> result = ServiceUtil.returnSuccess();
    
    // Check database connectivity
    Delegator delegator = dctx.getDelegator();
    try {
        delegator.findOne("SystemProperty", UtilMisc.toMap("systemResourceId", "general", 
                                                          "systemPropertyId", "instanceId"), false);
        result.put("database", "healthy");
    } catch (Exception e) {
        result.put("database", "unhealthy: " + e.getMessage());
    }
    
    // Check memory usage
    Runtime runtime = Runtime.getRuntime();
    long maxMemory = runtime.maxMemory();
    long totalMemory = runtime.totalMemory();
    long freeMemory = runtime.freeMemory();
    long usedMemory = totalMemory - freeMemory;
    
    Map<String, Object> memoryInfo = new HashMap<>();
    memoryInfo.put("used", usedMemory);
    memoryInfo.put("free", freeMemory);
    memoryInfo.put("total", totalMemory);
    memoryInfo.put("max", maxMemory);
    memoryInfo.put("usage_percent", (usedMemory * 100) / maxMemory);
    
    result.put("memory", memoryInfo);
    
    return result;
}
```

#### JMX Monitoring

Enable JMX for monitoring:

```bash
export JAVA_OPTS="$JAVA_OPTS \
  -Dcom.sun.management.jmxremote \
  