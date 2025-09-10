## Manufacturing Resource Planning

## Overview

The Manufacturing Resource Planning (MRP) module in Apache OFBiz provides comprehensive functionality for production planning, inventory management, and resource optimization within the enterprise framework. This module integrates seamlessly with OFBiz's service-oriented architecture, leveraging the entity engine and workflow management capabilities to deliver a complete manufacturing solution.

The MRP implementation follows OFBiz's standard patterns, utilizing XML-based entity definitions, service definitions, and screen configurations to provide a flexible and extensible manufacturing management system. The module is built on top of the core OFBiz framework components including the Entity Engine, Service Engine, and Widget Framework.

## Core Components and Architecture

### Entity Model Structure

The MRP module defines its data model through XML entity definitions located in the `applications/manufacturing/entitydef/` directory. Key entities include:

```xml
<entity entity-name="ProductionRun" package-name="org.apache.ofbiz.manufacturing.mrp">
    <field name="productionRunId" type="id-ne"/>
    <field name="productId" type="id"/>
    <field name="facilityId" type="id"/>
    <field name="workEffortName" type="name"/>
    <field name="description" type="description"/>
    <field name="quantityToProduce" type="fixed-point"/>
    <field name="quantityProduced" type="fixed-point"/>
    <field name="estimatedStartDate" type="date-time"/>
    <field name="estimatedCompletionDate" type="date-time"/>
    <prim-key field="productionRunId"/>
</entity>
```

The MRP system utilizes several interconnected entities:
- **MrpEvent**: Represents supply and demand events in the planning horizon
- **ProductionRun**: Manages manufacturing orders and production schedules
- **WorkEffort**: Handles task management and resource allocation
- **InventoryItem**: Tracks raw materials and finished goods inventory
- **ProductFacility**: Manages product-facility relationships and safety stock levels

### Service Layer Implementation

The MRP services are defined in `applications/manufacturing/servicedef/services_mrp.xml` and implemented in Java classes within the `org.apache.ofbiz.manufacturing.mrp` package. Core services include:

```xml
<service name="runMrp" engine="java" 
         location="org.apache.ofbiz.manufacturing.mrp.MrpServices" 
         invoke="runMrp" auth="true">
    <description>Run MRP for a facility</description>
    <attribute name="facilityId" type="String" mode="IN" optional="false"/>
    <attribute name="mrpName" type="String" mode="IN" optional="true"/>
    <attribute name="defaultYearsOffset" type="Integer" mode="IN" optional="true"/>
</service>
```

Key service implementations:

- **runMrp**: Executes the main MRP calculation algorithm
- **createProductionRun**: Generates production orders based on MRP recommendations
- **explodeBomComponent**: Performs bill-of-materials explosion for material requirements
- **calculateInventoryAvailableToPromise**: Computes ATP quantities for planning

## MRP Algorithm Implementation

### Planning Process Flow

The MRP engine follows a systematic approach implemented in the `MrpServices.java` class:

1. **Demand Collection**: Gathers requirements from sales orders, forecasts, and safety stock
2. **Supply Analysis**: Evaluates existing inventory, scheduled receipts, and production capacity
3. **Net Requirements Calculation**: Determines shortfalls requiring action
4. **Time-Phased Planning**: Schedules production and procurement activities
5. **Capacity Validation**: Verifies resource availability and constraints

```java
public static Map<String, Object> runMrp(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    String facilityId = (String) context.get("facilityId");
    String mrpName = (String) context.get("mrpName");
    
    // Initialize MRP events and process demand/supply
    List<GenericValue> mrpEvents = FastList.newInstance();
    
    // Process sales orders and forecasts
    processDemandEvents(delegator, facilityId, mrpEvents);
    
    // Process inventory and scheduled receipts
    processSupplyEvents(delegator, facilityId, mrpEvents);
    
    // Execute MRP logic
    executeMrpLogic(delegator, dispatcher, mrpEvents);
    
    return ServiceUtil.returnSuccess();
}
```

### Bill of Materials Processing

The BOM explosion functionality recursively processes product structures to determine component requirements:

```java
private static void explodeBom(Delegator delegator, String productId, 
                              BigDecimal quantity, Map<String, BigDecimal> requirements) {
    try {
        List<GenericValue> bomComponents = EntityQuery.use(delegator)
            .from("ProductAssoc")
            .where("productId", productId, "productAssocTypeId", "MANUF_COMPONENT")
            .filterByDate()
            .queryList();
            
        for (GenericValue component : bomComponents) {
            BigDecimal componentQty = component.getBigDecimal("quantity");
            BigDecimal totalRequired = quantity.multiply(componentQty);
            
            String componentProductId = component.getString("productIdTo");
            requirements.put(componentProductId, 
                           requirements.getOrDefault(componentProductId, BigDecimal.ZERO)
                           .add(totalRequired));
        }
    } catch (GenericEntityException e) {
        Debug.logError(e, "Error exploding BOM for product: " + productId, module);
    }
}
```

## Integration Points

### ERP Module Integration

The MRP system integrates extensively with other OFBiz applications:

- **Order Management**: Consumes sales order demand and generates purchase requisitions
- **Inventory Management**: Updates stock levels and reservation quantities
- **Accounting**: Creates financial transactions for production costs and inventory valuations
- **Human Resources**: Interfaces with workforce scheduling and capacity planning
- **Facility Management**: Coordinates with warehouse operations and material handling

### Workflow Integration

Production runs leverage OFBiz's WorkEffort framework for task management:

```xml
<service name="createProductionRunTasksFromRoutingTasks" engine="java"
         location="org.apache.ofbiz.manufacturing.jobshopmgt.ProductionRunServices"
         invoke="createProductionRunTasksFromRoutingTasks">
    <attribute name="productionRunId" type="String" mode="IN" optional="false"/>
    <attribute name="routing" type="GenericValue" mode="IN" optional="true"/>
    <attribute name="workEffortId" type="String" mode="OUT" optional="true"/>
</service>
```

## Configuration and Customization

### MRP Parameters

System-wide MRP parameters are configured through the `MrpEventType` and `ProductFacility` entities:

```xml
<ProductFacility productId="PROD_001" facilityId="WebStoreWarehouse"
                 minimumStock="10.0" reorderQuantity="100.0"
                 daysToShip="2" lastInventoryCount="2023-01-15 00:00:00"/>
```

### Custom Planning Strategies

Organizations can extend the MRP functionality by implementing custom services:

```java
@Override
public Map<String, Object> customMrpStrategy(DispatchContext dctx, 
                                           Map<String, Object> context) {
    // Custom logic for specialized planning requirements
    // Integration with external planning systems
    // Industry-specific calculations
    
    return ServiceUtil.returnSuccess("Custom MRP strategy executed");
}
```

## Performance Considerations

### Database Optimization

The MRP module includes several performance optimizations:

- **Indexed Views**: Pre-calculated inventory positions for faster queries
- **Batch Processing**: Bulk operations for large-scale planning runs
- **Caching Strategies**: Frequently accessed BOM and routing data caching

### Scalability Features

- **Facility-based Partitioning**: Parallel processing across multiple facilities
- **Incremental Planning**: Net-change MRP for reduced processing time
- **Background Processing**: Asynchronous

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:31:34*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*