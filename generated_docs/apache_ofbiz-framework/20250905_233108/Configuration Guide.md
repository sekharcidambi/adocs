## Configuration Guide

## Overview

Apache OFBiz (Open For Business) is a comprehensive enterprise resource planning (ERP) and customer relationship management (CRM) suite built on Java. The configuration system in OFBiz is highly flexible and modular, allowing administrators to customize virtually every aspect of the framework without modifying core source code. This guide covers the essential configuration files, patterns, and best practices for setting up and maintaining an OFBiz installation.

## Core Configuration Architecture

OFBiz follows a hierarchical configuration approach where settings cascade from framework-level defaults down to application-specific overrides. The configuration system is built around several key concepts:

### Configuration File Hierarchy

```
framework/
├── base/config/          # Core framework configurations
├── entity/config/        # Entity engine configurations
├── service/config/       # Service engine configurations
└── webapp/config/        # Web application configurations

applications/
├── [app-name]/config/    # Application-specific configurations
└── [app-name]/webapp/WEB-INF/
```

### Primary Configuration Files

#### 1. `framework/base/config/general.properties`

This is the primary configuration file containing system-wide settings:

```properties
# Database configuration
entity.default.datasource.default=localderby
entity.config.file=entityengine.xml

# Security settings
security.login.password.encrypt=true
security.login.password.encrypt.hash.type=SHA

# Performance tuning
entity.cache.enabled=true
service.semaphore.wait.time=120000

# Debug and logging
debug.level=info
log4j.configuration=log4j2.xml
```

#### 2. `framework/entity/config/entityengine.xml`

Defines database connections, entity groups, and data source configurations:

```xml
<entity-config>
    <resource-loader name="fieldfile" 
                     class="org.apache.ofbiz.base.config.FileLoader"
                     prepend-env="ofbiz.home" 
                     prefix="/framework/entity/fieldtype/"/>
    
    <transaction-factory class="org.apache.ofbiz.entity.transaction.JNDIFactory">
        <user-transaction-jndi jndi-server-name="default" 
                               jndi-name="java:comp/UserTransaction"/>
        <transaction-manager-jndi jndi-server-name="default" 
                                  jndi-name="java:comp/TransactionManager"/>
    </transaction-factory>
    
    <delegator name="default" entity-model-reader="main" 
               entity-group-reader="main" entity-eca-reader="main">
        <group-map group-name="org.apache.ofbiz" datasource-name="localderby"/>
    </delegator>
</entity-config>
```

#### 3. `framework/service/config/serviceengine.xml`

Configures the service engine, including job scheduling and service groups:

```xml
<service-config>
    <service-engine name="default">
        <thread-pool send-to-pool="pool" 
                     purge-job-days="4" 
                     failed-retry-min="3" 
                     ttl="120000" 
                     jobs="100" 
                     min-threads="2" 
                     max-threads="5"/>
        
        <run-from-pool name="pool"/>
        
        <service-log type="file"/>
        
        <global-services loader="main"/>
        
        <service-groups loader="main"/>
    </service-engine>
</service-config>
```

## Database Configuration

### Datasource Setup

OFBiz supports multiple database systems through JDBC configurations. The most common setup involves configuring datasources in `entityengine.xml`:

```xml
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
            character-set="utf8"
            collate="utf8_general_ci">
    
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
```

### Entity Model Configuration

Entity definitions are loaded through the entity model reader configuration:

```xml
<entity-model-reader name="main">
    <resource loader="fieldfile" location="fieldtypepostgres.xml"/>
    <resource loader="main" location="entitymodel.xml"/>
    <resource loader="main" location="entitygroup.xml"/>
</entity-model-reader>
```

## Web Application Configuration

### Catalina Container Setup

OFBiz includes an embedded Tomcat container configured through `framework/catalina/ofbiz-component.xml`:

```xml
<ofbiz-component name="catalina"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="lib/*"/>
    <classpath type="jar" location="build/lib/*"/>
    
    <container name="catalina-container" 
               loaders="main" 
               class="org.apache.ofbiz.catalina.container.CatalinaContainer">
        <property name="delegator-name" value="default"/>
        <property name="use-naming" value="false"/>
        <property name="debug" value="0"/>
        <property name="catalina-runtime-home" value="runtime/catalina"/>
        <property name="apps-context-reloadable" value="false"/>
        <property name="apps-cross-context" value="false"/>
        <property name="apps-distributable" value="false"/>
    </container>
</ofbiz-component>
```

### Security Configuration

Security settings are managed through multiple configuration layers:

#### Login and Authentication

```properties
# In security.properties
login.max.attempts=3
login.disable.minutes=30
password.length.min=5
password.lowercase.count=0
password.uppercase.count=0
password.numeric.count=1
password.special.char.count=0
```

#### SSL/TLS Configuration

```xml
<!-- In web.xml -->
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

## Performance Tuning

### Cache Configuration

OFBiz provides extensive caching capabilities configured in `cache.properties`:

```properties
# Entity cache settings
cache.entity.default.size=1000
cache.entity.default.expire=0
cache.entity.default.useSoftReference=true

# Service cache settings
cache.service.default.size=500
cache.service.default.expire=3600000

# Specific entity cache overrides
cache.entity.Product.size=10000
cache.entity.ProductCategory.size=5000
```

### JVM Configuration

Recommended JVM

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:47:52*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*