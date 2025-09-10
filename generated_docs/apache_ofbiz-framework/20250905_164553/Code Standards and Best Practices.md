## Code Standards and Best Practices

## Overview

Apache OFBiz follows strict code standards and best practices to maintain consistency, readability, and maintainability across its extensive ERP framework codebase. These standards are essential for a multi-tier enterprise application that spans presentation, business logic, and data access layers while supporting multiple programming languages and frameworks.

## Java Code Standards

### Naming Conventions

OFBiz adheres to standard Java naming conventions with specific ERP-focused extensions:

```java
// Service classes should end with "Services"
public class ProductServices {
    public static Map<String, Object> createProduct(DispatchContext dctx, Map<String, ? extends Object> context) {
        // Implementation
    }
}

// Entity names use CamelCase matching entity definitions
GenericValue productStore = EntityQuery.use(delegator)
    .from("ProductStore")
    .where("productStoreId", productStoreId)
    .queryOne();

// Constants use UPPER_SNAKE_CASE with module prefixes
public static final String MODULE = ProductServices.class.getName();
public static final String PRODUCT_CREATED = "PRODUCT_CREATED";
```

### Service Implementation Patterns

All business services in OFBiz must follow the standard service pattern:

```java
public static Map<String, Object> updateProductPrice(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    Security security = dctx.getSecurity();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    Locale locale = (Locale) context.get("locale");
    
    // Security check
    if (!security.hasEntityPermission("CATALOG", "_UPDATE", userLogin)) {
        return ServiceUtil.returnError(UtilProperties.getMessage("ProductErrorUiLabels", 
            "ProductSecurityErrorToRunUpdateProductPrice", locale));
    }
    
    try {
        // Business logic implementation
        String productId = (String) context.get("productId");
        BigDecimal price = (BigDecimal) context.get("price");
        
        // Entity operations
        GenericValue product = EntityQuery.use(delegator)
            .from("Product")
            .where("productId", productId)
            .queryOne();
            
        if (product == null) {
            return ServiceUtil.returnError("Product not found: " + productId);
        }
        
        // Update logic here
        
        return ServiceUtil.returnSuccess();
    } catch (GenericEntityException e) {
        Debug.logError(e, "Error updating product price: " + e.getMessage(), MODULE);
        return ServiceUtil.returnError("Error updating product price: " + e.getMessage());
    }
}
```

### Error Handling and Logging

OFBiz uses a centralized logging system with specific patterns:

```java
// Use module-specific loggers
private static final String MODULE = OrderServices.class.getName();

// Structured error handling
try {
    // Business logic
} catch (GenericEntityException e) {
    Debug.logError(e, "Database error in order processing: " + e.getMessage(), MODULE);
    return ServiceUtil.returnError(UtilProperties.getMessage("OrderErrorUiLabels", 
        "OrderProcessingError", locale));
} catch (GenericServiceException e) {
    Debug.logError(e, "Service error in order processing: " + e.getMessage(), MODULE);
    return ServiceUtil.returnError("Service execution failed");
}
```

## Groovy Standards

### DSL Usage in Entity Definitions

OFBiz uses Groovy for concise entity and service definitions:

```groovy
// Entity definition in entitymodel.xml alternatives
entity {
    name = "ProductCategory"
    package = "org.apache.ofbiz.product.category"
    title = "Product Category Entity"
    
    field {
        name = "productCategoryId"
        type = "id-ne"
        isPk = true
    }
    
    field {
        name = "categoryName"
        type = "name"
    }
}

// Service definitions
service {
    name = "createProductCategory"
    engine = "groovy"
    location = "component://product/groovyScripts/category/CategoryServices.groovy"
    invoke = "createProductCategory"
    auth = true
    
    attribute {
        name = "categoryName"
        type = "String"
        mode = "IN"
        optional = false
    }
}
```

### Screen Widget Groovy Actions

```groovy
// Screen preparation logic
productId = parameters.productId
if (productId) {
    product = from("Product").where("productId", productId).queryOne()
    context.product = product
    
    // Get related categories
    productCategories = from("ProductCategoryMember")
        .where("productId", productId)
        .filterByDate()
        .queryList()
    context.productCategories = productCategories
}
```

## XML Configuration Standards

### Service Definitions

Service definitions must include comprehensive metadata:

```xml
<service name="createProduct" engine="java"
         location="org.apache.ofbiz.product.product.ProductServices" invoke="createProduct" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="productGenericPermission" main-action="CREATE"/>
    <attribute name="productId" type="String" mode="INOUT" optional="true"/>
    <attribute name="productTypeId" type="String" mode="IN" optional="false"/>
    <attribute name="productName" type="String" mode="IN" optional="true"/>
    <attribute name="description" type="String" mode="IN" optional="true"/>
    <attribute name="priceDetailText" type="String" mode="IN" optional="true"/>
</service>
```

### Entity Definitions

Entity definitions require proper relationships and indexes:

```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product" title="Product Entity">
    <field name="productId" type="id-ne"></field>
    <field name="productTypeId" type="id"></field>
    <field name="productName" type="name"></field>
    <field name="salesDiscontinuationDate" type="date-time"></field>
    
    <prim-key field="productId"/>
    
    <relation type="one" fk-name="PROD_PRODTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
    
    <index name="PRODUCT_NAME_IDX">
        <index-field name="productName"/>
    </index>
</entity>
```

## Frontend Standards

### Screen Widget Architecture

OFBiz uses a declarative screen widget system:

```xml
<screen name="ProductDetail">
    <section>
        <actions>
            <entity-one entity-name="Product" value-field="product"/>
            <script location="component://product/groovyScripts/catalog/product/ProductDetail.groovy"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonProductDecorator" location="${parameters.productDecoratorLocation}">
                <decorator-section name="body">
                    <section>
                        <condition>
                            <not><if-empty field="product"/></not>
                        </condition>
                        <widgets>
                            <include-form name="ProductForm" location="component://product/widget/catalog/ProductForms.xml"/>
                        </widgets>
                        <fail-widgets>
                            <label style="h3">${uiLabelMap.ProductProductNotFound}</label>
                        </fail-widgets>
                    </section>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

### Form Widget Standards

```xml
<form name="EditProduct" type="single" target="updateProduct" title="" default-map-name="product">
    <alt-target use-when="product==null" target="createProduct"/>
    
    <auto-fields-service service-name="updateProduct" default-field-type="edit"/>
    
    <field name

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:10:03*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*