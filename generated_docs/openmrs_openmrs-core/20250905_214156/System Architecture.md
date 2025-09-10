# System Architecture

## Overview

OpenMRS Core follows a modular, service-oriented architecture designed to provide a flexible and extensible platform for medical record systems. The architecture is built on a layered approach that separates concerns between data persistence, business logic, web services, and presentation layers. This design enables healthcare organizations to customize and extend the platform while maintaining a stable core foundation.

## Core Architectural Layers

### Data Access Layer (DAO)
The Data Access Object pattern forms the foundation of OpenMRS data persistence, providing abstraction between the business logic and database operations.

```java
public interface PatientDAO {
    Patient savePatient(Patient patient) throws DAOException;
    Patient getPatient(Integer patientId) throws DAOException;
    List<Patient> getPatients(String query, boolean includeVoided, Integer start, Integer length);
}
```

Key characteristics:
- **Hibernate-based ORM**: Utilizes Hibernate for object-relational mapping with MySQL/PostgreSQL databases
- **Transaction Management**: Implements declarative transaction management through Spring's `@Transactional` annotations
- **Audit Trail Support**: Built-in support for tracking data changes through `OpenmrsObject` base classes
- **Soft Delete Pattern**: Uses voiding mechanism instead of hard deletes to maintain data integrity

### Service Layer Architecture
The service layer implements the core business logic and acts as the primary API for all OpenMRS operations.

```java
@Service
@Transactional
public class PatientServiceImpl extends BaseOpenmrsService implements PatientService {
    
    private PatientDAO dao;
    
    @Transactional(readOnly = true)
    public Patient getPatient(Integer patientId) throws APIException {
        return dao.getPatient(patientId);
    }
}
```

**Service Layer Features:**
- **Context-based Access**: All services accessed through `Context.getService()` pattern
- **Security Integration**: Method-level security through custom annotations (`@Authorized`)
- **Event-driven Architecture**: Publishes domain events for create, update, delete operations
- **Validation Framework**: Integrated validation using custom validators and JSR-303 annotations

### Module System Architecture
OpenMRS implements a sophisticated module system that allows runtime loading and unloading of functionality.

```xml
<!-- Module configuration example -->
<module configVersion="1.2">
    <id>basicmodule</id>
    <name>Basic Module</name>
    <version>1.0.0</version>
    <package>org.openmrs.module.basicmodule</package>
    <author>OpenMRS</author>
    <require_version>2.0.0</require_version>
</module>
```

**Module System Components:**
- **ModuleClassLoader**: Custom classloader hierarchy enabling module isolation
- **Activator Pattern**: Lifecycle management through `BaseModuleActivator` implementations
- **Dependency Resolution**: Automatic resolution of module dependencies and version conflicts
- **Hot Deployment**: Runtime module installation without system restart

### Web Architecture
The web layer follows the Model-View-Controller pattern with Spring MVC as the primary framework.

```java
@Controller
@RequestMapping("/patient")
public class PatientController {
    
    @RequestMapping(method = RequestMethod.GET)
    public String showPatient(@RequestParam("patientId") Integer patientId, 
                             ModelMap model) {
        Patient patient = Context.getPatientService().getPatient(patientId);
        model.addAttribute("patient", patient);
        return "patient/show";
    }
}
```

**Web Layer Features:**
- **RESTful Web Services**: Comprehensive REST API through the webservices.rest module
- **Legacy Web Framework**: Custom MVC framework for backward compatibility
- **Internationalization**: Built-in i18n support with message source resolution
- **Security Filter Chain**: Custom authentication and authorization filters

## Data Model Architecture

### Domain Object Hierarchy
OpenMRS implements a rich domain model with clear inheritance hierarchies:

```java
public abstract class BaseOpenmrsObject implements OpenmrsObject {
    private String uuid;
    // Base functionality for all domain objects
}

public abstract class BaseOpenmrsData extends BaseOpenmrsObject 
    implements OpenmrsData {
    private User creator;
    private Date dateCreated;
    private Boolean voided = Boolean.FALSE;
    // Auditing and lifecycle management
}
```

**Key Domain Patterns:**
- **Person-Patient-User Hierarchy**: Flexible person management supporting multiple roles
- **Concept Dictionary**: Standardized medical terminology through the Concept model
- **Encounter-Observation Pattern**: Clinical data capture through structured encounters
- **Location Hierarchy**: Supports complex organizational structures

### Metadata Framework
The platform provides extensive metadata capabilities for customization:

```java
// Custom form fields through metadata
FormField formField = new FormField();
formField.setForm(form);
formField.setField(field);
formField.setFieldNumber(1);
formField.setRequired(true);
```

## Integration Architecture

### API Integration Points
OpenMRS provides multiple integration mechanisms:

**REST API Endpoints:**
```bash
# Patient operations
GET /openmrs/ws/rest/v1/patient/{uuid}
POST /openmrs/ws/rest/v1/patient
PUT /openmrs/ws/rest/v1/patient/{uuid}

# Concept dictionary access
GET /openmrs/ws/rest/v1/concept?q=malaria
```

**Event-Driven Integration:**
```java
@Component
public class PatientEventListener {
    
    @EventListener
    public void handlePatientCreated(PatientCreatedEvent event) {
        // Custom logic for patient creation
        Patient patient = event.getPatient();
        // Integration with external systems
    }
}
```

### Security Architecture
Multi-layered security implementation:

- **Authentication**: Pluggable authentication providers (database, LDAP, OAuth)
- **Authorization**: Role-based access control with privilege inheritance
- **Method Security**: AOP-based method-level security enforcement
- **Data Filtering**: Automatic filtering based on user permissions

## Performance and Scalability Considerations

### Caching Strategy
```java
@Cacheable(value = "conceptCache", key = "#conceptId")
public Concept getConcept(Integer conceptId) {
    return conceptDAO.getConcept(conceptId);
}
```

### Database Optimization
- **Connection Pooling**: Configurable connection pools through C3P0
- **Query Optimization**: Hibernate query optimization and caching
- **Indexing Strategy**: Comprehensive database indexing for performance
- **Partitioning Support**: Large dataset handling through table partitioning

This architecture enables OpenMRS to serve as a robust foundation for healthcare information systems while maintaining flexibility for diverse implementation requirements across different healthcare contexts and organizational structures.

## Subsections

- [Overall Architecture](./Overall Architecture.md)
- [API Layer Design](./API Layer Design.md)
- [Web Application Structure](./Web Application Structure.md)
- [Data Flow and Processing](./Data Flow and Processing.md)

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Overall Architecture**: Detailed coverage of overall architecture
- **API Layer Design**: Detailed coverage of api layer design
- **Web Application Structure**: Detailed coverage of web application structure
- **Data Flow and Processing**: Detailed coverage of data flow and processing

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:43:18*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*