## Data Access Layer

## Overview

The Data Access Layer in Apache OFBiz serves as the foundational abstraction between the business logic and underlying data storage systems. This layer implements OFBiz's unique Entity Engine, a sophisticated ORM-like framework that provides database-agnostic data access capabilities across multiple database systems including MySQL, PostgreSQL, and Derby. Unlike traditional ORM frameworks, the Entity Engine is specifically designed for enterprise applications with complex data relationships and multi-tenant architectures.

## Entity Engine Architecture

### Core Components

The Entity Engine consists of several key components that work together to provide robust data access:

- **Entity Definitions**: XML-based schema definitions located in `entitydef` directories
- **Delegator**: The primary interface for all database operations
- **GenericEntity**: Base class for all entity objects
- **EntityCondition**: Type-safe query condition builder
- **EntityListIterator**: Memory-efficient result set iteration

### Entity Definition Structure

Entity definitions are declared in XML files following the `entitymodel.xsd` schema:

```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productTypeId" type="id"/>
    <field name="primaryProductCategoryId" type="id"/>
    <field name="productName" type="name"/>
    <field name="description" type="very-long"/>
    <field name="createdDate" type="date-time"/>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRODTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

## Database Configuration and Multi-Database Support

### Datasource Configuration

OFBiz supports multiple database configurations through the `entityengine.xml` file located in `framework/entity/config/`. Each datasource can be configured for different database types:

```xml
<datasource name="localderby" helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="derby" check-on-start="true" add-missing-on-start="true"
            use-pk-constraint-names="false" use-indices-unique="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <inline-jdbc jdbc-driver="org.apache.derby.jdbc.EmbeddedDriver"
                 jdbc-uri="jdbc:derby:runtime/data/derby/ofbiz;create=true"
                 jdbc-username="ofbiz" jdbc-password="ofbiz"
                 isolation-level="ReadCommitted" pool-minsize="2" pool-maxsize="250"/>
</datasource>
```

### Database Migration and Schema Management

The Entity Engine automatically handles schema creation and updates through:

- **Schema Synchronization**: `./gradlew syncdb` command synchronizes entity definitions with database schema
- **Data Loading**: Hierarchical data loading system supporting seed, demo, and production data
- **Migration Scripts**: Groovy-based migration scripts in `framework/entity/src/main/groovy/`

## Delegator Pattern Implementation

### Primary Interface

The Delegator serves as the primary interface for all database operations, providing a consistent API regardless of the underlying database:

```java
// Obtaining delegator instance
Delegator delegator = DelegatorFactory.getDelegator("default");

// Creating entities
GenericValue product = delegator.makeValue("Product");
product.set("productId", "DEMO_PRODUCT");
product.set("productName", "Demo Product");
product.set("productTypeId", "FINISHED_GOOD");
delegator.create(product);

// Querying with conditions
List<GenericValue> products = delegator.findList("Product", 
    EntityCondition.makeCondition("productTypeId", "FINISHED_GOOD"),
    null, null, null, false);
```

### Transaction Management

The Delegator integrates with OFBiz's transaction management system:

```java
try {
    TransactionUtil.begin();
    
    // Multiple database operations
    delegator.create(product);
    delegator.store(relatedEntity);
    
    TransactionUtil.commit();
} catch (GenericTransactionException e) {
    TransactionUtil.rollback();
    throw new ServiceException("Transaction failed", e);
}
```

## Advanced Query Capabilities

### EntityCondition Framework

The EntityCondition framework provides type-safe, composable query conditions:

```java
EntityCondition condition = EntityCondition.makeCondition(
    EntityCondition.makeCondition("productTypeId", "FINISHED_GOOD"),
    EntityOperator.AND,
    EntityCondition.makeCondition("createdDate", EntityOperator.GREATER_THAN, 
        UtilDateTime.getDayStart(UtilDateTime.nowTimestamp()))
);

EntityFindOptions findOptions = new EntityFindOptions();
findOptions.setMaxRows(100);
findOptions.setOffset(0);

List<GenericValue> results = delegator.findList("Product", condition, 
    null, UtilMisc.toList("productName"), findOptions, false);
```

### Dynamic View Entities

OFBiz supports dynamic view creation for complex queries spanning multiple entities:

```java
DynamicViewEntity dve = new DynamicViewEntity();
dve.addMemberEntity("PROD", "Product");
dve.addMemberEntity("CAT", "ProductCategory");
dve.addViewLink("PROD", "CAT", false, 
    ModelKeyMap.makeKeyMapList("primaryProductCategoryId", "productCategoryId"));
dve.addAlias("PROD", "productId");
dve.addAlias("PROD", "productName");
dve.addAlias("CAT", "categoryName");

EntityListIterator eli = delegator.findListIteratorByCondition(dve, 
    condition, null, null);
```

## Integration with Business Logic Layer

### Service Engine Integration

The Data Access Layer seamlessly integrates with OFBiz's Service Engine through service implementations:

```java
public static Map<String, Object> createProduct(DispatchContext dctx, 
        Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    
    try {
        GenericValue product = delegator.makeValue("Product", context);
        product = delegator.createSetNextSeqId(product);
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        result.put("productId", product.get("productId"));
        return result;
    } catch (GenericEntityException e) {
        return ServiceUtil.returnError("Error creating product: " + e.getMessage());
    }
}
```

### Entity Maintenance Integration

The framework provides automatic entity maintenance capabilities through the Entity Maintenance screens, which dynamically generate CRUD interfaces based on entity definitions.

## Performance Optimization and Caching

### Entity Cache Management

OFBiz implements sophisticated caching mechanisms at the entity level:

- **Distributed Cache**: Integration with cache frameworks for multi-server deployments
- **Cache Partitioning**: Tenant-aware caching for multi-tenant installations
- **Selective Caching**: Entity-specific cache configuration through `cache.xml`

### Connection Pool Management

Database connection pooling is configured per datasource with monitoring capabilities:

```xml
<inline-jdbc jdbc-driver="com.mysql.cj.jdbc.Driver"
             jdbc-uri="jdbc:mysql://localhost:3306/ofbiz"
             pool-minsize="5" pool-maxsize="50"
             pool-sleeptime="300000" pool-lifetime="600000"
             pool-deadlock-maxwait="300000"/>
```

## Best Practices and Patterns

### Entity Design Patterns

- **Consistent Naming**: Follow OFBiz naming conventions for entities and fields
- **Proper Relationships**: Define foreign key relationships for data integrity
- **Audit Fields**: Include standard audit fields (`createdDate`, `lastModifiedDate`)
- **Status Management**: Implement status entities for workflow management

### Performance Considerations

- Use `EntityListIterator` for large result sets to avoid memory issues
-

## Subsections

- [Database Abstraction](./Database Abstraction.md)
- [ORM Integration (Hibernate)](./ORM Integration (Hibernate).md)

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

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Database Abstraction**: Detailed coverage of database abstraction
- **ORM Integration (Hibernate)**: Detailed coverage of orm integration (hibernate)

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:53:56*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*