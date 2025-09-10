## Database Support

## Overview

Apache OFBiz provides comprehensive database support through its Entity Engine, a sophisticated Object-Relational Mapping (ORM) framework that abstracts database operations and provides a unified interface for data persistence across multiple database management systems. The database support layer is fundamental to OFBiz's architecture, enabling seamless integration with various RDBMS platforms while maintaining consistency and performance across the entire framework.

## Supported Database Systems

OFBiz's Entity Engine supports a wide range of database systems through its flexible datasource configuration:

### Primary Supported Databases
- **Derby** - Default embedded database for development and testing
- **MySQL/MariaDB** - Popular open-source databases for production deployments
- **PostgreSQL** - Advanced open-source database with extensive feature support
- **Oracle Database** - Enterprise-grade commercial database solution
- **Microsoft SQL Server** - Microsoft's enterprise database platform
- **H2 Database** - Lightweight Java-based database for testing scenarios

### Database-Specific Configurations

Each database system requires specific JDBC drivers and connection parameters configured in the `framework/entity/config/entityengine.xml` file:

```xml
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    constraint-name-clip-length="30">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?autoReconnect=true&amp;characterEncoding=UTF-8"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

## Entity Engine Architecture

### Entity Definitions

The Entity Engine uses XML-based entity definitions located in `framework/entity/entitydef/` and component-specific directories. These definitions create a database-agnostic data model:

```xml
<entity entity-name="Party" package-name="org.apache.ofbiz.party.party">
    <field name="partyId" type="id-ne"/>
    <field name="partyTypeId" type="id"/>
    <field name="externalId" type="id"/>
    <field name="preferredCurrencyUomId" type="id"/>
    <field name="description" type="description"/>
    <field name="statusId" type="id"/>
    <field name="createdDate" type="date-time"/>
    <field name="createdByUserLogin" type="id-vlong"/>
    <field name="lastModifiedDate" type="date-time"/>
    <field name="lastModifiedByUserLogin" type="id-vlong"/>
    <field name="dataSourceId" type="id"/>
    <field name="isUnread" type="indicator"/>
    <prim-key field="partyId"/>
</entity>
```

### Field Types and Database Mapping

OFBiz defines abstract field types in `framework/entity/fieldtype/` that map to database-specific SQL types:

```xml
<field-type-def type="id" sql-type="VARCHAR(20)" java-type="String"/>
<field-type-def type="id-long" sql-type="VARCHAR(60)" java-type="String"/>
<field-type-def type="id-vlong" sql-type="VARCHAR(250)" java-type="String"/>
<field-type-def type="very-short" sql-type="VARCHAR(10)" java-type="String"/>
<field-type-def type="short-varchar" sql-type="VARCHAR(60)" java-type="String"/>
<field-type-def type="long-varchar" sql-type="VARCHAR(255)" java-type="String"/>
```

## Database Operations and APIs

### GenericDelegator Interface

The `GenericDelegator` serves as the primary interface for database operations, providing methods for CRUD operations, queries, and transaction management:

```java
// Entity creation and storage
GenericValue party = delegator.makeValue("Party");
party.set("partyId", "PARTY_001");
party.set("partyTypeId", "PERSON");
party.create();

// Entity retrieval
GenericValue retrievedParty = delegator.findOne("Party", 
    UtilMisc.toMap("partyId", "PARTY_001"), false);

// Complex queries using EntityCondition
List<GenericValue> parties = delegator.findList("Party",
    EntityCondition.makeCondition("partyTypeId", "PERSON"),
    null, null, null, false);
```

### Entity Query Builder

OFBiz provides a fluent query builder API for complex database operations:

```java
List<GenericValue> results = EntityQuery.use(delegator)
    .from("OrderHeader")
    .where("statusId", "ORDER_APPROVED")
    .orderBy("orderDate DESC")
    .filterByDate()
    .queryList();
```

## Connection Pool Management

### JDBC Connection Pooling

OFBiz implements sophisticated connection pooling mechanisms to optimize database performance:

```xml
<inline-jdbc
    jdbc-driver="org.postgresql.Driver"
    jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz"
    jdbc-username="ofbiz"
    jdbc-password="ofbiz"
    isolation-level="ReadCommitted"
    pool-minsize="5"
    pool-maxsize="50"
    pool-sleeptime="300000"
    pool-lifetime="600000"
    pool-deadlock-maxwait="300000"
    pool-deadlock-retrywait="10000"
    validation-query="SELECT 1"/>
```

### Connection Pool Monitoring

The framework provides JMX beans and administrative tools for monitoring connection pool health and performance metrics through the WebTools application.

## Transaction Management

### Distributed Transaction Support

OFBiz supports distributed transactions across multiple datasources using JTA (Java Transaction API):

```java
boolean beganTransaction = false;
try {
    beganTransaction = TransactionUtil.begin();
    
    // Perform multiple database operations
    delegator.create(entity1);
    delegator.store(entity2);
    delegator.removeByAnd("EntityName", conditions);
    
    TransactionUtil.commit(beganTransaction);
} catch (GenericTransactionException e) {
    TransactionUtil.rollback(beganTransaction, "Error message", e);
}
```

### Transaction Isolation Levels

Different isolation levels can be configured per datasource to balance consistency and performance requirements based on specific use cases.

## Database Schema Management

### Automatic Schema Generation

The Entity Engine can automatically generate database schemas from entity definitions:

```bash
./gradlew "ofbiz --load-data readers=seed,seed-initial,ext"
```

### Schema Updates and Migrations

OFBiz provides tools for schema evolution and data migration:

- **Entity Sync Tools** - Synchronize entity definitions with database schema
- **Data Migration Utilities** - Transform and migrate data between schema versions
- **Backup and Restore** - Built-in utilities for database backup and restoration

## Performance Optimization

### Query Optimization Features

- **Entity Caching** - Multi-level caching system for frequently accessed entities
- **View Entities** - Database views defined in XML for complex queries
- **Batch Operations** - Bulk insert, update, and delete operations
- **Connection Pooling** - Optimized connection management and reuse

### Monitoring and Profiling

The framework includes comprehensive database performance monitoring through:

- SQL query logging and analysis
- Connection pool metrics
- Transaction performance tracking
- Cache hit/miss statistics

## Integration with OFBiz Components

The database support layer integrates seamlessly with all OFBiz components:

- **Service Engine** - Automatic transaction management for service calls
- **Security Framework** - Entity-level security and access

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:39:48*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*