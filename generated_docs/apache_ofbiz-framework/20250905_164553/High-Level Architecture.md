# High-Level Architecture

## Overview

Apache OFBiz implements a sophisticated multi-tier architecture designed to support enterprise-scale ERP operations with high modularity, scalability, and maintainability. The framework follows a service-oriented architecture (SOA) pattern with clear separation of concerns across presentation, business logic, and data access layers. This architecture enables organizations to customize and extend functionality while maintaining system integrity and performance.

## Core Architectural Layers

### Presentation Layer
The presentation layer in OFBiz provides multiple interface options to accommodate diverse user requirements and integration scenarios:

- **Web Interface**: Built using the OFBiz Widget System, providing responsive HTML/CSS/JavaScript interfaces
- **REST API**: RESTful web services for external system integration and mobile applications
- **SOAP Services**: Legacy web service support for enterprise system integration
- **Screen Widgets**: Declarative UI components defined in XML that render to HTML

```xml
<!-- Example Screen Widget Definition -->
<screen name="EditProduct">
    <section>
        <actions>
            <entity-one entity-name="Product" value-field="product"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonProductDecorator">
                <decorator-section name="body">
                    <include-form name="EditProduct" location="component://product/widget/catalog/ProductForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

### Business Logic Layer
The business logic layer implements the core ERP functionality through a comprehensive service engine architecture:

#### Service Engine
OFBiz's service engine provides a unified framework for business logic execution with built-in support for:

- **Transaction Management**: Automatic transaction handling with configurable isolation levels
- **Security Authorization**: Role-based access control at the service level
- **Asynchronous Processing**: Job scheduling and background task execution
- **Service Composition**: Ability to chain and orchestrate multiple services

```xml
<!-- Service Definition Example -->
<service name="createProduct" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="catalogPermissionCheck" main-action="CREATE"/>
    <auto-attributes entity-name="Product" include="pk" mode="INOUT" optional="true"/>
    <auto-attributes entity-name="Product" include="nonpk" mode="IN" optional="true"/>
</service>
```

#### Entity Engine
The Entity Engine provides object-relational mapping (ORM) capabilities with:

- **Database Abstraction**: Support for multiple database systems (MySQL, PostgreSQL, Derby)
- **Dynamic Queries**: Flexible query building without SQL
- **Caching**: Multi-level caching for improved performance
- **Data Import/Export**: XML-based data management tools

```java
// Entity Engine Usage Example
GenericValue product = EntityQuery.use(delegator)
    .from("Product")
    .where("productId", productId)
    .queryOne();

List<GenericValue> orders = EntityQuery.use(delegator)
    .from("OrderHeader")
    .where("statusId", "ORDER_APPROVED")
    .orderBy("orderDate")
    .queryList();
```

### Data Access Layer
The data access layer implements a flexible, database-agnostic approach to data management:

#### Entity Model
OFBiz uses XML-based entity definitions that map to database tables:

```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productTypeId" type="id"/>
    <field name="primaryProductCategoryId" type="id"/>
    <field name="productName" type="name"/>
    <field name="description" type="very-long"/>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

#### Database Configuration
The framework supports multiple database configurations through the `entityengine.xml` configuration:

```xml
<datasource name="localderby"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="OFBIZ"
    field-type-name="derby"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
</datasource>
```

## Component Architecture

### Application Components
OFBiz organizes functionality into modular components, each containing:

- **Entity Definitions**: Data model specifications
- **Service Definitions**: Business logic services
- **Screen Definitions**: User interface components
- **Form Definitions**: Input/output form specifications
- **Menu Definitions**: Navigation structure

```
applications/
├── accounting/
│   ├── entitydef/
│   ├── servicedef/
│   ├── widget/
│   └── webapp/
├── manufacturing/
├── humanres/
└── order/
```

### Framework Components
Core framework components provide foundational services:

- **Security**: Authentication, authorization, and encryption services
- **Common**: Shared utilities and common functionality
- **Entity**: Data access and ORM capabilities
- **Service**: Business logic execution engine
- **Webapp**: Web application framework

## Integration Architecture

### External System Integration
OFBiz provides multiple integration patterns for connecting with external systems:

#### Web Services Integration
```groovy
// Groovy service calling external web service
def result = [:]
try {
    def soapClient = new SOAPClient("http://external-system/service?wsdl")
    def response = soapClient.call("getCustomerData", [customerId: parameters.customerId])
    result.customerData = response.data
} catch (Exception e) {
    return ServiceUtil.returnError("Failed to retrieve customer data: ${e.message}")
}
return result
```

#### Message Queue Integration
The framework supports asynchronous messaging through:
- **JMS Integration**: Java Message Service for enterprise messaging
- **Job Scheduler**: Built-in job scheduling for batch processing
- **Event System**: Publish-subscribe event handling

### API Gateway Pattern
OFBiz implements an API gateway pattern through its REST interface:

```java
@Path("/products")
public class ProductResource {
    
    @GET
    @Path("/{productId}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getProduct(@PathParam("productId") String productId) {
        // Service call to retrieve product
        Map<String, Object> result = dispatcher.runSync("getProduct", 
            UtilMisc.toMap("productId", productId));
        return Response.ok(result.get("product")).build();
    }
}
```

## Deployment Architecture

### Multi-Tenant Support
OFBiz supports multi-tenant deployments with:
- **Tenant Isolation**: Separate data spaces for different organizations
- **Shared Services**: Common business logic across tenants
- **Configurable Branding**: Tenant-specific UI customization

### Scalability Patterns
The architecture supports horizontal scaling through:
- **Load Balancing**: Multiple application server instances
- **Database Clustering**: Master-slave database configurations
- **Caching Strategies**: Distributed caching with Redis or Hazelcast

```bash
# Example deployment with Docker
docker-compose up -d --scale ofbiz-app=3
```

This multi-tier architecture provides Apache OFBiz with the flexibility to handle complex enterprise requirements while maintaining clean separation of concerns and enabling extensive customization capabilities.

## Subsections

- [Multi-tier Architecture Overview](./Multi-tier Architecture Overview.md)
- [System Components Mapping](./System Components Mapping.md)

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

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Multi-tier Architecture Overview**: Detailed coverage of multi-tier architecture overview
- **System Components Mapping**: Detailed coverage of system components mapping

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:47:45*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*