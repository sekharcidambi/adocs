# Database Architecture

The Apache OFBiz framework provides a robust and flexible database architecture designed to support enterprise-level applications across various business domains. This architecture abstracts database operations through a sophisticated entity engine that enables seamless integration with multiple database systems while maintaining data integrity and performance.

## Overview

OFBiz's database architecture is built around the Entity Engine, a powerful Object-Relational Mapping (ORM) layer that provides database abstraction and management capabilities. The architecture supports multiple database vendors, transaction management, connection pooling, and advanced features like geospatial data handling.

### Key Components

- **Entity Engine**: Core ORM layer for database abstraction
- **Entity Definitions**: XML-based schema definitions
- **Delegator**: Primary interface for database operations
- **Connection Pooling**: Efficient database connection management
- **Transaction Management**: ACID compliance and distributed transactions
- **Data Source Configuration**: Flexible database connectivity options

## Database Integration

The OFBiz framework provides comprehensive database integration capabilities through its Entity Engine, supporting multiple database vendors and providing a unified interface for data operations.

### Supported Database Systems

OFBiz supports a wide range of database systems out of the box:

- **PostgreSQL** (Recommended)
- **MySQL/MariaDB**
- **Oracle Database**
- **Microsoft SQL Server**
- **Apache Derby** (Default for development)
- **H2 Database** (In-memory testing)
- **IBM DB2**
- **Firebird**

### Entity Engine Configuration

The database integration is configured through the `entityengine.xml` file located in the framework configuration directory:

```xml
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entity-config.xsd">
    
    <!-- Database connection configuration -->
    <datasource name="localderby"
                helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
                field-type-name="derby"
                check-on-start="true"
                add-missing-on-start="true"
                use-pk-constraint-names="false"
                constraint-name-clip-length="18">
        
        <read-data reader-name="tenant"/>
        <read-data reader-name="seed"/>
        <read-data reader-name="seed-initial"/>
        <read-data reader-name="demo"/>
        <read-data reader-name="ext"/>
        
        <inline-jdbc
                jdbc-driver="org.apache.derby.jdbc.EmbeddedDriver"
                jdbc-uri="jdbc:derby:runtime/data/derby/ofbiz;create=true"
                jdbc-username="ofbiz"
                jdbc-password="ofbiz"
                isolation-level="ReadCommitted"
                pool-minsize="2"
                pool-maxsize="250"
                time-between-eviction-runs-millis="600000"/>
    </datasource>
</entity-config>
```

### Entity Definitions

Entities are defined using XML schema files that describe the database structure:

```xml
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
        <field name="productId" type="id-ne"/>
        <field name="productTypeId" type="id"/>
        <field name="productName" type="name"/>
        <field name="description" type="description"/>
        <field name="createdDate" type="date-time"/>
        <field name="lastModifiedDate" type="date-time"/>
        
        <prim-key field="productId"/>
        
        <relation type="one" fk-name="PROD_PRTP" rel-entity-name="ProductType">
            <key-map field-name="productTypeId"/>
        </relation>
    </entity>
</entitymodel>
```

### Delegator Interface

The Delegator is the primary interface for database operations in OFBiz:

```java
// Obtaining a delegator instance
Delegator delegator = DelegatorFactory.getDelegator("default");

// Creating a new entity
GenericValue product = delegator.makeValue("Product");
product.put("productId", "PROD_001");
product.put("productName", "Sample Product");
product.put("createdDate", UtilDateTime.nowTimestamp());

// Storing the entity
delegator.create(product);

// Finding entities
List<GenericValue> products = delegator.findByAnd("Product", 
    UtilMisc.toMap("productTypeId", "FINISHED_GOOD"), null, false);

// Using EntityQuery for complex queries
List<GenericValue> activeProducts = EntityQuery.use(delegator)
    .from("Product")
    .where("productTypeId", "FINISHED_GOOD")
    .filterByDate()
    .queryList();
```

### Connection Pooling

OFBiz implements sophisticated connection pooling to optimize database performance:

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
    time-between-eviction-runs-millis="600000"/>
```

### Transaction Management

OFBiz provides comprehensive transaction management capabilities:

```java
// Programmatic transaction management
TransactionUtil.begin();
try {
    // Database operations
    delegator.create(entity1);
    delegator.store(entity2);
    
    TransactionUtil.commit();
} catch (GenericEntityException e) {
    TransactionUtil.rollback();
    throw new ServiceException("Transaction failed", e);
}

// Service-level transaction management
public static Map<String, Object> createProduct(DispatchContext dctx, 
                                               Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    
    // Operations within service transaction boundary
    GenericValue product = delegator.makeValue("Product", context);
    delegator.create(product);
    
    return ServiceUtil.returnSuccess();
}
```

### Performance Optimization

#### Entity Caching

OFBiz provides multiple levels of caching for improved performance:

```xml
<entity entity-name="ProductType" 
        package-name="org.apache.ofbiz.product.product"
        cache="true">
    <!-- Entity definition -->
</entity>
```

#### View Entities

Complex queries can be optimized using view entities:

```xml
<view-entity entity-name="ProductAndType" package-name="org.apache.ofbiz.product.product">
    <member-entity entity-alias="PROD" entity-name="Product"/>
    <member-entity entity-alias="PRTP" entity-name="ProductType"/>
    
    <alias-all entity-alias="PROD"/>
    <alias entity-alias="PRTP" name="description" field="typeDescription"/>
    
    <view-link entity-alias="PROD" rel-entity-alias="PRTP">
        <key-map field-name="productTypeId"/>
    </view-link>
</view-entity>
```

## Geospatial Data Support

OFBiz includes comprehensive support for geospatial data operations, enabling location-based services and geographic information system (GIS) capabilities within enterprise applications.

### Geospatial Entity Types

The framework provides specialized field types for geospatial data:

```xml
<field-type-def type="geo-point">
    <validate method="isGeoPoint"/>
    <sql-type sql-type="GEOMETRY" sql-type-alias="POINT"/>
</field-type-def>

<field-type-def type="geo-polygon">
    <validate method="isGeoPolygon"/>
    <sql-type sql-type="GEOMETRY" sql-type-alias="POLYGON"/>
</field-type-def>

<field-type-def type="geo-line">
    <validate method="isGeoLine"/>
    <sql-type sql-type="GEOMETRY" sql-type-alias="LINESTRING"/>
</field-type-def>
```

### Geospatial Entity Definitions

Entities can include geospatial fields for storing location data:

```xml
<entity entity-name="GeoPoint" package-name="org.apache.ofbiz.common.geo">
    <field name="geoPointId" type="id-ne"/>
    <field name="geoPointTypeId" type="id"/>
    <field name="description" type="description"/>
    <field name="dataSourceId" type="id"/>
    <field name="latitude" type="floating-point"/>
    <field name="longitude" type="floating-point"/>
    <field name="elevation" type="floating-point"/>
    <field name="information" type="comment"/>
    
    <prim-key field="geoPointId"/>
    
    <relation type="one" fk-name="GEO_PT_TYPE" rel-entity-name="GeoPointType">
        <key-map field-name="geoPointTypeId"/>
    </relation>
</entity>

<entity entity-name="Facility" package-name="org.apache.ofbiz.product.facility">
    <field name="facilityId" type="id-ne"/>
    <field name="facilityName" type="name"/>
    <field name="geoPointId" type="id"/>
    <field name="geoLocation" type="geo-point"/>
    <field name="serviceArea" type="geo-polygon"/>
    
    <prim-key field="facilityId"/>
    
    <relation type="one" fk-name="FAC_GEO_PT" rel-entity-name="GeoPoint">
        <key-map field-name="geoPointId"/>
    </relation>
</entity>
```

### Geospatial Operations

OFBiz provides utilities for common geospatial operations:

```java
// Creating geospatial data
public static Map<String, Object> createGeoPoint(DispatchContext dctx, 
                                                Map<String, Object> context) {
    Delegator delegator = dctx.getDelegator();
    
    GenericValue geoPoint = delegator.makeValue("GeoPoint");
    geoPoint.put("geoPointId", context.get("geoPointId"));
    geoPoint.put("latitude", context.get("latitude"));
    geoPoint.put("longitude", context.get("longitude"));
    
    // Create WKT (Well-Known Text) representation
    String wktPoint = String.format("POINT(%s %s)", 
        context.get("longitude"), context.get("latitude"));
    geoPoint.put("geoLocation", wktPoint);
    
    delegator.create(geoPoint);
    
    return ServiceUtil.returnSuccess();
}

// Geospatial queries
public static List<GenericValue> findNearbyFacilities(Delegator delegator, 
                                                     double latitude, 
                                                     double longitude, 
                                                     double radiusKm) {
    
    // Using PostGIS functions for proximity search
    String sql = "SELECT facility_id, facility_name, " +
                 "ST_Distance(geo_location, ST_GeomFromText(?, 4326)) as distance " +
                 "FROM facility " +
                 "WHERE ST_DWithin(geo_location, ST_GeomFromText(?, 4326), ?) " +
                 "ORDER BY distance";
    
    String pointWKT = String.format("POINT(%f %f)", longitude, latitude);
    double radiusMeters = radiusKm * 1000;
    
    // Execute spatial query
    SQLProcessor sqlProcessor = new SQLProcessor(delegator, delegator.getGroupHelperName("default"));
    ResultSet rs = sqlProcessor.executeQuery(sql, Arrays.asList(pointWKT, pointWKT, radiusMeters));
    
    // Process results
    List<GenericValue> nearbyFacilities = new ArrayList<>();
    // ... result processing logic
    
    return nearbyFacilities;
}
```

### Spatial Indexing

For optimal geospatial query performance, spatial indexes should be created:

```sql
-- PostgreSQL/PostGIS spatial index
CREATE INDEX idx_facility_geo_location ON facility USING GIST (geo_location);

-- MySQL spatial index
CREATE SPATIAL INDEX idx_facility_geo_location ON facility (geo_location);
```

### Integration with Mapping Services

OFBiz can integrate with external mapping services for enhanced geospatial capabilities:

```java
// Geocoding service integration
public static Map<String, Object> geocodeAddress(DispatchContext dctx, 
                                                Map<String, Object> context) {
    String address = (String) context.get("address");
    
    // Integration with geocoding service
    GeocodingService geocoder = new GeocodingService();
    GeoPoint coordinates = geocoder.geocode(address);
    
    Map<String, Object> result = ServiceUtil.returnSuccess();
    result.put("latitude", coordinates.getLatitude());
    result.put("longitude", coordinates.getLongitude());
    
    return result;
}
```

### Best Practices for Geospatial Data

1. **Use appropriate spatial reference systems (SRS)**:
   ```java
   // WGS84 (EPSG:4326) for global applications
   String wktPoint = String.format("SRID=4326;POINT(%f %f)", longitude, latitude);
   ```

2. **Implement proper validation**:
   ```java
   public static boolean isValidCoordinate(double latitude, double longitude) {
       return latitude >= -90 && latitude <= 90 && 
              longitude >= -180 && longitude <= 180;
   }
   ```

3. **Optimize spatial queries**:
   ```java
   // Use bounding box queries for initial filtering
   EntityCondition boundingBoxCondition = EntityCondition.makeCondition(
       EntityCondition.makeCondition("latitude", EntityOperator.GREATER_THAN_EQUAL_TO, minLat),
       EntityCondition.makeCondition("latitude", EntityOperator.LESS_THAN_EQUAL_TO, maxLat),
       EntityCondition.makeCondition("longitude", EntityOperator.GREATER_THAN_EQUAL_TO, minLon),
       EntityCondition.makeCondition("longitude", EntityOperator.LESS_THAN_EQUAL_TO, maxLon)
   );
   ```

## Database Migration and Versioning

OFBiz provides tools for database schema evolution and data migration:

### Schema Updates

```xml
<!-- Entity model updates -->
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <extend-entity entity-name="Product">
        <field name="newField" type="description"/>
        <field name="geoLocation" type="geo-point"/>
    </extend-entity>
</entitymodel>
```

### Data Migration Scripts

```java
// Migration service
public static Map<String, Object> migrateProductData(DispatchContext dctx, 
                                                    Map<String, Object> context) {
    Delegator delegator = dctx.getDelegator();
    
    // Batch processing for large datasets
    EntityListIterator productIterator = null;
    try {
        productIterator = delegator.find("Product", null, null, null, null, null);
        
        GenericValue product;
        while ((product = productIterator.next()) != null) {
            // Migration logic
            product.