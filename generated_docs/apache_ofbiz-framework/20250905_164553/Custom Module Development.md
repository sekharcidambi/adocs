## Custom Module Development

## Overview

Custom module development in Apache OFBiz allows developers to extend the framework's functionality while maintaining separation from the core system. This approach ensures that custom business logic remains intact during framework upgrades and follows OFBiz's component-based architecture. Custom modules integrate seamlessly with OFBiz's multi-tier architecture, leveraging the presentation layer for UI components, business logic layer for services and entities, and data access layer for database operations.

## Module Structure and Architecture

### Component Directory Layout

Custom modules in OFBiz follow a standardized directory structure within the framework's component-based architecture:

```
/framework/
/applications/
/specialpurpose/
/hot-deploy/          # Legacy location for custom modules
/plugins/             # Recommended location for custom modules
  /your-custom-module/
    ├── build.gradle
    ├── ofbiz-component.xml
    ├── config/
    ├── data/
    ├── entitydef/
    ├── servicedef/
    ├── src/
    ├── webapp/
    └── widget/
```

### Component Configuration

The `ofbiz-component.xml` file serves as the module's configuration backbone:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="your-custom-module"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="build/lib/*"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" 
                    loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" 
                    loader="main" location="data/CustomModuleTypeData.xml"/>
    
    <service-resource type="model" loader="main" 
                     location="servicedef/services.xml"/>
    
    <webapp name="custommodule" title="Custom Module"
            server="default-server" location="webapp/custommodule"
            base-permission="CUSTOMMODULE" mount-point="/custommodule"/>
</ofbiz-component>
```

## Entity Development

### Entity Definition

Custom entities are defined in `entitydef/entitymodel.xml` and automatically integrate with OFBiz's data access layer:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <entity entity-name="CustomProduct" package-name="com.yourcompany.custommodule">
        <field name="customProductId" type="id-ne"/>
        <field name="productName" type="name"/>
        <field name="description" type="very-long"/>
        <field name="price" type="currency-amount"/>
        <field name="createdDate" type="date-time"/>
        <field name="lastModifiedDate" type="date-time"/>
        
        <prim-key field="customProductId"/>
        
        <relation type="one" fk-name="CUST_PROD_PARTY" rel-entity-name="Party">
            <key-map field-name="partyId"/>
        </relation>
    </entity>
</entitymodel>
```

### Entity Data Loading

Seed data can be loaded through XML files in the `data/` directory:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<entity-engine-xml>
    <CustomProduct customProductId="CUSTOM_001" 
                   productName="Sample Custom Product"
                   description="This is a sample custom product"
                   price="99.99"
                   createdDate="2024-01-01 00:00:00"/>
</entity-engine-xml>
```

## Service Development

### Service Definition

Services form the core of OFBiz's business logic layer. Define custom services in `servicedef/services.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/services.xsd">
    
    <service name="createCustomProduct" engine="groovy"
             location="component://your-custom-module/groovyScripts/CustomProductServices.groovy"
             invoke="createCustomProduct">
        <description>Create a new custom product</description>
        <attribute name="productName" type="String" mode="IN" optional="false"/>
        <attribute name="description" type="String" mode="IN" optional="true"/>
        <attribute name="price" type="BigDecimal" mode="IN" optional="false"/>
        <attribute name="customProductId" type="String" mode="OUT" optional="false"/>
    </service>
    
    <service name="updateCustomProduct" engine="java"
             location="com.yourcompany.custommodule.CustomProductServices"
             invoke="updateCustomProduct">
        <description>Update an existing custom product</description>
        <attribute name="customProductId" type="String" mode="IN" optional="false"/>
        <attribute name="productName" type="String" mode="IN" optional="true"/>
        <attribute name="price" type="BigDecimal" mode="IN" optional="true"/>
    </service>
</services>
```

### Service Implementation

#### Groovy Implementation

Create service implementations in `groovyScripts/CustomProductServices.groovy`:

```groovy
import org.apache.ofbiz.base.util.UtilDateTime
import org.apache.ofbiz.entity.util.EntityUtil

def createCustomProduct() {
    customProductId = delegator.getNextSeqId("CustomProduct")
    
    customProduct = [
        customProductId: customProductId,
        productName: parameters.productName,
        description: parameters.description,
        price: parameters.price,
        createdDate: UtilDateTime.nowTimestamp(),
        lastModifiedDate: UtilDateTime.nowTimestamp()
    ]
    
    delegator.create("CustomProduct", customProduct)
    
    return [customProductId: customProductId]
}
```

#### Java Implementation

For complex business logic, implement services in Java within `src/main/java/`:

```java
package com.yourcompany.custommodule;

import org.apache.ofbiz.base.util.Debug;
import org.apache.ofbiz.base.util.UtilMisc;
import org.apache.ofbiz.entity.Delegator;
import org.apache.ofbiz.entity.GenericValue;
import org.apache.ofbiz.service.DispatchContext;
import org.apache.ofbiz.service.ServiceUtil;

import java.util.Map;

public class CustomProductServices {
    
    public static Map<String, Object> updateCustomProduct(DispatchContext dctx, 
                                                         Map<String, ? extends Object> context) {
        Delegator delegator = dctx.getDelegator();
        String customProductId = (String) context.get("customProductId");
        
        try {
            GenericValue customProduct = delegator.findOne("CustomProduct", 
                UtilMisc.toMap("customProductId", customProductId), false);
            
            if (customProduct != null) {
                customProduct.setNonPKFields(context);
                customProduct.store();
                return ServiceUtil.returnSuccess();
            } else {
                return ServiceUtil.returnError("Custom product not found");
            }
        } catch (Exception e) {
            Debug.logError(e, "Error updating custom product", module);
            return ServiceUtil.returnError("Error updating custom product: " + e.getMessage());
        }

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: Apache OFBiz is an open source enterprise resource planning (ERP) system
- **Business Domain**: Enterprise Resource Planning
- **Architecture Pattern**: Multi-tier Architecture
- **Key Components**: Presentation Layer, Business Logic Layer, Data Access Layer
- **Stars**: 1200
- **Forks**: 800
- **Size**: 50000 KB

## Technology Stack

### Languages
- Java
- Groovy
- JavaScript

### Frameworks
- Apache OFBiz Framework
- Spring
- Hibernate

### Databases
- MySQL
- PostgreSQL
- Derby

### Frontend
- React
- Angular
- Vue.js

### Devops
- Docker
- Jenkins
- Maven

## Quick Setup

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
./gradlew build
./gradlew ofbiz
```

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:04:32*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*