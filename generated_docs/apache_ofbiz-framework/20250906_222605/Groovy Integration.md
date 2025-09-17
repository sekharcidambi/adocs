# Groovy Integration

Apache OFBiz provides comprehensive integration with Groovy, a dynamic programming language that runs on the Java Virtual Machine. This integration allows developers to write more concise, expressive code while maintaining full access to OFBiz's extensive framework capabilities.

## Overview

Groovy integration in OFBiz enables developers to:
- Write business logic using Groovy's simplified syntax
- Create dynamic web pages with Groovy Server Pages (GSP)
- Implement services using Groovy scripts
- Develop event handlers and utility functions
- Leverage Groovy's powerful features like closures, builders, and metaprogramming

## Architecture and Components

### Groovy Script Engine Integration

OFBiz integrates Groovy through the Java Scripting API (JSR 223), providing seamless execution of Groovy scripts within the framework's context.

```java
// Example of Groovy script execution in OFBiz
ScriptEngineManager manager = new ScriptEngineManager();
ScriptEngine engine = manager.getEngineByName("groovy");
engine.put("context", context);
engine.put("dispatcher", dispatcher);
engine.eval(scriptContent);
```

### Service Engine Integration

Groovy services are defined in service definition files and implemented as Groovy scripts:

```xml
<!-- servicedef/services.xml -->
<service name="createCustomerGroovy" engine="groovy"
         location="component://mycomponent/groovyScripts/CreateCustomer.groovy"
         invoke="">
    <description>Create a new customer using Groovy</description>
    <attribute name="firstName" type="String" mode="IN" optional="false"/>
    <attribute name="lastName" type="String" mode="IN" optional="false"/>
    <attribute name="partyId" type="String" mode="OUT" optional="false"/>
</service>
```

## Groovy Services

### Service Implementation

Groovy services in OFBiz follow a specific structure and have access to framework components:

```groovy
// groovyScripts/CreateCustomer.groovy
import org.apache.ofbiz.entity.GenericValue
import org.apache.ofbiz.service.ServiceUtil

// Access to standard OFBiz service context variables
def dispatcher = context.dispatcher
def delegator = context.delegator
def userLogin = context.userLogin

try {
    // Create party
    def createPartyResult = dispatcher.runSync("createPerson", [
        firstName: parameters.firstName,
        lastName: parameters.lastName,
        userLogin: userLogin
    ])
    
    if (ServiceUtil.isError(createPartyResult)) {
        return createPartyResult
    }
    
    def partyId = createPartyResult.partyId
    
    // Additional business logic
    def party = delegator.findOne("Party", [partyId: partyId], false)
    if (party) {
        // Update party status
        party.statusId = "PARTY_ENABLED"
        party.store()
    }
    
    return ServiceUtil.returnSuccess("Customer created successfully", [partyId: partyId])
    
} catch (Exception e) {
    return ServiceUtil.returnError("Error creating customer: ${e.getMessage()}")
}
```

### Service Context Variables

Groovy services automatically have access to these context variables:

| Variable | Type | Description |
|----------|------|-------------|
| `parameters` | Map | Input parameters passed to the service |
| `context` | Map | Service execution context |
| `dispatcher` | LocalDispatcher | Service dispatcher for calling other services |
| `delegator` | Delegator | Entity engine delegator for database operations |
| `userLogin` | GenericValue | Current user's login information |
| `locale` | Locale | Current user's locale |
| `timeZone` | TimeZone | Current user's time zone |

## Event Handlers

### Groovy Event Implementation

Event handlers can be implemented in Groovy for processing web requests:

```groovy
// webapp/mycomponent/WEB-INF/actions/ProcessOrder.groovy
import org.apache.ofbiz.base.util.UtilValidate
import org.apache.ofbiz.entity.condition.EntityCondition
import org.apache.ofbiz.entity.condition.EntityOperator

def orderId = parameters.orderId
def dispatcher = request.getAttribute("dispatcher")
def delegator = request.getAttribute("delegator")

if (UtilValidate.isEmpty(orderId)) {
    request.setAttribute("_ERROR_MESSAGE_", "Order ID is required")
    return "error"
}

try {
    // Fetch order details
    def order = delegator.findOne("OrderHeader", [orderId: orderId], false)
    
    if (!order) {
        request.setAttribute("_ERROR_MESSAGE_", "Order not found: ${orderId}")
        return "error"
    }
    
    // Get order items
    def orderItems = delegator.findByAnd("OrderItem", 
        [orderId: orderId], 
        ["orderItemSeqId"], 
        false)
    
    // Process business logic
    def totalAmount = 0.0
    orderItems.each { item ->
        totalAmount += item.getBigDecimal("quantity") * item.getBigDecimal("unitPrice")
    }
    
    // Set results in request
    request.setAttribute("order", order)
    request.setAttribute("orderItems", orderItems)
    request.setAttribute("totalAmount", totalAmount)
    
    return "success"
    
} catch (Exception e) {
    request.setAttribute("_ERROR_MESSAGE_", "Error processing order: ${e.getMessage()}")
    return "error"
}
```

### Controller Configuration

Configure Groovy event handlers in the controller:

```xml
<!-- controller.xml -->
<request-map uri="processOrder">
    <security https="true" auth="true"/>
    <event type="groovy" path="component://mycomponent/webapp/mycomponent/WEB-INF/actions/ProcessOrder.groovy"/>
    <response name="success" type="view" value="orderDetails"/>
    <response name="error" type="view" value="orderError"/>
</request-map>
```

## Screen Actions and Form Actions

### Screen Widget Integration

Groovy scripts can be used in screen widgets for data preparation:

```xml
<!-- widget/MyScreens.xml -->
<screen name="CustomerList">
    <section>
        <actions>
            <script location="component://mycomponent/webapp/mycomponent/WEB-INF/actions/CustomerList.groovy"/>
        </actions>
        <widgets>
            <decorator-screen name="CommonDecorator">
                <decorator-section name="body">
                    <include-form name="ListCustomers" location="component://mycomponent/widget/MyForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

```groovy
// WEB-INF/actions/CustomerList.groovy
import org.apache.ofbiz.entity.condition.EntityCondition
import org.apache.ofbiz.entity.condition.EntityOperator

def delegator = request.getAttribute("delegator")

// Build search conditions
def conditions = []
if (parameters.firstName) {
    conditions.add(EntityCondition.makeCondition("firstName", 
        EntityOperator.LIKE, "%${parameters.firstName}%"))
}

def entityCondition = null
if (conditions) {
    entityCondition = EntityCondition.makeCondition(conditions, EntityOperator.AND)
}

// Fetch customers
def customers = delegator.findList("Person", entityCondition, null, ["lastName"], null, false)

// Prepare data for display
def customerList = []
customers.each { customer ->
    customerList.add([
        partyId: customer.partyId,
        firstName: customer.firstName,
        lastName: customer.lastName,
        fullName: "${customer.firstName} ${customer.lastName}"
    ])
}

context.customerList = customerList
context.customerCount = customerList.size()
```

## Entity Operations

### CRUD Operations in Groovy

Groovy provides elegant syntax for entity operations:

```groovy
// Create entity
def newParty = delegator.makeValue("Party", [
    partyId: delegator.getNextSeqId("Party"),
    partyTypeId: "PERSON",
    statusId: "PARTY_ENABLED"
])
newParty.create()

// Find operations
def party = delegator.findOne("Party", [partyId: "10000"], false)
def parties = delegator.findByAnd("Party", [partyTypeId: "PERSON"], null, false)

// Update operations
party.statusId = "PARTY_DISABLED"
party.store()

// Complex queries with conditions
def condition = EntityCondition.makeCondition([
    EntityCondition.makeCondition("partyTypeId", EntityOperator.EQUALS, "PERSON"),
    EntityCondition.makeCondition("statusId", EntityOperator.EQUALS, "PARTY_ENABLED")
], EntityOperator.AND)

def activePersons = delegator.findList("Party", condition, null, ["lastName", "firstName"], null, false)
```

### Dynamic View Entities

Create and use dynamic view entities in Groovy:

```groovy
// Create dynamic view entity
def dynamicView = delegator.makeDynamicViewEntity("PartyAndPerson")
dynamicView.addMemberEntity("PT", "Party")
dynamicView.addMemberEntity("PE", "Person")
dynamicView.addAlias("PT", "partyId")
dynamicView.addAlias("PT", "statusId")
dynamicView.addAlias("PE", "firstName")
dynamicView.addAlias("PE", "lastName")
dynamicView.addViewLink("PT", "PE", false, [partyId: "partyId"])

// Use the dynamic view
def results = delegator.findList(dynamicView, null, null, ["lastName"], null, false)
```

## Best Practices

### Code Organization

1. **Separate Concerns**: Keep business logic in services, UI logic in screen actions
2. **Reusable Functions**: Create utility Groovy scripts for common operations
3. **Error Handling**: Always implement proper exception handling

```groovy
// utils/CustomerUtils.groovy
class CustomerUtils {
    static def validateCustomerData(parameters) {
        def errors = []
        
        if (!parameters.firstName?.trim()) {
            errors.add("First name is required")
        }
        
        if (!parameters.lastName?.trim()) {
            errors.add("Last name is required")
        }
        
        if (parameters.email && !isValidEmail(parameters.email)) {
            errors.add("Invalid email format")
        }
        
        return errors
    }
    
    static def isValidEmail(email) {
        return email ==~ /^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$/
    }
}
```

### Performance Considerations

1. **Script Compilation**: OFBiz caches compiled Groovy scripts
2. **Database Operations**: Use batch operations for multiple entity operations
3. **Service Calls**: Minimize service calls in loops

```groovy
// Efficient batch operations
def partiesToCreate = []
customerData.each { data ->
    partiesToCreate.add(delegator.makeValue("Party", data))
}
delegator.storeAll(partiesToCreate)
```

### Security Guidelines

1. **Input Validation**: Always validate input parameters
2. **SQL Injection Prevention**: Use parameterized queries
3. **Access Control**: Implement proper permission checks

```groovy
// Input validation example
import org.apache.ofbiz.base.util.UtilValidate
import org.apache.ofbiz.security.Security

def security = request.getAttribute("security")
def userLogin = session.getAttribute("userLogin")

// Check permissions
if (!security.hasEntityPermission("PARTY", "_CREATE", userLogin)) {
    request.setAttribute("_ERROR_MESSAGE_", "Permission denied")
    return "error"
}

// Validate inputs
if (UtilValidate.isEmpty(parameters.partyId)) {
    request.setAttribute("_ERROR_MESSAGE_", "Party ID cannot be empty")
    return "error"
}
```

## Testing Groovy Components

### Unit Testing Services

```groovy
// test/groovy/CustomerServiceTest.groovy
import org.apache.ofbiz.testtools.GroovyScriptTestCase

class CustomerServiceTest extends GroovyScriptTestCase {
    
    void testCreateCustomer() {
        def result = dispatcher.runSync("createCustomerGroovy", [
            firstName: "John",
            lastName: "Doe",
            userLogin: userLogin
        ])
        
        assert result.responseMessage == "success"
        assert result.partyId != null
        
        // Verify customer was created
        def party = delegator.findOne("Party", [partyId: result.partyId], false)
        assert party != null
        assert party.statusId == "PARTY_ENABLED"
    }
}
```

## Integration with Java Components

### Calling Java from Groovy

```groovy
// Import Java classes
import org.apache.ofbiz.base.util.UtilDateTime
import org.apache.ofbiz.base.util.UtilValidate
import java.sql.Timestamp

// Use Java utilities
def now = UtilDateTime.nowTimestamp()
def isValid = UtilValidate.isNotEmpty(parameters.customerId)

// Call Java services
def javaServiceResult = dispatcher.runSync("javaServiceName", parameters)
```

### Groovy Builders for XML/JSON

```groovy
import groovy.json.JsonBuilder
import groovy.xml.MarkupBuilder

// JSON response
def jsonBuilder = new JsonBuilder()
jsonBuilder {
    customers customerList.collect { customer ->
        [
            id: customer.partyId,
            name: "${customer.firstName} ${customer.lastName}",
            status: customer.statusId
        ]
    }
}

response.setContentType("application/json")
response.getWriter().write(jsonBuilder.toString())
```

## Troubleshooting

### Common Issues

1. **ClassPath Issues**: Ensure Groovy scripts can access required OFBiz classes
2. **Context Variables**: Verify correct context variable names and types
3. **Script Compilation**: Check for syntax errors in Groovy scripts

### Debugging Tips

1. **Logging**: Use OFBiz logging framework in Groovy scripts
2. **Exception Handling**: Implement comprehensive error handling
3. **Development Mode**: Enable script reloading during development

```groovy
import org.apache.ofbiz.base.util.Debug

// Logging in Groovy scripts
Debug.logInfo("Processing customer: ${parameters.customerId}", "CustomerService")
Debug.logError("Error occurred: ${e.getMessage()}", "CustomerService")

// Development debugging
if (Debug.verboseOn()) {
    Debug.logVerbose("Customer data: ${parameters}", "CustomerService")
}
```

This comprehensive integration allows developers to leverage Groovy's expressive syntax while maintaining full access to OFBiz's robust framework capabilities, resulting in more maintainable and readable business applications.