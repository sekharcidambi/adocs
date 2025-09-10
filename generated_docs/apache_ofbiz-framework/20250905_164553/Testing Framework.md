## Testing Framework

## Overview

Apache OFBiz provides a comprehensive testing framework designed to ensure the reliability and stability of its enterprise resource planning components. The framework supports multiple testing methodologies including unit tests, integration tests, and functional tests, all integrated seamlessly with the multi-tier architecture. Built on top of JUnit and TestNG, the testing infrastructure leverages OFBiz's service engine and entity framework to provide realistic testing scenarios that mirror production environments.

## Testing Architecture

The OFBiz testing framework follows the same multi-tier architecture pattern as the main application:

### Test Structure Layers

- **Presentation Layer Tests**: Frontend component testing using Jest and Selenium WebDriver
- **Business Logic Layer Tests**: Service and workflow testing using OFBiz's built-in test harness
- **Data Access Layer Tests**: Entity engine and database interaction testing with embedded Derby

The framework utilizes OFBiz's delegator pattern to provide isolated test environments while maintaining access to the full service stack.

## Core Testing Components

### OFBiz Test Suite Framework

The primary testing mechanism is built around the `TestSuite` entity and `runTestSuite` service:

```java
// Example test service implementation
public static Map<String, Object> testCreateCustomer(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    
    try {
        Map<String, Object> createCustomerMap = UtilMisc.toMap(
            "partyId", "TEST_CUSTOMER_001",
            "partyTypeId", "PERSON",
            "firstName", "Test",
            "lastName", "Customer"
        );
        
        Map<String, Object> result = dispatcher.runSync("createPerson", createCustomerMap);
        
        if (ServiceUtil.isError(result)) {
            return ServiceUtil.returnError("Failed to create test customer");
        }
        
        return ServiceUtil.returnSuccess("Customer creation test passed");
    } catch (GenericServiceException e) {
        return ServiceUtil.returnError("Test failed: " + e.getMessage());
    }
}
```

### Entity Engine Testing

OFBiz provides specialized testing utilities for entity operations:

```groovy
// Groovy-based entity test example
import org.apache.ofbiz.entity.test.EntityTestSuite

class ProductEntityTest extends EntityTestSuite {
    
    void testProductCreation() {
        def product = delegator.makeValue("Product", [
            productId: "TEST_PRODUCT_001",
            productTypeId: "FINISHED_GOOD",
            productName: "Test Product"
        ])
        
        product.create()
        
        def retrievedProduct = from("Product")
            .where("productId", "TEST_PRODUCT_001")
            .queryOne()
            
        assert retrievedProduct != null
        assert retrievedProduct.productName == "Test Product"
    }
}
```

## Test Execution Methods

### Gradle-based Test Execution

OFBiz integrates testing with its Gradle build system:

```bash
# Run all tests
./gradlew test

# Run specific test suite
./gradlew test -Dtest.single=AccountingTests

# Run tests with specific component
./gradlew :applications:accounting:test

# Run integration tests
./gradlew integrationTest
```

### Service-based Test Execution

Tests can be executed through OFBiz services:

```bash
# Execute test suite via service call
./gradlew ofbiz --load-data readers=seed,demo,ext --test component=order

# Run specific test case
./gradlew ofbiz --test case=testCreateOrderHeader
```

## Database Testing Strategy

### Test Data Management

OFBiz employs a sophisticated test data management system using XML entity data files:

```xml
<!-- test-data/OrderTestData.xml -->
<entity-engine-xml>
    <OrderHeader orderId="TEST_ORDER_001" 
                 orderTypeId="SALES_ORDER" 
                 orderDate="2023-01-01 00:00:00" 
                 statusId="ORDER_CREATED"
                 currencyUom="USD"/>
    
    <OrderItem orderId="TEST_ORDER_001" 
               orderItemSeqId="00001" 
               productId="TEST_PRODUCT_001" 
               quantity="2" 
               unitPrice="29.99"/>
</entity-engine-xml>
```

### Transaction Isolation

Tests utilize OFBiz's transaction management for proper isolation:

```java
public class TransactionalTest extends OFBizTestCase {
    
    @Override
    protected void setUp() throws Exception {
        super.setUp();
        // Begin test transaction
        TransactionUtil.begin();
    }
    
    @Override
    protected void tearDown() throws Exception {
        // Rollback test transaction to maintain clean state
        TransactionUtil.rollback();
        super.tearDown();
    }
}
```

## Integration Testing Patterns

### Service Chain Testing

Complex business processes are tested through service orchestration:

```java
public void testOrderProcessingWorkflow() {
    // Create customer
    Map<String, Object> customerResult = dispatcher.runSync("createCustomer", customerData);
    String partyId = (String) customerResult.get("partyId");
    
    // Create order
    Map<String, Object> orderData = UtilMisc.toMap("partyId", partyId);
    Map<String, Object> orderResult = dispatcher.runSync("createOrder", orderData);
    String orderId = (String) orderResult.get("orderId");
    
    // Process payment
    Map<String, Object> paymentResult = dispatcher.runSync("processOrderPayment", 
        UtilMisc.toMap("orderId", orderId));
    
    // Verify order status
    GenericValue order = delegator.findOne("OrderHeader", 
        UtilMisc.toMap("orderId", orderId), false);
    assertEquals("ORDER_APPROVED", order.getString("statusId"));
}
```

## Frontend Testing Integration

### JavaScript Testing with Jest

Frontend components are tested using Jest framework:

```javascript
// tests/js/components/ProductCatalog.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import ProductCatalog from '../../../webapp/catalog/js/components/ProductCatalog';

describe('ProductCatalog Component', () => {
    test('renders product list correctly', async () => {
        const mockProducts = [
            { productId: 'PROD_001', productName: 'Test Product 1' },
            { productId: 'PROD_002', productName: 'Test Product 2' }
        ];
        
        render(<ProductCatalog products={mockProducts} />);
        
        expect(screen.getByText('Test Product 1')).toBeInTheDocument();
        expect(screen.getByText('Test Product 2')).toBeInTheDocument();
    });
});
```

### Selenium WebDriver Integration

End-to-end testing utilizes Selenium for browser automation:

```java
public class EcommerceWebTest extends OFBizSeleniumTest {
    
    @Test
    public void testProductOrderProcess() {
        driver.get("https://localhost:8443/ecommerce");
        
        // Navigate to product
        WebElement productLink = driver.findElement(By.linkText("Test Product"));
        productLink.click();
        
        // Add to cart
        WebElement addToCartBtn = driver.findElement(By.id("add-to-cart"));
        addToCartBtn.click();
        
        // Verify cart contents
        WebElement cartCount = driver.findElement(By.id("cart-count"));
        assertEquals("1", cartCount.getText());
    }
}
```

## Continuous Integration Testing

### Jenkins Pipeline Integration

OFBiz testing integrates with Jenkins for continuous integration:

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh './gradlew test'

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:10:34*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*