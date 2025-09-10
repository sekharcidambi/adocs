## Custom Application Development

## Overview

Apache OFBiz provides a comprehensive framework for developing custom applications that leverage its robust enterprise architecture. Custom application development in OFBiz involves creating specialized business modules that integrate seamlessly with the framework's existing components while maintaining the established patterns for data modeling, service definitions, and user interface development.

The framework's modular architecture allows developers to create standalone applications or extend existing functionality through custom components that follow OFBiz conventions. This approach ensures that custom applications benefit from the framework's built-in features including security, internationalization, workflow management, and data persistence layers.

## Application Structure and Organization

### Component Architecture

Custom applications in OFBiz are organized as components within the framework's hierarchical structure. Each custom application should be created as a separate component under the appropriate directory:

```
/framework/
  /base/           # Core framework components
  /common/         # Shared utilities
/applications/     # Standard business applications
/specialpurpose/   # Specialized applications
/hot-deploy/       # Custom applications (development)
/plugins/          # Custom applications (production)
```

For production deployments, custom applications should be placed in the `/plugins/` directory, while development work typically occurs in `/hot-deploy/`. Each component follows a standardized directory structure:

```
custom-app/
├── build.xml                    # Ant build configuration
├── ofbiz-component.xml         # Component definition
├── config/                     # Configuration files
├── data/                       # Seed and demo data
├── entitydef/                  # Entity definitions
├── servicedef/                 # Service definitions
├── src/                        # Java source code
├── webapp/                     # Web application resources
└── widget/                     # Screen, form, and menu definitions
```

### Component Definition

The `ofbiz-component.xml` file serves as the primary configuration for custom applications, defining resource locations, web applications, and dependencies:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="custom-app"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="build/lib/*"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" 
                    loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" 
                    loader="main" location="data/CustomAppSecurityData.xml"/>
    
    <service-resource type="model" loader="main" 
                     location="servicedef/services.xml"/>
    
    <webapp name="custom-app" title="Custom Application"
            server="default-server" location="webapp/custom-app"
            base-permission="CUSTOMAPP" mount-point="/custom-app"/>
</ofbiz-component>
```

## Data Modeling and Entity Development

### Entity Definitions

Custom applications leverage OFBiz's entity engine for data persistence. Entity definitions are created in XML files within the `entitydef/` directory, following the framework's established patterns:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <entity entity-name="CustomProduct" package-name="org.apache.ofbiz.customapp"
            title="Custom Product Entity">
        <field name="productId" type="id-ne"/>
        <field name="productName" type="name"/>
        <field name="description" type="very-long"/>
        <field name="categoryId" type="id"/>
        <field name="createdDate" type="date-time"/>
        <field name="createdByUserLogin" type="id-vlong"/>
        
        <prim-key field="productId"/>
        
        <relation type="one" fk-name="CUST_PROD_CAT" 
                 rel-entity-name="ProductCategory">
            <key-map field-name="categoryId"/>
        </relation>
        
        <relation type="one" fk-name="CUST_PROD_USER" 
                 rel-entity-name="UserLogin">
            <key-map field-name="createdByUserLogin" rel-field-name="userLoginId"/>
        </relation>
    </entity>
</entitymodel>
```

### Database Integration

The entity engine automatically handles database schema generation and maintenance. Custom applications can define upgrade scripts and migration procedures in the `data/` directory to manage schema evolution across deployments.

## Service Layer Development

### Service Definitions

Business logic in custom applications is implemented through services defined in the `servicedef/` directory. Services provide a standardized interface for business operations and integrate with OFBiz's transaction management and security systems:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/services.xsd">
    
    <service name="createCustomProduct" engine="java"
            location="org.apache.ofbiz.customapp.product.ProductServices"
            invoke="createCustomProduct" auth="true">
        <description>Create a new custom product</description>
        <attribute name="productName" type="String" mode="IN" optional="false"/>
        <attribute name="description" type="String" mode="IN" optional="true"/>
        <attribute name="categoryId" type="String" mode="IN" optional="false"/>
        <attribute name="productId" type="String" mode="OUT" optional="false"/>
    </service>
    
    <service name="updateCustomProduct" engine="java"
            location="org.apache.ofbiz.customapp.product.ProductServices"
            invoke="updateCustomProduct" auth="true">
        <description>Update an existing custom product</description>
        <attribute name="productId" type="String" mode="IN" optional="false"/>
        <attribute name="productName" type="String" mode="IN" optional="true"/>
        <attribute name="description" type="String" mode="IN" optional="true"/>
    </service>
</services>
```

### Java Service Implementation

Service implementations are developed as Java classes that follow OFBiz conventions for parameter handling and result processing:

```java
package org.apache.ofbiz.customapp.product;

import java.util.Map;
import org.apache.ofbiz.base.util.Debug;
import org.apache.ofbiz.base.util.UtilMisc;
import org.apache.ofbiz.entity.Delegator;
import org.apache.ofbiz.entity.GenericValue;
import org.apache.ofbiz.service.DispatchContext;
import org.apache.ofbiz.service.ServiceUtil;

public class ProductServices {
    
    public static Map<String, Object> createCustomProduct(DispatchContext dctx, 
                                                         Map<String, ? extends Object> context) {
        Delegator delegator = dctx.getDelegator();
        String productId = delegator.getNextSeqId("CustomProduct");
        
        try {
            GenericValue customProduct = delegator.makeValue("CustomProduct", 
                UtilMisc.toMap("productId", productId,
                              "productName", context.get("productName"),
                              "description", context.get("description"),
                              "categoryId", context.get("categoryId")));
            
            customProduct = delegator.createSetNextSeqId(customProduct);
            
            Map<String, Object> result = ServiceUtil.returnSuccess();
            result.put("productId", productId);
            return result;
            
        } catch (Exception e) {
            Debug.logError(e, "Error creating custom product", module);
            return ServiceUtil.returnError("Error creating custom product

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:50:04*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*