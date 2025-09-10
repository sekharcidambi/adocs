## Multi-tier Architecture Overview

## Architecture Overview

Apache OFBiz implements a sophisticated multi-tier architecture that separates concerns across distinct layers, enabling scalability, maintainability, and flexibility for enterprise resource planning operations. This architecture follows the traditional three-tier pattern while incorporating additional specialized layers to handle the complexity of ERP systems.

### Core Architecture Layers

#### Presentation Layer (Web Tier)
The presentation layer in OFBiz handles all user interactions and client-side operations through multiple frontend technologies:

```
framework/webapp/
├── src/main/java/org/apache/ofbiz/webapp/
├── control/
│   ├── RequestHandler.java
│   └── ControlServlet.java
└── view/
    ├── ViewHandler.java
    └── ViewHandlerException.java
```

**Key Components:**
- **Control Servlet**: Central request dispatcher that routes incoming HTTP requests
- **Screen Widgets**: Declarative UI components defined in XML for consistent rendering
- **Form Widgets**: Reusable form components that integrate with the entity engine
- **Menu Widgets**: Navigation structures that adapt based on user permissions

**Frontend Integration:**
```javascript
// Example React component integration
import { OFBizService } from '@ofbiz/webapp-common';

const ProductCatalog = () => {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    OFBizService.call('getProductCatalog', {
      catalogId: 'DEFAULT_CATALOG'
    }).then(setProducts);
  }, []);
};
```

#### Business Logic Layer (Service Tier)
The service layer encapsulates all business logic and rules through OFBiz's Service Engine:

```
framework/service/
├── src/main/java/org/apache/ofbiz/service/
│   ├── ServiceDispatcher.java
│   ├── LocalDispatcher.java
│   └── engine/
└── servicedef/
    └── services.xml
```

**Service Definition Example:**
```xml
<service name="createProduct" engine="java" 
         location="org.apache.ofbiz.product.ProductServices" 
         invoke="createProduct">
    <description>Create a new product</description>
    <attribute name="productId" type="String" mode="OUT" optional="true"/>
    <attribute name="productName" type="String" mode="IN" optional="false"/>
    <attribute name="productTypeId" type="String" mode="IN" optional="false"/>
</service>
```

**Service Engine Types:**
- **Java Services**: Direct Java method invocation for complex business logic
- **Simple Services**: XML-defined services for basic CRUD operations
- **Groovy Services**: Dynamic scripting for flexible business rules
- **Workflow Services**: Process orchestration using XPDL definitions

#### Data Access Layer (Entity Tier)
OFBiz's Entity Engine provides a sophisticated ORM layer that abstracts database operations:

```
framework/entity/
├── src/main/java/org/apache/ofbiz/entity/
│   ├── GenericDelegator.java
│   ├── GenericEntity.java
│   └── condition/
└── entitydef/
    └── entitymodel.xml
```

**Entity Definition:**
```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"/>
    <field name="productTypeId" type="id"/>
    <field name="productName" type="name"/>
    <field name="description" type="very-long"/>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

**Database Operations:**
```java
// Entity CRUD operations
GenericValue product = delegator.makeValue("Product");
product.set("productId", "DEMO_PRODUCT");
product.set("productName", "Demo Product");
product.set("productTypeId", "FINISHED_GOOD");
product.create();

// Complex queries with EntityCondition
List<GenericValue> products = delegator.findList("Product",
    EntityCondition.makeCondition("productTypeId", "FINISHED_GOOD"),
    null, null, null, false);
```

### Integration Architecture

#### Service-Entity Integration
The architecture ensures seamless integration between service and entity layers through the Service Control Architecture (SECA):

```xml
<seca>
    <service name="createProduct">
        <condition field-name="autoCreateInventoryItem" operator="equals" value="Y"/>
        <action service="createInventoryItem" mode="sync"/>
    </seca>
</service>
```

#### Event-Driven Architecture
OFBiz implements event-driven patterns through:

**Event Handlers:**
```java
public static String updateProductPrice(HttpServletRequest request, 
                                      HttpServletResponse response) {
    LocalDispatcher dispatcher = (LocalDispatcher) request.getAttribute("dispatcher");
    Map<String, Object> serviceContext = UtilHttp.getParameterMap(request);
    
    try {
        dispatcher.runSync("updateProductPrice", serviceContext);
        return "success";
    } catch (GenericServiceException e) {
        return "error";
    }
}
```

### Technology Stack Integration

#### Database Layer Configuration
Multi-database support through delegator configuration:

```xml
<delegator name="default" entity-model-reader="main" 
           entity-group-reader="main" entity-eca-reader="main">
    <group-map group-name="org.apache.ofbiz" datasource-name="localderby"/>
    <group-map group-name="org.apache.ofbiz.olap" datasource-name="localderbyolap"/>
</delegator>
```

#### Container Architecture
OFBiz uses a container-based architecture for service lifecycle management:

```xml
<container name="service-container" loaders="main,rmi,http,https"
           class="org.apache.ofbiz.service.ServiceContainer">
    <property name="dispatcher-factory" value="org.apache.ofbiz.service.GenericDispatcherFactory"/>
    <property name="send-validation-request" value="true"/>
</container>
```

### Performance and Scalability Considerations

#### Connection Pooling
```xml
<datasource name="localpostgres"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            schema-name="public"
            field-type-name="postgres"
            check-on-start="true"
            add-missing-on-start="true"
            use-pk-constraint-names="false"
            constraint-name-clip-length="30">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
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
```

#### Caching Strategy
OFBiz implements multi-level caching across all tiers:
- **Entity Cache**: Automatic entity-level caching with configurable expiration
- **Service Cache**: Result caching for expensive service operations
- **Screen Cache**: Rendered screen fragment caching for improved response times

This multi-tier architecture enables OFBiz to handle complex ERP requirements while maintaining separation of concerns, supporting horizontal scaling, and providing flexibility for customization across different business domains.

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:48:19*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*