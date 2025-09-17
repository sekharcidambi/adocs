# Supply Chain Management

## Overview

The Supply Chain Management (SCM) module in Apache OFBiz provides a comprehensive framework for managing the flow of goods, services, and information throughout the entire supply chain lifecycle. Built on OFBiz's robust entity engine and service framework, the SCM module integrates seamlessly with other business applications including inventory management, procurement, manufacturing, and order fulfillment.

## Architecture

### Core Components

The Supply Chain Management system in OFBiz is built around several key architectural components:

```
applications/
├── product/          # Product catalog and inventory management
├── order/           # Order management and fulfillment
├── shipment/        # Shipping and logistics
├── manufacturing/   # Production planning and execution
└── purchasing/      # Procurement and vendor management
```

### Entity Model

The SCM module leverages OFBiz's entity-relationship model with key entities including:

- **Product**: Core product definitions and attributes
- **InventoryItem**: Physical inventory tracking
- **OrderHeader/OrderItem**: Order management
- **Shipment**: Logistics and delivery tracking
- **WorkEffort**: Manufacturing and production activities
- **SupplierProduct**: Vendor-product relationships

## Key Features

### 1. Inventory Management

#### Real-time Inventory Tracking

```java
// Example: Check available inventory
public static Map<String, Object> getInventoryAvailable(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    String productId = (String) context.get("productId");
    String facilityId = (String) context.get("facilityId");
    
    try {
        List<GenericValue> inventoryItems = EntityQuery.use(delegator)
            .from("InventoryItem")
            .where("productId", productId, "facilityId", facilityId)
            .queryList();
            
        BigDecimal availableToPromise = BigDecimal.ZERO;
        for (GenericValue item : inventoryItems) {
            BigDecimal atp = item.getBigDecimal("availableToPromiseTotal");
            if (atp != null) {
                availableToPromise = availableToPromise.add(atp);
            }
        }
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        result.put("availableToPromise", availableToPromise);
        return result;
        
    } catch (GenericEntityException e) {
        return ServiceUtil.returnError("Error retrieving inventory: " + e.getMessage());
    }
}
```

#### Multi-facility Support

OFBiz supports complex multi-facility inventory management:

```xml
<!-- Example facility configuration -->
<Facility facilityId="MAIN_WAREHOUSE" 
          facilityName="Main Distribution Center"
          facilityTypeId="WAREHOUSE"
          primaryFacilityGroupId="DISTRIBUTION"/>

<FacilityLocation facilityId="MAIN_WAREHOUSE"
                  locationSeqId="A001"
                  areaId="ZONE_A"
                  aisleId="01"
                  sectionId="A"
                  levelId="1"
                  positionId="001"/>
```

### 2. Procurement Management

#### Supplier Integration

```java
// Service for creating purchase orders
public static Map<String, Object> createPurchaseOrder(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    try {
        // Create order header
        Map<String, Object> orderHeaderMap = UtilMisc.toMap(
            "orderTypeId", "PURCHASE_ORDER",
            "orderDate", UtilDateTime.nowTimestamp(),
            "statusId", "ORDER_CREATED",
            "currencyUom", context.get("currencyUom"),
            "userLogin", userLogin
        );
        
        Map<String, Object> orderResult = dispatcher.runSync("createOrderHeader", orderHeaderMap);
        String orderId = (String) orderResult.get("orderId");
        
        // Add order items
        List<Map<String, Object>> orderItems = (List<Map<String, Object>>) context.get("orderItems");
        for (Map<String, Object> item : orderItems) {
            Map<String, Object> orderItemMap = UtilMisc.toMap(
                "orderId", orderId,
                "productId", item.get("productId"),
                "quantity", item.get("quantity"),
                "unitPrice", item.get("unitPrice"),
                "userLogin", userLogin
            );
            dispatcher.runSync("createOrderItem", orderItemMap);
        }
        
        return ServiceUtil.returnSuccess("Purchase order created successfully", 
                                       UtilMisc.toMap("orderId", orderId));
                                       
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("Failed to create purchase order: " + e.getMessage());
    }
}
```

#### Vendor Management

```xml
<!-- Supplier product configuration -->
<SupplierProduct partyId="SUPPLIER_001"
                 productId="PRODUCT_123"
                 availableFromDate="2024-01-01 00:00:00"
                 supplierPrefOrderId="10_MAIN_SUPPL"
                 minimumOrderQuantity="10"
                 orderQtyIncrements="5"
                 lastPrice="25.99"
                 currencyUomId="USD"/>
```

### 3. Order Fulfillment

#### Automated Order Processing

```groovy
// Groovy script for order fulfillment workflow
import org.apache.ofbiz.entity.util.EntityQuery
import org.apache.ofbiz.service.ServiceUtil

// Check inventory availability
def checkInventoryService = [
    productId: parameters.productId,
    facilityId: parameters.facilityId,
    quantity: parameters.quantity
]

def inventoryResult = dispatcher.runSync("isStoreInventoryAvailable", checkInventoryService)

if (inventoryResult.availableToPromise >= parameters.quantity) {
    // Reserve inventory
    def reserveService = [
        productId: parameters.productId,
        facilityId: parameters.facilityId,
        quantity: parameters.quantity,
        orderId: parameters.orderId,
        orderItemSeqId: parameters.orderItemSeqId
    ]
    
    def reserveResult = dispatcher.runSync("createInventoryReservation", reserveService)
    
    if (ServiceUtil.isSuccess(reserveResult)) {
        // Update order status
        def updateOrderService = [
            orderId: parameters.orderId,
            statusId: "ORDER_APPROVED"
        ]
        dispatcher.runSync("changeOrderStatus", updateOrderService)
    }
}
```

### 4. Manufacturing Resource Planning (MRP)

#### Bill of Materials (BOM) Management

```xml
<!-- Product BOM definition -->
<ProductAssoc productId="FINISHED_GOOD_001"
              productIdTo="COMPONENT_A"
              productAssocTypeId="MANUF_COMPONENT"
              fromDate="2024-01-01 00:00:00"
              quantity="2.0"
              sequenceNum="10"/>

<ProductAssoc productId="FINISHED_GOOD_001"
              productIdTo="COMPONENT_B"
              productAssocTypeId="MANUF_COMPONENT"
              fromDate="2024-01-01 00:00:00"
              quantity="1.0"
              sequenceNum="20"/>
```

#### Production Planning

```java
// MRP calculation service
public static Map<String, Object> runMrpCalculation(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    String facilityId = (String) context.get("facilityId");
    String productId = (String) context.get("productId");
    BigDecimal requiredQuantity = (BigDecimal) context.get("requiredQuantity");
    Timestamp requiredByDate = (Timestamp) context.get("requiredByDate");
    
    try {
        // Get current inventory levels
        Map<String, Object> inventoryContext = UtilMisc.toMap(
            "productId", productId,
            "facilityId", facilityId
        );
        
        Map<String, Object> inventoryResult = dispatcher.runSync("getInventoryAvailableByFacility", inventoryContext);
        BigDecimal availableInventory = (BigDecimal) inventoryResult.get("availableToPromiseTotal");
        
        // Calculate net requirements
        BigDecimal netRequirement = requiredQuantity.subtract(availableInventory);
        
        if (netRequirement.compareTo(BigDecimal.ZERO) > 0) {
            // Create production requirement
            Map<String, Object> requirementContext = UtilMisc.toMap(
                "requirementTypeId", "PRODUCT_REQUIREMENT",
                "productId", productId,
                "facilityId", facilityId,
                "quantity", netRequirement,
                "requirementStartDate", UtilDateTime.nowTimestamp(),
                "requiredByDate", requiredByDate,
                "statusId", "REQ_CREATED"
            );
            
            dispatcher.runSync("createRequirement", requirementContext);
        }
        
        return ServiceUtil.returnSuccess();
        
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("MRP calculation failed: " + e.getMessage());
    }
}
```

## Integration Points

### 1. ERP Integration

The SCM module integrates with other OFBiz applications:

```java
// Integration with accounting for cost tracking
public static Map<String, Object> createInventoryVarianceAccounting(DispatchContext dctx, Map<String, ? extends Object> context) {
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    String inventoryItemId = (String) context.get("inventoryItemId");
    BigDecimal varianceQuantity = (BigDecimal) context.get("varianceQuantity");
    BigDecimal unitCost = (BigDecimal) context.get("unitCost");
    
    try {
        // Create accounting transaction
        Map<String, Object> acctgTransContext = UtilMisc.toMap(
            "acctgTransTypeId", "INVENTORY_VARIANCE",
            "transactionDate", UtilDateTime.nowTimestamp(),
            "description", "Inventory variance adjustment"
        );
        
        Map<String, Object> transResult = dispatcher.runSync("createAcctgTrans", acctgTransContext);
        String acctgTransId = (String) transResult.get("acctgTransId");
        
        // Create debit entry
        BigDecimal varianceAmount = varianceQuantity.multiply(unitCost);
        Map<String, Object> debitEntry = UtilMisc.toMap(
            "acctgTransId", acctgTransId,
            "acctgTransEntrySeqId", "00001",
            "glAccountId", "140000", // Inventory Asset Account
            "debitCreditFlag", "D",
            "amount", varianceAmount.abs()
        );
        
        dispatcher.runSync("createAcctgTransEntry", debitEntry);
        
        return ServiceUtil.returnSuccess();
        
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("Failed to create accounting entries: " + e.getMessage());
    }
}
```

### 2. External System Integration

#### EDI Integration

```xml
<!-- EDI configuration for supplier communication -->
<DataResource dataResourceId="EDI_850_TEMPLATE"
              dataResourceTypeId="ELECTRONIC_TEXT"
              dataTemplateTypeId="FTL"
              statusId="CTNT_PUBLISHED"
              dataResourceName="EDI 850 Purchase Order Template"/>

<ElectronicText dataResourceId="EDI_850_TEMPLATE">
    <textData><![CDATA[
ST*850*${orderHeader.orderId}
BEG*00*SA*${orderHeader.orderId}**${orderHeader.orderDate?string("yyyyMMdd")}
<#list orderItems as item>
PO1*${item.orderItemSeqId}*${item.quantity}*EA*${item.unitPrice}**BP*${item.productId}
</#list>
SE*${segmentCount}*${orderHeader.orderId}
    ]]></textData>
</ElectronicText>
```

#### REST API Integration

```java
// REST endpoint for external system integration
@Path("/supply-chain")
public class SupplyChainResource {
    
    @POST
    @Path("/inventory/update")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response updateInventory(InventoryUpdateRequest request) {
        try {
            Map<String, Object> serviceContext = UtilMisc.toMap(
                "inventoryItemId", request.getInventoryItemId(),
                "quantityOnHandDiff", request.getQuantityChange(),
                "availableToPromiseDiff", request.getQuantityChange(),
                "reasonEnumId", "VAR_FOUND",
                "userLogin", getUserLogin()
            );
            
            Map<String, Object> result = dispatcher.runSync("createInventoryItemDetail", serviceContext);
            
            if (ServiceUtil.isSuccess(result)) {
                return Response.ok().entity(new SuccessResponse("Inventory updated successfully")).build();
            } else {
                return Response.status(Response.Status.BAD_REQUEST)
                              .entity(new ErrorResponse(ServiceUtil.getErrorMessage(result)))
                              .build();
            }
            
        } catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                          .entity(new ErrorResponse("Internal server error"))
                          .build();
        }
    }
}
```

## Configuration and Setup

### 1. Database Configuration

```xml
<!-- Entity group configuration for SCM -->
<entity-group group="org.apache.ofbiz.tenant" 
               entity="Product"/>
<entity-group group="org.apache.ofbiz.tenant" 
               entity="InventoryItem"/>
<entity-group group="org.apache.ofbiz.tenant" 
               entity="OrderHeader"/>
<entity-group group="org.apache.ofbiz.tenant" 
               entity="Shipment"/>
```

### 2. Service Configuration

```xml
<!-- Service definitions for SCM -->
<service name="calculateInventoryReorderLevel" engine="java"
         location="org.apache.ofbiz.product.inventory.InventoryServices"
         invoke="calculateReorderLevel">
    <description>Calculate reorder level based on demand history</description>
    <attribute name="productId" type="String" mode="IN" optional="false"/>
    <attribute name="facilityId" type="String" mode="IN" optional="false"/>
    <attribute name="daysToInclude" type="Integer" mode="IN" optional="true"/>
    <attribute name="reorderLevel" type="BigDecimal" mode="OUT" optional="false"/>
</service>
```

### 3. Security Configuration

```xml
<!-- Security permissions for SCM -->
<SecurityPermission permissionId="CATALOG_ADMIN" 
                    description="Permission to administer product catalog"/>
<SecurityPermission permissionId="FACILITY_ADMIN" 
                    description="Permission to administer facilities"/>
<SecurityPermission permissionId="ORDERMGR_CREATE" 
                    description="Permission to create orders"/>

<SecurityGroupPermission groupId="ORDERADMIN" 
                        permissionId="ORDERMGR_CREATE" 
                        fromDate="2001-01-01 12:00:00.0"/>
```

## Best Practices

### 1.