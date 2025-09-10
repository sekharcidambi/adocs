## Configuration Guide

## Overview

Apache OFBiz (Open For Business) is a comprehensive enterprise resource planning (ERP) and customer relationship management (CRM) suite built on Java. The configuration system in OFBiz is highly modular and flexible, allowing administrators to customize nearly every aspect of the framework without modifying core source code. This guide covers the essential configuration files, patterns, and best practices for setting up and maintaining an OFBiz installation.

## Core Configuration Architecture

OFBiz follows a component-based architecture where configuration is distributed across multiple layers:

- **Framework-level configuration**: Global settings that affect the entire system
- **Component-level configuration**: Settings specific to individual business modules
- **Application-level configuration**: Runtime configurations for web applications
- **Entity-level configuration**: Database and data model configurations

### Configuration File Hierarchy

The configuration system follows a strict hierarchy that allows for inheritance and overrides:

```
framework/
├── base/config/
│   ├── cache.xml
│   ├── debug.xml
│   └── general.properties
├── entity/config/
│   ├── entityengine.xml
│   └── delegator.xml
├── service/config/
│   └── serviceengine.xml
└── webapp/config/
    └── url.properties
```

## Essential Configuration Files

### Entity Engine Configuration (`entityengine.xml`)

The Entity Engine is OFBiz's Object-Relational Mapping (ORM) layer. Configuration is managed through `framework/entity/config/entityengine.xml`:

```xml
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entity-config.xsd">
    
    <resource-loader name="fieldfile" class="org.apache.ofbiz.base.config.FileLoader"
                     prepend-env="ofbiz.home" prefix="/framework/entity/fieldtype/"/>
    
    <delegator name="default" entity-model-reader="main" 
               entity-group-reader="main" entity-eca-reader="main">
        <group-map group-name="org.apache.ofbiz" datasource-name="localderby"/>
    </delegator>
    
    <datasource name="localderby"
                helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
                schema-name="OFBIZ"
                check-on-start="true"
                add-missing-on-start="true">
        <read-data reader-name="tenant"/>
        <read-data reader-name="seed"/>
        <read-data reader-name="seed-initial"/>
        <read-data reader-name="demo"/>
        <read-data reader-name="ext"/>
    </datasource>
</entity-config>
```

Key configuration aspects:

- **Delegators**: Define how entities are mapped to data sources
- **Data Sources**: Configure database connections and connection pooling
- **Field Types**: Map OFBiz field types to database-specific column types
- **Entity Groups**: Organize entities for distributed database scenarios

### Service Engine Configuration (`serviceengine.xml`)

OFBiz's Service Oriented Architecture (SOA) is configured through `framework/service/config/serviceengine.xml`:

```xml
<service-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/service-config.xsd">
    
    <service-engine name="default">
        <authorization service-name="userLogin"/>
        <thread-pool send-to-pool="pool"
                     purge-job-days="4"
                     failed-retry-min="3"
                     ttl="120000"
                     jobs="100"
                     min-threads="2"
                     max-threads="5"
                     poll-enabled="true"
                     poll-db-millis="30000">
            <run-from-pool name="pool"/>
        </thread-pool>
    </service-engine>
    
    <service-location name="main-rmi" location="rmi://localhost:1099/RMIDispatcher"/>
    <service-location name="main-http" location="http://localhost:8080/webtools/control/httpService"/>
    
    <notification-group name="default">
        <notification subject="Service Notification"
                      screen="component://content/widget/EmailScreens.xml#ServiceNotification"/>
    </notification-group>
</service-config>
```

Critical configuration elements:

- **Thread Pool Management**: Controls concurrent service execution
- **Service Locations**: Define RMI and HTTP endpoints for distributed services
- **Authorization**: Configure security for service calls
- **Notification Groups**: Set up service result notifications

### Cache Configuration (`cache.xml`)

OFBiz implements extensive caching through `framework/base/config/cache.xml`:

```xml
<cache-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/cache.xsd">
    
    <cache-configuration>
        <default-cache-config>
            <property name="maxInMemory" value="10000"/>
            <property name="eternal" value="false"/>
            <property name="timeToIdleSeconds" value="1800"/>
            <property name="timeToLiveSeconds" value="3600"/>
            <property name="overflowToDisk" value="false"/>
            <property name="diskPersistent" value="false"/>
        </default-cache-config>
        
        <cache name="entity.default" max-size="1000" expire-time="3600000"/>
        <cache name="service.default" max-size="500" expire-time="1800000"/>
        <cache name="content.rendered" max-size="2000" expire-time="7200000"/>
    </cache-configuration>
</cache-config>
```

## Component Configuration

### Component Definition (`ofbiz-component.xml`)

Each OFBiz component requires an `ofbiz-component.xml` file in its root directory:

```xml
<ofbiz-component name="accounting"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="build/lib/*"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/AccountingTypeData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    <service-resource type="eca" loader="main" location="servicedef/secas.xml"/>
    
    <webapp name="accounting"
            title="Accounting"
            server="default-server"
            location="webapp/accounting"
            base-permission="OFBTOOLS,ACCOUNTING"
            mount-point="/accounting"/>
</ofbiz-component>
```

### Web Application Configuration

Each webapp requires a `WEB-INF/web.xml` and `WEB-INF/controller.xml`:

```xml
<!-- controller.xml excerpt -->
<site-conf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/site-conf.xsd">
    
    <include location="component://common/webcommon/WEB-INF/common-controller.xml"/>
    
    <description>Accounting Manager Module Site Configuration File</description>
    
    <handler name="service" type="request" class="org.apache.ofbiz.webapp.event.ServiceEventHandler"/>
    <handler name="service-

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:45:05*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*