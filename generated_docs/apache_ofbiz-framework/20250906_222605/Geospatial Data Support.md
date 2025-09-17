# Geospatial Data Support

## Overview

Apache OFBiz provides comprehensive geospatial data support to enable location-based services, geographic information system (GIS) capabilities, and spatial data management within enterprise applications. This functionality is essential for businesses requiring geographic data processing, location-aware services, and spatial analysis capabilities.

The geospatial support in OFBiz leverages industry-standard spatial data formats and integrates seamlessly with the framework's entity engine, service layer, and web framework components.

## Architecture

### Core Components

The geospatial data support in OFBiz is built around several key architectural components:

- **Spatial Entity Engine Extensions**: Enhanced entity definitions supporting geometric data types
- **Geographic Service Layer**: Services for spatial operations and calculations
- **Coordinate System Management**: Support for various coordinate reference systems (CRS)
- **Spatial Data Import/Export**: Tools for handling standard geospatial formats

### Database Integration

OFBiz's geospatial support is designed to work with spatial database extensions:

```xml
<!-- Example entity definition with geospatial fields -->
<entity entity-name="GeoPoint" package-name="org.apache.ofbiz.common.geo">
    <field name="geoPointId" type="id-ne"/>
    <field name="geoPointTypeEnumId" type="id"/>
    <field name="description" type="description"/>
    <field name="dataSourceId" type="id"/>
    <field name="latitude" type="floating-point"/>
    <field name="longitude" type="floating-point"/>
    <field name="elevation" type="floating-point"/>
    <field name="information" type="comment"/>
    <prim-key field="geoPointId"/>
    <relation type="one" fk-name="GEO_POINT_TYPE" rel-entity-name="Enumeration">
        <key-map field-name="geoPointTypeEnumId" rel-field-name="enumId"/>
    </relation>
</entity>
```

## Data Models

### Geographic Entities

OFBiz provides several built-in entities for managing geospatial data:

#### GeoPoint Entity
Represents individual geographic points with coordinates:

```xml
<entity entity-name="GeoPoint">
    <field name="geoPointId" type="id-ne"/>
    <field name="latitude" type="floating-point"/>
    <field name="longitude" type="floating-point"/>
    <field name="elevation" type="floating-point"/>
    <!-- Additional fields for metadata -->
</entity>
```

#### Geo Entity
Manages geographic boundaries and regions:

```xml
<entity entity-name="Geo">
    <field name="geoId" type="id-ne"/>
    <field name="geoTypeId" type="id"/>
    <field name="geoName" type="name"/>
    <field name="geoCode" type="short-varchar"/>
    <field name="geoSecCode" type="short-varchar"/>
    <field name="abbreviation" type="short-varchar"/>
    <field name="wellKnownText" type="very-long"/>
    <prim-key field="geoId"/>
</entity>
```

### Spatial Relationships

Define relationships between geographic entities:

```xml
<entity entity-name="GeoAssoc">
    <field name="geoId" type="id-ne"/>
    <field name="geoIdTo" type="id-ne"/>
    <field name="geoAssocTypeId" type="id-ne"/>
    <field name="fromDate" type="date-time"/>
    <field name="thruDate" type="date-time"/>
    <prim-key field="geoId"/>
    <prim-key field="geoIdTo"/>
    <prim-key field="geoAssocTypeId"/>
    <prim-key field="fromDate"/>
</entity>
```

## Service Layer

### Geographic Services

OFBiz provides various services for geospatial operations:

#### Distance Calculation Service

```groovy
// Example service implementation for distance calculation
import org.apache.ofbiz.base.util.UtilMisc
import org.apache.ofbiz.entity.GenericValue

def calculateDistance() {
    GenericValue geoPoint1 = from("GeoPoint").where("geoPointId", parameters.geoPointId1).queryOne()
    GenericValue geoPoint2 = from("GeoPoint").where("geoPointId", parameters.geoPointId2).queryOne()
    
    if (!geoPoint1 || !geoPoint2) {
        return error("Geographic points not found")
    }
    
    double lat1 = geoPoint1.getDouble("latitude")
    double lon1 = geoPoint1.getDouble("longitude")
    double lat2 = geoPoint2.getDouble("latitude")
    double lon2 = geoPoint2.getDouble("longitude")
    
    double distance = calculateHaversineDistance(lat1, lon1, lat2, lon2)
    
    return success([distance: distance, unit: "kilometers"])
}

private double calculateHaversineDistance(double lat1, double lon1, double lat2, double lon2) {
    final int R = 6371 // Earth's radius in kilometers
    
    double latDistance = Math.toRadians(lat2 - lat1)
    double lonDistance = Math.toRadians(lon2 - lon1)
    
    double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2) +
               Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
               Math.sin(lonDistance / 2) * Math.sin(lonDistance / 2)
    
    double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    
    return R * c
}
```

#### Geocoding Service

```xml
<!-- Service definition for geocoding -->
<service name="geocodeAddress" engine="groovy" 
         location="component://common/groovyScripts/GeoServices.groovy" invoke="geocodeAddress">
    <description>Convert address to geographic coordinates</description>
    <attribute name="address" type="String" mode="IN" optional="false"/>
    <attribute name="city" type="String" mode="IN" optional="true"/>
    <attribute name="stateProvinceGeoId" type="String" mode="IN" optional="true"/>
    <attribute name="countryGeoId" type="String" mode="IN" optional="true"/>
    <attribute name="postalCode" type="String" mode="IN" optional="true"/>
    <attribute name="latitude" type="Double" mode="OUT" optional="true"/>
    <attribute name="longitude" type="Double" mode="OUT" optional="true"/>
    <attribute name="geoPointId" type="String" mode="OUT" optional="true"/>
</service>
```

### Spatial Query Services

```groovy
// Service for finding nearby points
def findNearbyPoints() {
    double centerLat = parameters.latitude
    double centerLon = parameters.longitude
    double radiusKm = parameters.radius ?: 10.0
    
    // Calculate bounding box for initial filtering
    double latDelta = radiusKm / 111.0 // Approximate km per degree latitude
    double lonDelta = radiusKm / (111.0 * Math.cos(Math.toRadians(centerLat)))
    
    List<GenericValue> nearbyPoints = from("GeoPoint")
        .where(EntityCondition.makeCondition([
            EntityCondition.makeCondition("latitude", EntityOperator.GREATER_THAN_EQUAL_TO, centerLat - latDelta),
            EntityCondition.makeCondition("latitude", EntityOperator.LESS_THAN_EQUAL_TO, centerLat + latDelta),
            EntityCondition.makeCondition("longitude", EntityOperator.GREATER_THAN_EQUAL_TO, centerLon - lonDelta),
            EntityCondition.makeCondition("longitude", EntityOperator.LESS_THAN_EQUAL_TO, centerLon + lonDelta)
        ], EntityOperator.AND))
        .queryList()
    
    // Filter by actual distance
    List<Map> results = []
    nearbyPoints.each { point ->
        double distance = calculateHaversineDistance(
            centerLat, centerLon,
            point.getDouble("latitude"), point.getDouble("longitude")
        )
        
        if (distance <= radiusKm) {
            results.add([
                geoPointId: point.geoPointId,
                latitude: point.latitude,
                longitude: point.longitude,
                distance: distance
            ])
        }
    }
    
    // Sort by distance
    results.sort { it.distance }
    
    return success([nearbyPoints: results])
}
```

## Data Import and Export

### Supported Formats

OFBiz supports various geospatial data formats:

#### Well-Known Text (WKT)
```java
// Example of storing WKT data
public class GeoDataImporter {
    
    public static ServiceUtil importWKTData(DispatchContext dctx, Map<String, Object> context) {
        String wktData = (String) context.get("wktData");
        String geoId = (String) context.get("geoId");
        
        try {
            GenericValue geo = dctx.getDelegator().findOne("Geo", 
                UtilMisc.toMap("geoId", geoId), false);
            
            if (geo != null) {
                geo.set("wellKnownText", wktData);
                geo.store();
            }
            
            return ServiceUtil.returnSuccess("WKT data imported successfully");
        } catch (GenericEntityException e) {
            return ServiceUtil.returnError("Error importing WKT data: " + e.getMessage());
        }
    }
}
```

#### GeoJSON Support
```groovy
// Service for importing GeoJSON data
def importGeoJSON() {
    String geoJsonData = parameters.geoJsonData
    
    try {
        def jsonSlurper = new groovy.json.JsonSlurper()
        def geoJson = jsonSlurper.parseText(geoJsonData)
        
        if (geoJson.type == "FeatureCollection") {
            geoJson.features.each { feature ->
                if (feature.geometry.type == "Point") {
                    def coordinates = feature.geometry.coordinates
                    def properties = feature.properties
                    
                    // Create GeoPoint entity
                    def geoPoint = makeValue("GeoPoint", [
                        geoPointId: delegator.getNextSeqId("GeoPoint"),
                        longitude: coordinates[0],
                        latitude: coordinates[1],
                        description: properties.name ?: properties.description
                    ])
                    
                    geoPoint.create()
                }
            }
        }
        
        return success("GeoJSON data imported successfully")
    } catch (Exception e) {
        return error("Error importing GeoJSON: " + e.getMessage())
    }
}
```

## Web Framework Integration

### RESTful Geospatial APIs

OFBiz provides REST endpoints for geospatial operations:

```xml
<!-- Controller configuration for geospatial APIs -->
<request-map uri="geopoint">
    <security https="false" auth="false"/>
    <event type="service" invoke="getGeoPoint"/>
    <response name="success" type="request" value="json"/>
    <response name="error" type="request" value="json"/>
</request-map>

<request-map uri="geopoint/nearby">
    <security https="false" auth="false"/>
    <event type="service" invoke="findNearbyPoints"/>
    <response name="success" type="request" value="json"/>
    <response name="error" type="request" value="json"/>
</request-map>
```

### JavaScript Integration

Client-side integration with mapping libraries:

```javascript
// Example JavaScript for integrating with OFBiz geospatial services
class OFBizGeoService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async findNearbyPoints(latitude, longitude, radius) {
        const response = await fetch(`${this.baseUrl}/geopoint/nearby`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude,
                radius: radius
            })
        });
        
        return await response.json();
    }
    
    async geocodeAddress(address) {
        const response = await fetch(`${this.baseUrl}/geocode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                address: address
            })
        });
        
        return await response.json();
    }
}

// Usage with mapping libraries like Leaflet or OpenLayers
const geoService = new OFBizGeoService('/ofbiz/control');

// Example with Leaflet
function loadNearbyPoints(map, center, radius) {
    geoService.findNearbyPoints(center.lat, center.lng, radius)
        .then(result => {
            if (result.nearbyPoints) {
                result.nearbyPoints.forEach(point => {
                    L.marker([point.latitude, point.longitude])
                        .addTo(map)
                        .bindPopup(`Distance: ${point.distance.toFixed(2)} km`);
                });
            }
        });
}
```

## Configuration

### Database Configuration

Configure spatial database support:

```xml
<!-- entityengine.xml configuration for spatial databases -->
<datasource name="localmysql"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="mysql"
            check-on-start="true"
            add-missing-on-start="true"
            use-pk-constraint-names="false"
            use-indices-unique="false"
            alias-view-columns="false"
            drop-fk-use-foreign-key-keyword="true"
            table-type="InnoDB"
            character-set="utf8"
            collate="utf8_general_ci">
    
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?autoReconnect=true&amp;useSSL=false&amp;allowPublicKeyRetrieval=true"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

### Service Configuration

```xml
<!-- services.xml for geospatial services -->
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/services.xsd">
    
    <description>Geospatial Services</description>
    <vendor>Apache OFBiz</vendor>
    <version>1.0</version>
    
    <service name="calculateDistance" engine="groovy"
             location="component://common/groovyScripts/GeoServices.groovy" invoke="calculateDistance">
        <description>Calculate distance between two geographic points</description>
        <attribute name="geoPointId1" type="String" mode="IN" optional="false"/>
        <attribute name="geoPointId2" type="String" mode="IN" optional="