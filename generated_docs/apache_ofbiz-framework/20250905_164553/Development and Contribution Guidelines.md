# Development and Contribution Guidelines

## Development Environment Setup

Before contributing to Apache OFBiz, ensure your development environment meets the following requirements:

### Prerequisites
- **Java Development Kit (JDK) 11 or higher** - OFBiz requires Java 11+ for compilation and runtime
- **Git** - For version control and repository management
- **Gradle** - Build automation (included via Gradle Wrapper)
- **Database** - MySQL 8.0+, PostgreSQL 12+, or Apache Derby (default)

### Initial Setup
```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
./gradlew build
./gradlew ofbiz
```

### IDE Configuration
For optimal development experience, configure your IDE with:
- **Code Style**: Import the OFBiz code style configuration from `tools/code-style/`
- **Encoding**: Set UTF-8 as default encoding
- **Line Endings**: Use Unix-style line endings (LF)
- **Indentation**: 4 spaces for Java/Groovy, 2 spaces for XML/JavaScript

## Code Structure and Architecture Guidelines

### Multi-tier Architecture Compliance
When contributing code, ensure adherence to OFBiz's multi-tier architecture:

#### Presentation Layer
- **Location**: `themes/`, `webapp/` directories
- **Technologies**: Freemarker templates, JavaScript (React/Angular/Vue.js)
- **Guidelines**: 
  - Separate presentation logic from business logic
  - Use OFBiz screen widgets and forms for UI consistency
  - Implement responsive design patterns

```xml
<!-- Example screen widget structure -->
<screens xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <screen name="MyCustomScreen">
        <section>
            <actions>
                <service service-name="getCustomData" result-map="customData"/>
            </actions>
            <widgets>
                <decorator-screen name="CommonDecorator">
                    <decorator-section name="body">
                        <include-form name="CustomForm" location="component://mycomponent/widget/Forms.xml"/>
                    </decorator-section>
                </decorator-screen>
            </widgets>
        </section>
    </screen>
</screens>
```

#### Business Logic Layer
- **Location**: `src/main/java/`, `src/main/groovy/`, `servicedef/`
- **Patterns**: Service-oriented architecture, event-driven processing
- **Guidelines**:
  - Implement business logic as services in `servicedef/services.xml`
  - Use proper transaction management with `require-new-transaction` or `use-transaction`
  - Follow the Service Engine patterns for data validation and processing

```xml
<!-- Service definition example -->
<service name="createCustomEntity" engine="entity-auto" invoke="create" auth="true">
    <description>Create Custom Entity</description>
    <auto-attributes entity-name="CustomEntity" include="pk" mode="OUT" optional="false"/>
    <auto-attributes entity-name="CustomEntity" include="nonpk" mode="IN" optional="true"/>
    <override name="customField" optional="false"/>
</service>
```

#### Data Access Layer
- **Location**: `entitydef/`, `data/`
- **Guidelines**:
  - Define entities in `entitydef/entitymodel.xml`
  - Use proper field types and relationships
  - Include seed data in appropriate XML files

```xml
<!-- Entity definition example -->
<entity entity-name="CustomEntity" package-name="org.apache.ofbiz.custom">
    <field name="customId" type="id-ne"/>
    <field name="description" type="description"/>
    <field name="createdDate" type="date-time"/>
    <prim-key field="customId"/>
    <relation type="one" fk-name="CUSTOM_PARTY" rel-entity-name="Party">
        <key-map field-name="partyId"/>
    </relation>
</entity>
```

## Coding Standards and Best Practices

### Java/Groovy Development
- **Naming Conventions**: Use camelCase for methods and variables, PascalCase for classes
- **Documentation**: Include comprehensive Javadoc for all public methods and classes
- **Error Handling**: Use OFBiz's ServiceUtil for service responses and proper exception handling
- **Security**: Always validate input parameters and use proper authorization checks

```java
public static Map<String, Object> createCustomRecord(DispatchContext dctx, Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    try {
        // Input validation
        String customId = (String) context.get("customId");
        if (UtilValidate.isEmpty(customId)) {
            return ServiceUtil.returnError("Custom ID is required");
        }
        
        // Business logic implementation
        GenericValue customEntity = delegator.makeValue("CustomEntity");
        customEntity.setAllFields(context, false, null, null);
        customEntity.create();
        
        return ServiceUtil.returnSuccess("Custom record created successfully");
    } catch (GenericEntityException e) {
        Debug.logError(e, "Error creating custom record", module);
        return ServiceUtil.returnError("Error creating custom record: " + e.getMessage());
    }
}
```

### Database Integration
- **Entity Engine**: Use OFBiz Entity Engine for all database operations
- **Transactions**: Implement proper transaction boundaries using `TransactionUtil`
- **Performance**: Utilize entity caching and proper indexing strategies

## Testing Requirements

### Unit Testing
- **Framework**: Use JUnit 5 for unit tests
- **Location**: Place tests in `src/test/java/`
- **Coverage**: Aim for minimum 80% code coverage for new features
- **Mocking**: Use Mockito for external dependencies

```java
@Test
public void testCreateCustomRecord() {
    Map<String, Object> serviceContext = new HashMap<>();
    serviceContext.put("customId", "TEST_001");
    serviceContext.put("description", "Test Record");
    serviceContext.put("userLogin", userLogin);
    
    Map<String, Object> result = dispatcher.runSync("createCustomRecord", serviceContext);
    assertTrue(ServiceUtil.isSuccess(result));
}
```

### Integration Testing
- **Database**: Use Derby in-memory database for integration tests
- **Services**: Test complete service chains and workflows
- **Data**: Include test data setup and cleanup procedures

## Contribution Workflow

### Branch Strategy
1. **Fork** the repository to your GitHub account
2. **Create feature branch** from `trunk`: `git checkout -b feature/OFBIZ-XXXXX-description`
3. **Implement changes** following coding standards
4. **Test thoroughly** with unit and integration tests
5. **Commit** with descriptive messages referencing JIRA tickets

### Pull Request Process
1. **JIRA Ticket**: Ensure corresponding JIRA ticket exists at https://issues.apache.org/jira/browse/OFBIZ
2. **Code Review**: Submit PR with detailed description and test results
3. **Documentation**: Update relevant documentation and comments
4. **Backwards Compatibility**: Ensure changes don't break existing functionality

### Commit Message Format
```
OFBIZ-XXXXX: Brief description of the change

Detailed explanation of what was changed and why.
Include any breaking changes or migration notes.

- Specific change 1
- Specific change 2
```

## Component Development Guidelines

### Creating New Components
When developing new OFBiz components:

1. **Structure**: Follow standard component directory structure
```
component/
├── config/
├── data/
├── entitydef/
├── script/
├── servicedef/
├── src/main/java/
├── webapp/
├── widget/
└── ofbiz-component.xml
```

2. **Component Descriptor**: Define proper component dependencies in `ofbiz-component.xml`
```xml
<ofbiz-component name="mycomponent" enabled="true">
    <depends-on component-name="base"/>
    <depends-on component-name="entity"/>
    <resource-loader name="main" type="component"/>

## Subsections

- [Development Environment Setup](./Development Environment Setup.md)
- [Code Standards and Best Practices](./Code Standards and Best Practices.md)
- [Testing Framework](./Testing Framework.md)

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

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Development Environment Setup**: Detailed coverage of development environment setup
- **Code Standards and Best Practices**: Detailed coverage of code standards and best practices
- **Testing Framework**: Detailed coverage of testing framework

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:08:59*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*