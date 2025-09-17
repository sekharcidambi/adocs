# Database Integration

## Overview

Apache OFBiz provides a comprehensive database integration layer that abstracts database operations through its Entity Engine. This sophisticated framework enables seamless interaction with multiple database systems while maintaining data consistency, transaction integrity, and optimal performance across enterprise applications.

The Entity Engine serves as the core component for all database operations in OFBiz, providing object-relational mapping (ORM) capabilities, connection pooling, transaction management, and database-agnostic query execution.

## Architecture

### Entity Engine Components

The OFBiz Entity Engine consists of several key components:

- **Entity Definition**: XML-based entity models that define database schema
- **Delegator**: Primary interface for database operations
- **GenericEntity**: Base class for all entity objects
- **EntityCondition**: Query condition builder
- **Connection Factory**: Database connection management
- **Transaction Manager**: Handles distributed transactions

```java
// Core Entity Engine interaction
Delegator delegator = DelegatorFactory.getDelegator("default");
GenericValue product = delegator.findOne("Product", 
    UtilMisc.toMap("productId", "DEMO_PRODUCT"), false);
```

### Database Abstraction Layer

OFBiz supports multiple database systems through its abstraction layer:

- **PostgreSQL** (Recommended)
- **MySQL/MariaDB**
- **Oracle Database**
- **Microsoft SQL Server**
- **Apache Derby** (Development/Testing)
- **H2 Database** (Development/Testing)

## Configuration

### Database Connection Setup

Database connections are configured in the `entityengine.xml` file located in `framework/entity/config/`:

```xml
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entity-config.xsd">
    
    <resource-loader name="fieldfile" class="org.apache.ofbiz.base.config.FileLoader"
            prepend-env="ofbiz.home" prefix="/framework/entity/fieldtype/"/>
    
    <transaction-factory class="org.apache.ofbiz.entity.transaction.JNDIFactory">
        <user-transaction-jndi jndi-server-name="localjndi" jndi-name="java:comp/UserTransaction"/>
        <transaction-manager-jndi jndi-server-name="localjndi" jndi-name="java:comp/TransactionManager"/>
    </transaction-factory>
    
    <connection-factory class="org.apache.ofbiz.entity.connection.DBCPConnectionFactory"/>
    
    <delegator name="default" entity-model-reader="main" entity-group-reader="main" 
               entity-eca-reader="main" distributed-cache-clear-enabled="false">
        <group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>
        <group-map group-name="org.apache.ofbiz.olap" datasource-name="localpostgresolap"/>
        <group-map group-name="org.apache.ofbiz.tenant" datasource-name="localpostgrestenant"/>
    </delegator>
    
    <datasource name="localpostgres"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="postgres"
            check-on-start="true"
            add-missing-on-start="true"
            use-pk-constraint-names="false"
            use-indices-unique="false"
            alias-view-columns="false"
            drop-fk-use-foreign-key-keyword="true"
            table-type="TABLE"
            character-set="utf8"
            collate="utf8_general_ci">
        <read-data reader-name="tenant"/>
        <read-data reader-name="seed"/>
        <read-data reader-name="seed-initial"/>
        <read-data reader-name="demo"/>
        <read-data reader-name="ext"/>
        <inline-jdbc
                jdbc-driver="org.postgresql.Driver"
                jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
                jdbc-username="ofbiz"
                jdbc-password="ofbiz"
                isolation-level="ReadCommitted"
                pool-minsize="2"
                pool-maxsize="250"
                time-between-eviction-runs-millis="600000"/>
    </datasource>
</entity-config>
```

### Field Type Mapping

Database-specific field types are defined in field type definition files:

```xml
<!-- fieldtypepostgres.xml -->
<fieldtypes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/fieldtypes.xsd">
    <field-type name="blob" sql-type="BYTEA" java-type="java.sql.Blob"/>
    <field-type name="date-time" sql-type="TIMESTAMPTZ" java-type="java.sql.Timestamp"/>
    <field-type name="currency-amount" sql-type="NUMERIC(18,3)" java-type="java.math.BigDecimal"/>
    <field-type name="id" sql-type="VARCHAR(20)" java-type="String"/>
    <field-type name="id-long" sql-type="VARCHAR(60)" java-type="String"/>
    <field-type name="id-vlong" sql-type="VARCHAR(250)" java-type="String"/>
    <field-type name="indicator" sql-type="CHAR(1)" java-type="String"/>
    <field-type name="very-long" sql-type="TEXT" java-type="String"/>
</fieldtypes>
```

## Entity Definition

### Entity Model Structure

Entities are defined in XML files using the entity model schema:

```xml
<!-- entitymodel.xml -->
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <entity entity-name="Product" package-name="org.apache.ofbiz.product.product" 
            title="Product Entity">
        <field name="productId" type="id-ne"/>
        <field name="productTypeId" type="id"/>
        <field name="primaryProductCategoryId" type="id"/>
        <field name="productName" type="name"/>
        <field name="description" type="description"/>
        <field name="longDescription" type="very-long"/>
        <field name="priceDetailText" type="long-varchar"/>
        <field name="smallImageUrl" type="url"/>
        <field name="mediumImageUrl" type="url"/>
        <field name="largeImageUrl" type="url"/>
        <field name="detailImageUrl" type="url"/>
        <field name="originalImageUrl" type="url"/>
        <field name="detailScreen" type="long-varchar"/>
        <field name="inventoryMessage" type="description"/>
        <field name="inventoryItemTypeId" type="id"/>
        <field name="requireInventory" type="indicator"/>
        <field name="quantityUomId" type="id"/>
        <field name="quantityIncluded" type="fixed-point"/>
        <field name="piecesIncluded" type="numeric"/>
        <field name="requireAmount" type="indicator"/>
        <field name="fixedAmount" type="currency-amount"/>
        <field name="amountUomTypeId" type="id"/>
        <field name="weightUomId" type="id"/>
        <field name="shippingWeight" type="fixed-point"/>
        <field name="productWeight" type="fixed-point"/>
        <field name="heightUomId" type="id"/>
        <field name="productHeight" type="fixed-point"/>
        <field name="shippingHeight" type="fixed-point"/>
        <field name="widthUomId" type="id"/>
        <field name="productWidth" type="fixed-point"/>
        <field name="shippingWidth" type="fixed-point"/>
        <field name="depthUomId" type="id"/>
        <field name="productDepth" type="fixed-point"/>
        <field name="shippingDepth" type="fixed-point"/>
        <field name="diameterUomId" type="id"/>
        <field name="productDiameter" type="fixed-point"/>
        <field name="productRating" type="fixed-point"/>
        <field name="ratingTypeEnum" type="id"/>
        <field name="returnable" type="indicator"/>
        <field name="taxable" type="indicator"/>
        <field name="chargeShipping" type="indicator"/>
        <field name="autoCreateKeywords" type="indicator"/>
        <field name="includeInPromotions" type="indicator"/>
        <field name="isVirtual" type="indicator"/>
        <field name="isVariant" type="indicator"/>
        <field name="virtualVariantMethodEnum" type="id"/>
        <field name="originGeoId" type="id"/>
        <field name="requirementMethodEnumId" type="id"/>
        <field name="billOfMaterialLevel" type="numeric"/>
        <field name="reservMaxPersons" type="fixed-point"/>
        <field name="reserv2ndPPPerc" type="fixed-point"/>
        <field name="reservNthPPPerc" type="fixed-point"/>
        <field name="configId" type="long-varchar"/>
        <field name="createdDate" type="date-time"/>
        <field name="createdByUserLogin" type="id-vlong"/>
        <field name="lastModifiedDate" type="date-time"/>
        <field name="lastModifiedByUserLogin" type="id-vlong"/>
        <field name="inShippingBox" type="indicator"/>
        <field name="defaultShipmentBoxTypeId" type="id"/>
        <field name="lotIdFilledIn" type="long-varchar"/>
        <field name="orderDecimalQuantity" type="indicator"/>
        <field name="lastUpdatedStamp" type="date-time"/>
        <field name="lastUpdatedTxStamp" type="date-time"/>
        <field name="createdStamp" type="date-time"/>
        <field name="createdTxStamp" type="date-time"/>
        
        <prim-key field="productId"/>
        
        <relation type="one" fk-name="PROD_PRDT_TYPE" rel-entity-name="ProductType">
            <key-map field-name="productTypeId"/>
        </relation>
        <relation type="one" fk-name="PROD_PRIM_CTGRY" rel-entity-name="ProductCategory">
            <key-map field-name="primaryProductCategoryId" rel-field-name="productCategoryId"/>
        </relation>
        <relation type="many" rel-entity-name="ProductAssoc">
            <key-map field-name="productId" rel-field-name="productId"/>
        </relation>
        
        <index name="PRODUCT_PRDTPE">
            <index-field name="productTypeId"/>
        </index>
        <index name="PRODUCT_VRTL">
            <index-field name="isVirtual"/>
        </index>
    </entity>
</entitymodel>
```

### View Entities

OFBiz supports complex view entities that join multiple tables:

```xml
<view-entity entity-name="ProductAndPrice" package-name="org.apache.ofbiz.product.product"
        title="Product And Price View Entity">
    <member-entity entity-alias="PROD" entity-name="Product"/>
    <member-entity entity-alias="PRICE" entity-name="ProductPrice"/>
    
    <alias-all entity-alias="PROD"/>
    <alias entity-alias="PRICE" name="price"/>
    <alias entity-alias="PRICE" name="currencyUomId"/>
    <alias entity-alias="PRICE" name="productPriceTypeId"/>
    <alias entity-alias="PRICE" name="productPricePurposeId"/>
    <alias entity-alias="PRICE" name="fromDate"/>
    <alias entity-alias="PRICE" name="thruDate"/>
    
    <view-link entity-alias="PROD" rel-entity-alias="PRICE">
        <key-map field-name="productId"/>
    </view-link>
    
    <relation type="one-nofk" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</view-entity>
```

## Database Operations

### Basic CRUD Operations

#### Create Operations

```java
// Creating a new entity
Delegator delegator = DelegatorFactory.getDelegator("default");

GenericValue product = delegator.makeValue("Product");
product.put("productId", "NEW_PRODUCT_001");
product.put("productName", "New Product");
product.put("productTypeId", "FINISHED_GOOD");
product.put("isVirtual", "N");
product.put("isVariant", "N");

try {
    product = delegator.create(product);
    Debug.logInfo("Product created successfully: " + product.get("productId"), MODULE);
} catch (GenericEntityException e) {
    Debug.logError(e, "Error creating product", MODULE);
}
```

#### Read Operations

```java
// Find by primary key
GenericValue product = delegator.findOne("Product", 
    UtilMisc.toMap("productId", "DEMO_PRODUCT"), false);

// Find with conditions
List<GenericValue> products = delegator.findByAnd("Product", 
    UtilMisc.toMap("productTypeId", "FINISHED_GOOD", "isVirtual", "N"), 
    null, false);

// Find with complex conditions
EntityCondition condition = EntityCondition.makeCondition(
    UtilMisc.toList(
        EntityCondition.makeCondition("productTypeId", EntityOperator.EQUALS, "FINISHED_GOOD"),
        EntityCondition.makeCondition("isVirtual", EntityOperator.EQUALS, "N"),
        EntityCondition.makeCondition("productName", EntityOperator.LIKE, "%Demo%")
    ), EntityOperator.AND);

List<GenericValue> filteredProducts = delegator.findList("Product", condition, 
    null, UtilMisc.toList("productName"), null, false);
```

#### Update Operations

```java
// Update existing entity
GenericValue product = delegator.findOne("Product", 
    UtilMisc.toMap("productId", "DEMO_PRODUCT"), false);

if (product != null) {
    product.put("productName", "Updated Product Name");
    product.put("description", "Updated description");
    
    try {
        product.store();
        Debug.logInfo("Product updated successfully", MODULE);
    } catch (GenericEntityException e) {
        Debug.logError(e, "Error updating product", MODULE);
    }
}

// Bulk update
delegator.storeByCondition("Product", 
    UtilMisc.toMap("taxable", "Y"), 
    EntityCondition.makeCondition("productTypeId", EntityOperator.EQUALS, "FINISHED_GOOD"));
```

#### Delete Operations

```java
// Delete by primary key
delegator.removeByPrimaryKey(delegator.makePK("Product", "productId", "DEMO_PRODUCT"));

// Delete with conditions
delegator.removeByCondition("ProductKeyword", 
    EntityCondition.makeCondition("productId", EntityOperator.EQUALS, "DEMO_PRODUCT"));
```

### Advanced Query Operations

#### Dynamic Queries with EntityQuery

```java
// Using EntityQuery API (recommended approach)
List<GenericValue> products = EntityQuery.use(delegator)
    .from("Product")
    .where("productTypeId", "FINISHED