# Framework Architecture

## Overview

Apache OFBiz (Open For Business) implements a sophisticated multi-layered framework architecture designed to support enterprise-grade business applications. The framework follows a service-oriented architecture (SOA) pattern with clear separation of concerns across presentation, business logic, and data access layers. This architecture enables rapid development of complex business applications while maintaining scalability, modularity, and extensibility.

## Core Architectural Layers

### Entity Engine Layer

The Entity Engine serves as OFBiz's object-relational mapping (ORM) foundation, providing database abstraction and data modeling capabilities:

```xml
<!-- Example entity definition in entitymodel.xml -->
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"></field>
    <field name="productTypeId" type="id"></field>
    <field name="productName" type="name"></field>
    <field name="description" type="very-long"></field>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRODTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

Key characteristics:
- **Database Independence**: Supports multiple database systems through JDBC
- **Dynamic Schema Generation**: Automatically creates database tables from entity definitions
- **Relationship Management**: Handles complex entity relationships and foreign key constraints
- **Caching Layer**: Implements distributed caching for improved performance

### Service Engine Layer

The Service Engine implements the business logic layer using a service-oriented approach:

```xml
<!-- Service definition example -->
<service name="createProduct" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="productGenericPermission" main-action="CREATE"/>
    <auto-attributes include="pk" mode="INOUT" optional="false"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
</service>
```

Service engine features:
- **Multiple Engine Types**: Java, Simple, Entity-auto, Script, and workflow engines
- **Transaction Management**: Automatic transaction handling with rollback capabilities
- **Security Integration**: Built-in authentication and authorization
- **Asynchronous Processing**: Support for background job execution
- **Service Composition**: Ability to chain and orchestrate services

### Web Framework Layer

The presentation layer utilizes a custom MVC framework built on Java servlets:

```xml
<!-- Controller configuration example -->
<request-map uri="createProduct">
    <security https="true" auth="true"/>
    <event type="service" invoke="createProduct"/>
    <response name="success" type="view" value="ProductCreated"/>
    <response name="error" type="view" value="ProductForm"/>
</request-map>

<view-map name="ProductForm" type="screen">
    <screen-path>/component/product/widget/catalog/ProductScreens.xml#ProductForm</screen-path>
</view-map>
```

## Component-Based Architecture

### Component Structure

OFBiz organizes functionality into discrete components, each containing:

```
component/
├── config/
│   └── ComponentName.properties
├── data/
│   └── ComponentNameData.xml
├── entitydef/
│   └── entitymodel.xml
├── servicedef/
│   └── services.xml
├── webapp/
│   ├── WEB-INF/
│   │   └── controller.xml
│   └── widget/
├── script/
└── src/main/java/
```

### Component Integration

Components integrate through well-defined interfaces:

- **Entity Dependencies**: Components can extend or reference entities from other components
- **Service Dependencies**: Cross-component service invocation through the service engine
- **Event Handlers**: Shared event processing across component boundaries
- **Widget Inheritance**: UI components can extend widgets from other components

## Widget Framework

The widget system provides a declarative approach to UI development:

```xml
<!-- Screen widget example -->
<screen name="ProductList">
    <section>
        <actions>
            <service service-name="performFind" result-map="result">
                <field-map field-name="entityName" value="Product"/>
            </service>
        </actions>
        <widgets>
            <decorator-screen name="CommonProductDecorator">
                <decorator-section name="body">
                    <include-grid name="ProductGrid" location="component://product/widget/catalog/ProductForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

Widget types include:
- **Screens**: Page-level containers with actions and rendering logic
- **Forms**: Data entry and display forms with validation
- **Menus**: Navigation structures with conditional rendering
- **Trees**: Hierarchical data display components

## Framework Extensions

### Custom Engine Implementation

Developers can extend the framework by implementing custom service engines:

```java
public class CustomServiceEngine implements GenericEngine {
    public Object runSync(String localName, ModelService modelService, 
                         Map<String, Object> context) throws GenericServiceException {
        // Custom service execution logic
        return ServiceUtil.returnSuccess();
    }
}
```

### Event Handler Extensions

Custom event handlers enable specialized request processing:

```java
public class CustomEventHandler {
    public static String customEvent(HttpServletRequest request, 
                                   HttpServletResponse response) {
        // Custom event processing logic
        return "success";
    }
}
```

## Configuration Management

### Framework Configuration

The framework uses a hierarchical configuration system:

```properties
# framework/start/src/main/resources/start.properties
ofbiz.container.default=component-container
ofbiz.admin.port=10523
ofbiz.admin.key=so3du5kasd5dn
```

### Component Configuration

Each component maintains its own configuration:

```xml
<!-- Component descriptor -->
<ofbiz-component name="product" enabled="true">
    <resource-loader name="main" type="component"/>
    <entity-resource type="model" reader-name="main" 
                    loader="main" location="entitydef/entitymodel.xml"/>
    <service-resource type="model" loader="main" 
                     location="servicedef/services.xml"/>
    <webapp name="catalog" title="Product Catalog" 
            server="default-server" location="webapp/catalog" 
            mount-point="/catalog"/>
</ofbiz-component>
```

## Performance and Scalability

### Caching Strategy

The framework implements multi-level caching:
- **Entity Cache**: Distributed entity-level caching with configurable expiration
- **Service Cache**: Result caching for expensive service operations
- **Screen Cache**: Rendered content caching for improved response times

### Database Optimization

- **Connection Pooling**: Configurable database connection pools per tenant
- **Query Optimization**: Automatic query generation with performance hints
- **Batch Processing**: Bulk operations for large data sets

This architectural approach enables OFBiz to serve as both a complete ERP solution and a flexible framework for custom business application development, supporting everything from small businesses to large enterprise deployments.

## Subsections

- [High-Level Architecture Overview](./High-Level Architecture Overview.md)
- [Framework Components](./Framework Components.md)
- [Service Engine Architecture](./Service Engine Architecture.md)
- [Entity Engine Architecture](./Entity Engine Architecture.md)

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **High-Level Architecture Overview**: Detailed coverage of high-level architecture overview
- **Framework Components**: Detailed coverage of framework components
- **Service Engine Architecture**: Detailed coverage of service engine architecture
- **Entity Engine Architecture**: Detailed coverage of entity engine architecture

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:35:52*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*