# Development and Customization

## Overview

Apache OFBiz (Open For Business) is a comprehensive enterprise automation software suite that provides a robust framework for developing and customizing business applications. The development and customization capabilities of OFBiz are built around its component-based architecture, service-oriented design, and extensive configuration options that allow developers to extend functionality without modifying core framework code.

## Development Architecture

### Component-Based Structure

OFBiz follows a modular component architecture where each business function is encapsulated in separate components. Development and customization work primarily within this structure:

```
framework/
├── applications/          # Business applications (accounting, catalog, etc.)
├── base/                 # Core framework components
├── common/               # Shared utilities and services
├── entity/               # Entity engine and data model
├── service/              # Service engine
├── webapp/               # Web application framework
└── widget/               # Screen, form, and menu widgets
```

### Hot-Deploy Components

The most common approach for customization is creating hot-deploy components that extend or override default functionality:

```
hot-deploy/
└── your-component/
    ├── config/
    │   └── ComponentConfig.xml
    ├── data/
    │   └── YourComponentData.xml
    ├── entitydef/
    │   └── entitymodel.xml
    ├── script/
    ├── servicedef/
    │   └── services.xml
    ├── webapp/
    │   └── your-webapp/
    └── widget/
        ├── CommonScreens.xml
        ├── YourForms.xml
        └── YourMenus.xml
```

## Service Development

### Service Definition and Implementation

OFBiz services are the primary mechanism for implementing business logic. Services are defined in XML and implemented in various languages:

```xml
<!-- servicedef/services.xml -->
<service name="createCustomProduct" engine="java"
         location="com.yourcompany.product.ProductServices" invoke="createCustomProduct">
    <description>Create a custom product with additional validation</description>
    <attribute name="productId" type="String" mode="INOUT" optional="true"/>
    <attribute name="productName" type="String" mode="IN" optional="false"/>
    <attribute name="customAttribute" type="String" mode="IN" optional="true"/>
</service>
```

Java implementation example:

```java
public static Map<String, Object> createCustomProduct(DispatchContext dctx, Map<String, ?> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    try {
        // Custom validation logic
        String customAttribute = (String) context.get("customAttribute");
        if (UtilValidate.isNotEmpty(customAttribute)) {
            // Perform custom validation
        }
        
        // Call standard product creation service
        Map<String, Object> createProductContext = UtilMisc.toMap(
            "productName", context.get("productName"),
            "userLogin", userLogin
        );
        
        Map<String, Object> result = dispatcher.runSync("createProduct", createProductContext);
        
        return ServiceUtil.returnSuccess("Custom product created successfully");
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("Error creating custom product: " + e.getMessage());
    }
}
```

## Entity Customization

### Extending Data Models

Custom entities and field extensions are defined through entity model XML files:

```xml
<!-- entitydef/entitymodel.xml -->
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <!-- Extend existing entity -->
    <extend-entity entity-name="Product">
        <field name="customField1" type="short-varchar"/>
        <field name="customField2" type="date-time"/>
    </extend-entity>
    
    <!-- Define new custom entity -->
    <entity entity-name="CustomProductAttribute" package-name="org.apache.ofbiz.product.product">
        <field name="productId" type="id-ne"/>
        <field name="attributeName" type="short-varchar"/>
        <field name="attributeValue" type="long-varchar"/>
        <prim-key field="productId"/>
        <prim-key field="attributeName"/>
        <relation type="one" fk-name="CUST_PROD_ATTR_PROD" rel-entity-name="Product">
            <key-map field-name="productId"/>
        </relation>
    </entity>
</entitymodel>
```

## Screen and Form Customization

### Widget-Based UI Development

OFBiz uses a widget-based system for creating user interfaces. Screens, forms, and menus are defined declaratively:

```xml
<!-- widget/CommonScreens.xml -->
<screens xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/widget-screen.xsd">
    
    <screen name="CustomProductView">
        <section>
            <actions>
                <entity-one entity-name="Product" value-field="product"/>
                <service service-name="getCustomProductData" result-map="customData">
                    <field-map field-name="productId" from-field="parameters.productId"/>
                </service>
            </actions>
            <widgets>
                <decorator-screen name="CommonProductDecorator" location="component://product/widget/catalog/CommonScreens.xml">
                    <decorator-section name="body">
                        <include-form name="CustomProductForm" location="component://your-component/widget/YourForms.xml"/>
                    </decorator-section>
                </decorator-screen>
            </widgets>
        </section>
    </screen>
</screens>
```

## Configuration and Properties

### Component Configuration

Each component requires a ComponentConfig.xml file that defines its structure and dependencies:

```xml
<ofbiz-component name="your-component"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="dir" location="build/classes"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/YourComponentData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="your-webapp"
        title="Your Custom Application"
        server="default-server"
        location="webapp/your-webapp"
        base-permission="YOURAPP"
        mount-point="/yourapp"/>
</ofbiz-component>
```

## Best Practices for Development

### Service Layer Design

1. **Separation of Concerns**: Keep business logic in services, not in screens or forms
2. **Transaction Management**: Use service ECAs (Event Condition Actions) for complex workflows
3. **Error Handling**: Always return proper service responses with success/error status
4. **Security**: Implement proper permission checking in services

### Data Model Extensions

1. **Non-Intrusive Extensions**: Use extend-entity rather than modifying core entities
2. **Relationship Integrity**: Maintain proper foreign key relationships
3. **Performance Considerations**: Index custom fields appropriately

### Component Organization

1. **Logical Grouping**: Organize related functionality within single components
2. **Dependency Management**: Minimize dependencies between custom components
3. **Documentation**: Maintain comprehensive documentation for custom components

### Testing and Deployment

Custom components should include comprehensive test suites and follow OFBiz testing patterns:

```java
public class

## Subsections

- [Framework Extension Points](./Framework Extension Points.md)
- [Custom Application Development](./Custom Application Development.md)
- [Data Model Customization](./Data Model Customization.md)
- [Build System and Tools](./Build System and Tools.md)

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
- **Data Model Customization**: Detailed coverage of data model customization
- **Build System and Tools**: Detailed coverage of build system and tools

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:46:38*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*