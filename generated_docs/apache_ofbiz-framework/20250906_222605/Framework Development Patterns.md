# Framework Development Patterns

This section outlines the core development patterns and architectural principles used throughout the Apache OFBiz framework. Understanding these patterns is essential for effective development, customization, and extension of OFBiz applications.

## Overview

Apache OFBiz follows established enterprise application patterns combined with framework-specific conventions. These patterns ensure consistency, maintainability, and scalability across the entire framework ecosystem.

## Core Architectural Patterns

### Model-View-Controller (MVC) Pattern

OFBiz implements a sophisticated MVC architecture that separates concerns across different layers:

#### Model Layer
- **Entity Engine**: Handles data persistence and database operations
- **Service Engine**: Manages business logic through service-oriented architecture
- **Data Model**: XML-based entity definitions

```xml
<!-- Example entity definition -->
<entity entity-name="Product" package-name="org.apache.ofbiz.product.product">
    <field name="productId" type="id-ne"></field>
    <field name="productTypeId" type="id"></field>
    <field name="productName" type="name"></field>
    <field name="description" type="very-long"></field>
    <prim-key field="productId"/>
</entity>
```

#### View Layer
- **Screen Widgets**: XML-based screen definitions
- **Form Widgets**: Reusable form components
- **FreeMarker Templates**: Dynamic content rendering

```xml
<!-- Example screen widget -->
<screen name="ProductDetail">
    <section>
        <actions>
            <entity-one entity-name="Product" value-field="product"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonProductDecorator">
                <decorator-section name="body">
                    <include-form name="ProductForm" location="component://product/widget/ProductForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

#### Controller Layer
- **Request/Response Handlers**: Process HTTP requests
- **Event Handlers**: Handle user interactions
- **Control Servlet**: Central request dispatcher

```xml
<!-- Example controller configuration -->
<request-map uri="createProduct">
    <security https="true" auth="true"/>
    <event type="service" invoke="createProduct"/>
    <response name="success" type="view" value="ProductDetail"/>
    <response name="error" type="view" value="ProductForm"/>
</request-map>
```

### Service-Oriented Architecture (SOA)

#### Service Definition Pattern

Services in OFBiz are defined declaratively and follow consistent patterns:

```xml
<service name="createProduct" engine="entity-auto" invoke="create" auth="true">
    <description>Create a Product</description>
    <permission-service service-name="productGenericPermission" main-action="CREATE"/>
    <auto-attributes entity-name="Product" include="pk" mode="INOUT" optional="false"/>
    <auto-attributes entity-name="Product" include="nonpk" mode="IN" optional="true"/>
</service>
```

#### Service Implementation Patterns

**Java Service Implementation:**
```java
public static Map<String, Object> calculateProductPrice(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    String productId = (String) context.get("productId");
    BigDecimal quantity = (BigDecimal) context.get("quantity");
    
    try {
        GenericValue product = EntityQuery.use(delegator)
            .from("Product")
            .where("productId", productId)
            .queryOne();
            
        // Business logic implementation
        BigDecimal price = calculatePrice(product, quantity);
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        result.put("price", price);
        return result;
        
    } catch (GenericEntityException e) {
        return ServiceUtil.returnError("Error calculating price: " + e.getMessage());
    }
}
```

**Groovy Service Implementation:**
```groovy
// File: applications/product/groovyScripts/product/ProductServices.groovy
def updateProductPrice() {
    product = from("Product").where("productId", parameters.productId).queryOne()
    if (product) {
        product.price = parameters.price
        product.lastModifiedDate = UtilDateTime.nowTimestamp()
        product.store()
        return success("Product price updated successfully")
    }
    return error("Product not found")
}
```

### Entity Engine Patterns

#### Data Access Object (DAO) Pattern

OFBiz implements a sophisticated DAO pattern through the Entity Engine:

```java
// Query patterns
public List<GenericValue> findActiveProducts(Delegator delegator) throws GenericEntityException {
    return EntityQuery.use(delegator)
        .from("Product")
        .where("isActive", "Y")
        .orderBy("productName")
        .queryList();
}

// Complex query with joins
public List<GenericValue> findProductsWithCategory(Delegator delegator, String categoryId) 
        throws GenericEntityException {
    return EntityQuery.use(delegator)
        .from("ProductCategoryMember")
        .where("productCategoryId", categoryId)
        .filterByDate()
        .queryList();
}
```

#### Entity Relationship Patterns

```xml
<!-- One-to-Many Relationship -->
<relation type="many" rel-entity-name="ProductCategoryMember">
    <key-map field-name="productId"/>
</relation>

<!-- Many-to-One Relationship -->
<relation type="one" rel-entity-name="ProductType">
    <key-map field-name="productTypeId"/>
</relation>

<!-- View Entity Pattern -->
<view-entity entity-name="ProductAndCategory" package-name="org.apache.ofbiz.product">
    <member-entity entity-alias="PROD" entity-name="Product"/>
    <member-entity entity-alias="PCM" entity-name="ProductCategoryMember"/>
    <alias-all entity-alias="PROD"/>
    <alias entity-alias="PCM" name="productCategoryId"/>
    <view-link entity-alias="PROD" rel-entity-alias="PCM">
        <key-map field-name="productId"/>
    </view-link>
</view-entity>
```

## Widget Framework Patterns

### Screen Widget Composition

#### Decorator Pattern
```xml
<screen name="CommonProductDecorator">
    <section>
        <actions>
            <set field="headerItem" value="products"/>
        </actions>
        <widgets>
            <decorator-screen name="main-decorator" location="${parameters.mainDecoratorLocation}">
                <decorator-section name="pre-body">
                    <include-menu name="ProductTabBar" location="component://product/widget/ProductMenus.xml"/>
                </decorator-section>
                <decorator-section name="body">
                    <decorator-section-include name="body"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

#### Template Method Pattern
```xml
<screen name="ProductList">
    <section>
        <actions>
            <script location="component://product/groovyScripts/product/ProductList.groovy"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonProductDecorator">
                <decorator-section name="body">
                    <screenlet title="${uiLabelMap.ProductProducts}">
                        <include-grid name="ProductGrid" location="component://product/widget/ProductForms.xml"/>
                    </screenlet>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

### Form Widget Patterns

#### Dynamic Form Generation
```xml
<form name="ProductForm" type="single" target="updateProduct">
    <auto-fields-service service-name="updateProduct"/>
    <field name="productId"><display/></field>
    <field name="productName"><text size="30"/></field>
    <field name="productTypeId">
        <drop-down allow-empty="false">
            <entity-options entity-name="ProductType" description="${description}">
                <entity-order-by field-name="description"/>
            </entity-options>
        </drop-down>
    </field>
    <field name="submitButton" title="${uiLabelMap.CommonUpdate}"><submit/></field>
</form>
```

## Event Handling Patterns

### Request Processing Pipeline

#### Event Chain Pattern
```java
public class ProductEvents {
    public static String createProductEvent(HttpServletRequest request, HttpServletResponse response) {
        Delegator delegator = (Delegator) request.getAttribute("delegator");
        LocalDispatcher dispatcher = (LocalDispatcher) request.getAttribute("dispatcher");
        
        try {
            Map<String, Object> serviceContext = UtilHttp.getParameterMap(request);
            Map<String, Object> result = dispatcher.runSync("createProduct", serviceContext);
            
            if (ServiceUtil.isError(result)) {
                request.setAttribute("_ERROR_MESSAGE_", ServiceUtil.getErrorMessage(result));
                return "error";
            }
            
            request.setAttribute("productId", result.get("productId"));
            return "success";
            
        } catch (GenericServiceException e) {
            request.setAttribute("_ERROR_MESSAGE_", e.getMessage());
            return "error";
        }
    }
}
```

### AJAX Event Patterns
```javascript
// Client-side AJAX pattern
function updateProductPrice(productId, newPrice) {
    jQuery.ajax({
        url: 'updateProductPrice',
        type: 'POST',
        data: {
            productId: productId,
            price: newPrice
        },
        success: function(data) {
            if (data._ERROR_MESSAGE_) {
                showErrorMessage(data._ERROR_MESSAGE_);
            } else {
                showSuccessMessage('Price updated successfully');
                refreshProductGrid();
            }
        },
        error: function() {
            showErrorMessage('Network error occurred');
        }
    });
}
```

## Component Architecture Patterns

### Plugin Architecture

#### Component Structure
```
component/
├── config/
│   └── ComponentConfig.xml
├── data/
│   ├── ProductTypeData.xml
│   └── ProductSecurityData.xml
├── entitydef/
│   └── entitymodel.xml
├── servicedef/
│   └── services.xml
├── src/main/java/
│   └── org/apache/ofbiz/product/
├── webapp/
│   ├── WEB-INF/
│   │   └── web.xml
│   └── catalog/
└── widget/
    ├── ProductScreens.xml
    ├── ProductForms.xml
    └── ProductMenus.xml
```

#### Component Configuration
```xml
<ofbiz-component name="product"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/ProductTypeData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="catalog"
            title="Product Catalog"
            server="default-server"
            location="webapp/catalog"
            base-permission="OFBTOOLS,CATALOG"
            mount-point="/catalog"/>
</ofbiz-component>
```

### Dependency Injection Pattern

#### Service Context Injection
```java
@Component
public class ProductService {
    
    public static Map<String, Object> processProduct(DispatchContext dctx, Map<String, Object> context) {
        // Framework automatically injects dependencies
        Delegator delegator = dctx.getDelegator();
        LocalDispatcher dispatcher = dctx.getDispatcher();
        GenericValue userLogin = (GenericValue) context.get("userLogin");
        
        // Service implementation
        return ServiceUtil.returnSuccess();
    }
}
```

## Security Patterns

### Permission-Based Access Control

#### Service-Level Security
```xml
<service name="updateProduct" engine="java" auth="true">
    <permission-service service-name="productGenericPermission" main-action="UPDATE"/>
    <!-- Service definition -->
</service>
```

#### Screen-Level Security
```xml
<screen name="ProductAdmin">
    <section>
        <condition>
            <if-has-permission permission="CATALOG" action="_ADMIN"/>
        </condition>
        <widgets>
            <!-- Admin interface -->
        </widgets>
    </section>
</screen>
```

### Data Security Patterns

#### Entity Filtering
```java
// Automatic security filtering
public List<GenericValue> findUserProducts(Delegator delegator, String partyId) 
        throws GenericEntityException {
    return EntityQuery.use(delegator)
        .from("Product")
        .where("createdByUserLogin", partyId)
        .filterByDate()
        .queryList();
}
```

## Testing Patterns

### Unit Testing Pattern
```java
public class ProductServiceTest extends OFBizTestCase {
    
    @Test
    public void testCreateProduct() throws Exception {
        Map<String, Object> serviceContext = new HashMap<>();
        serviceContext.put("productId", "TEST_PRODUCT");
        serviceContext.put("productName", "Test Product");
        serviceContext.put("productTypeId", "FINISHED_GOOD");
        serviceContext.put("userLogin", getUserLogin());
        
        Map<String, Object> result = dispatcher.runSync("createProduct", serviceContext);
        
        assertTrue("Service should succeed", ServiceUtil.isSuccess(result));
        assertNotNull("Product ID should be returned", result.get("productId"));
    }
}
```

### Integration Testing Pattern
```java
public class ProductWebTest extends OFBizTestCase {
    
    @Test
    public void testProductCRUD() throws Exception {
        // Test complete product lifecycle through web interface
        WebTestSuite suite = new WebTestSuite("Product CRUD Test");
        suite.addTest(new CreateProductTest());
        suite.addTest(new UpdateProductTest());
        suite.addTest(new DeleteProductTest());
        suite.run();
    }
}
```

## Performance Patterns

### Caching Strategies

#### Entity Caching
```java
// Cached entity lookup
GenericValue product = EntityQuery.use(delegator)
    .from("Product")
    .where("productId", productId)
    .cache(true)  // Enable caching
    .queryOne();
```

#### Service Result Caching
```xml
<service name="getProductInfo" engine="java" auth="false" use-transaction="false">
    <attribute name="productId" type="String" mode="IN" optional="false"/>
    <attribute name="productInfo" type="Map" mode="OUT" optional="false"/>
    <!-- Cache results for 5 minutes -->
    <cache-result timeout="300"/>
</service>
```

### Lazy Loading Pattern
```java
public class ProductWrapper {
    private String productId;
    private GenericValue product;
    private List<GenericValue> categories;
    
    public List<GenericValue> getCategories() {
        if (categories == null) {
            // Lazy load categories when first accessed
            categories = loadProductCategories();
        }
        return categories;
    }
}
```

## Best Practices

### Code Organization
1. **Separation of Concerns**: Keep business logic in services, presentation in screens/forms
2. **Consistent Naming**: Follow OFBiz naming conventions for entities, services, and screens
3. **Reusability**: Create reusable widgets and services
4. **Documentation**: Document complex business