## Supply Chain Management

## Overview

The Supply Chain Management (SCM) module in Apache OFBiz provides comprehensive functionality for managing the entire supply chain lifecycle, from procurement and inventory management to order fulfillment and supplier relationships. Built on OFBiz's multi-tier architecture, the SCM module leverages the framework's entity engine, service engine, and workflow capabilities to deliver enterprise-grade supply chain operations.

The SCM implementation spans across multiple OFBiz applications including Manufacturing, Inventory, Purchasing, and Order Management, providing seamless integration between supply chain processes and other business functions like accounting, customer relationship management, and human resources.

## Architecture and Components

### Data Model Structure

The SCM module utilizes OFBiz's entity-relationship model with key entities stored in the framework's database layer:

```xml
<!-- Core SCM Entities -->
<entity entity-name="InventoryItem" package-name="org.apache.ofbiz.product.inventory">
    <field name="inventoryItemId" type="id-ne"/>
    <field name="inventoryItemTypeId" type="id"/>
    <field name="productId" type="id"/>
    <field name="facilityId" type="id"/>
    <field name="quantityOnHandTotal" type="fixed-point"/>
    <field name="availableToPromiseTotal" type="fixed-point"/>
</entity>

<entity entity-name="SupplierProduct" package-name="org.apache.ofbiz.product.supplier">
    <field name="productId" type="id-ne"/>
    <field name="partyId" type="id-ne"/>
    <field name="availableFromDate" type="date-time"/>
    <field name="supplierPrefOrderId" type="id"/>
    <field name="minimumOrderQuantity" type="fixed-point"/>
</entity>
```

### Service Layer Implementation

The SCM module implements business logic through OFBiz's service-oriented architecture:

```groovy
// Example: Inventory Management Service
def updateInventoryItem() {
    Map result = success()
    
    GenericValue inventoryItem = from("InventoryItem")
        .where("inventoryItemId", parameters.inventoryItemId)
        .queryOne()
    
    if (inventoryItem) {
        inventoryItem.quantityOnHandTotal = parameters.quantityOnHandTotal
        inventoryItem.availableToPromiseTotal = parameters.availableToPromiseTotal
        inventoryItem.store()
        
        // Trigger reorder point check
        dispatcher.runSync("checkInventoryReorderLevel", 
            [productId: inventoryItem.productId, 
             facilityId: inventoryItem.facilityId])
    }
    
    return result
}
```

## Key Functional Areas

### Inventory Management

The inventory management system provides real-time tracking of stock levels across multiple facilities and warehouses:

- **Multi-facility Support**: Track inventory across different locations with facility-specific configurations
- **Lot and Serial Number Tracking**: Complete traceability for regulated industries
- **Automated Reorder Points**: Configurable minimum stock levels with automatic purchase requisition generation

```java
// Inventory reservation example
public static Map<String, Object> reserveInventory(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    String productId = (String) context.get("productId");
    String facilityId = (String) context.get("facilityId");
    BigDecimal quantity = (BigDecimal) context.get("quantity");
    
    // Check ATP (Available to Promise)
    Map<String, Object> atpResult = dispatcher.runSync("getInventoryAvailableByFacility", 
        UtilMisc.toMap("productId", productId, "facilityId", facilityId));
    
    BigDecimal availableToPromise = (BigDecimal) atpResult.get("availableToPromiseTotal");
    
    if (availableToPromise.compareTo(quantity) >= 0) {
        // Create inventory reservation
        GenericValue reservation = delegator.makeValue("InventoryReservation");
        reservation.set("inventoryReservationId", delegator.getNextSeqId("InventoryReservation"));
        reservation.set("productId", productId);
        reservation.set("quantity", quantity);
        reservation.create();
    }
    
    return ServiceUtil.returnSuccess();
}
```

### Procurement and Supplier Management

The procurement module handles the complete purchase-to-pay cycle:

- **Supplier Qualification**: Comprehensive supplier evaluation and certification workflows
- **RFQ Management**: Request for Quote processing with multi-supplier comparison
- **Purchase Order Automation**: Automated PO generation based on inventory levels and demand forecasting

### Manufacturing Resource Planning (MRP)

OFBiz's MRP functionality integrates with the SCM module to provide:

- **Bill of Materials (BOM) Management**: Multi-level BOM structures with variant configurations
- **Production Planning**: Master production scheduling with capacity planning
- **Work Order Management**: Shop floor control with real-time production tracking

```xml
<!-- MRP Configuration Example -->
<entity entity-name="ProductionRun" package-name="org.apache.ofbiz.manufacturing.mrp">
    <field name="productionRunId" type="id-ne"/>
    <field name="productId" type="id"/>
    <field name="facilityId" type="id"/>
    <field name="quantityToProduce" type="fixed-point"/>
    <field name="estimatedStartDate" type="date-time"/>
    <field name="estimatedCompletionDate" type="date-time"/>
</entity>
```

## Integration Points

### ERP Integration

The SCM module seamlessly integrates with other OFBiz applications:

- **Financial Integration**: Automatic GL postings for inventory transactions, purchase accruals, and cost of goods sold
- **Sales Order Integration**: Real-time ATP checking during order entry with automatic allocation
- **Accounting Integration**: Standard costing, average costing, and FIFO/LIFO inventory valuation methods

### External System Connectivity

OFBiz provides multiple integration options for SCM data exchange:

```java
// EDI Integration Example
public class EDI850Processor {
    public static Map<String, Object> processInboundPurchaseOrder(
            DispatchContext dctx, Map<String, ? extends Object> context) {
        
        String ediMessage = (String) context.get("ediContent");
        LocalDispatcher dispatcher = dctx.getDispatcher();
        
        // Parse EDI 850 message
        EDI850Parser parser = new EDI850Parser();
        PurchaseOrderData poData = parser.parse(ediMessage);
        
        // Create OFBiz purchase order
        Map<String, Object> createPOResult = dispatcher.runSync("createPurchaseOrder", 
            UtilMisc.toMap("supplierId", poData.getSupplierId(),
                          "orderItems", poData.getLineItems()));
        
        return ServiceUtil.returnSuccess();
    }
}
```

## Configuration and Customization

### Facility Configuration

Configure warehouses and distribution centers through the facility management interface:

```properties
# facility.properties
default.facility.id=WebStoreWarehouse
inventory.facility.default=WebStoreWarehouse
manufacturing.facility.default=MainFactory
```

### Workflow Customization

Customize approval workflows using OFBiz's workflow engine:

```xml
<!-- Purchase Order Approval Workflow -->
<simple-method method-name="purchaseOrderApprovalWorkflow">
    <if-compare field="parameters.orderTotal" operator="greater" value="10000" type="BigDecimal">
        <set field="requiresApproval" value="true"/>
        <call-service service-name="createWorkEffort">
            <field-map field-name="workEffortTypeId" value="APPROVAL_WORKFLOW"/>
            <field-map field-name="currentStatusId" value="WF_RUNNING"/>
        </call-service>
    </if-compare>
</simple-method>
```

## Performance Optimization

### Database Optimization

For high-volume SCM operations, consider these database optimizations:

```sql

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

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:57:50*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*