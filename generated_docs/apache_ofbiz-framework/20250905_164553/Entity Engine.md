### Entity Engine

## Overview

The Entity Engine is the cornerstone of Apache OFBiz's data access layer, providing a sophisticated Object-Relational Mapping (ORM) framework that abstracts database operations and enables seamless interaction with multiple database systems. As part of OFBiz's multi-tier architecture, the Entity Engine serves as the primary interface between the business logic layer and the underlying data storage, supporting MySQL, PostgreSQL, and Derby databases out of the box.

The Entity Engine implements a metadata-driven approach where entity definitions are declared in XML files, allowing for database-agnostic operations and dynamic schema management. This design philosophy aligns perfectly with OFBiz's enterprise-grade requirements for flexibility, scalability, and maintainability.

## Core Architecture Components

### Entity Definitions and Metadata

Entity definitions in OFBiz are stored in `entitymodel.xml` files located throughout the framework's component structure. These XML files define the schema, relationships, and constraints for all business entities:

```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"></field>
    <field name="productTypeId" type="id"></field>
    <field name="primaryProductCategoryId" type="id"></field>
    <field name="productName" type="name"></field>
    <field name="description" type="very-long"></field>
    <field name="createdDate" type="date-time"></field>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRODTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

### Delegator Pattern Implementation

The `Delegator` interface serves as the primary entry point for all entity operations. It implements the delegation pattern to route database operations through appropriate handlers:

```java
// Obtaining a delegator instance
Delegator delegator = DelegatorFactory.getDelegator("default");

// Creating a new entity
GenericValue product = delegator.makeValue("Product");
product.set("productId", "DEMO_PRODUCT_001");
product.set("productName", "Demo Product");
product.set("productTypeId", "FINISHED_GOOD");
delegator.create(product);
```

### GenericValue and GenericEntity

The Entity Engine utilizes `GenericValue` objects as dynamic entity representations, eliminating the need for traditional POJOs while maintaining type safety through metadata validation:

```java
// Finding entities with conditions
List<GenericValue> products = delegator.findByAnd("Product", 
    UtilMisc.toMap("productTypeId", "FINISHED_GOOD"), null, false);

// Working with related entities
GenericValue product = delegator.findOne("Product", 
    UtilMisc.toMap("productId", "DEMO_PRODUCT_001"), false);
List<GenericValue> productCategories = product.getRelated("ProductCategoryMember", null, null, false);
```

## Database Abstraction and Multi-Database Support

### Database Configuration

The Entity Engine's database abstraction is configured through `entityengine.xml`, supporting multiple datasources and database types:

```xml
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?autoReconnect=true"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"/>
</datasource>
```

### Field Type Mapping

Database-specific field types are defined in `fieldtype*.xml` files, ensuring proper data type mapping across different database systems:

```xml
<field-type name="id" sql-type="VARCHAR(20)" java-type="String"/>
<field-type name="id-long" sql-type="VARCHAR(60)" java-type="String"/>
<field-type name="very-long" sql-type="TEXT" java-type="String"/>
<field-type name="currency-amount" sql-type="DECIMAL(18,3)" java-type="BigDecimal"/>
```

## Advanced Query Capabilities

### EntityCondition Framework

The Entity Engine provides a sophisticated condition framework for building complex queries programmatically:

```java
// Building complex conditions
EntityCondition condition = EntityCondition.makeCondition(
    EntityCondition.makeCondition("productTypeId", EntityOperator.EQUALS, "FINISHED_GOOD"),
    EntityOperator.AND,
    EntityCondition.makeCondition("createdDate", EntityOperator.GREATER_THAN, 
        UtilDateTime.getDayStart(UtilDateTime.nowTimestamp()))
);

// Using EntityListIterator for large result sets
EntityListIterator eli = delegator.find("Product", condition, null, null, null, null);
try {
    GenericValue product;
    while ((product = eli.next()) != null) {
        // Process each product
    }
} finally {
    eli.close();
}
```

### Dynamic View Entities

The Entity Engine supports dynamic view creation for complex reporting and data aggregation:

```java
DynamicViewEntity dve = new DynamicViewEntity();
dve.addMemberEntity("P", "Product");
dve.addMemberEntity("PC", "ProductCategory");
dve.addViewLink("P", "PC", Boolean.FALSE, 
    ModelKeyMap.makeKeyMapList("primaryProductCategoryId", "productCategoryId"));
dve.addAlias("P", "productId");
dve.addAlias("P", "productName");
dve.addAlias("PC", "categoryName");

List<GenericValue> results = delegator.findList(dve, condition, null, null, null, false);
```

## Transaction Management and Performance

### Transaction Handling

The Entity Engine integrates with OFBiz's transaction management system, supporting both programmatic and declarative transaction control:

```java
// Programmatic transaction management
boolean beganTransaction = false;
try {
    beganTransaction = TransactionUtil.begin();
    
    // Perform multiple entity operations
    delegator.create(product);
    delegator.store(relatedEntity);
    
    TransactionUtil.commit(beganTransaction);
} catch (GenericEntityException e) {
    TransactionUtil.rollback(beganTransaction, "Error in entity operations", e);
    throw e;
}
```

### Caching Strategy

The Entity Engine implements multi-level caching to optimize performance:

- **Entity Cache**: Caches individual entity instances
- **Condition Cache**: Caches query results based on conditions
- **View Cache**: Caches complex view entity results

```xml
<!-- Cache configuration in cache.xml -->
<cache name="entity.Product" 
    max-size="1000" 
    expire-time="1800000"
    use-soft-reference="true"/>
```

## Integration with Business Logic Layer

### Service Engine Integration

The Entity Engine seamlessly integrates with OFBiz's Service Engine, providing automatic transaction management and data validation:

```java
public static Map<String, Object> createProduct(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    
    try {
        GenericValue product = delegator.makeValue("Product", context);
        product = delegator.createSetNextSeqId(product);
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        result.put("productId", product.get("productId"));
        return result;
    } catch (GenericEntityException e) {
        return ServiceUtil.returnError("Error creating product: " + e.getMessage());

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:52:46*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*