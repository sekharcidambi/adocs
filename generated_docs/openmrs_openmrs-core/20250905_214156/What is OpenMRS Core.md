# What is OpenMRS Core?

## Overview

OpenMRS Core is the foundational Java-based platform that powers the OpenMRS (Open Medical Record System) electronic health record system. As a comprehensive healthcare informatics framework, OpenMRS Core provides the essential APIs, data models, services, and infrastructure components that enable healthcare organizations worldwide to build, customize, and deploy robust medical record systems tailored to their specific needs.

This repository contains the heart of the OpenMRS ecosystem - a modular, extensible platform designed to handle complex healthcare workflows, patient data management, clinical decision support, and interoperability requirements across diverse healthcare settings, from small clinics in resource-limited environments to large hospital networks.

## Core Architecture Components

### Data Model Foundation

OpenMRS Core implements a flexible, concept-driven data model that forms the backbone of all clinical data storage and retrieval:

```java
// Example of core domain objects
Patient patient = new Patient();
PersonName name = new PersonName("John", "Middle", "Doe");
patient.addName(name);

Encounter encounter = new Encounter();
encounter.setPatient(patient);
encounter.setEncounterType(encounterService.getEncounterType("ADULTINITIAL"));
```

The platform's data model centers around key entities:
- **Patient**: Core demographic and identifier information
- **Person**: Base class for all human entities in the system
- **Encounter**: Clinical interactions between patients and healthcare providers
- **Observation**: Clinical findings, lab results, and other measurable data points
- **Concept**: Standardized medical terminology and coded values

### Service Layer Architecture

OpenMRS Core employs a service-oriented architecture with clearly defined service interfaces that abstract business logic from data access:

```java
@Autowired
private PatientService patientService;

@Autowired
private ConceptService conceptService;

@Autowired
private EncounterService encounterService;

// Service methods provide transactional, secure access to domain objects
List<Patient> patients = patientService.getPatients("John", null, null, false);
Concept weightConcept = conceptService.getConceptByName("Weight");
```

Key service layers include:
- **PatientService**: Patient registration, search, and demographic management
- **ConceptService**: Medical terminology and coded value management
- **EncounterService**: Clinical encounter workflow management
- **ObsService**: Clinical observation data handling
- **UserService**: Authentication, authorization, and user management

### Modular Extension Framework

The platform's module system enables extensibility without modifying core functionality:

```xml
<!-- Module configuration example -->
<module configVersion="1.2">
    <id>customreports</id>
    <name>Custom Reports Module</name>
    <version>2.1.0</version>
    <require_version>2.0.0</require_version>
    
    <activator>org.openmrs.module.customreports.CustomReportsActivator</activator>
    
    <require_modules>
        <require_module version="1.8.0">org.openmrs.module.reporting</require_module>
    </require_modules>
</module>
```

## Technology Stack Integration

### Spring Framework Integration

OpenMRS Core leverages Spring Framework extensively for dependency injection, transaction management, and aspect-oriented programming:

```java
@Component
@Transactional
public class CustomPatientService {
    
    @Autowired
    private PatientDAO patientDAO;
    
    @Transactional(readOnly = true)
    public List<Patient> findPatientsByCustomCriteria(String criteria) {
        return patientDAO.findByCriteria(criteria);
    }
}
```

### Hibernate ORM Configuration

The platform uses Hibernate for object-relational mapping, with sophisticated mapping configurations for complex medical data relationships:

```xml
<!-- Example Hibernate mapping for Patient entity -->
<hibernate-mapping package="org.openmrs">
    <class name="Patient" table="patient">
        <id name="patientId" type="int" column="patient_id">
            <generator class="native" />
        </id>
        
        <many-to-one name="creator" class="User" column="creator" not-null="true" />
        <property name="dateCreated" type="timestamp" column="date_created" not-null="true" />
        
        <set name="identifiers" lazy="true" inverse="true" cascade="all-delete-orphan">
            <key column="patient_id" />
            <one-to-many class="PatientIdentifier" />
        </set>
    </class>
</hibernate-mapping>
```

## API Design Patterns

### RESTful Web Services

OpenMRS Core provides comprehensive REST APIs following healthcare interoperability standards:

```java
@RestController
@RequestMapping("/rest/v1/patient")
public class PatientController {
    
    @GetMapping("/{uuid}")
    public ResponseEntity<PatientResource> getPatient(@PathVariable String uuid) {
        Patient patient = patientService.getPatientByUuid(uuid);
        return ResponseEntity.ok(new PatientResource(patient));
    }
    
    @PostMapping
    public ResponseEntity<PatientResource> createPatient(@RequestBody PatientResource resource) {
        Patient patient = resource.toPatient();
        Patient savedPatient = patientService.savePatient(patient);
        return ResponseEntity.created(URI.create("/rest/v1/patient/" + savedPatient.getUuid()))
                           .body(new PatientResource(savedPatient));
    }
}
```

### Event-Driven Architecture

The platform implements an event system for loose coupling between components:

```java
// Event publishing
@Component
public class PatientEventPublisher {
    
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    public void publishPatientCreated(Patient patient) {
        PatientCreatedEvent event = new PatientCreatedEvent(this, patient);
        eventPublisher.publishEvent(event);
    }
}

// Event handling
@EventListener
public void handlePatientCreated(PatientCreatedEvent event) {
    Patient patient = event.getPatient();
    // Perform additional processing
    auditService.logPatientCreation(patient);
}
```

## Security and Authentication Framework

OpenMRS Core implements a role-based access control system with fine-grained permissions:

```java
@PreAuthorize("hasRole('ROLE_VIEW_PATIENTS')")
public List<Patient> getAllPatients() {
    return patientService.getAllPatients();
}

@PreAuthorize("hasRole('ROLE_EDIT_PATIENTS') and hasPrivilege('Edit Patients')")
public Patient updatePatient(Patient patient) {
    return patientService.savePatient(patient);
}
```

## Integration and Interoperability

### HL7 FHIR Support

The platform provides FHIR resource mapping for healthcare interoperability:

```java
// FHIR Patient resource mapping
public class PatientFHIRMapper {
    
    public org.hl7.fhir.r4.model.Patient toFHIRPatient(Patient openMRSPatient) {
        org.hl7.fhir.r4.model.Patient fhirPatient = new org.hl7.fhir.r4.model.Patient();
        
        // Map identifiers
        for (PatientIdentifier identifier : openMRSPatient.getIdentifiers()) {
            Identifier fhirIdentifier = new Identifier();
            fhirIdentifier.setValue(identifier.getIdentifier());
            fhirIdentifier.setSystem(identifier.getIdentifierType().getName());
            fhirPatient.addIdentifier(fhirIdentifier);
        }
        
        return fhirPatient;
    }
}
```

### Database Abstraction Layer

OpenMRS Core supports multiple database backends through its abstraction layer:

```properties
# MySQL configuration
connection.driver_class=com.mysql.cj.jdbc.Driver
connection.url=jdbc:mysql://localhost:3306/openmrs
connection.username=openmrs
connection.password=openmrs

# PostgreSQL configuration  
connection.driver_class=org.postgresql.Driver
connection.url=jdbc:postgresql://localhost:5432/openmrs
connection.username=openmrs
connection.password=openmrs
```

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:42:38*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*