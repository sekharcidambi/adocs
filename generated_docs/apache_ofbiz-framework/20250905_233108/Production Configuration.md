## Production Configuration

## Overview

Apache OFBiz production configuration encompasses the critical settings, optimizations, and deployment strategies required to run OFBiz applications in enterprise production environments. This configuration layer transforms the development-friendly default settings into a robust, secure, and performant system capable of handling real-world business operations across multiple domains including ERP, CRM, and e-commerce.

The production configuration in OFBiz is distributed across multiple configuration files, primarily located in the `framework/base/config/`, `framework/entity/config/`, `framework/security/config/`, and application-specific configuration directories. These configurations control everything from database connections and security policies to performance tuning and logging strategies.

## Database Configuration for Production

### Entity Engine Configuration

The heart of OFBiz production database configuration lies in the `entityengine.xml` file. For production deployments, this configuration must be optimized for your specific database platform:

```xml
<delegator name="default" entity-model-reader="main" entity-group-reader="main" entity-eca-reader="main" distributed-cache-clear-enabled="false">
    <group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>
    <group-map group-name="org.apache.ofbiz.olap" datasource-name="localpostgresolap"/>
    <group-map group-name="org.apache.ofbiz.tenant" datasource-name="localpostgrestenant"/>
</delegator>

<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="public"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    drop-fk-use-foreign-key-keyword="true"
    table-type="TABLE"
    character-set="utf8"
    collate="utf8_general_ci">
    
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://prod-db-server:5432/ofbiz"
        jdbc-username="${env:OFBIZ_DB_USER}"
        jdbc-password="${env:OFBIZ_DB_PASSWORD}"
        isolation-level="ReadCommitted"
        pool-minsize="5"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

### Connection Pool Optimization

Production environments require careful tuning of database connection pools. The `pool-maxsize` should be calculated based on your expected concurrent user load and database server capacity. A general rule is to set this to 2-3 times your CPU core count on the database server, but this should be validated through load testing.

Key production database settings include:
- **Connection validation**: Enable `test-on-borrow="true"` and set appropriate validation queries
- **Connection timeout**: Configure `pool-sleeptime`, `pool-lifetime`, and `deadlock-maxwait` parameters
- **Transaction isolation**: Set appropriate isolation levels based on your consistency requirements

## Security Configuration

### HTTPS and SSL/TLS Configuration

Production OFBiz deployments must enforce HTTPS across all web applications. Configure the `web.xml` files in each web application to include security constraints:

```xml
<security-constraint>
    <web-resource-collection>
        <web-resource-name>Entire Application</web-resource-name>
        <url-pattern>/*</url-pattern>
    </web-resource-collection>
    <user-data-constraint>
        <transport-guarantee>CONFIDENTIAL</transport-guarantee>
    </user-data-constraint>
</security-constraint>
```

### Authentication and Authorization

The `security.properties` file contains critical production security settings:

```properties
# Password encryption settings
password.encrypt=true
password.encrypt.hash.type=SHA-256
password.encrypt.key.location=component://base/config/ofbizsetup.conf

# Session security
security.login.password.allow.reuse.days=90
security.login.password.change.history.limit=12
security.login.password.min.length=8
security.login.password.max.length=50

# Login attempt restrictions
max.failed.logins=3
login.disable.minutes=30

# CSRF protection
csrf.defense.strategy=token
```

### Token-Based Security

For API integrations and service-oriented architectures, configure JWT token settings in `general.properties`:

```properties
# JWT Configuration
security.jwt.token.expireTime=1800000
security.jwt.token.issuer=Apache-OFBiz
security.jwt.token.audience=ofbiz-users
security.jwt.token.signatureAlgorithm=HS512
```

## Performance and Caching Configuration

### Entity Cache Configuration

OFBiz's distributed caching system requires careful configuration for production environments. The `cache.properties` file should be tuned based on your memory availability and data access patterns:

```properties
# Entity cache settings
cache.entity.max.in.memory=10000
cache.entity.expire.time=3600000
cache.entity.use.soft.reference=true

# Distributed cache settings
cache.distributed.enable=true
cache.distributed.invalidate.across.webapps=true
cache.distributed.invalidate.across.servers=true

# Memory management
cache.memory.max.size=512MB
cache.memory.eviction.policy=LRU
```

### Service Engine Performance

Configure the service engine for optimal performance in `serviceengine.xml`:

```xml
<service-engine name="main">
    <thread-pool send-to-pool="pool" purge-job-days="4" failed-retry-min="3" ttl="120000" jobs="100" min-threads="5" max-threads="15" poll-enabled="true" poll-db-millis="30000">
        <run-from-pool name="pool"/>
    </thread-pool>
    
    <service-location name="main-rmi" location="rmi://localhost:1099/RMIDispatcher"/>
    <service-location name="main-http" location="http://localhost:8080/webtools/control/httpService"/>
    
    <notification-group name="default">
        <notification subject="Service Failure" screen="component://content/widget/EmailScreens.xml#ServiceNotification"/>
        <notify type="email" address="admin@yourcompany.com"/>
    </notification-group>
</service-engine>
```

## Logging and Monitoring Configuration

### Production Logging Strategy

Configure `log4j2.xml` for production environments with appropriate log levels and rotation policies:

```xml
<Configuration status="WARN">
    <Appenders>
        <RollingFile name="RollingFile" fileName="runtime/logs/ofbiz.log" 
                     filePattern="runtime/logs/ofbiz-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} |%X{localDispatcherName}| %5p | %t | %c{1} | %m%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1" modulate="true"/>
                <SizeBasedTriggeringPolicy size="100 MB"/>
            </Policies>
            <DefaultRolloverStrategy max="30"/>
        </RollingFile>
        
        <RollingFile name="ErrorFile" fileName="runtime/logs/error.log"
                     filePattern="runtime/logs/error-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} |%X{localDispatcherName}| %5p | %t | %c{1} | %m%n

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:52:25*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*