# Custom Application Development

## Overview

Apache OFBiz provides a comprehensive framework for developing custom business applications. This section covers the essential concepts, patterns, and practices for building custom applications within the OFBiz ecosystem, leveraging its robust data model, service engine, and web framework capabilities.

## Architecture Foundation

### Framework Components

OFBiz custom applications are built on several core components:

- **Entity Engine**: Object-relational mapping and database abstraction
- **Service Engine**: Business logic execution framework
- **Widget System**: UI rendering and form management
- **Security Framework**: Authentication and authorization
- **Event System**: Request handling and workflow management

### Application Structure

Custom applications in OFBiz follow a standardized directory structure:

```
applications/
└── your-custom-app/
    ├── build.gradle
    ├── ofbiz-component.xml
    ├── config/
    ├── data/
    ├── entitydef/
    ├── script/
    ├── servicedef/
    ├── src/
    ├── webapp/
    └── widget/
```

## Component Configuration

### Component Definition

Every custom application requires an `ofbiz-component.xml` file to define the component:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="your-custom-app"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="build/lib/*"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/CustomAppSecurityPermissionSeedData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="your-custom-app"
            title="Your Custom Application"
            server="default-server"
            location="webapp/your-custom-app"
            base-permission="CUSTOMAPP"
            mount-point="/customapp"/>
</ofbiz-component>
```

### Build Configuration

Create a `build.gradle` file for dependency management:

```gradle
dependencies {
    pluginLibsCompile project(':framework:base')
    pluginLibsCompile project(':framework:entity')
    pluginLibsCompile project(':framework:service')
    pluginLibsCompile project(':framework:webapp')
    pluginLibsCompile project(':framework:widget')
}
```

## Entity Development

### Entity Definition

Define custom entities in `entitydef/entitymodel.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <entity entity-name="CustomProduct" package-name="org.apache.ofbiz.customapp.product">
        <field name="customProductId" type="id-ne"/>
        <field name="productName" type="name"/>
        <field name="description" type="description"/>
        <field name="price" type="currency-amount"/>
        <field name="categoryId" type="id"/>
        <field name="createdDate" type="date-time"/>
        <field name="lastModifiedDate" type="date-time"/>
        
        <prim-key field="customProductId"/>
        
        <relation type="one" fk-name="CUST_PROD_CAT" rel-entity-name="ProductCategory">
            <key-map field-name="categoryId"/>
        </relation>
    </entity>
    
    <entity entity-name="CustomOrder" package-name="org.apache.ofbiz.customapp.order">
        <field name="customOrderId" type="id-ne"/>
        <field name="customerId" type="id"/>
        <field name="orderDate" type="date-time"/>
        <field name="totalAmount" type="currency-amount"/>
        <field name="statusId" type="id"/>
        
        <prim-key field="customOrderId"/>
        
        <relation type="one" fk-name="CUST_ORD_PARTY" rel-entity-name="Party">
            <key-map field-name="customerId" rel-field-name="partyId"/>
        </relation>
    </entity>
</entitymodel>
```

### Entity Operations

Implement entity operations using the Entity Engine:

```java
// Java service implementation
public static Map<String, Object> createCustomProduct(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    String customProductId = delegator.getNextSeqId("CustomProduct");
    String productName = (String) context.get("productName");
    String description = (String) context.get("description");
    BigDecimal price = (BigDecimal) context.get("price");
    
    try {
        GenericValue customProduct = delegator.makeValue("CustomProduct");
        customProduct.set("customProductId", customProductId);
        customProduct.set("productName", productName);
        customProduct.set("description", description);
        customProduct.set("price", price);
        customProduct.set("createdDate", UtilDateTime.nowTimestamp());
        
        customProduct = delegator.createSetNextSeqId(customProduct);
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        result.put("customProductId", customProductId);
        return result;
        
    } catch (GenericEntityException e) {
        Debug.logError(e, "Error creating custom product", module);
        return ServiceUtil.returnError("Error creating custom product: " + e.getMessage());
    }
}
```

## Service Development

### Service Definition

Define services in `servicedef/services.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/services.xsd">
    
    <service name="createCustomProduct" engine="java"
            location="org.apache.ofbiz.customapp.product.ProductServices" invoke="createCustomProduct">
        <description>Create a Custom Product</description>
        <required-permissions join-type="OR">
            <check-permission permission="CUSTOMAPP_CREATE"/>
        </required-permissions>
        <attribute name="productName" type="String" mode="IN" optional="false"/>
        <attribute name="description" type="String" mode="IN" optional="true"/>
        <attribute name="price" type="BigDecimal" mode="IN" optional="false"/>
        <attribute name="categoryId" type="String" mode="IN" optional="true"/>
        <attribute name="customProductId" type="String" mode="OUT" optional="false"/>
    </service>
    
    <service name="updateCustomProduct" engine="java"
            location="org.apache.ofbiz.customapp.product.ProductServices" invoke="updateCustomProduct">
        <description>Update a Custom Product</description>
        <required-permissions join-type="OR">
            <check-permission permission="CUSTOMAPP_UPDATE"/>
        </required-permissions>
        <attribute name="customProductId" type="String" mode="IN" optional="false"/>
        <attribute name="productName" type="String" mode="IN" optional="true"/>
        <attribute name="description" type="String" mode="IN" optional="true"/>
        <attribute name="price" type="BigDecimal" mode="IN" optional="true"/>
    </service>
</services>
```

### Groovy Services

Implement services using Groovy scripts in the `script/` directory:

```groovy
// script/org/apache/ofbiz/customapp/product/ProductServices.groovy

import org.apache.ofbiz.base.util.UtilDateTime
import org.apache.ofbiz.entity.GenericValue
import org.apache.ofbiz.service.ServiceUtil

def getCustomProductsByCategory() {
    String categoryId = parameters.categoryId
    
    if (!categoryId) {
        return ServiceUtil.returnError("Category ID is required")
    }
    
    try {
        List<GenericValue> products = from("CustomProduct")
            .where("categoryId", categoryId)
            .orderBy("productName")
            .queryList()
        
        Map result = ServiceUtil.returnSuccess()
        result.products = products
        return result
        
    } catch (Exception e) {
        logError("Error retrieving products: ${e.getMessage()}")
        return ServiceUtil.returnError("Error retrieving products: ${e.getMessage()}")
    }
}

def calculateOrderTotal() {
    String customOrderId = parameters.customOrderId
    
    try {
        List<GenericValue> orderItems = from("CustomOrderItem")
            .where("customOrderId", customOrderId)
            .queryList()
        
        BigDecimal total = BigDecimal.ZERO
        orderItems.each { item ->
            BigDecimal itemTotal = item.getBigDecimal("quantity") * item.getBigDecimal("unitPrice")
            total = total.add(itemTotal)
        }
        
        // Update order total
        GenericValue order = from("CustomOrder").where("customOrderId", customOrderId).queryOne()
        order.set("totalAmount", total)
        order.set("lastModifiedDate", UtilDateTime.nowTimestamp())
        order.store()
        
        Map result = ServiceUtil.returnSuccess()
        result.totalAmount = total
        return result
        
    } catch (Exception e) {
        logError("Error calculating order total: ${e.getMessage()}")
        return ServiceUtil.returnError("Error calculating order total: ${e.getMessage()}")
    }
}
```

## Web Application Development

### Controller Configuration

Configure request mappings in `webapp/your-custom-app/WEB-INF/controller.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<site-conf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/site-conf.xsd">
    
    <include location="component://common/webcommon/WEB-INF/common-controller.xml"/>
    
    <description>Custom Application Controller Configuration</description>
    
    <handler name="java" type="request" class="org.apache.ofbiz.webapp.event.JavaEventHandler"/>
    <handler name="service" type="request" class="org.apache.ofbiz.webapp.event.ServiceEventHandler"/>
    
    <request-map uri="main">
        <security https="false" auth="true"/>
        <response name="success" type="view" value="main"/>
    </request-map>
    
    <request-map uri="createProduct">
        <security https="true" auth="true"/>
        <event type="service" invoke="createCustomProduct"/>
        <response name="success" type="view" value="ProductCreated"/>
        <response name="error" type="view" value="ProductForm"/>
    </request-map>
    
    <request-map uri="editProduct">
        <security https="false" auth="true"/>
        <response name="success" type="view" value="EditProduct"/>
    </request-map>
    
    <view-map name="main" type="screen" page="component://your-custom-app/widget/CustomAppScreens.xml#main"/>
    <view-map name="ProductForm" type="screen" page="component://your-custom-app/widget/ProductScreens.xml#ProductForm"/>
    <view-map name="EditProduct" type="screen" page="component://your-custom-app/widget/ProductScreens.xml#EditProduct"/>
</site-conf>
```

### Screen Widgets

Create screen definitions in `widget/CustomAppScreens.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<screens xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/widget-screen.xsd">
    
    <screen name="main-decorator">
        <section>
            <actions>
                <property-map resource="CustomAppUiLabels" map-name="uiLabelMap" global="true"/>
                <set field="layoutSettings.companyName" from-field="uiLabelMap.CustomAppCompanyName"/>
                <set field="layoutSettings.companySubtitle" from-field="uiLabelMap.CustomAppCompanySubtitle"/>
                <set field="applicationMenuName" value="CustomAppAppBar" global="true"/>
                <set field="applicationMenuLocation" value="component://your-custom-app/widget/CustomAppMenus.xml" global="true"/>
                <set field="applicationTitle" value="${uiLabelMap.CustomAppApplication}" global="true"/>
            </actions>
            <widgets>
                <include-screen name="ApplicationDecorator" location="component://commonext/widget/CommonScreens.xml"/>
            </widgets>
        </section>
    </screen>
    
    <screen name="main">
        <section>
            <actions>
                <set field="headerItem" value="main"/>
                <set field="titleProperty" value="CustomAppMainPage"/>
            </actions>
            <widgets>
                <decorator-screen name="main-decorator" location="${parameters.mainDecoratorLocation}">
                    <decorator-section name="body">
                        <screenlet title="${uiLabelMap.CustomAppWelcome}">
                            <container>
                                <label style="h2" text="${uiLabelMap.CustomAppMainPageDescription}"/>
                            </container>
                            <container>
                                <link target="ProductList" text="${uiLabelMap.CustomAppViewProducts}" style="buttontext"/>
                                <link target="ProductForm" text="${uiLabelMap.CustomAppCreateProduct}" style="buttontext"/>
                            </container>
                        </screenlet>
                    </decorator-section>
                </decorator-screen>
            </widgets>
        </section>
    </screen>
</screens>
```

### Form Widgets

Define forms in `widget/CustomAppForms.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<forms xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/widget-form.xsd">
    
    <form name="ProductForm" type="single" target="createProduct" title="" default-map-name="product">
        <alt-target use-when="product!=null" target="updateProduct"/>
        
        <auto-fields-service service-name="createCustomProduct"/>
        
        <field name="customProductId" use-when="product!=null" tooltip="${uiLabelMap.CommonNotModifRecreat}">
            <display/>
        </field>
        <field name="customProductId" use-when="product==null">
            <ignored/>
        </field>
        
        <field name="productName">
            <text size="30" maxlength="100"/>
        </field>
        
        <field name="description">
            <textarea cols="60" rows="4"/>
        </field>
        
        <field name="price">
            <text size="