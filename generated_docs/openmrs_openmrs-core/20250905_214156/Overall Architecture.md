## Overall Architecture

## Core Architecture Overview

OpenMRS Core follows a modular, service-oriented architecture designed to provide a robust foundation for medical record systems in resource-constrained environments. The architecture is built on Java/Spring framework principles with a clear separation of concerns across multiple architectural layers.

### Architectural Layers

The OpenMRS Core architecture is organized into distinct layers that promote maintainability, testability, and extensibility:

#### **Presentation Layer**
- **Web Controllers**: Spring MVC controllers handle HTTP requests and coordinate between the web layer and service layer
- **REST API**: RESTful web services provide programmatic access to OpenMRS functionality
- **Legacy Web Pages**: JSP-based user interfaces for administrative and clinical functions
- **API Documentation**: Swagger/OpenAPI integration for REST endpoint documentation

#### **Service Layer**
The service layer contains the core business logic and is divided into several key components:

```java
@Service
@Transactional
public class PatientServiceImpl extends BaseOpenmrsService implements PatientService {
    // Business logic implementation
    // Transaction management
    // Security enforcement
}
```

Key service categories include:
- **Clinical Services**: `PatientService`, `EncounterService`, `ObsService`
- **Administrative Services**: `UserService`, `LocationService`, `ConceptService`
- **System Services**: `AdministrationService`, `ContextService`, `AlertService`

#### **Data Access Layer**
- **Hibernate ORM**: Object-relational mapping for database interactions
- **DAO Pattern**: Data Access Objects provide abstraction over database operations
- **Database Abstraction**: Support for MySQL, PostgreSQL, and other RDBMS

```java
public interface PatientDAO extends OpenmrsObjectDAO<Patient> {
    List<Patient> getPatients(String query, List<PatientIdentifierType> identifierTypes, 
                             boolean matchIdentifierExactly) throws DAOException;
}
```

### Module System Architecture

OpenMRS Core implements a sophisticated module system that allows for runtime extension and customization:

#### **Module Lifecycle Management**
- **Dynamic Loading**: Modules can be installed, started, stopped, and uninstalled at runtime
- **Dependency Resolution**: Automatic handling of module dependencies and version conflicts
- **Classloader Isolation**: Each module operates in its own classloader to prevent conflicts

```xml
<!-- Module configuration example -->
<module configVersion="1.2">
    <id>basicmodule</id>
    <name>Basic Module</name>
    <version>1.0.0</version>
    <require_modules>
        <require_module version="2.0.0">org.openmrs.module.webservices.rest</require_module>
    </require_modules>
</module>
```

#### **Extension Points**
The architecture provides numerous extension points for modules:
- **Service Extension**: Modules can provide additional services or override existing ones
- **Web Resource Integration**: Automatic inclusion of module CSS, JavaScript, and images
- **Database Schema Management**: Liquibase integration for module-specific schema changes
- **Privilege and Role Management**: Fine-grained security extensions

### Data Model Architecture

#### **Core Domain Objects**
The architecture centers around key domain objects that represent medical concepts:

```java
@Entity
@Table(name = "patient")
public class Patient extends BasePersonData implements java.io.Serializable {
    @OneToMany(mappedBy = "patient", cascade = CascadeType.ALL)
    private Set<PatientIdentifier> identifiers;
    
    @OneToMany(mappedBy = "patient", cascade = CascadeType.ALL)
    private Set<PatientProgram> programs;
}
```

- **Person/Patient**: Core demographic and identity information
- **Encounter**: Clinical interactions between patients and providers
- **Observation (Obs)**: Clinical data points and measurements
- **Concept**: Standardized medical terminology and coding

#### **Metadata Management**
- **Concept Dictionary**: Centralized management of medical terminology
- **Form Management**: Dynamic form creation and management
- **Location Hierarchy**: Support for complex organizational structures

### Security Architecture

#### **Authentication and Authorization**
```java
@Secured({"PRIVILEGE_VIEW_PATIENTS"})
public List<Patient> getAllPatients(boolean includeVoided) throws APIException {
    return dao.getAllPatients(includeVoided);
}
```

- **Role-Based Access Control (RBAC)**: Fine-grained permissions system
- **Context-Aware Security**: User context maintained throughout request lifecycle
- **API Key Authentication**: Support for programmatic access via REST APIs

#### **Audit and Logging**
- **Comprehensive Audit Trail**: All data modifications are logged with user and timestamp
- **Event-Driven Logging**: AOP-based logging for service method invocations
- **Security Event Monitoring**: Failed authentication attempts and privilege violations

### Integration Architecture

#### **Interoperability Standards**
- **HL7 Support**: Integration capabilities for HL7 message processing
- **FHIR Compatibility**: RESTful API following FHIR standards (via modules)
- **Standard Vocabularies**: Support for SNOMED CT, ICD-10, LOINC, and other medical coding systems

#### **External System Integration**
```java
// Example of external system integration point
public interface MessageService extends OpenmrsService {
    void sendMessage(Message message) throws MessageException;
    List<Message> getMessages(User user, boolean includeRead);
}
```

### Performance and Scalability Considerations

#### **Caching Strategy**
- **Hibernate Second-Level Cache**: Entity and query result caching
- **Application-Level Caching**: Strategic caching of frequently accessed metadata
- **Session Management**: Optimized database session handling

#### **Database Optimization**
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Strategic use of lazy loading and fetch strategies
- **Index Management**: Database-specific index optimization

### Configuration Management

The architecture supports flexible configuration through multiple mechanisms:

```properties
# Global properties configuration
connection.url=jdbc:mysql://localhost:3306/openmrs
hibernate.dialect=org.hibernate.dialect.MySQLDialect
module.allow_web_admin=true
```

- **Global Properties**: Runtime configuration stored in database
- **Application Properties**: File-based configuration for system-level settings
- **Module-Specific Configuration**: Isolated configuration management per module

This architectural foundation enables OpenMRS to serve as a flexible, scalable platform for medical record management while maintaining the extensibility needed for diverse healthcare environments and use cases.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:43:48*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*