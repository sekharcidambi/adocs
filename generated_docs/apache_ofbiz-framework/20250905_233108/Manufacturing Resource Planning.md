## Manufacturing Resource Planning

## Overview

The Manufacturing Resource Planning (MRP) module in Apache OFBiz provides comprehensive functionality for managing manufacturing operations, production planning, and resource allocation within the enterprise framework. This module integrates seamlessly with OFBiz's service-oriented architecture, leveraging the Entity Engine for data persistence and the Service Engine for business logic execution.

The MRP implementation follows OFBiz's component-based architecture pattern, residing primarily in the `applications/manufacturing` component. It utilizes the framework's built-in capabilities for workflow management, inventory tracking, and financial integration to deliver a complete manufacturing management solution.

## Core Components and Architecture

### Entity Model Structure

The MRP module defines several key entities that form the foundation of manufacturing operations:

```xml
<!-- Production Run entities -->
<entity entity-name="WorkEffort" package-name="org.apache.ofbiz.workeffort">
    <field name="workEffortId" type="id-ne"/>
    <field name="workEffortTypeId" type="id"/>
    <field name="currentStatusId" type="id"/>
    <field name="workEffortName" type="name"/>
    <field name="description" type="description"/>
    <field name="quantityToProduce" type="fixed-point"/>
    <field name="quantityProduced" type="fixed-point"/>
</entity>

<!-- Bill of Materials -->
<entity entity-name="ProductAssoc" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productIdTo" type="id-ne"/>
    <field name="productAssocTypeId" type="id-ne"/>
    <field name="quantity" type="fixed-point"/>
    <field name="scrapFactor" type="fixed-point"/>
</entity>
```

### Service Layer Implementation

The MRP module implements business logic through OFBiz services, following the framework's service definition patterns:

```xml
<service name="createProductionRun" engine="java"
         location="org.apache.ofbiz.manufacturing.mrp.MrpServices"
         invoke="createProductionRun">
    <description>Create a Production Run</description>
    <attribute name="productId" type="String" mode="IN" optional="false"/>
    <attribute name="quantity" type="BigDecimal" mode="IN" optional="false"/>
    <attribute name="startDate" type="Timestamp" mode="IN" optional="true"/>
    <attribute name="workEffortId" type="String" mode="OUT" optional="false"/>
</service>
```

## Manufacturing Workflows

### Production Run Management

The production run workflow represents the core of the MRP system, managing the entire lifecycle from planning to completion:

1. **Planning Phase**: Utilizes the `MrpServices.createMrpPlan()` service to analyze demand and generate production requirements
2. **Scheduling**: Implements capacity planning through the `SchedulingServices` to optimize resource allocation
3. **Execution**: Tracks progress through work effort status transitions and inventory movements
4. **Completion**: Handles finished goods receipt and cost accounting integration

```java
// Example service implementation pattern
public static Map<String, Object> createProductionRun(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    String productId = (String) context.get("productId");
    BigDecimal quantity = (BigDecimal) context.get("quantity");
    
    // Create work effort for production run
    Map<String, Object> workEffortContext = UtilMisc.toMap(
        "workEffortTypeId", "PROD_ORDER_HEADER",
        "currentStatusId", "PRUN_CREATED",
        "quantityToProduce", quantity
    );
    
    return dispatcher.runSync("createWorkEffort", workEffortContext);
}
```

### Bill of Materials (BOM) Processing

The BOM functionality integrates with the Product component to define manufacturing recipes and component relationships:

- **Multi-level BOMs**: Support for nested product structures with unlimited depth
- **Routing Integration**: Links BOMs with manufacturing routings for complete production definitions
- **Variant Management**: Handles product variants and optional components through configurable BOMs

## MRP Planning Engine

### Demand Calculation

The MRP planning engine analyzes multiple demand sources to generate comprehensive production plans:

```xml
<service name="executeMrp" engine="java"
         location="org.apache.ofbiz.manufacturing.mrp.MrpServices"
         invoke="executeMrp">
    <description>Execute MRP Planning</description>
    <attribute name="facilityId" type="String" mode="IN" optional="false"/>
    <attribute name="mrpName" type="String" mode="IN" optional="false"/>
    <attribute name="defaultYearsOffset" type="Integer" mode="IN" optional="true"/>
</service>
```

The planning process considers:
- Sales forecasts from the Order Management module
- Existing sales orders and their delivery requirements
- Current inventory levels and safety stock parameters
- Existing production runs and purchase orders

### Capacity Planning

Resource capacity management integrates with the Human Resources and Fixed Asset modules:

- **Work Center Definition**: Links manufacturing resources to calendar availability
- **Routing Operations**: Defines standard times and resource requirements for each production step
- **Finite Scheduling**: Considers resource constraints when generating production schedules

## Integration Points

### Inventory Management Integration

The MRP module seamlessly integrates with OFBiz's Inventory Management through standardized service interfaces:

```java
// Inventory reservation for production runs
Map<String, Object> reserveInventoryContext = UtilMisc.toMap(
    "productId", componentProductId,
    "facilityId", facilityId,
    "quantityNotAvailable", requiredQuantity,
    "workEffortId", productionRunId
);
dispatcher.runSync("reserveProductInventory", reserveInventoryContext);
```

### Accounting Integration

Manufacturing costs flow automatically to the General Ledger through the Accounting component:

- **Standard Costing**: Maintains product standard costs for planning and variance analysis
- **Actual Cost Tracking**: Records actual labor, material, and overhead costs during production
- **Variance Reporting**: Calculates and posts manufacturing variances to appropriate GL accounts

### Order Management Integration

The MRP system responds to sales demand through integration with Order Management:

- **Make-to-Order**: Creates production runs directly from sales order line items
- **Make-to-Stock**: Generates production plans based on forecast demand and inventory policies
- **Available-to-Promise**: Considers planned production when calculating delivery dates

## Configuration and Customization

### Manufacturing Parameters

Key configuration entities control MRP behavior:

```xml
<!-- Facility-specific manufacturing settings -->
<entity entity-name="FacilityAttribute">
    <field name="facilityId" type="id-ne"/>
    <field name="attrName" type="name"/>
    <field name="attrValue" type="value"/>
</entity>
```

Common configuration parameters include:
- `MRP_PLANNING_HORIZON`: Defines the planning time fence in days
- `DEFAULT_LEAD_TIME`: Standard manufacturing lead time for capacity planning
- `SAFETY_STOCK_DAYS`: Buffer stock calculation parameter

### Custom Routing Operations

Manufacturing routings can be extended with custom operation types:

```xml
<WorkEffortAssoc workEffortIdFrom="ROUTING_001" workEffortIdTo="OP_010"
                 workEffortAssocTypeId="ROUTING_COMPONENT"
                 sequenceNum="10" estimatedSetupMillis="1800000"
                 estimatedMilliSeconds="300000"/>
```

## Best Practices and Performance Considerations

### Data Model Optimization

- **Indexing Strategy**: Ensure proper database indexes on frequently queried fields like `workEffortId`, `productId`, and status fields
- **Archival Policies**: Implement data retention policies for completed production runs to maintain system performance
- **Batch Processing**: Use OFBiz's job scheduler for resource-intensive MRP planning operations

### Service Design Patterns

- **Transaction Management**: Leverage OFBiz's transaction management for data consistency across manufacturing operations
- **Error Handling**: Implement comprehensive

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:35:17*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*