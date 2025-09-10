# Core Framework Architecture

## Overview

Apache OFBiz's core framework architecture is built on a sophisticated multi-tier design that provides a robust foundation for enterprise resource planning operations. The framework implements a service-oriented architecture (SOA) with clear separation of concerns across presentation, business logic, and data access layers. This architecture enables scalable, maintainable, and extensible enterprise applications through a combination of proven design patterns and modern Java technologies.

## Architectural Layers

### Presentation Layer
The presentation layer in OFBiz utilizes a flexible rendering engine that supports multiple UI technologies:

```xml
<!-- Example screen widget definition -->
<screen name="FindParty">
    <section>
        <actions>
            <set field="titleProperty" value="PartyFindParty"/>
            <set field="headerItem" value="parties"/>
        </actions>
        <widgets>
            <decorator-screen name="main-decorator" location="${parameters.mainDecoratorLocation}">
                <decorator-section name="body">
                    <include-form name="FindParty" location="component://party/widget/partymgr/PartyForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

The framework supports modern frontend frameworks through RESTful APIs while maintaining backward compatibility with its widget-based system.

### Business Logic Layer
The business logic layer is implemented through OFBiz's service engine, which provides:

- **Service Definition Framework**: Services are defined in XML with automatic parameter validation
- **Transaction Management**: Built-in support for distributed transactions across multiple data sources
- **Security Integration**: Role-based access control at the service level

```xml
<!-- Service definition example -->
<service name="createParty" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Party</description>
    <permission-service service-name="partyPermissionCheck" main-action="CREATE"/>
    <auto-attributes include="pk" mode="OUT" optional="false"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
    <override name="statusId" optional="false"/>
</service>
```

### Data Access Layer
OFBiz implements a sophisticated entity engine that provides:

- **Entity Abstraction**: Database-agnostic data modeling through XML entity definitions
- **Connection Pooling**: Optimized database connection management
- **Caching Strategy**: Multi-level caching for improved performance

```xml
<!-- Entity definition example -->
<entity entity-name="Party" package-name="org.apache.ofbiz.party.party">
    <field name="partyId" type="id-ne"/>
    <field name="partyTypeId" type="id"/>
    <field name="externalId" type="id"/>
    <field name="statusId" type="id"/>
    <prim-key field="partyId"/>
    <relation type="one" fk-name="PARTY_PTY_TYP" rel-entity-name="PartyType">
        <key-map field-name="partyTypeId"/>
    </relation>
</entity>
```

## Core Framework Components

### Component Architecture
OFBiz organizes functionality into discrete components, each containing:

```
component/
├── config/
│   └── ComponentName.properties
├── data/
│   └── ComponentNameData.xml
├── entitydef/
│   └── entitymodel.xml
├── script/
│   └── org/apache/ofbiz/component/
├── servicedef/
│   └── services.xml
├── webapp/
│   └── component/
└── widget/
    ├── ComponentScreens.xml
    ├── ComponentForms.xml
    └── ComponentMenus.xml
```

### Service Engine Integration
The service engine provides a unified interface for business logic execution:

```java
// Service invocation example
public static Map<String, Object> createCustomerService(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    try {
        Map<String, Object> createPartyResult = dispatcher.runSync("createParty", context);
        if (ServiceUtil.isError(createPartyResult)) {
            return ServiceUtil.returnError("Error creating party");
        }
        
        return ServiceUtil.returnSuccess("Customer created successfully");
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("Service execution failed: " + e.getMessage());
    }
}
```

### Entity Engine Configuration
The entity engine supports multiple database configurations through datasource definitions:

```xml
<!-- framework/entity/config/entityengine.xml -->
<datasource name="localderby" helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="derby" check-on-start="true" add-missing-on-start="true"
            use-pk-constraint-names="false" use-indices-unique="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="demo"/>
    <inline-jdbc jdbc-driver="org.apache.derby.jdbc.EmbeddedDriver"
                 jdbc-uri="jdbc:derby:runtime/data/derby/ofbiz;create=true"
                 jdbc-username="ofbiz" jdbc-password="ofbiz"
                 isolation-level="ReadCommitted" pool-minsize="2" pool-maxsize="250"/>
</datasource>
```

## Integration Patterns

### Inter-Component Communication
Components communicate through well-defined service interfaces, promoting loose coupling:

```groovy
// Groovy service implementation
import org.apache.ofbiz.service.ServiceUtil

def processOrder = { context ->
    def dispatcher = context.dispatcher
    def delegator = context.delegator
    
    // Validate inventory
    def inventoryResult = dispatcher.runSync("checkInventoryAvailability", [
        productId: context.productId,
        quantity: context.quantity
    ])
    
    if (ServiceUtil.isError(inventoryResult)) {
        return ServiceUtil.returnError("Insufficient inventory")
    }
    
    // Process payment
    def paymentResult = dispatcher.runSync("processPayment", context)
    
    return ServiceUtil.returnSuccess("Order processed successfully")
}
```

### Event-Driven Architecture
OFBiz implements an event-driven model through its Event Condition Action (ECA) system:

```xml
<!-- Event-Condition-Action rule -->
<eca entity="OrderHeader" operation="create" event="return">
    <condition field-name="statusId" operator="equals" value="ORDER_APPROVED"/>
    <action service="sendOrderConfirmation" mode="async"/>
    <action service="updateInventoryReservation" mode="sync"/>
</eca>
```

## Performance Optimization

### Caching Strategy
The framework implements multiple caching layers:

- **Entity Cache**: Automatic caching of frequently accessed entities
- **Service Result Cache**: Configurable caching of service results
- **Screen Widget Cache**: Rendered screen caching for improved response times

### Database Optimization
Entity engine optimizations include:

- **View Entities**: Complex queries defined as virtual entities
- **Batch Operations**: Bulk insert/update capabilities
- **Connection Pooling**: Configurable connection pool management

```xml
<!-- View entity example for reporting -->
<view-entity entity-name="OrderItemAndProduct" package-name="org.apache.ofbiz.order.order">
    <member-entity entity-alias="OI" entity-name="OrderItem"/>
    <member-entity entity-alias="PR" entity-name="Product"/>
    <alias-all entity-alias="OI"/>
    <alias-all entity-alias="PR" prefix="product"/>
    <view-link entity-alias="OI" rel-entity-alias="PR">
        <key-map field-name="productId"/>
    </view-link>
</view-entity>
```

This architecture provides OFBiz with the flexibility to handle complex enterprise requirements while maintaining performance and scalability across diverse deployment scenarios.

## Subsections

- [Presentation Layer](./Presentation Layer.md)
- [Business Logic Layer](./Business Logic Layer.md)
- [Data Access Layer](./Data Access Layer.md)

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

- **Presentation Layer**: Detailed coverage of presentation layer
- **Business Logic Layer**: Detailed coverage of business logic layer
- **Data Access Layer**: Detailed coverage of data access layer

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:49:24*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*