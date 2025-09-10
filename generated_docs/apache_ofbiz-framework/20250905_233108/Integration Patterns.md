## Integration Patterns

## Overview

Apache OFBiz implements a comprehensive set of integration patterns that enable seamless connectivity between internal components and external systems. The framework's integration architecture is built around service-oriented principles, providing multiple integration mechanisms including web services, REST APIs, message queues, and database connectivity patterns.

## Core Integration Architecture

### Service Engine Integration

The OFBiz Service Engine serves as the primary integration hub, orchestrating communication between different system components:

```xml
<service name="exampleIntegrationService" engine="java" 
         location="org.apache.ofbiz.integration.ExampleService" invoke="processIntegration">
    <description>Example integration service</description>
    <attribute name="inputData" type="Map" mode="IN" optional="false"/>
    <attribute name="result" type="Map" mode="OUT" optional="false"/>
</service>
```

The service engine supports multiple execution contexts:
- **Synchronous Services**: Direct method invocation for real-time processing
- **Asynchronous Services**: Job scheduling for background integration tasks
- **Remote Services**: Cross-system communication via HTTP, JMS, or RMI

### Entity Engine Integration Patterns

The Entity Engine provides robust data integration capabilities through:

#### Delegator Pattern
```java
// Direct entity access for integration scenarios
GenericValue product = delegator.findOne("Product", 
    UtilMisc.toMap("productId", "DEMO_PRODUCT"), false);

// Bulk data operations for ETL processes
List<GenericValue> orderItems = delegator.findByAnd("OrderItem", 
    UtilMisc.toMap("orderId", orderId), null, false);
```

#### View Entities for Data Aggregation
```xml
<view-entity entity-name="ProductInventoryView" package-name="org.apache.ofbiz.product.inventory">
    <member-entity entity-alias="PROD" entity-name="Product"/>
    <member-entity entity-alias="INV" entity-name="InventoryItem"/>
    <alias-all entity-alias="PROD"/>
    <alias-all entity-alias="INV"/>
    <view-link entity-alias="PROD" rel-entity-alias="INV">
        <key-map field-name="productId"/>
    </view-link>
</view-entity>
```

## Web Service Integration Patterns

### SOAP Web Services

OFBiz provides comprehensive SOAP web service support through the `webtools` component:

```xml
<!-- Service definition in services.xml -->
<service name="createCustomer" engine="java" export="true"
         location="org.apache.ofbiz.party.party.PartyServices" invoke="createPerson">
    <description>Create Customer via Web Service</description>
    <attribute name="firstName" type="String" mode="IN" optional="false"/>
    <attribute name="lastName" type="String" mode="IN" optional="false"/>
    <attribute name="partyId" type="String" mode="OUT" optional="false"/>
</service>
```

Access patterns:
- **WSDL Generation**: Automatic WSDL creation from service definitions
- **Authentication Integration**: Seamless integration with OFBiz security framework
- **Transaction Management**: Automatic transaction handling for web service calls

### RESTful API Integration

The framework supports REST integration through the `rest` component:

```java
// REST endpoint configuration
@Path("/api/products")
public class ProductRestService {
    
    @GET
    @Path("/{productId}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getProduct(@PathParam("productId") String productId) {
        // Service invocation pattern
        Map<String, Object> serviceContext = UtilMisc.toMap("productId", productId);
        Map<String, Object> result = dispatcher.runSync("getProduct", serviceContext);
        return Response.ok(result).build();
    }
}
```

## Message Queue Integration

### JMS Integration Pattern

OFBiz supports asynchronous integration through JMS:

```xml
<!-- JMS service configuration -->
<service name="processOrderMessage" engine="jms" 
         location="jms://orderQueue" invoke="processOrder">
    <description>Process order via JMS</description>
    <attribute name="orderData" type="String" mode="IN"/>
</service>
```

Implementation approaches:
- **Queue-based Processing**: Point-to-point message delivery
- **Topic-based Broadcasting**: Publish-subscribe pattern for event distribution
- **Dead Letter Handling**: Error recovery mechanisms for failed messages

### Job Scheduler Integration

The Job Scheduler provides temporal integration patterns:

```xml
<TemporalExpression tempExprId="EVERY_HOUR" tempExprTypeId="FREQUENCY">
    <FrequencyExpression frequencyTypeId="HOURLY" intervalNumber="1"/>
</TemporalExpression>

<JobSandbox jobId="INTEGRATION_SYNC" jobName="Integration Synchronization"
            runTime="2024-01-01 00:00:00" serviceName="syncExternalData"
            tempExprId="EVERY_HOUR"/>
```

## Database Integration Patterns

### Multi-Datasource Configuration

OFBiz supports multiple database connections for integration scenarios:

```xml
<!-- entityengine.xml configuration -->
<datasource name="externaldb" helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="mysql" check-on-start="true" add-missing-on-start="true"
            use-pk-constraint-names="false" use-indices-unique="false">
    <read-data reader-name="ext-data"/>
    <inline-jdbc jdbc-driver="com.mysql.cj.jdbc.Driver"
                 jdbc-uri="jdbc:mysql://external-host:3306/external_db"
                 jdbc-username="integration_user"
                 jdbc-password="secure_password"/>
</datasource>
```

### ETL Service Patterns

```java
public class DataIntegrationService {
    
    public static Map<String, Object> syncExternalCustomers(DispatchContext dctx, 
                                                           Map<String, Object> context) {
        Delegator delegator = dctx.getDelegator();
        Delegator externalDelegator = DelegatorFactory.getDelegator("externaldb");
        
        // Extract from external system
        List<GenericValue> externalCustomers = externalDelegator.findAll("Customer", false);
        
        // Transform and load into OFBiz
        for (GenericValue extCustomer : externalCustomers) {
            GenericValue party = delegator.makeValue("Party");
            party.put("partyId", delegator.getNextSeqId("Party"));
            party.put("partyTypeId", "PERSON");
            // Transform logic here
            delegator.create(party);
        }
        
        return ServiceUtil.returnSuccess();
    }
}
```

## Event-Driven Integration

### Entity Event Handlers

OFBiz supports event-driven integration through entity change listeners:

```xml
<entity-eca entity="OrderHeader" operation="create" event="return">
    <condition field-name="statusId" operator="equals" value="ORDER_APPROVED"/>
    <action service="notifyExternalSystem" mode="async"/>
</entity-eca>
```

### Custom Event Handlers

```java
public class IntegrationEventHandler {
    
    public static String handleOrderCreation(HttpServletRequest request, 
                                           HttpServletResponse response) {
        // Extract order data
        String orderId = request.getParameter("orderId");
        
        // Trigger external system notification
        LocalDispatcher dispatcher = (LocalDispatcher) request.getAttribute("dispatcher");
        Map<String, Object> serviceContext = UtilMisc.toMap("orderId", orderId);
        
        try {
            dispatcher.runAsync("notifyExternalOrderSystem", serviceContext);
        } catch (GenericServiceException e) {
            Debug.logError(e, "Failed to notify external system", MODULE);
            return "error";
        }
        
        return "success";
    }
}
```

## Security Integration Patterns

### Authentication Integration

OFBiz provides flexible authentication integration:

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:50:38*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*