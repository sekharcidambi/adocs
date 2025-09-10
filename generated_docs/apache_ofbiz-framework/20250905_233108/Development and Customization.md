# Development and Customization

## Overview

Apache OFBiz is a highly customizable enterprise framework that provides extensive development and customization capabilities. The framework's modular architecture allows developers to extend existing functionality, create custom applications, and integrate third-party systems while maintaining upgrade compatibility and system integrity.

## Development Environment Setup

### Prerequisites and Configuration

Before beginning development work on OFBiz, ensure your environment meets the framework's requirements:

```bash
# Clone the repository
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework

# Build the framework
./gradlew build

# Load seed and demo data
./gradlew loadAll

# Start the development server
./gradlew ofbiz
```

### IDE Configuration

OFBiz development is optimized for modern IDEs with specific configurations:

- **Eclipse**: Import as Gradle project with OFBiz-specific code formatting rules
- **IntelliJ IDEA**: Configure with Groovy and Freemarker plugin support
- **VS Code**: Install Java Extension Pack and Gradle support

## Component Architecture for Customization

### Component Structure

OFBiz follows a component-based architecture where each component contains:

```
component-name/
├── config/
│   └── ComponentName.properties
├── data/
│   ├── ComponentNameSecurityData.xml
│   └── ComponentNameTypeData.xml
├── entitydef/
│   └── entitymodel.xml
├── script/
│   └── org/apache/ofbiz/componentname/
├── servicedef/
│   └── services.xml
├── src/
│   └── main/java/org/apache/ofbiz/componentname/
├── template/
│   └── ComponentNameScreens.xml
├── webapp/
│   └── componentname/
└── ofbiz-component.xml
```

### Creating Custom Components

To create a new component without modifying core framework files:

```bash
# Create component directory structure
mkdir -p hot-deploy/mycomponent/{config,data,entitydef,script,servicedef,src/main/java,template,webapp}

# Create component descriptor
cat > hot-deploy/mycomponent/ofbiz-component.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="mycomponent"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    <resource-loader name="main" type="component"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/MyComponentTypeData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="mycomponent" title="My Component" server="default-server"
            location="webapp/mycomponent" base-permission="OFBTOOLS,MYCOMPONENT"
            mount-point="/mycomponent"/>
</ofbiz-component>
EOF
```

## Entity Customization Patterns

### Extending Existing Entities

OFBiz supports entity extension through view-entities and field extensions:

```xml
<!-- entitydef/entitymodel.xml -->
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <!-- Extend existing entity -->
    <extend-entity entity-name="Product">
        <field name="customField" type="description"/>
        <field name="customDate" type="date-time"/>
    </extend-entity>
    
    <!-- Create view entity for complex queries -->
    <view-entity entity-name="ProductWithCustomInfo" package-name="org.apache.ofbiz.product.product">
        <member-entity entity-alias="PROD" entity-name="Product"/>
        <member-entity entity-alias="CUST" entity-name="CustomProductInfo"/>
        <alias-all entity-alias="PROD"/>
        <alias entity-alias="CUST" name="customInfo"/>
        <view-link entity-alias="PROD" rel-entity-alias="CUST">
            <key-map field-name="productId"/>
        </view-link>
    </view-entity>
</entitymodel>
```

### Custom Entity Creation

For completely new entities, follow OFBiz naming conventions and relationship patterns:

```xml
<entity entity-name="CustomOrder" package-name="org.apache.ofbiz.mycomponent">
    <field name="customOrderId" type="id" is-pk="true"/>
    <field name="partyId" type="id"/>
    <field name="statusId" type="id"/>
    <field name="orderDate" type="date-time"/>
    <field name="lastUpdatedStamp" type="date-time"/>
    <field name="lastUpdatedTxStamp" type="date-time"/>
    <field name="createdStamp" type="date-time"/>
    <field name="createdTxStamp" type="date-time"/>
    
    <prim-key field="customOrderId"/>
    
    <relation type="one" fk-name="CUST_ORD_PARTY" rel-entity-name="Party">
        <key-map field-name="partyId"/>
    </relation>
    <relation type="one" fk-name="CUST_ORD_STATUS" rel-entity-name="StatusItem">
        <key-map field-name="statusId"/>
    </relation>
</entity>
```

## Service Development and Customization

### Service Implementation Patterns

OFBiz services can be implemented in Java, Groovy, or as entity-auto services:

```xml
<!-- servicedef/services.xml -->
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/services.xsd">
    
    <!-- Java service implementation -->
    <service name="createCustomOrder" engine="java" export="true" auth="true"
            location="org.apache.ofbiz.mycomponent.CustomOrderServices" invoke="createCustomOrder">
        <description>Create Custom Order</description>
        <attribute name="partyId" type="String" mode="IN" optional="false"/>
        <attribute name="orderItems" type="List" mode="IN" optional="false"/>
        <attribute name="customOrderId" type="String" mode="OUT" optional="false"/>
    </service>
    
    <!-- Groovy service implementation -->
    <service name="processCustomOrder" engine="groovy" export="true" auth="true"
            location="component://mycomponent/script/CustomOrderServices.groovy" invoke="processCustomOrder">
        <attribute name="customOrderId" type="String" mode="IN" optional="false"/>
        <attribute name="processResult" type="String" mode="OUT" optional="false"/>
    </service>
    
    <!-- Entity-auto service for CRUD operations -->
    <service name="updateCustomOrder" engine="entity-auto" invoke="update" default-entity-name="CustomOrder">
        <description>Update Custom Order</description>
        <auto-attributes include="pk" mode="IN" optional="false"/>
        <auto-attributes include="nonpk" mode="IN" optional="true"/>
    </service>
</services>
```

### Service Implementation Example

```java
// src/main/java/org/apache/ofbiz/mycomponent/CustomOrderServices.java
package org.apache.ofbiz.mycomponent;

import org.apache.ofbiz.base.util.Debug;
import org.apache.ofbiz.base.util.UtilMisc;
import org.apache.ofbiz.entity.Delegator;
import org.apache.ofbiz.entity.GenericValue;
import org.apache.ofbiz.service.Disp

## Subsections

- [Framework Extension Points](./Framework Extension Points.md)
- [Custom Application Development](./Custom Application Development.md)
- [Integration Patterns](./Integration Patterns.md)

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Framework Extension Points**: Detailed coverage of framework extension points
- **Custom Application Development**: Detailed coverage of custom application development
- **Integration Patterns**: Detailed coverage of integration patterns

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:48:58*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*