# Configuration Management

## Overview

Apache OFBiz framework provides a comprehensive configuration management system that allows developers and system administrators to customize and control various aspects of the application without modifying the core source code. The configuration management system is designed to be flexible, hierarchical, and environment-aware, supporting different deployment scenarios from development to production.

## Configuration Architecture

### Configuration Hierarchy

OFBiz follows a layered configuration approach where settings can be overridden at different levels:

1. **Framework Level** - Core framework configurations
2. **Component Level** - Individual component configurations
3. **Application Level** - Application-specific settings
4. **Runtime Level** - Dynamic runtime configurations

### Configuration File Types

The framework utilizes several types of configuration files:

- **Properties Files** (`.properties`) - Key-value configuration pairs
- **XML Configuration Files** - Structured configuration data
- **Groovy Configuration Scripts** - Dynamic configuration logic
- **JSON Configuration Files** - Modern structured configuration format

## Core Configuration Files

### framework/base/config/

#### general.properties
The primary configuration file containing system-wide settings:

```properties
# Database configuration
entityengine.name=default
delegator.name=default

# Security settings
security.login.password.encrypt=true
security.login.password.encrypt.hash.type=SHA

# Cache settings
cache.properties.url=cache.properties

# Debug settings
debug=false
verbose=false
```

#### cache.properties
Cache configuration for improved performance:

```properties
# Default cache settings
cache.default.maxInMemory=10000
cache.default.expireTime=3600000
cache.default.useSoftReference=true

# Entity cache configuration
cache.entity.maxInMemory=5000
cache.entity.expireTime=0
cache.entity.useSoftReference=true
```

#### debug.properties
Debug and logging configuration:

```properties
# Print all SQL statements
print.sql=false
print.entity.sql=false

# Transaction debugging
transaction.debug=false

# Performance monitoring
timer.debug=false
```

### Component Configuration

#### component-load.xml
Defines which components are loaded and their loading order:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component-loader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/component-loader.xsd">
    
    <!-- Framework components -->
    <load-component component-location="framework/start"/>
    <load-component component-location="framework/base"/>
    <load-component component-location="framework/entity"/>
    <load-component component-location="framework/security"/>
    
    <!-- Application components -->
    <load-component component-location="applications/party"/>
    <load-component component-location="applications/product"/>
    <load-component component-location="applications/order"/>
    
    <!-- Custom components -->
    <load-component component-location="plugins/mycompany"/>
</component-loader>
```

#### ofbiz-component.xml
Individual component configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="party"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <!-- Entity model definitions -->
    <entity-resource type="model" reader-name="main" 
                    loader="main" location="entitydef/entitymodel.xml"/>
    
    <!-- Service definitions -->
    <service-resource type="model" loader="main" 
                     location="servicedef/services.xml"/>
    
    <!-- Web applications -->
    <webapp name="party"
            title="Party Manager"
            server="default-server"
            location="webapp/party"
            base-permission="PARTYMGR,PARTY"
            mount-point="/party"/>
</ofbiz-component>
```

## Database Configuration

### Entity Engine Configuration

#### framework/entity/config/entityengine.xml
Central database configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entity-config.xsd">
    
    <!-- Resource loaders -->
    <resource-loader name="fieldfile" class="org.apache.ofbiz.base.config.FileLoader"
            prepend-env="ofbiz.home" prefix="/framework/entity/fieldtype/"/>
    
    <!-- Transaction factory -->
    <transaction-factory class="org.apache.ofbiz.entity.transaction.JNDIFactory">
        <user-transaction-jndi jndi-server-name="default" jndi-name="java:comp/UserTransaction"/>
        <transaction-manager-jndi jndi-server-name="default" jndi-name="java:comp/TransactionManager"/>
    </transaction-factory>
    
    <!-- Delegator -->
    <delegator name="default" entity-model-reader="main" entity-group-reader="main">
        <group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>
        <group-map group-name="org.apache.ofbiz.olap" datasource-name="localpostgresOlap"/>
    </delegator>
    
    <!-- Datasource definitions -->
    <datasource name="localpostgres"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="postgres"
            check-on-start="true"
            add-missing-on-start="true"
            use-pk-constraint-names="false">
        
        <read-data reader-name="tenant"/>
        <read-data reader-name="seed"/>
        <read-data reader-name="seed-initial"/>
        <read-data reader-name="demo"/>
        <read-data reader-name="ext"/>
        
        <inline-jdbc
                jdbc-driver="org.postgresql.Driver"
                jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
                jdbc-username="ofbiz"
                jdbc-password="ofbiz"
                isolation-level="ReadCommitted"
                pool-minsize="2"
                pool-maxsize="250"
                time-between-eviction-runs-millis="600000"/>
    </datasource>
</entity-config>
```

### Field Type Configuration

Database-specific field type mappings:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<fieldtypes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/fieldtypes.xsd">
    
    <field-type-def type="blob" sql-type="BYTEA" java-type="java.sql.Blob"/>
    <field-type-def type="date-time" sql-type="TIMESTAMPTZ" java-type="java.sql.Timestamp"/>
    <field-type-def type="currency-amount" sql-type="NUMERIC(18,3)" java-type="java.math.BigDecimal"/>
    <field-type-def type="id" sql-type="VARCHAR(20)" java-type="String"/>
    <field-type-def type="id-long" sql-type="VARCHAR(60)" java-type="String"/>
    <field-type-def type="id-vlong" sql-type="VARCHAR(250)" java-type="String"/>
</fieldtypes>
```

## Web Application Configuration

### Server Configuration

#### framework/catalina/config/server.xml
Tomcat server configuration for web applications:

```xml
<Server port="8005" shutdown="SHUTDOWN">
    <Service name="Catalina">
        <Connector port="8080" protocol="HTTP/1.1"
                   connectionTimeout="20000"
                   redirectPort="8443"
                   maxParameterCount="10000"/>
        
        <Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
                   maxThreads="150" SSLEnabled="true" scheme="https" secure="true"
                   clientAuth="false" sslProtocol="TLS"
                   keystoreFile="framework/base/config/ofbizssl.jks"
                   keystoreType="JKS" keystorePass="changeit"/>
        
        <Engine name="Catalina" defaultHost="localhost">
            <Host name="localhost" appBase="."
                  unpackWARs="true" autoDeploy="true">
                <Valve className="org.apache.catalina.valves.AccessLogValve"
                       directory="runtime/logs"
                       prefix="access_log." suffix=".log"
                       pattern="%h %l %u %t &quot;%r&quot; %s %b" />
            </Host>
        </Engine>
    </Service>
</Server>
```

### Web Application Descriptor

#### WEB-INF/web.xml
Standard web application configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://java.sun.com/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_3_0.xsd"
         version="3.0">
    
    <display-name>OFBiz Party Manager</display-name>
    
    <!-- Context parameters -->
    <context-param>
        <param-name>entityDelegatorName</param-name>
        <param-value>default</param-value>
    </context-param>
    
    <context-param>
        <param-name>localDispatcherName</param-name>
        <param-value>party</param-value>
    </context-param>
    
    <!-- Filters -->
    <filter>
        <filter-name>ContextFilter</filter-name>
        <filter-class>org.apache.ofbiz.webapp.control.ContextFilter</filter-class>
    </filter>
    
    <filter-mapping>
        <filter-name>ContextFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    
    <!-- Control servlet -->
    <servlet>
        <servlet-name>ControlServlet</servlet-name>
        <servlet-class>org.apache.ofbiz.webapp.control.ControlServlet</servlet-class>
        <load-on-startup>1</load-on-startup>
    </servlet>
    
    <servlet-mapping>
        <servlet-name>ControlServlet</servlet-name>
        <url-pattern>/control/*</url-pattern>
    </servlet-mapping>
</web-app>
```

## Security Configuration

### Security Configuration Files

#### framework/security/config/security.properties
Security-related configurations:

```properties
# Password encryption
password.encrypt=true
password.encrypt.hash.type=SHA-256
password.encrypt.key.location=framework/security/config/security.key

# Login settings
login.max.attempts=3
login.disable.minutes=30
login.password.require.digits=true
login.password.require.lowercase=true
login.password.require.uppercase=true
login.password.require.symbols=true
login.password.min.length=8

# Session settings
security.session.timeout=3600
security.session.strict=true

# CSRF protection
csrf.defense.enabled=true
csrf.defense.strategy=token
```

#### HTTPS Configuration
SSL/TLS configuration for secure communications:

```properties
# SSL settings
https.port=8443
https.keystore=framework/base/config/ofbizssl.jks
https.keystore.type=JKS
https.keystore.password=changeit
https.key.alias=ofbiz
https.key.password=changeit

# Force HTTPS for sensitive operations
force.https.login=true
force.https.checkout=true
force.https.payment=true
```

## Service Configuration

### Service Engine Configuration

#### framework/service/config/serviceengine.xml
Service engine and job scheduler configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<service-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/service-config.xsd">
    
    <service-engine name="default">
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
        
        <notification-group name="default">
            <notification subject="Service Failure"
                         screen="component://content/widget/EmailScreens.xml#ServiceNotification"/>
        </notification-group>
    </service-engine>
    
    <!-- JMS Configuration -->
    <jms-service name="serviceMessenger" send-mode="all">
        <server jndi-server-name="default"
                jndi-name="connectionFactory"
                topic-queue="topic"
                type="topic"
                username="admin"
                password="admin"
                listen="true"/>
    </jms-service>
</service-config>
```

## Environment-Specific Configuration

### Development Configuration

Create environment-specific property files:

```properties
# config/development.properties
debug=true
verbose=true
print.sql=true
cache.entity.expireTime=60000

# Development database
entityengine.name=development
jdbc-uri=jdbc:postgresql://localhost:5432/ofbiz_dev
```

### Production Configuration

```properties
# config/production.properties
debug=false
verbose=false
print.sql=false
cache.entity.expireTime=0

# Production database with connection pooling
entityengine.name=production
jdbc-uri=jdbc:postgresql://prod-db:5432/ofbiz_prod
pool-maxsize=100
pool-minsize=10
```

### Configuration Loading Strategy

```java
// Example of environment-aware configuration loading
public class ConfigurationManager {
    
    public static Properties loadConfiguration() {
        Properties props = new Properties();
        
        // Load base configuration
        props.load(new FileInputStream("config/general.properties"));
        
        // Override with environment-specific settings
        String environment = System.getProperty("ofbiz.environment", "development");
        File envConfig = new File("config/" + environment + ".properties");
        
        if (envConfig.exists()) {
            Properties envProps = new Properties();
            envProps.load(new FileInputStream(envConfig));
            props.putAll(envProps);
        }
        
        // Override with system properties
        props.putAll(System.getProperties());
        
        return props;
    }
}
```

## Plugin Configuration Management

### Plugin Configuration Structure

```
plugins/
├── mycompany/
│   ├── config/
│   │   ├── MyCompanyConfig.properties
│   │   └── MyCompanyUiLabels.xml
│   ├── ofbiz-component.xml
│   └── servicedef/
│       └── services.xml
```

### Plugin Component Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="mycompany"
        xmlns:xsi="http