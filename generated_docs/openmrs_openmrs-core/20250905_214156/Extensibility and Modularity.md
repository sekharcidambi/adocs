## Extensibility and Modularity

## Overview

OpenMRS Core is designed as a highly extensible and modular platform that enables healthcare organizations to customize and extend functionality without modifying the core codebase. The architecture follows a plugin-based approach where modules can be dynamically loaded, configured, and integrated to meet specific healthcare implementation requirements.

## Module Architecture

### Core Module System

The OpenMRS module system is built around the `Module` class and associated infrastructure that allows for runtime loading and management of extensions. Modules are packaged as `.omod` files (OpenMRS Module files) that contain:

```java
// Example module structure
public class MyHealthcareModule implements Module {
    @Override
    public void started() {
        // Module initialization logic
        ModuleFactory.getStartedModulesMap().put(getModuleId(), this);
    }
    
    @Override
    public void stopped() {
        // Cleanup logic when module is stopped
    }
}
```

### Module Configuration

Each module includes a `config.xml` file that defines metadata, dependencies, and extension points:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<module configVersion="1.2">
    <id>mymodule</id>
    <name>My Healthcare Module</name>
    <version>1.0.0</version>
    <package>org.openmrs.module.mymodule</package>
    <author>Healthcare Developer</author>
    <description>Custom healthcare functionality</description>
    
    <require_version>2.0.0</require_version>
    
    <extension>
        <point>org.openmrs.admin.list</point>
        <class>org.openmrs.module.mymodule.extension.AdminListExt</class>
    </extension>
</module>
```

## Extension Points

### Service Layer Extensions

OpenMRS Core provides numerous extension points through its service architecture. Custom modules can implement service interfaces or extend existing services:

```java
@Component
public class CustomPatientService extends BasePatientService {
    
    @Override
    public Patient savePatient(Patient patient) throws APIException {
        // Custom validation logic
        validateCustomBusinessRules(patient);
        
        // Call parent implementation
        return super.savePatient(patient);
    }
    
    private void validateCustomBusinessRules(Patient patient) {
        // Implementation-specific validation
    }
}
```

### Data Access Object (DAO) Extensions

The DAO layer can be extended to provide custom data access patterns:

```java
public interface CustomPatientDAO extends PatientDAO {
    List<Patient> findPatientsByCustomCriteria(String criteria);
}

@Repository
public class HibernateCustomPatientDAO extends HibernatePatientDAO 
    implements CustomPatientDAO {
    
    @Override
    public List<Patient> findPatientsByCustomCriteria(String criteria) {
        Query query = sessionFactory.getCurrentSession()
            .createQuery("from Patient p where p.customField = :criteria");
        query.setParameter("criteria", criteria);
        return query.list();
    }
}
```

## Web Layer Modularity

### Controller Extensions

Modules can contribute new web controllers and endpoints:

```java
@Controller
@RequestMapping("/module/mymodule")
public class MyModuleController {
    
    @Autowired
    private PatientService patientService;
    
    @RequestMapping(value = "/patients/custom", method = RequestMethod.GET)
    public String showCustomPatientView(ModelMap model) {
        model.addAttribute("patients", patientService.getAllPatients());
        return "/module/mymodule/customPatientView";
    }
}
```

### UI Framework Integration

OpenMRS Core supports UI framework extensions through fragment controllers and pages:

```java
public class PatientDashboardFragmentController {
    
    public void controller(FragmentModel model, 
                          @FragmentParam("patientId") Patient patient) {
        model.addAttribute("patient", patient);
        model.addAttribute("customData", getCustomPatientData(patient));
    }
    
    private Object getCustomPatientData(Patient patient) {
        // Custom data retrieval logic
        return customService.getPatientSpecificData(patient);
    }
}
```

## Database Schema Extensions

### Liquibase Integration

Modules can extend the database schema using Liquibase changesets:

```xml
<!-- liquibase.xml in module resources -->
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog">
    <changeSet id="mymodule-1.0.0-1" author="developer">
        <createTable tableName="mymodule_custom_data">
            <column name="id" type="int" autoIncrement="true">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="patient_id" type="int">
                <constraints nullable="false"/>
            </column>
            <column name="custom_field" type="varchar(255)"/>
            <column name="date_created" type="datetime">
                <constraints nullable="false"/>
            </column>
        </createTable>
        
        <addForeignKeyConstraint 
            baseTableName="mymodule_custom_data" 
            baseColumnNames="patient_id"
            referencedTableName="patient" 
            referencedColumnNames="patient_id"
            constraintName="mymodule_patient_fk"/>
    </changeSet>
</databaseChangeLog>
```

## Configuration Management

### Global Properties

Modules can define configurable properties through the global properties system:

```java
public class MyModuleConstants {
    public static final String GP_CUSTOM_SETTING = "mymodule.customSetting";
    public static final String GP_INTEGRATION_URL = "mymodule.integrationUrl";
}

// In module activator
public class MyModuleActivator extends ModuleActivator {
    
    @Override
    public void started() {
        AdministrationService adminService = Context.getAdministrationService();
        
        // Set default values for global properties
        setGlobalPropertyIfNotExists(GP_CUSTOM_SETTING, "defaultValue");
        setGlobalPropertyIfNotExists(GP_INTEGRATION_URL, "http://localhost:8080/api");
    }
}
```

## Event-Driven Architecture

### Application Events

OpenMRS Core supports event-driven modularity through application events:

```java
@Component
public class PatientEventListener {
    
    @EventListener
    public void handlePatientCreated(PatientCreatedEvent event) {
        Patient patient = event.getPatient();
        // Custom logic when patient is created
        performCustomPatientProcessing(patient);
    }
    
    @EventListener
    public void handlePatientUpdated(PatientUpdatedEvent event) {
        // Custom logic for patient updates
        auditPatientChanges(event.getPatient(), event.getChanges());
    }
}
```

## Best Practices

### Module Development Guidelines

1. **Dependency Management**: Always specify minimum required OpenMRS version and module dependencies
2. **Service Isolation**: Use dependency injection and avoid direct class instantiation
3. **Database Migrations**: Use Liquibase for all schema changes with proper rollback strategies
4. **Configuration Externalization**: Use global properties for configurable values
5. **Event Publishing**: Publish domain events for significant business operations to enable other modules to react

### Integration Patterns

```java
// Example of proper service integration
@Component
public class IntegratedHealthcareService {
    
    @Autowired
    private PatientService patientService;
    
    @Autowired
    private ConceptService conceptService;
    
    @Autowired
    @Qualifier("mymodule.CustomService")
    private CustomService customService;
    
    public void processPatientData(Integer patientId) {
        Patient patient = patientService.getPatient(patientId);
        List<Concept> relevantConcepts = conceptService.getConceptsByName("diagnosis");
        
        // Integrate with custom module functionality
        customService.processPatientConcepts(patient, relevantConcepts);
    }
}
```

This modular architecture enables healthcare implementations to extend OpenMRS Core functionality while maintaining upgrade compatibility an

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:50:53*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*