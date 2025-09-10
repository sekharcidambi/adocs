## Data Model Customization

## Overview

Apache OFBiz provides a sophisticated data model customization framework that allows developers to extend, modify, and adapt the existing entity definitions without directly modifying the core framework files. This approach ensures upgrade compatibility while enabling businesses to tailor the data structures to their specific requirements.

The data model in OFBiz is defined through XML entity definition files located throughout the framework, with the primary definitions residing in the `framework/entity/entitydef` directory and application-specific definitions in their respective `entitydef` directories within each component.

## Entity Definition Structure

### Core Entity Files

The OFBiz data model is organized into several key entity definition files:

- **entitymodel.xml**: Contains core business entities (Party, Product, Order, etc.)
- **entitygroup.xml**: Defines logical groupings of entities for datasource assignment
- **entityengine.xml**: Configures database connections and entity engine settings

### Entity Definition Syntax

Entities in OFBiz are defined using a declarative XML syntax:

```xml
<entity entity-name="CustomProduct" 
        package-name="org.apache.ofbiz.product.product"
        title="Custom Product Entity">
    <field name="productId" type="id-ne"/>
    <field name="customAttribute" type="description"/>
    <field name="createdDate" type="date-time"/>
    <field name="lastModifiedDate" type="date-time"/>
    <prim-key field="productId"/>
    <relation type="one" fk-name="CUST_PROD_PRODUCT" rel-entity-name="Product">
        <key-map field-name="productId"/>
    </relation>
</entity>
```

## Customization Approaches

### 1. Entity Extension

OFBiz supports extending existing entities through the `extend-entity` element, allowing you to add new fields without modifying core definitions:

```xml
<extend-entity entity-name="Product">
    <field name="customField1" type="description"/>
    <field name="customField2" type="currency-amount"/>
    <field name="customField3" type="indicator"/>
</extend-entity>
```

This approach is particularly useful for:
- Adding custom attributes to standard entities
- Maintaining upgrade compatibility
- Implementing tenant-specific customizations

### 2. Custom Entity Creation

For complex business requirements, create entirely new entities:

```xml
<entity entity-name="ProductCustomization" 
        package-name="com.company.product"
        title="Product Customization Options">
    <field name="customizationId" type="id-ne"/>
    <field name="productId" type="id-ne"/>
    <field name="customizationType" type="id"/>
    <field name="customizationValue" type="value"/>
    <field name="additionalCost" type="currency-amount"/>
    <prim-key field="customizationId"/>
    <relation type="one" fk-name="PROD_CUST_PRODUCT" rel-entity-name="Product">
        <key-map field-name="productId"/>
    </relation>
    <relation type="one" fk-name="PROD_CUST_TYPE" rel-entity-name="ProductCustomizationType">
        <key-map field-name="customizationType" rel-field-name="customizationTypeId"/>
    </relation>
</entity>
```

### 3. View Entity Customization

OFBiz allows creation of view entities for complex queries and reporting:

```xml
<view-entity entity-name="ProductSalesView" 
             package-name="com.company.product.sales"
             title="Product Sales Summary View">
    <member-entity entity-alias="PROD" entity-name="Product"/>
    <member-entity entity-alias="OI" entity-name="OrderItem"/>
    <member-entity entity-alias="OH" entity-name="OrderHeader"/>
    
    <alias-all entity-alias="PROD" prefix="product"/>
    <alias entity-alias="OI" name="quantity" field="quantity"/>
    <alias entity-alias="OI" name="unitPrice" field="unitPrice"/>
    <alias entity-alias="OH" name="orderDate" field="orderDate"/>
    
    <view-link entity-alias="PROD" rel-entity-alias="OI">
        <key-map field-name="productId"/>
    </view-link>
    <view-link entity-alias="OI" rel-entity-alias="OH">
        <key-map field-name="orderId"/>
    </view-link>
    
    <relation type="one-nofk" rel-entity-name="Product">
        <key-map field-name="productProductId" rel-field-name="productId"/>
    </relation>
</view-entity>
```

## Field Types and Validation

### Standard Field Types

OFBiz provides numerous predefined field types in `framework/entity/fieldtype/`:

- **id**: Primary key fields
- **id-ne**: Non-empty ID fields  
- **description**: Variable length text
- **currency-amount**: Monetary values with precision
- **date-time**: Timestamp fields
- **indicator**: Boolean Y/N fields

### Custom Field Type Definition

Define custom field types for specific business needs:

```xml
<field-type name="product-code" 
            sql-type="VARCHAR(20)" 
            java-type="String">
    <validate method="isProductCode"/>
</field-type>
```

## Integration with Entity Engine

### Delegator Configuration

The Entity Engine's Delegator provides the primary interface for data operations. Custom entities integrate seamlessly:

```java
// Accessing custom entities through Delegator
Delegator delegator = DelegatorFactory.getDelegator("default");

// Create custom entity instance
GenericValue customProduct = delegator.makeValue("CustomProduct");
customProduct.set("productId", "CUSTOM_001");
customProduct.set("customAttribute", "Special Configuration");
customProduct.create();

// Query with custom view entities
List<GenericValue> salesData = delegator.findList("ProductSalesView", 
    EntityCondition.makeCondition("productProductId", "PROD_001"), 
    null, null, null, false);
```

### Entity Condition Integration

Custom entities support the full range of EntityCondition operations:

```java
EntityCondition condition = EntityCondition.makeCondition(
    EntityCondition.makeCondition("customField1", EntityOperator.NOT_EQUAL, null),
    EntityOperator.AND,
    EntityCondition.makeCondition("customField2", EntityOperator.GREATER_THAN, BigDecimal.ZERO)
);
```

## Best Practices

### 1. Component Organization

Place custom entity definitions in appropriate component directories:
```
hot-deploy/
└── custom-component/
    ├── entitydef/
    │   ├── entitymodel.xml
    │   └── entitygroup.xml
    ├── script/
    └── servicedef/
```

### 2. Naming Conventions

- Use descriptive, business-meaningful entity names
- Prefix custom entities to avoid conflicts
- Follow OFBiz field naming patterns (camelCase)
- Use consistent relationship naming

### 3. Performance Considerations

- Create appropriate indexes for frequently queried fields
- Use view entities judiciously to avoid complex joins
- Consider denormalization for reporting entities
- Implement proper field sizing for storage efficiency

### 4. Migration and Versioning

Implement data migration scripts for schema changes:

```xml
<!-- In data/CustomDemoData.xml -->
<entity-engine-xml>
    <ProductCustomization customizationId="CUST_001" 
                         productId="GZ-1000" 
                         customizationType="COLOR" 
                         customizationValue="Blue"
                         additionalCost="15.00"/>
</entity-engine-xml>
```

This comprehensive approach to data model customization ensures that OFBiz implementations can adapt to diverse business requirements while maintaining system integrity and upgrade compatibility.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:49:08*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*