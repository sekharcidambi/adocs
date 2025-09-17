# High-Level Architecture

Apache OFBiz (Open For Business) is a comprehensive enterprise resource planning (ERP) framework built on Java that provides a robust foundation for developing business applications. The framework follows a multi-layered architecture pattern that promotes modularity, scalability, and maintainability.

## Overview

The OFBiz framework architecture is designed around several key principles:

- **Component-based architecture**: Modular design allowing for independent development and deployment
- **Service-oriented architecture (SOA)**: Business logic encapsulated in reusable services
- **Model-View-Controller (MVC)**: Clear separation of concerns for web applications
- **Entity abstraction**: Database-agnostic data access layer
- **Plugin extensibility**: Support for custom extensions without modifying core framework

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│                    Web Framework                           │
├─────────────────────────────────────────────────────────────┤
│                    Service Engine                          │
├─────────────────────────────────────────────────────────────┤
│                    Entity Engine                           │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Framework Components

The OFBiz framework consists of several core components that work together to provide a complete enterprise application platform.

### Entity Engine

The Entity Engine serves as the Object-Relational Mapping (ORM) layer, providing database abstraction and data access functionality.

**Key Features:**
- Database-agnostic data access
- XML-based entity definitions
- Automatic SQL generation
- Connection pooling and transaction management
- Support for multiple databases (PostgreSQL, MySQL, Oracle, etc.)

**Entity Definition Example:**
```xml
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"></field>
    <field name="productTypeId" type="id"></field>
    <field name="productName" type="name"></field>
    <field name="description" type="very-long"></field>
    <field name="createdDate" type="date-time"></field>
    <prim-key field="productId"/>
    <relation type="one" fk-name="PROD_PRODTP" rel-entity-name="ProductType">
        <key-map field-name="productTypeId"/>
    </relation>
</entity>
```

**Data Access Pattern:**
```java
// Using Entity Engine for data operations
GenericValue product = EntityQuery.use(delegator)
    .from("Product")
    .where("productId", "DEMO_PRODUCT")
    .queryOne();

List<GenericValue> products = EntityQuery.use(delegator)
    .from("Product")
    .where("productTypeId", "FINISHED_GOOD")
    .queryList();
```

### Service Engine

The Service Engine implements the business logic layer, providing a framework for defining and executing business services.

**Service Characteristics:**
- Location and implementation transparency
- Multiple invocation methods (synchronous, asynchronous, scheduled)
- Built-in transaction management
- Parameter validation and type conversion
- Support for multiple implementation languages (Java, Groovy, XML)

**Service Definition Example:**
```xml
<service name="createProduct" default-entity-name="Product" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="productGenericPermission" main-action="CREATE"/>
    <auto-attributes include="pk" mode="INOUT" optional="false"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
    <override name="createdDate" mode="OUT"/>
    <override name="createdByUserLogin" mode="OUT"/>
</service>
```

**Service Implementation in Java:**
```java
public static Map<String, Object> calculateProductPrice(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    String productId = (String) context.get("productId");
    BigDecimal quantity = (BigDecimal) context.get("quantity");
    
    Map<String, Object> result = ServiceUtil.returnSuccess();
    
    try {
        // Business logic implementation
        GenericValue product = EntityQuery.use(delegator)
            .from("Product")
            .where("productId", productId)
            .queryOne();
            
        // Price calculation logic
        BigDecimal price = calculatePrice(product, quantity);
        result.put("price", price);
        
    } catch (GenericEntityException e) {
        return ServiceUtil.returnError("Error calculating price: " + e.getMessage());
    }
    
    return result;
}
```

### Security Framework

OFBiz implements a comprehensive security model with role-based access control.

**Security Components:**
- User authentication and authorization
- Permission-based access control
- Security groups and roles
- HTTPS support and SSL configuration
- CSRF protection and input validation

**Permission Definition:**
```xml
<SecurityPermission description="Product Admin Permission" permissionId="CATALOG_ADMIN"/>
<SecurityGroup description="Product Administrators" groupId="CATALOG_ADMIN"/>
<SecurityGroupPermission groupId="CATALOG_ADMIN" permissionId="CATALOG_ADMIN"/>
```

### Widget System

The Widget System provides a declarative approach to building user interfaces.

**Widget Types:**
- **Forms**: Data entry and display forms
- **Screens**: Page layout and content organization  
- **Menus**: Navigation structures
- **Trees**: Hierarchical data display

**Form Widget Example:**
```xml
<form name="EditProduct" type="single" target="updateProduct">
    <field name="productId"><hidden/></field>
    <field name="productName" title="Product Name">
        <text size="30" maxlength="100"/>
    </field>
    <field name="description" title="Description">
        <textarea cols="60" rows="5"/>
    </field>
    <field name="submitButton" title="Update">
        <submit button-type="button"/>
    </field>
</form>
```

## Web Framework Architecture

The OFBiz Web Framework implements a sophisticated MVC architecture that handles HTTP requests and generates responses through a series of configurable components.

### Request Processing Flow

```
HTTP Request → Control Servlet → Request Handler → Event/Service → View Handler → Response
```

**Detailed Flow:**
1. **Control Servlet**: Entry point for all HTTP requests
2. **Request Mapping**: URL patterns mapped to request handlers
3. **Event Processing**: Business logic execution
4. **View Rendering**: Template processing and response generation
5. **Response Delivery**: Final HTTP response to client

### Controller Configuration

The web framework uses XML configuration files to define request mappings and handlers.

**Controller.xml Example:**
```xml
<site-conf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <request-map uri="createProduct">
        <security https="true" auth="true"/>
        <event type="service" invoke="createProduct"/>
        <response name="success" type="view" value="ProductCreated"/>
        <response name="error" type="view" value="ProductForm"/>
    </request-map>
    
    <view-map name="ProductForm" type="screen" page="component://product/widget/ProductScreens.xml#ProductForm"/>
    <view-map name="ProductCreated" type="screen" page="component://product/widget/ProductScreens.xml#ProductList"/>
</site-conf>
```

### Screen Widget Architecture

Screens provide the view layer implementation using a widget-based approach.

**Screen Definition:**
```xml
<screen name="ProductForm">
    <section>
        <actions>
            <entity-one entity-name="Product" value-field="product"/>
            <set field="titleProperty" value="ProductCreateProduct"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonProductDecorator">
                <decorator-section name="body">
                    <include-form name="EditProduct" location="component://product/widget/ProductForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

### Template Integration

OFBiz supports multiple template engines for rendering views:

**FreeMarker Template Example:**
```html
<#-- ProductDetail.ftl -->
<div class="product-detail">
    <h2>${product.productName!}</h2>
    <p class="description">${product.description!}</p>
    
    <#if product.productTypeId??>
        <p>Type: ${productType.description!}</p>
    </#if>
    
    <div class="actions">
        <a href="<@ofbizUrl>EditProduct?productId=${product.productId}</@ofbizUrl>" class="btn btn-primary">
            Edit Product
        </a>
    </div>
</div>
```

### RESTful Web Services

OFBiz provides REST API capabilities for modern web and mobile applications.

**REST Service Configuration:**
```xml
<resource name="products" description="Product Management API">
    <operation verb="GET" path="/products" service="getProductList"/>
    <operation verb="GET" path="/products/{productId}" service="getProduct"/>
    <operation verb="POST" path="/products" service="createProduct"/>
    <operation verb="PUT" path="/products/{productId}" service="updateProduct"/>
    <operation verb="DELETE" path="/products/{productId}" service="deleteProduct"/>
</resource>
```

### Component Architecture

OFBiz applications are organized into components that encapsulate related functionality.

**Component Structure:**
```
component/
├── config/
│   └── ComponentName.properties
├── data/
│   └── ComponentNameData.xml
├── entitydef/
│   └── entitymodel.xml
├── script/
│   └── groovy/
├── servicedef/
│   └── services.xml
├── webapp/
│   └── componentname/
├── widget/
│   ├── ComponentScreens.xml
│   ├── ComponentForms.xml
│   └── ComponentMenus.xml
└── ofbiz-component.xml
```

**Component Descriptor (ofbiz-component.xml):**
```xml
<ofbiz-component name="product" enabled="true">
    <resource-loader name="main" type="component"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/ProductTypeData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="catalog" title="Product Catalog" server="default-server"
            location="webapp/catalog" base-permission="OFBTOOLS,CATALOG"
            mount-point="/catalog"/>
</ofbiz-component>
```

This architecture provides a solid foundation for building scalable enterprise applications while maintaining flexibility and extensibility through its component-based design and comprehensive framework services.