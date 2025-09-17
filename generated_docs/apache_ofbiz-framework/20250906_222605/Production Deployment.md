# Production Deployment

This section provides comprehensive guidance for deploying Apache OFBiz framework applications to production environments. It covers security hardening, performance optimization, monitoring, and maintenance procedures specific to OFBiz-based systems.

## Overview

Production deployment of OFBiz requires careful consideration of security, performance, scalability, and maintainability. This framework, being a comprehensive enterprise resource planning (ERP) and customer relationship management (CRM) suite, handles sensitive business data and requires robust deployment practices.

## Pre-Deployment Checklist

### System Requirements Verification

Before deploying to production, ensure your environment meets the following requirements:

- **Java Version**: OpenJDK 11 or higher (recommended: OpenJDK 17 LTS)
- **Memory**: Minimum 4GB RAM (recommended: 8GB+ for production workloads)
- **Storage**: SSD storage with adequate space for database growth
- **Network**: Stable network connectivity with appropriate bandwidth

### Database Configuration

#### Supported Database Systems

OFBiz supports multiple database systems for production deployment:

```xml
<!-- Example database configuration in entityengine.xml -->
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    drop-fk-use-foreign-key-keyword="true"
    table-type="TABLE"
    character-set="UTF-8"
    collate="utf8_general_ci">
    
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

#### Database Performance Tuning

Configure your database for optimal performance:

```sql
-- PostgreSQL optimization example
-- Adjust postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

## Security Hardening

### SSL/TLS Configuration

Configure HTTPS for secure communication:

```xml
<!-- framework/webapp/config/url.properties -->
port.https=8443
port.https.enabled=true

<!-- Configure SSL in ofbiz-containers.xml -->
<container name="catalina-container" loaders="main,rmi,pos" class="org.apache.ofbiz.catalina.container.CatalinaContainer">
    <property name="delegator-name" value="default"/>
    <property name="use-naming" value="false"/>
    <property name="debug" value="0"/>
    <property name="catalina-runtime-home" value="runtime/catalina"/>
    <property name="apps-context-reloadable" value="false"/>
    <property name="apps-cross-context" value="false"/>
    <property name="apps-distributable" value="false"/>
    
    <!-- HTTPS Connector -->
    <property name="https-port" value="8443"/>
    <property name="https-host" value="0.0.0.0"/>
    <property name="ssl-accelerator-port" value="8443"/>
    <property name="enable-cross-subdomain-sessions" value="false"/>
    <property name="keystore-file" value="framework/base/config/ofbizssl.jks"/>
    <property name="keystore-pass" value="changeit"/>
    <property name="keystore-type" value="JKS"/>
    <property name="keystore-alias" value="ofbiz"/>
</container>
```

### Authentication and Authorization

#### Configure Strong Password Policies

```xml
<!-- framework/security/config/security.properties -->
password.length.min=8
password.lowercase.count=1
password.uppercase.count=1
password.digit.count=1
password.special.count=1
login.max.failed.attempts=3
login.disable.minutes=30
```

#### Session Security

```xml
<!-- Configure session timeout and security -->
<session-config>
    <session-timeout>30</session-timeout>
    <cookie-config>
        <http-only>true</http-only>
        <secure>true</secure>
        <same-site>Strict</same-site>
    </cookie-config>
    <tracking-mode>COOKIE</tracking-mode>
</session-config>
```

### Firewall and Network Security

Configure your firewall to allow only necessary ports:

```bash
# Example iptables rules
iptables -A INPUT -p tcp --dport 8080 -j DROP  # Block HTTP in production
iptables -A INPUT -p tcp --dport 8443 -j ACCEPT # Allow HTTPS
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH access
iptables -A INPUT -p tcp --dport 5432 -j DROP   # Block direct database access
```

## Performance Optimization

### JVM Tuning

Configure JVM parameters for production workloads:

```bash
# Example JVM settings in start script
export JAVA_OPTS="-server \
    -Xms2048m \
    -Xmx4096m \
    -XX:MaxMetaspaceSize=512m \
    -XX:+UseG1GC \
    -XX:+UseStringDeduplication \
    -XX:+OptimizeStringConcat \
    -XX:+UseCompressedOops \
    -Djava.awt.headless=true \
    -Djava.net.preferIPv4Stack=true \
    -Dfile.encoding=UTF-8"
```

### Caching Configuration

#### Entity Cache Optimization

```xml
<!-- framework/entity/config/cache.xml -->
<cache-config>
    <cache name="entity.default" 
           max-size="10000" 
           expire-time="3600000"
           use-soft-reference="true"/>
    
    <cache name="entity.Product" 
           max-size="5000" 
           expire-time="1800000"/>
    
    <cache name="entity.Party" 
           max-size="2000" 
           expire-time="3600000"/>
</cache-config>
```

#### Service Cache Configuration

```xml
<!-- Configure service-level caching -->
<service name="getProductPrice" engine="java" 
         location="org.apache.ofbiz.product.price.PriceServices" 
         invoke="calculateProductPrice" 
         use-transaction="false"
         max-retry="0">
    <attribute name="product" type="GenericValue" mode="IN"/>
    <attribute name="prodCatalogId" type="String" mode="IN" optional="true"/>
    <attribute name="webSiteId" type="String" mode="IN" optional="true"/>
    <attribute name="partyId" type="String" mode="IN" optional="true"/>
    <attribute name="productStoreGroupId" type="String" mode="IN" optional="true"/>
    
    <!-- Enable result caching -->
    <attribute name="basePrice" type="BigDecimal" mode="OUT" optional="true"/>
    <attribute name="price" type="BigDecimal" mode="OUT" optional="true"/>
    <attribute name="listPrice" type="BigDecimal" mode="OUT" optional="true"/>
    <attribute name="defaultPrice" type="BigDecimal" mode="OUT" optional="true"/>
    
    <override name="cache-timeout" value="300"/>
</service>
```

### Database Connection Pooling

Optimize database connection pools for production load:

```xml
<inline-jdbc
    jdbc-driver="org.postgresql.Driver"
    jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz"
    jdbc-username="ofbiz"
    jdbc-password="ofbiz"
    isolation-level="ReadCommitted"
    pool-minsize="10"
    pool-maxsize="100"
    pool-sleeptime="300000"
    pool-lifetime="600000"
    pool-deadlock-maxwait="300000"
    pool-deadlock-retrywait="10000"
    time-between-eviction-runs-millis="600000"
    pool-minsize="5"
    pool-maxsize="50"
    test-on-borrow="true"
    test-on-return="false"
    test-while-idle="true"
    validation-query="SELECT 1"/>
```

## Load Balancing and Clustering

### Multi-Instance Deployment

For high availability, deploy multiple OFBiz instances behind a load balancer:

```nginx
# Nginx load balancer configuration
upstream ofbiz_backend {
    server 10.0.1.10:8080 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8080 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8080 weight=2 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://ofbiz_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Session affinity
        proxy_cookie_path / "/; HTTPOnly; Secure";
    }
}
```

### Session Clustering

Configure session replication across instances:

```xml
<!-- Configure distributed sessions -->
<Manager className="org.apache.catalina.ha.session.DeltaManager"
         expireSessionsOnShutdown="false"
         notifyListenersOnReplication="true"
         maxInactiveInterval="1800"/>

<Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster"
         channelSendOptions="8">
    
    <Manager className="org.apache.catalina.ha.session.DeltaManager"
             expireSessionsOnShutdown="false"
             notifyListenersOnReplication="true"/>
             
    <Channel className="org.apache.catalina.tribes.group.GroupChannel">
        <Membership className="org.apache.catalina.tribes.membership.McastService"
                    address="228.0.0.4"
                    port="45564"
                    frequency="500"
                    dropTime="3000"/>
    </Channel>
</Cluster>
```

## Monitoring and Logging

### Application Monitoring

#### JMX Configuration

Enable JMX for monitoring:

```bash
export JAVA_OPTS="$JAVA_OPTS \
    -Dcom.sun.management.jmxremote \
    -Dcom.sun.management.jmxremote.port=9999 \
    -Dcom.sun.management.jmxremote.authenticate=true \
    -Dcom.sun.management.jmxremote.ssl=true \
    -Dcom.sun.management.jmxremote.access.file=/path/to/jmxremote.access \
    -Dcom.sun.management.jmxremote.password.file=/path/to/jmxremote.password"
```

#### Health Check Endpoints

Create custom health check services:

```java
// Custom health check service
public class HealthCheckServices {
    
    public static Map<String, Object> systemHealthCheck(DispatchContext dctx, 
                                                        Map<String, ?> context) {
        Map<String, Object> result = ServiceUtil.returnSuccess();
        Map<String, Object> healthStatus = new HashMap<>();
        
        // Check database connectivity
        try {
            Delegator delegator = dctx.getDelegator();
            delegator.findOne("SystemProperty", 
                UtilMisc.toMap("systemResourceId", "general", 
                              "systemPropertyId", "instanceId"), false);
            healthStatus.put("database", "healthy");
        } catch (Exception e) {
            healthStatus.put("database", "unhealthy: " + e.getMessage());
        }
        
        // Check memory usage
        Runtime runtime = Runtime.getRuntime();
        long maxMemory = runtime.maxMemory();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        long usedMemory = totalMemory - freeMemory;
        
        double memoryUsagePercent = (double) usedMemory / maxMemory * 100;
        healthStatus.put("memoryUsage", String.format("%.2f%%", memoryUsagePercent));
        
        result.put("healthStatus", healthStatus);
        return result;
    }
}
```

### Logging Configuration

#### Production Logging Setup

```xml
<!-- framework/base/config/log4j2.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN" shutdownHook="disable">
    <Appenders>
        <!-- Console appender for immediate feedback -->
        <Console name="stdout" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} |%X{localDispatcherName}| %5p | %t | %c{1} | %m%n"/>
        </Console>
        
        <!-- File appenders for production logging -->
        <RollingFile name="main-log" fileName="runtime/logs/ofbiz.log"
                     filePattern="runtime/logs/ofbiz-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} |%X{localDispatcherName}| %5p | %t | %c{1} | %m%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1" modulate="true"/>
                <SizeBasedTriggeringPolicy size="100MB"/>
            </Policies>
            <DefaultRolloverStrategy max="30"/>
        </RollingFile>
        
        <!-- Error log for critical issues -->
        <RollingFile name="error-log" fileName="runtime/logs/error.log"
                     filePattern="runtime/logs/error-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} |%X{localDispatcherName}| %5p | %t | %c{1} | %m%n"/>
            <ThresholdFilter level="ERROR" onMatch="ACCEPT" onMismatch="DENY"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1" modulate="true"/>
                <SizeBasedTriggeringPolicy size="50MB"/>
            </Policies>
            <DefaultRolloverStrategy max="60"/>
        </RollingFile>
    </Appenders>
    
    <Loggers>
        <!-- Reduce verbose logging in production -->
        <Logger name="org.apache.of