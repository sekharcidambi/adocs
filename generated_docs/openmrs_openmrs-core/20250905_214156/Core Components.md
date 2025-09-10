# Core Components

## Overview

The OpenMRS Core Components form the foundational architecture of the OpenMRS medical record system, providing essential services and abstractions that enable healthcare data management, clinical workflows, and extensibility through modules. These components implement a service-oriented architecture with clear separation of concerns, following enterprise Java patterns with Spring Framework integration.

## Service Layer Architecture

### Core Service Pattern

OpenMRS Core implements a comprehensive service layer that abstracts business logic from data access and presentation layers. Each domain area is represented by a service interface and implementation:

```java
@Service("patientService")
@Transactional
public class PatientServiceImpl extends BaseOpenmrsService implements PatientService {
    
    private PatientDAO dao;
    
    @Override
    public Patient savePatient(Patient patient) throws APIException {
        // Business logic validation
        ValidateUtil.validate(patient);
        
        // Audit logging
        if (patient.getPatientId() == null) {
            patient.setCreator(Context.getAuthenticatedUser());
            patient.setDateCreated(new Date());
        }
        
        return dao.savePatient(patient);
    }
}
```

Key service components include:

- **PatientService**: Patient demographics, identifiers, and relationships
- **EncounterService**: Clinical encounters and visit management
- **ObsService**: Clinical observations and measurements
- **ConceptService**: Medical terminology and concept dictionary
- **UserService**: Authentication, authorization, and user management
- **LocationService**: Healthcare facility and location hierarchy
- **ProgramWorkflowService**: Patient care programs and workflows

### Context and Service Access

The `Context` class provides centralized access to all core services through a static API:

```java
// Service access pattern
Patient patient = Context.getPatientService().getPatient(patientId);
Encounter encounter = Context.getEncounterService().getEncounter(encounterId);
User currentUser = Context.getAuthenticatedUser();

// Transaction management
Context.openSession();
try {
    // Service operations
    Context.getPatientService().savePatient(patient);
} finally {
    Context.closeSession();
}
```

## Data Access Layer (DAO Pattern)

### Hibernate Integration

Core components utilize Hibernate ORM for data persistence, with DAO implementations providing database abstraction:

```java
public class HibernatePatientDAO implements PatientDAO {
    
    private SessionFactory sessionFactory;
    
    @Override
    public Patient getPatient(Integer patientId) {
        return (Patient) sessionFactory.getCurrentSession()
            .get(Patient.class, patientId);
    }
    
    @Override
    public List<Patient> getPatients(String query, boolean includeVoided, 
                                   Integer start, Integer length) {
        Criteria criteria = sessionFactory.getCurrentSession()
            .createCriteria(Patient.class);
        
        if (!includeVoided) {
            criteria.add(Restrictions.eq("voided", false));
        }
        
        return criteria.list();
    }
}
```

### Database Schema Management

Core components include Liquibase changesets for schema evolution:

```xml
<changeSet id="core-data-1.9.0" author="openmrs">
    <createTable tableName="patient">
        <column name="patient_id" type="int" autoIncrement="true">
            <constraints primaryKey="true" nullable="false"/>
        </column>
        <column name="creator" type="int">
            <constraints nullable="false"/>
        </column>
        <column name="date_created" type="datetime">
            <constraints nullable="false"/>
        </column>
        <column name="voided" type="boolean" defaultValueBoolean="false">
            <constraints nullable="false"/>
        </column>
    </createTable>
</changeSet>
```

## Domain Model Components

### Base Entity Hierarchy

All domain objects extend from base classes providing common functionality:

```java
@MappedSuperclass
public abstract class BaseOpenmrsObject implements OpenmrsObject {
    private String uuid = UUID.randomUUID().toString();
    
    // Standard getters/setters and utility methods
}

@MappedSuperclass
public abstract class BaseOpenmrsData extends BaseOpenmrsObject 
    implements OpenmrsData {
    
    private User creator;
    private Date dateCreated;
    private User changedBy;
    private Date dateChanged;
    private Boolean voided = Boolean.FALSE;
    private User voidedBy;
    private Date dateVoided;
    private String voidReason;
}
```

### Core Domain Entities

**Patient Entity**: Central healthcare record with demographics and identifiers

```java
@Entity
@Table(name = "patient")
public class Patient extends BaseOpenmrsData {
    
    @OneToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "patient_id")
    private Person person;
    
    @OneToMany(mappedBy = "patient", cascade = CascadeType.ALL)
    private Set<PatientIdentifier> identifiers;
    
    @OneToMany(mappedBy = "patient")
    private Set<PatientProgram> programs;
}
```

**Encounter Entity**: Clinical interactions with structured data capture

```java
@Entity
@Table(name = "encounter")
public class Encounter extends BaseOpenmrsData {
    
    @ManyToOne
    @JoinColumn(name = "patient_id")
    private Patient patient;
    
    @ManyToOne
    @JoinColumn(name = "encounter_type")
    private EncounterType encounterType;
    
    @OneToMany(mappedBy = "encounter", cascade = CascadeType.ALL)
    private Set<Obs> obs = new HashSet<>();
}
```

## Event and Extension Framework

### Application Event System

Core components publish domain events for loose coupling and extensibility:

```java
@Component
public class PatientServiceEventPublisher {
    
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    public void publishPatientCreated(Patient patient) {
        PatientCreatedEvent event = new PatientCreatedEvent(this, patient);
        eventPublisher.publishEvent(event);
    }
}

@EventListener
public void handlePatientCreated(PatientCreatedEvent event) {
    Patient patient = event.getPatient();
    // Custom processing logic
}
```

### Module Extension Points

Core components provide extension mechanisms for modules:

```java
public interface PatientServiceExtension {
    void beforePatientSave(Patient patient);
    void afterPatientSave(Patient patient);
}

// Module implementation
@Component
public class CustomPatientExtension implements PatientServiceExtension {
    
    @Override
    public void beforePatientSave(Patient patient) {
        // Custom validation or processing
        validateCustomBusinessRules(patient);
    }
}
```

## Configuration and Initialization

### Spring Configuration

Core components are configured through Spring XML and annotations:

```xml
<bean id="patientService" 
      class="org.openmrs.api.impl.PatientServiceImpl">
    <property name="dao" ref="patientDAO"/>
</bean>

<bean id="patientDAO" 
      class="org.openmrs.api.db.hibernate.HibernatePatientDAO">
    <property name="sessionFactory" ref="sessionFactory"/>
</bean>
```

### Runtime Properties

Core behavior is controlled through global properties:

```java
// Accessing runtime configuration
String property = Context.getAdministrationService()
    .getGlobalProperty("patient.identifierRegex");

boolean allowDuplicateNames = Context.getAdministrationService()
    .getGlobalPropertyValue("patient.allowDuplicateNames", false);
```

## Integration Patterns

### Transaction Management

Core components utilize Spring's declarative transaction management:

```java
@Transactional(readOnly = true)
public class ConceptServiceImpl implements ConceptService {
    
    @Transactional
    public Concept saveConcept(Concept concept) throws APIException {
        // Transactional operation
        return dao.saveConcept(concept);
    }
}
```

### Security Integration

Core components integrate with OpenMRS privilege-based security:

```java

## Subsections

- [API Framework](./API Framework.md)
- [Web Application Layer](./Web Application Layer.md)
- [Service Layer](./Service Layer.md)
- [Data Access Layer](./Data Access Layer.md)

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **API Framework**: Detailed coverage of api framework
- **Web Application Layer**: Detailed coverage of web application layer
- **Service Layer**: Detailed coverage of service layer
- **Data Access Layer**: Detailed coverage of data access layer

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:45:56*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*