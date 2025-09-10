## Database Support (MySQL/PostgreSQL/Derby)

## Overview

Apache OFBiz provides comprehensive database abstraction and multi-database support through its Entity Engine, enabling seamless integration with MySQL, PostgreSQL, and Derby databases. This database-agnostic architecture allows enterprises to choose their preferred database solution while maintaining consistent data access patterns across the entire ERP system.

The framework's database support is built around the **Data Access Layer** of OFBiz's multi-tier architecture, providing a unified interface for all database operations regardless of the underlying database technology. This abstraction layer ensures that business logic remains independent of database-specific implementations.

## Supported Database Configurations

### MySQL Support

MySQL integration in OFBiz leverages the MySQL Connector/J driver and supports both MySQL 5.7+ and MySQL 8.0+ versions. The framework includes optimized configurations for MySQL's specific features:

```xml
<!-- framework/entity/config/entityengine.xml -->
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?autoReconnect=true&amp;characterEncoding=UTF-8&amp;sessionVariables=sql_mode=''"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

### PostgreSQL Integration

PostgreSQL support includes advanced features like JSON data types, full-text search capabilities, and optimized connection pooling:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="true"
    use-indices-unique="true">
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"/>
</datasource>
```

### Derby Embedded Database

Derby serves as the default embedded database for development and testing environments, requiring no external database server setup:

```xml
<datasource name="localderby"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="derby"
    check-on-start="true"
    add-missing-on-start="true">
    <inline-jdbc
        jdbc-driver="org.apache.derby.jdbc.EmbeddedDriver"
        jdbc-uri="jdbc:derby:runtime/data/derby/ofbiz;create=true"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"/>
</datasource>
```

## Entity Engine Architecture

The Entity Engine serves as OFBiz's Object-Relational Mapping (ORM) layer, providing database-agnostic data access through several key components:

### Field Type Mapping

Each supported database has specific field type definitions that map OFBiz's generic field types to database-specific data types:

```xml
<!-- framework/entity/fieldtype/fieldtypemysql.xml -->
<fieldtype name="id" sql-type="VARCHAR(20)" java-type="String"/>
<fieldtype name="id-long" sql-type="VARCHAR(60)" java-type="String"/>
<fieldtype name="id-vlong" sql-type="VARCHAR(250)" java-type="String"/>
<fieldtype name="very-short" sql-type="VARCHAR(10)" java-type="String"/>
<fieldtype name="short-varchar" sql-type="VARCHAR(60)" java-type="String"/>
<fieldtype name="long-varchar" sql-type="VARCHAR(255)" java-type="String"/>
<fieldtype name="very-long" sql-type="LONGTEXT" java-type="String"/>
```

### Connection Pool Management

OFBiz implements sophisticated connection pooling strategies optimized for each database type:

```java
// framework/entity/src/main/java/org/apache/ofbiz/entity/connection/ConnectionFactory.java
public class ConnectionFactory {
    public static Connection getConnection(String helperName) throws SQLException {
        return getConnection(null, helperName);
    }
    
    public static Connection getConnection(String groupName, String helperName) 
            throws SQLException {
        // Database-specific connection logic
        GenericHelperInfo helperInfo = EntityConfigUtil.getEntityHelperInfo(helperName);
        return helperInfo.getConnectionSource().getConnection();
    }
}
```

## Database Migration and Schema Management

### Automatic Schema Generation

OFBiz automatically generates and maintains database schemas based on entity definitions:

```bash
# Generate schema for specific database
./gradlew "ofbiz --load-data readers=seed,seed-initial,ext --delegator-name=default"

# Update existing schema
./gradlew "ofbiz --load-data readers=seed --delegator-name=default --create-pks --drop-pks"
```

### Entity Model Definitions

Entities are defined in XML format and automatically mapped to database tables:

```xml
<!-- applications/accounting/entitydef/entitymodel.xml -->
<entity entity-name="Invoice" package-name="org.apache.ofbiz.accounting.invoice">
    <field name="invoiceId" type="id-ne"/>
    <field name="invoiceTypeId" type="id"/>
    <field name="partyId" type="id"/>
    <field name="partyIdFrom" type="id"/>
    <field name="billingAccountId" type="id"/>
    <field name="invoiceMessage" type="very-long"/>
    <field name="referenceNumber" type="long-varchar"/>
    <prim-key field="invoiceId"/>
    <relation type="one" fk-name="INVOICE_INVTYPE" rel-entity-name="InvoiceType">
        <key-map field-name="invoiceTypeId"/>
    </relation>
</entity>
```

## Performance Optimization

### Database-Specific Optimizations

Each database implementation includes specific performance tuning:

**MySQL Optimizations:**
- InnoDB engine configuration for ACID compliance
- Query cache optimization for frequently accessed data
- Index optimization for OFBiz's entity relationships

**PostgreSQL Optimizations:**
- VACUUM and ANALYZE scheduling for maintenance
- Partial index support for conditional queries
- Advanced statistics collection for query planning

**Derby Optimizations:**
- Embedded mode for reduced connection overhead
- Page cache sizing for memory-constrained environments
- Lock timeout configuration for concurrent access

### Query Performance Monitoring

OFBiz includes built-in database performance monitoring:

```java
// framework/entity/src/main/java/org/apache/ofbiz/entity/util/EntityQuery.java
public class EntityQuery {
    public EntityListIterator queryIterator() throws GenericEntityException {
        long startTime = System.currentTimeMillis();
        try {
            return this.getDelegator().find(dynamicViewEntity != null ? 
                dynamicViewEntity.getEntityName() : entityName, 
                whereEntityCondition, havingEntityCondition, fieldsToSelect, 
                orderBy, findOptions);
        } finally {
            if (Debug.

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:00:29*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*