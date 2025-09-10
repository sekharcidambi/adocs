## Manufacturing Resource Planning

## Overview

The Manufacturing Resource Planning (MRP) module in Apache OFBiz provides comprehensive manufacturing management capabilities within the enterprise resource planning framework. This module integrates deeply with OFBiz's service-oriented architecture, leveraging the entity engine for data persistence and the service engine for business logic execution. The MRP implementation follows OFBiz's convention-over-configuration approach, utilizing XML-based service definitions and entity models to create a flexible and extensible manufacturing system.

## Core Components

### Production Run Management

The MRP system centers around the `ProductionRun` entity, which represents individual manufacturing orders. Production runs are managed through a series of services that handle the complete lifecycle from creation to completion:

```xml
<service name="createProductionRun" engine="simple" 
         location="component://manufacturing/script/org/ofbiz/manufacturing/mrp/MrpServices.xml" 
         invoke="createProductionRun">
    <description>Create a Production Run</description>
    <attribute name="productId" type="String" mode="IN" optional="false"/>
    <attribute name="quantity" type="BigDecimal" mode="IN" optional="false"/>
    <attribute name="startDate" type="Timestamp" mode="IN" optional="true"/>
    <attribute name="workEffortName" type="String" mode="IN" optional="true"/>
</service>
```

The production run workflow integrates with OFBiz's WorkEffort framework, treating each manufacturing task as a work effort with associated routing operations, material requirements, and resource allocations.

### Bill of Materials (BOM) Integration

The MRP module leverages OFBiz's product association framework to manage bills of materials. The `ProductAssoc` entity with association type "MANUF_COMPONENT" defines the hierarchical structure of manufactured products:

```java
// Example of BOM explosion logic in MRP calculations
List<GenericValue> bomComponents = EntityQuery.use(delegator)
    .from("ProductAssoc")
    .where("productId", productId, 
           "productAssocTypeId", "MANUF_COMPONENT")
    .filterByDate()
    .queryList();
```

The system supports multi-level BOMs with automatic explosion capabilities, calculating net requirements across all levels of the product structure. This integration allows for dynamic BOM modifications without disrupting ongoing production planning processes.

### MRP Calculation Engine

The heart of the MRP system is the `runMrp` service, which performs comprehensive material requirements planning calculations:

```xml
<service name="runMrp" engine="java" 
         location="org.apache.ofbiz.manufacturing.mrp.MrpServices" 
         invoke="runMrp">
    <description>Run MRP</description>
    <attribute name="facilityId" type="String" mode="IN" optional="true"/>
    <attribute name="mrpName" type="String" mode="IN" optional="false"/>
    <attribute name="defaultYearsOffset" type="Integer" mode="IN" optional="true"/>
</service>
```

The MRP engine processes:
- **Gross Requirements**: Derived from sales forecasts, sales orders, and existing production runs
- **Scheduled Receipts**: Open purchase orders and production orders
- **Projected Available Balance**: Calculated inventory levels over time
- **Net Requirements**: Additional quantities needed to meet demand
- **Planned Orders**: Suggested purchase and production orders

### Routing and Work Center Management

Manufacturing routing is implemented through the WorkEffort framework, where each routing operation is represented as a `WorkEffort` entity with type "ROU_TASK". The system supports:

```xml
<entity entity-name="WorkEffortAssoc" package-name="org.apache.ofbiz.workeffort.workeffort">
    <field name="workEffortIdFrom" type="id-ne"/>
    <field name="workEffortIdTo" type="id-ne"/>
    <field name="workEffortAssocTypeId" type="id-ne"/>
    <field name="sequenceNum" type="numeric"/>
    <field name="fromDate" type="date-time"/>
    <field name="thruDate" type="date-time"/>
</entity>
```

Work centers are modeled as `FixedAsset` entities with specific asset types, enabling capacity planning and resource scheduling. The system calculates operation times based on setup time, run time per unit, and queue times defined in the routing.

## Integration Architecture

### Service Layer Integration

The MRP module extensively uses OFBiz's service engine for business logic encapsulation. Key service patterns include:

- **Synchronous Services**: For immediate calculations like BOM explosions
- **Asynchronous Services**: For long-running MRP calculations
- **Scheduled Services**: For periodic MRP runs and inventory updates

```java
// Example service call from MRP engine
Map<String, Object> serviceContext = UtilMisc.toMap(
    "productId", productId,
    "facilityId", facilityId,
    "quantity", requiredQuantity,
    "requiredByDate", requiredDate
);
Map<String, Object> serviceResult = dispatcher.runSync(
    "createRequirementForProduct", serviceContext);
```

### Entity Engine Utilization

The MRP system leverages OFBiz's entity engine for data persistence and retrieval. Key entities include:

- `MrpEvent`: Stores individual MRP calculation events
- `Requirement`: Represents material requirements
- `InventoryItem`: Tracks physical inventory
- `ProductionRun`: Manufacturing orders
- `ProductionRunTask`: Individual operations within production runs

### Integration with Other Modules

The MRP module integrates seamlessly with other OFBiz components:

**Order Management**: Sales orders automatically generate gross requirements for MRP calculations through the `OrderRequirementCommitment` entity.

**Purchasing**: MRP-generated requirements can be automatically converted to purchase requisitions using the requirement-to-purchase order workflow.

**Inventory Management**: Real-time inventory updates trigger MRP recalculations through service event handlers.

**Accounting**: Production run completion automatically generates accounting transactions for work-in-process and finished goods inventory.

## Configuration and Customization

### MRP Parameters

The system supports facility-specific MRP parameters through the `FacilityAttribute` entity:

```xml
<FacilityAttribute facilityId="WebStoreWarehouse" 
                   attrName="MRP_PLANNING_HORIZON" 
                   attrValue="365"/>
<FacilityAttribute facilityId="WebStoreWarehouse" 
                   attrName="MRP_LOT_SIZE_RULE" 
                   attrValue="LOT_FOR_LOT"/>
```

### Custom MRP Logic

Organizations can extend MRP functionality by implementing custom services that follow OFBiz service conventions:

```java
public static Map<String, Object> customMrpCalculation(
        DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    // Custom MRP logic implementation
    // Must return standard OFBiz service response format
    return ServiceUtil.returnSuccess();
}
```

## Performance Considerations

The MRP calculation engine is designed for scalability through:

- **Batch Processing**: Large MRP runs are processed in configurable batch sizes
- **Database Optimization**: Strategic use of database indexes on key MRP entities
- **Caching**: Frequently accessed BOM and routing data is cached using OFBiz's caching framework
- **Parallel Processing**: Independent facility calculations can be executed concurrently

The system monitors performance through built-in logging and provides detailed execution statistics for optimization purposes.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 21:45:33*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*