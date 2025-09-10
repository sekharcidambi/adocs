## Framework Extension Points

## Overview

Apache OFBiz provides a comprehensive set of extension points that allow developers to customize, extend, and integrate with the framework without modifying core components. These extension points are designed around OFBiz's service-oriented architecture and component-based structure, enabling clean separation of custom functionality from the base framework.

The framework's extensibility is built on several key architectural patterns including the Entity Engine, Service Engine, Screen Widget System, and Event Handler mechanisms. These extension points ensure that customizations remain upgrade-safe and maintainable across different versions of the framework.

## Core Extension Mechanisms

### Service Engine Extensions

The Service Engine serves as the primary extension point for business logic customization. Services can be extended through multiple approaches:

**Service Implementation Override**
```xml
<!-- In custom component's servicedef/services.xml -->
<service name="createCustomer" engine="java" 
         location="com.example.customer.CustomerServices" 
         invoke="createCustomer" override="true">
    <description>Custom customer creation logic</description>
    <attribute name="partyId" type="String" mode="OUT" optional="false"/>
    <attribute name="firstName" type="String" mode="IN" optional="false"/>
</service>
```

**Service Event Condition Actions (SECAs)**
SECAs provide hooks to execute additional logic before, after, or during service execution:

```xml
<!-- In custom component's servicedef/secas.xml -->
<service-eca>
    <eca service="createParty" event="commit">
        <condition field-name="partyTypeId" operator="equals" value="PERSON"/>
        <action service="sendWelcomeEmail" mode="async"/>
    </eca>
</service-eca>
```

### Entity Engine Extension Points

The Entity Engine supports several extension mechanisms for data layer customization:

**Entity Condition Actions (ECAs)**
ECAs trigger on entity operations, providing database-level extension points:

```xml
<!-- In custom component's entitydef/eecas.xml -->
<entity-eca>
    <eca entity="Party" operation="create" event="return">
        <condition field-name="statusId" operator="equals" value="PARTY_ENABLED"/>
        <action service="logPartyCreation" mode="sync"/>
    </eca>
</entity-eca>
```

**Custom Entity Definitions**
Extend existing entities or create new ones while maintaining referential integrity:

```xml
<!-- In custom component's entitydef/entitymodel.xml -->
<extend-entity entity-name="Party">
    <field name="customField" type="long-varchar"/>
    <field name="integrationId" type="id"/>
</extend-entity>
```

### Screen Widget System Extensions

The Screen Widget System provides multiple extension points for UI customization:

**Screen Decoration and Inheritance**
```xml
<!-- Custom screen extending base functionality -->
<screen name="CustomPartyProfile">
    <section>
        <actions>
            <set field="titleProperty" value="CustomPartyProfile"/>
            <entity-one entity-name="Party" value-field="party"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonPartyDecorator" location="${parameters.mainDecoratorLocation}">
                <decorator-section name="body">
                    <include-screen name="PartyProfile" location="component://party/widget/partymgr/PartyScreens.xml"/>
                    <container style="custom-section">
                        <include-form name="CustomPartyForm" location="component://custom/widget/CustomForms.xml"/>
                    </container>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

### Event Handler Extensions

The framework supports custom event handlers for request processing:

**Controller Configuration**
```xml
<!-- In custom component's webapp/WEB-INF/controller.xml -->
<request-map uri="customPartyUpdate">
    <security https="true" auth="true"/>
    <event type="java" path="com.example.events.PartyEvents" invoke="updateCustomParty"/>
    <response name="success" type="view" value="PartyProfile"/>
    <response name="error" type="view" value="EditParty"/>
</request-map>
```

**Custom Event Handler Implementation**
```java
public class PartyEvents {
    public static String updateCustomParty(HttpServletRequest request, HttpServletResponse response) {
        Delegator delegator = (Delegator) request.getAttribute("delegator");
        LocalDispatcher dispatcher = (LocalDispatcher) request.getAttribute("dispatcher");
        GenericValue userLogin = (GenericValue) request.getSession().getAttribute("userLogin");
        
        // Custom business logic implementation
        Map<String, Object> serviceContext = UtilHttp.getParameterMap(request);
        serviceContext.put("userLogin", userLogin);
        
        try {
            Map<String, Object> result = dispatcher.runSync("updateParty", serviceContext);
            if (ServiceUtil.isError(result)) {
                request.setAttribute("_ERROR_MESSAGE_", ServiceUtil.getErrorMessage(result));
                return "error";
            }
        } catch (GenericServiceException e) {
            Debug.logError(e, "Error updating party", MODULE);
            return "error";
        }
        
        return "success";
    }
}
```

## Component-Based Extension Architecture

### Hot-Deploy Components

OFBiz supports runtime component deployment through the hot-deploy mechanism:

```
hot-deploy/
└── custom-component/
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

**Component Descriptor Configuration**
```xml
<!-- hot-deploy/custom-component/ofbiz-component.xml -->
<ofbiz-component name="custom-component"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="dir" location="build/classes"/>
    <classpath type="jar" location="lib/*"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/CustomSecurityData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    <service-resource type="eca" loader="main" location="servicedef/secas.xml"/>
    
    <webapp name="custom"
            title="Custom Application"
            server="default-server"
            location="webapp/custom"
            base-permission="CUSTOM"
            mount-point="/custom"/>
</ofbiz-component>
```

### Plugin Architecture

Modern OFBiz versions support a plugin architecture for cleaner separation:

```gradle
// plugins/custom-plugin/build.gradle
dependencies {
    pluginLibsCompile 'org.apache.commons:commons-csv:1.8'
    pluginLibsRuntime 'mysql:mysql-connector-java:8.0.23'
}
```

## Integration Patterns

### External System Integration

**Custom Service Engines**
Implement custom service engines for specialized integration requirements:

```java
public class RestServiceEngine extends GenericEngine {
    public Map<String, Object> runSync(String localName, ModelService modelService, Map<String, Object> context) 
            throws GenericServiceException {
        // Custom REST API integration logic
        return ServiceUtil.returnSuccess();
    }
}
```

**Data Import/Export Extensions**
Leverage the EntitySyncContext for custom data synchronization:

```xml
<service name="customDataSync" engine="java" 
         location="com.example.sync.DataSyncServices" 
         invoke="performCustomSync">
    <implements service="entitySyncPermissionInterface"/>
    <attribute name="entitySyncId" type="

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:47:30*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*