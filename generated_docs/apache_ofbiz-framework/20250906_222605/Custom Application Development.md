## Custom Application Development

## Overview

Apache OFBiz provides a comprehensive framework for developing custom applications that leverage its enterprise-grade architecture. Custom application development in OFBiz involves creating new components that integrate seamlessly with the framework's service-oriented architecture, entity engine, and web presentation layer. This approach allows developers to build specialized business applications while maintaining consistency with OFBiz's design patterns and benefiting from its robust infrastructure.

## Component Structure and Architecture

### Creating a Custom Component

Custom applications in OFBiz are organized as components within the framework's modular architecture. Each component follows a standardized directory structure:

```
applications/myapp/
├── build.xml
├── component-load.xml
├── config/
├── data/
├── entitydef/
├── script/
├── servicedef/
├── src/
├── testdef/
├── webapp/
└── widget/
```

The `component-load.xml` file defines the component's metadata and dependencies:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component-loader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/component-loader.xsd">
    <load-component component-location="applications/myapp"/>
</component-loader>
```

### Entity Model Definition

Custom applications typically require domain-specific data models. Entity definitions are created in the `entitydef/` directory using OFBiz's entity definition XML format:

```xml
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entitymodel.xsd">
    
    <entity entity-name="CustomProduct" package-name="org.apache.ofbiz.myapp">
        <field name="productId" type="id-ne"/>
        <field name="productName" type="name"/>
        <field name="description" type="very-long"/>
        <field name="createdDate" type="date-time"/>
        <prim-key field="productId"/>
    </entity>
</entitymodel>
```

## Service Layer Implementation

### Service Definition

Services form the backbone of business logic in OFBiz custom applications. Service definitions are specified in `servicedef/services.xml`:

```xml
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/services.xsd">
    
    <service name="createCustomProduct" engine="groovy"
            location="component://myapp/script/CustomProductServices.groovy" invoke="createCustomProduct">
        <description>Create a Custom Product</description>
        <attribute name="productName" type="String" mode="IN" optional="false"/>
        <attribute name="description" type="String" mode="IN" optional="true"/>
        <attribute name="productId" type="String" mode="OUT" optional="false"/>
    </service>
</services>
```

### Service Implementation

Service implementations can be written in Groovy, Java, or other supported languages. Groovy services are commonly used for their conciseness:

```groovy
// component://myapp/script/CustomProductServices.groovy
import org.apache.ofbiz.base.util.UtilDateTime
import org.apache.ofbiz.entity.util.EntityUtil

def createCustomProduct() {
    Map result = success()
    
    String productId = delegator.getNextSeqId("CustomProduct")
    
    Map productMap = [
        productId: productId,
        productName: parameters.productName,
        description: parameters.description,
        createdDate: UtilDateTime.nowTimestamp()
    ]
    
    delegator.create("CustomProduct", productMap)
    result.productId = productId
    
    return result
}
```

## Web Application Layer

### Controller Configuration

The web application layer is configured through `webapp/WEB-INF/controller.xml`, which defines request mappings and view configurations:

```xml
<site-conf xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/site-conf.xsd">
    
    <request-map uri="createCustomProduct">
        <security https="true" auth="true"/>
        <event type="service" invoke="createCustomProduct"/>
        <response name="success" type="view" value="CustomProductList"/>
        <response name="error" type="view" value="CustomProductForm"/>
    </request-map>
    
    <view-map name="CustomProductList" type="screen" 
              page="component://myapp/widget/CustomProductScreens.xml#CustomProductList"/>
</site-conf>
```

### Screen Widget Definitions

OFBiz uses a widget-based approach for UI definition. Screen widgets are defined in XML files within the `widget/` directory:

```xml
<screens xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/widget-screen.xsd">
    
    <screen name="CustomProductList">
        <section>
            <actions>
                <entity-condition entity-name="CustomProduct" list="customProducts"/>
            </actions>
            <widgets>
                <decorator-screen name="main-decorator" location="${parameters.mainDecoratorLocation}">
                    <decorator-section name="body">
                        <include-grid name="CustomProductGrid" location="component://myapp/widget/CustomProductForms.xml"/>
                    </decorator-section>
                </decorator-screen>
            </widgets>
        </section>
    </screen>
</screens>
```

## Integration Patterns

### Service Orchestration

Custom applications often need to integrate with existing OFBiz services. This is achieved through service orchestration using the Service Engine:

```groovy
def complexBusinessProcess() {
    // Call existing OFBiz service
    Map createPartyResult = dispatcher.runSync("createPerson", [
        firstName: parameters.firstName,
        lastName: parameters.lastName
    ])
    
    if (ServiceUtil.isError(createPartyResult)) {
        return createPartyResult
    }
    
    // Use result in custom service
    Map customResult = dispatcher.runSync("createCustomProduct", [
        productName: parameters.productName,
        ownerId: createPartyResult.partyId
    ])
    
    return customResult
}
```

### Event-Driven Architecture

Custom applications can leverage OFBiz's event system through Entity Condition Actions (ECAs) defined in `entitydef/eecas.xml`:

```xml
<entity-eca xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entityeca.xsd">
    
    <eca entity="CustomProduct" operation="create" event="return">
        <condition field-name="productName" operator="not-empty"/>
        <action service="sendCustomProductNotification" mode="async"/>
    </eca>
</entity-eca>
```

## Testing and Quality Assurance

### Unit Testing

Custom applications should include comprehensive test suites using OFBiz's testing framework. Test definitions are placed in `testdef/`:

```xml
<test-suite xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/test-suite.xsd">
    
    <test-case case-name="testCreateCustomProduct">
        <service-test service-name="createCustomProduct">
            <parameter name="productName" value="Test Product"/>
            <parameter name="description" value="Test Description"/>
        </service-test>
    </test-case>
</test-suite>
```

## Best Practices

### Security Implementation

Custom applications must implement proper security measures using O

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:48:17*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*