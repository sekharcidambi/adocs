# Framework Architecture

## Overview

Apache OFBiz (Open For Business) implements a sophisticated multi-layered framework architecture designed to support enterprise-grade business applications. The framework follows a service-oriented architecture (SOA) pattern with clear separation of concerns across presentation, business logic, and data access layers. This architecture enables rapid development of complex business applications while maintaining scalability, modularity, and extensibility.

## Core Architectural Layers

### Entity Engine Layer

The Entity Engine forms the foundation of OFBiz's data access architecture, providing a comprehensive Object-Relational Mapping (ORM) solution:

```xml
<!-- Example entity definition in entitymodel.xml -->
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productTypeId" type="id"/>
    <field name="productName" type="name"/>
    <field name="description" type="very-long"/>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

The Entity Engine abstracts database operations through:
- **Entity Definitions**: XML-based schema definitions that generate database tables
- **Delegator Pattern**: Central service for all database operations
- **Generic Values**: Type-safe data containers that eliminate SQL injection risks
- **Dynamic View Entities**: Runtime-generated complex queries without hardcoded SQL

### Service Engine Layer

The Service Engine implements the business logic layer using a service-oriented approach:

```xml
<!-- Service definition example -->
<service name="createProduct" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="productGenericPermission" main-action="CREATE"/>
    <auto-attributes entity-name="Product" include="pk" mode="INOUT" optional="false"/>
    <auto-attributes entity-name="Product" include="nonpk" mode="IN" optional="true"/>
</service>
```

Key service engine features include:
- **Service Definition Framework**: XML-based service contracts with automatic parameter validation
- **Multiple Engine Types**: Support for Java, Simple Methods, Entity-Auto, and Script engines
- **Transaction Management**: Declarative transaction boundaries with rollback capabilities
- **Asynchronous Processing**: Built-in job scheduling and queue management
- **Service Composition**: Ability to chain and orchestrate complex business processes

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
    <screen-map name="ProductForm" location="component://product/widget/ProductScreens.xml"/>
</view-map>
```

The web framework provides:
- **Request/Response Mapping**: Declarative URL routing with security constraints
- **Event Handling**: Integration with service engine for business logic execution
- **Screen Widget System**: Reusable UI components with inheritance and composition
- **Form Widget Framework**: Automatic form generation with validation and data binding

## Component Architecture

### Component Structure

OFBiz applications are organized into self-contained components following a standardized directory structure:

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
│   ├── componentname/
│   │   └── WEB-INF/
│   │       └── controller.xml
│   └── widget/
│       ├── ComponentScreens.xml
│       └── ComponentForms.xml
└── src/main/java/
    └── org/apache/ofbiz/component/
```

### Component Loading and Dependency Management

The framework implements a sophisticated component loading mechanism:

```xml
<!-- component-load.xml configuration -->
<component-loader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <load-component component-location="framework/start"/>
    <load-component component-location="framework/base"/>
    <load-component component-location="applications/product" depends-on="base"/>
</component-loader>
```

Components are loaded in dependency order, ensuring proper initialization sequence and circular dependency detection.

## Integration Patterns

### Inter-Component Communication

Components communicate through well-defined interfaces:

- **Service Calls**: Cross-component business logic invocation
- **Entity Relationships**: Foreign key relationships across component boundaries
- **Event Chains**: Coordinated request processing across multiple components
- **Data Import/Export**: Standardized XML data exchange formats

### External System Integration

The framework supports multiple integration patterns:

```java
// Example service engine integration
public static Map<String, Object> callExternalService(DispatchContext dctx, Map<String, Object> context) {
    LocalDispatcher dispatcher = dctx.getDispatcher();
    Delegator delegator = dctx.getDelegator();
    
    // Business logic implementation
    Map<String, Object> result = ServiceUtil.returnSuccess();
    return result;
}
```

## Configuration and Extensibility

### Framework Configuration

Core framework behavior is controlled through property files and XML configurations:

```properties
# framework/base/config/general.properties
entity.default.datasource.name=localderby
service.semaphore.wait.time=120000
webapp.stats.enable=true
```

### Extension Mechanisms

The architecture supports multiple extension points:

- **Custom Service Engines**: Pluggable execution environments
- **Entity Engine Extensions**: Custom field types and database adapters
- **Widget Extensions**: Custom widget types and renderers
- **Security Extensions**: Pluggable authentication and authorization providers

## Performance and Scalability Considerations

The framework architecture incorporates several performance optimization strategies:

- **Connection Pooling**: Database connection management with configurable pool sizes
- **Service Result Caching**: Automatic caching of service results with TTL support
- **Entity Caching**: Multi-level entity caching with distributed cache support
- **Lazy Loading**: On-demand loading of related entities and collections
- **Horizontal Scaling**: Support for clustered deployments with session replication

This architectural foundation enables OFBiz to handle enterprise-scale deployments while maintaining development agility and system maintainability.

## Subsections

- [High-Level Architecture Overview](./High-Level Architecture Overview.md)
- [Framework Components](./Framework Components.md)
- [Entity Engine Architecture](./Entity Engine Architecture.md)
- [Service Engine Architecture](./Service Engine Architecture.md)
- [Widget Framework](./Widget Framework.md)

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
- **Entity Engine Architecture**: Detailed coverage of entity engine architecture
- **Service Engine Architecture**: Detailed coverage of service engine architecture
- **Widget Framework**: Detailed coverage of widget framework

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:32:14*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*