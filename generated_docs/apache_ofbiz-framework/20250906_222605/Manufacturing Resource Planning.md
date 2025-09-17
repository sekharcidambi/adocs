# Manufacturing Resource Planning

## Overview

Manufacturing Resource Planning (MRP) in Apache OFBiz is a comprehensive enterprise resource planning module that manages the complete manufacturing lifecycle from demand forecasting to production execution. The MRP system integrates seamlessly with OFBiz's inventory management, purchasing, and accounting modules to provide end-to-end manufacturing operations support.

The OFBiz MRP implementation follows industry-standard MRP II principles while leveraging the framework's flexible entity engine and service-oriented architecture to deliver scalable manufacturing solutions for businesses of all sizes.

## Architecture and Core Components

### Entity Model Structure

The MRP module is built upon OFBiz's robust entity framework, utilizing key entities that represent manufacturing concepts:

```xml
<!-- Core MRP Entities -->
<entity entity-name="MrpEvent" package-name="org.apache.ofbiz.manufacturing.mrp">
    <field name="mrpEventId" type="id-ne"/>
    <field name="productId" type="id"/>
    <field name="mrpEventTypeId" type="id"/>
    <field name="eventDate" type="date-time"/>
    <field name="quantity" type="fixed-point"/>
    <field name="facilityId" type="id"/>
    <prim-key field="mrpEventId"/>
</entity>

<entity entity-name="MrpEventType" package-name="org.apache.ofbiz.manufacturing.mrp">
    <field name="mrpEventTypeId" type="id-ne"/>
    <field name="description" type="description"/>
    <prim-key field="mrpEventTypeId"/>
</entity>
```

### Service Layer Implementation

The MRP functionality is exposed through OFBiz services, following the framework's service-oriented architecture:

```java
// Example MRP Service Implementation
public class MrpServices {
    
    public static Map<String, Object> executeMrp(DispatchContext dctx, 
            Map<String, ? extends Object> context) {
        Delegator delegator = dctx.getDelegator();
        LocalDispatcher dispatcher = dctx.getDispatcher();
        GenericValue userLogin = (GenericValue) context.get("userLogin");
        
        String facilityId = (String) context.get("facilityId");
        Integer defaultYearsOffset = (Integer) context.get("defaultYearsOffset");
        
        try {
            // Initialize MRP run
            Map<String, Object> mrpContext = UtilMisc.toMap(
                "facilityId", facilityId,
                "userLogin", userLogin
            );
            
            // Execute MRP calculation logic
            Map<String, Object> result = dispatcher.runSync("runMrpCalculation", mrpContext);
            
            return ServiceUtil.returnSuccess("MRP execution completed successfully");
            
        } catch (GenericServiceException e) {
            Debug.logError(e, "Error executing MRP: " + e.getMessage(), MODULE);
            return ServiceUtil.returnError("MRP execution failed: " + e.getMessage());
        }
    }
}
```

## Key Features and Functionality

### 1. Demand Planning and Forecasting

The MRP system processes various demand sources to create comprehensive demand plans:

#### Sales Order Integration
```groovy
// Groovy script for processing sales order demand
import org.apache.ofbiz.entity.util.EntityQuery

def processSalesOrderDemand() {
    def salesOrders = EntityQuery.use(delegator)
        .from("OrderHeader")
        .where("orderTypeId", "SALES_ORDER", 
               "statusId", "ORDER_APPROVED")
        .queryList()
    
    salesOrders.each { order ->
        def orderItems = order.getRelated("OrderItem", null, null, false)
        orderItems.each { item ->
            // Create MRP events for sales demand
            def mrpEvent = delegator.makeValue("MrpEvent", [
                mrpEventId: delegator.getNextSeqId("MrpEvent"),
                productId: item.productId,
                mrpEventTypeId: "SALES_ORDER_SHIP",
                eventDate: order.shipByDate,
                quantity: item.quantity,
                facilityId: order.facilityId
            ])
            mrpEvent.create()
        }
    }
}
```

#### Forecast Management
```xml
<!-- Service definition for forecast processing -->
<service name="processForecastDemand" engine="java"
         location="org.apache.ofbiz.manufacturing.mrp.MrpServices" 
         invoke="processForecastDemand">
    <description>Process forecast demand for MRP</description>
    <attribute name="facilityId" type="String" mode="IN" optional="false"/>
    <attribute name="forecastId" type="String" mode="IN" optional="true"/>
    <attribute name="fromDate" type="Timestamp" mode="IN" optional="true"/>
    <attribute name="thruDate" type="Timestamp" mode="IN" optional="true"/>
</service>
```

### 2. Bill of Materials (BOM) Processing

The MRP system leverages OFBiz's product configuration capabilities to process multi-level BOMs:

```java
public static Map<String, Object> explodeBom(DispatchContext dctx, 
        Map<String, ? extends Object> context) {
    
    String productId = (String) context.get("productId");
    BigDecimal quantity = (BigDecimal) context.get("quantity");
    String facilityId = (String) context.get("facilityId");
    
    try {
        // Get BOM components
        List<GenericValue> bomComponents = EntityQuery.use(delegator)
            .from("ProductAssoc")
            .where("productId", productId,
                   "productAssocTypeId", "MANUF_COMPONENT")
            .filterByDate()
            .queryList();
        
        List<Map<String, Object>> explodedComponents = new ArrayList<>();
        
        for (GenericValue component : bomComponents) {
            BigDecimal componentQuantity = component.getBigDecimal("quantity")
                .multiply(quantity);
            
            Map<String, Object> componentInfo = UtilMisc.toMap(
                "productId", component.getString("productIdTo"),
                "quantity", componentQuantity,
                "requiredByDate", context.get("requiredByDate")
            );
            
            explodedComponents.add(componentInfo);
            
            // Recursive explosion for sub-assemblies
            if (isAssembly(component.getString("productIdTo"))) {
                Map<String, Object> subResult = explodeBom(dctx, componentInfo);
                explodedComponents.addAll((List) subResult.get("components"));
            }
        }
        
        return ServiceUtil.returnSuccess("BOM exploded successfully", 
            UtilMisc.toMap("components", explodedComponents));
            
    } catch (GenericEntityException e) {
        return ServiceUtil.returnError("Error exploding BOM: " + e.getMessage());
    }
}
```

### 3. Inventory Planning and Safety Stock

The system calculates optimal inventory levels considering lead times, safety stock, and reorder points:

```groovy
// Safety stock calculation service
def calculateSafetyStock() {
    def products = EntityQuery.use(delegator)
        .from("Product")
        .where("productTypeId", "FINISHED_GOOD")
        .queryList()
    
    products.each { product ->
        def demandHistory = getDemandHistory(product.productId, 12) // 12 months
        def avgDemand = demandHistory.sum() / demandHistory.size()
        def demandVariability = calculateStandardDeviation(demandHistory)
        
        // Safety stock = Z-score * sqrt(lead time) * demand variability
        def leadTime = getLeadTime(product.productId)
        def serviceLevel = 0.95 // 95% service level
        def zScore = 1.65 // Z-score for 95% service level
        
        def safetyStock = zScore * Math.sqrt(leadTime) * demandVariability
        
        // Update product facility record
        def productFacility = EntityQuery.use(delegator)
            .from("ProductFacility")
            .where("productId", product.productId, "facilityId", facilityId)
            .queryOne()
        
        if (productFacility) {
            productFacility.minimumStock = safetyStock
            productFacility.store()
        }
    }
}
```

### 4. Production Planning and Scheduling

#### Work Order Generation
```java
public static Map<String, Object> createProductionRuns(DispatchContext dctx, 
        Map<String, ? extends Object> context) {
    
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    try {
        // Get MRP events requiring production
        List<GenericValue> productionEvents = EntityQuery.use(delegator)
            .from("MrpEvent")
            .where("mrpEventTypeId", "PLANNED_PRODUCTION")
            .orderBy("eventDate")
            .queryList();
        
        for (GenericValue event : productionEvents) {
            // Create production run
            Map<String, Object> productionRunContext = UtilMisc.toMap(
                "productId", event.getString("productId"),
                "quantity", event.getBigDecimal("quantity"),
                "startDate", calculateStartDate(event.getTimestamp("eventDate")),
                "facilityId", event.getString("facilityId"),
                "userLogin", context.get("userLogin")
            );
            
            Map<String, Object> result = dispatcher.runSync(
                "createProductionRun", productionRunContext);
            
            if (ServiceUtil.isError(result)) {
                Debug.logError("Failed to create production run for product: " + 
                    event.getString("productId"), MODULE);
            }
        }
        
        return ServiceUtil.returnSuccess("Production runs created successfully");
        
    } catch (Exception e) {
        return ServiceUtil.returnError("Error creating production runs: " + 
            e.getMessage());
    }
}
```

#### Capacity Planning
```xml
<!-- Routing and capacity entities -->
<entity entity-name="WorkEffort" package-name="org.apache.ofbiz.workeffort.workeffort">
    <field name="workEffortId" type="id-ne"/>
    <field name="workEffortTypeId" type="id"/>
    <field name="currentStatusId" type="id"/>
    <field name="estimatedMilliSeconds" type="numeric"/>
    <field name="actualMilliSeconds" type="numeric"/>
    <field name="facilityId" type="id"/>
    <prim-key field="workEffortId"/>
</entity>
```

## Configuration and Setup

### 1. MRP Parameters Configuration

Configure MRP parameters through the OFBiz entity engine:

```xml
<!-- MRP Configuration Data -->
<entity-engine-xml>
    <MrpEventType mrpEventTypeId="SALES_ORDER_SHIP" description="Sales Order Shipment"/>
    <MrpEventType mrpEventTypeId="PURCHASE_ORDER_RECEIPT" description="Purchase Order Receipt"/>
    <MrpEventType mrpEventTypeId="PLANNED_PRODUCTION" description="Planned Production"/>
    <MrpEventType mrpEventTypeId="INVENTORY_ON_HAND" description="Inventory On Hand"/>
    
    <ProductFacility productId="PRODUCT_001" facilityId="WebStoreWarehouse" 
                     minimumStock="100" reorderQuantity="500" daysToShip="2"/>
</entity-engine-xml>
```

### 2. Service Definitions

```xml
<!-- services.xml for MRP module -->
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/services.xsd">
    
    <service name="runMrp" engine="java"
             location="org.apache.ofbiz.manufacturing.mrp.MrpServices" 
             invoke="executeMrp">
        <description>Execute MRP for a facility</description>
        <attribute name="facilityId" type="String" mode="IN" optional="false"/>
        <attribute name="defaultYearsOffset" type="Integer" mode="IN" optional="true"/>
        <attribute name="mrpName" type="String" mode="IN" optional="true"/>
    </service>
    
    <service name="initMrpEvents" engine="java"
             location="org.apache.ofbiz.manufacturing.mrp.MrpServices" 
             invoke="initMrpEvents">
        <description>Initialize MRP events from existing data</description>
        <attribute name="facilityId" type="String" mode="IN" optional="false"/>
        <attribute name="mrpId" type="String" mode="OUT" optional="false"/>
    </service>
</services>
```

## Integration Points

### 1. Inventory Management Integration

The MRP system seamlessly integrates with OFBiz inventory management:

```java
// Integration with inventory services
public static Map<String, Object> updateInventoryFromMrp(DispatchContext dctx, 
        Map<String, ? extends Object> context) {
    
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    try {
        // Get inventory variance from MRP recommendations
        List<GenericValue> inventoryVariances = getInventoryVariances(context);
        
        for (GenericValue variance : inventoryVariances) {
            if (variance.getBigDecimal("varianceQuantity").compareTo(BigDecimal.ZERO) > 0) {
                // Create inventory adjustment
                Map<String, Object> adjustmentContext = UtilMisc.toMap(
                    "inventoryItemId", variance.getString("inventoryItemId"),
                    "adjustmentQuantity", variance.getBigDecimal("varianceQuantity"),
                    "reasonEnumId", "IID_MRP_ADJUSTMENT",
                    "userLogin", context.get("userLogin")
                );
                
                dispatcher.runSync("createInventoryItemAdjustment", adjustmentContext);
            }
        }
        
        return ServiceUtil.returnSuccess();
        
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("Error updating inventory: " + e.getMessage());
    }
}
```

### 2. Purchasing Integration

Automatic purchase order generation based on MRP recommendations:

```groovy
// Purchase requisition generation
def generatePurchaseRequisitions() {
    def purchaseEvents = EntityQuery.use(delegator)
        .from("MrpEvent")
        .where("mrpEventTypeId", "PLANNED_PURCHASE")
        .queryList()
    
    def requisitionsBySupplier = [:]
    
    purchaseEvents.each { event ->
        def supplier = getPreferredSupplier(event.productId)
        if (!requisitionsBySupplier[supplier.partyId]) {
            requisitionsBySupplier[supplier.partyId] = []
        }
        
        requisitionsBySupplier[supplier.partyId] << [
            productId: event.productId,
            quantity: event.quantity,
            requiredByDate: event.eventDate
        ]
    }
    
    // Create purchase requisitions
    requisitionsBySupplier.each { supplierId, items ->
        def requisitionId = createPurchaseRequisition(supplierId, items)
        Debug.logInfo("Created purchase requisition ${requisitionId} for supplier ${supplierId}")
    }
}
```

## Best Practices and Performance Optimization

### 1. Database Optimization

```sql
-- Recommended indexes for MRP performance
CREATE INDEX idx_mrp_event_product_date ON mrp_event (product_id, event_date);
CREATE INDEX idx_mrp_event_facility_type ON mrp_event (facility_id, mrp_event_