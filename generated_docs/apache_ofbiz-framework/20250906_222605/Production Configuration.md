## Production Configuration

## Overview

Apache OFBiz production configuration encompasses the critical settings and optimizations required to deploy and operate the framework in enterprise environments. This configuration layer transforms the development-oriented default setup into a robust, secure, and performant production system capable of handling real-world e-commerce and ERP workloads.

The production configuration in OFBiz spans multiple domains including database connections, security policies, caching strategies, logging levels, and performance tuning parameters. These configurations are primarily managed through property files, XML descriptors, and environment-specific overrides that allow for deployment flexibility across different production environments.

## Core Configuration Files

### Entity Engine Configuration

The `framework/entity/config/entityengine.xml` file serves as the cornerstone of production database configuration. For production deployments, this file requires careful tuning of connection pool settings and transaction management:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="public"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="false"
    use-pk-constraint-names="false"
    constraint-name-clip-length="30">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://prod-db-server:5432/ofbiz"
        jdbc-username="${db.username}"
        jdbc-password="${db.password}"
        isolation-level="ReadCommitted"
        pool-minsize="10"
        pool-maxsize="100"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

Production environments typically require connection pool sizes of 50-200 connections depending on expected concurrent users, with `add-missing-on-start="false"` to prevent automatic schema modifications.

### Security Configuration

The `framework/security/config/security.properties` file contains critical production security settings:

```properties
# Password encryption
password.encrypt=true
password.encrypt.hash.type=SHA-256
password.encrypt.key.location=component://security/config/salt.dat

# Session security
security.login.password.allow.reuse=false
security.login.password.change.history.limit=12
security.login.max.failed.logins=3
security.login.disable.minutes=30

# HTTPS enforcement
security.require.https=true
security.secure.seed.load=true
```

Production deployments must enable password encryption and implement proper session management policies. The salt file location should be secured with appropriate file system permissions (600) and backed up separately from the application code.

### Performance and Caching Configuration

OFBiz utilizes a sophisticated caching system configured through `framework/base/config/cache.properties`:

```properties
# Entity cache settings for production
cache.entity.default.maxInMemory=10000
cache.entity.default.expireTime=3600000
cache.entity.default.useSoftReference=true

# Service cache configuration
cache.service.default.maxInMemory=5000
cache.service.default.expireTime=1800000

# Distributed cache settings
cache.distributed.enable=true
cache.distributed.invalidate.across.webapps=true
```

Production environments benefit from larger cache sizes and longer expiration times, balanced against available heap memory. The distributed cache settings become crucial in clustered deployments where cache invalidation must propagate across multiple application instances.

## Environment-Specific Overrides

### Property File Hierarchy

OFBiz implements a hierarchical property loading system that supports production-specific overrides:

1. **Base properties**: Located in component-specific `config/` directories
2. **Environment overrides**: `runtime/properties/` directory for deployment-specific values
3. **System properties**: JVM arguments that take highest precedence

Production deployments typically create environment-specific property files:

```bash
runtime/properties/
├── production.properties
├── database-production.properties
└── security-production.properties
```

### Database Connection Management

Production database configuration requires external credential management and connection pooling optimization:

```properties
# runtime/properties/database-production.properties
entityengine.datasource.default.connection.url=jdbc:postgresql://prod-cluster:5432/ofbiz_prod
entityengine.datasource.default.connection.username=${DB_USERNAME}
entityengine.datasource.default.connection.password=${DB_PASSWORD}
entityengine.datasource.default.pool.maxsize=150
entityengine.datasource.default.pool.minsize=25
entityengine.datasource.default.validation.query=SELECT 1
```

## Logging Configuration

Production logging configuration in `framework/base/config/log4j2.xml` requires careful balance between observability and performance:

```xml
<Configuration status="WARN">
    <Appenders>
        <RollingFile name="RollingFile" fileName="runtime/logs/ofbiz.log"
                     filePattern="runtime/logs/ofbiz-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} [%t] %-5level %logger{36} - %msg%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1" modulate="true"/>
                <SizeBasedTriggeringPolicy size="100MB"/>
            </Policies>
            <DefaultRolloverStrategy max="30"/>
        </RollingFile>
    </Appenders>
    <Loggers>
        <Logger name="org.apache.ofbiz" level="INFO"/>
        <Logger name="org.apache.ofbiz.entity.transaction" level="WARN"/>
        <Logger name="org.apache.ofbiz.service" level="INFO"/>
        <Root level="WARN">
            <AppenderRef ref="RollingFile"/>
        </Root>
    </Loggers>
</Configuration>
```

## JVM Configuration

Production JVM settings require careful tuning for OFBiz's memory usage patterns:

```bash
# Production JVM arguments
JAVA_OPTS="-server -Xms2048m -Xmx8192m -XX:MaxMetaspaceSize=512m \
           -XX:+UseG1GC -XX:MaxGCPauseMillis=200 \
           -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=runtime/logs/ \
           -Dfile.encoding=UTF-8 -Duser.timezone=UTC \
           -Dofbiz.home=/opt/ofbiz -Dderby.system.home=runtime/data/derby"
```

## Integration Considerations

### Load Balancer Configuration

Production OFBiz deployments often require session affinity configuration for load balancers. The framework supports both sticky sessions and session replication through the `framework/webapp/config/url.properties`:

```properties
# Session configuration for load balancing
webapp.session.cookie.secure=true
webapp.session.cookie.httponly=true
webapp.session.timeout=3600
```

### Monitoring and Health Checks

OFBiz provides built-in health check endpoints that integrate with production monitoring systems:

- `/control/ping` - Basic application health
- `/control/stats` - Performance metrics
- `/control/cache/stats` - Cache utilization data

These endpoints should be configured with appropriate authentication in production environments while remaining accessible to monitoring infrastructure.

The production configuration of Apache OFBiz requires comprehensive understanding of the framework's architecture and careful attention to security, performance, and operational requirements. Proper configuration ensures the platform can scale to handle enterprise workloads while maintaining security and reliability standards expected in production environments.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:51:48*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*