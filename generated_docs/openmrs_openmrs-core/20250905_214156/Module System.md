## Module System

## Overview

The OpenMRS Module System is a sophisticated plugin architecture that enables dynamic extension of the core OpenMRS platform without requiring modifications to the base codebase. This modular approach allows developers to create, distribute, and install custom functionality as self-contained modules, supporting the platform's flexibility across diverse healthcare implementations worldwide.

The module system operates on a hot-swappable architecture, allowing modules to be loaded, started, stopped, and unloaded at runtime without requiring system restarts. This capability is crucial for production healthcare environments where downtime must be minimized.

## Core Architecture Components

### Module Structure

Each OpenMRS module follows a standardized structure defined by the `org.openmrs.module.Module` class:

```java
public class Module {
    private String moduleId;
    private String name;
    private String version;
    private String packageName;
    private String author;
    private String description;
    private String activatorName;
    private List<String> requiredModules;
    private String requiredOpenmrsVersion;
    // Additional metadata and configuration
}
```

### Module Activator Pattern

Every module implements the `ModuleActivator` interface, providing lifecycle hooks:

```java
public interface ModuleActivator {
    public void willRefreshContext();
    public void contextRefreshed();
    public void willStart();
    public void started();
    public void willStop();
    public void stopped();
}
```

This pattern ensures proper initialization and cleanup of module resources, database connections, and Spring context integration.

### Configuration Management

Modules are configured through the `config.xml` file located in the module's metadata directory:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<module configVersion="1.2">
    <id>basicmodule</id>
    <name>Basic Module</name>
    <version>1.0.0</version>
    <package>org.openmrs.module.basicmodule</package>
    <author>OpenMRS Community</author>
    <description>A basic module template</description>
    <activator>org.openmrs.module.basicmodule.BasicModuleActivator</activator>
    
    <require_version>2.0.0</require_version>
    <require_modules>
        <require_module version="1.2.0">org.openmrs.module.uiframework</require_module>
    </require_modules>
</module>
```

## Module Loading and Management

### ModuleFactory and ModuleClassLoader

The `ModuleFactory` class serves as the primary entry point for module operations:

```java
public class ModuleFactory {
    public static Module loadModule(File moduleFile) throws ModuleException;
    public static void startModule(Module module) throws ModuleException;
    public static void stopModule(Module module, boolean skipRefresh);
    public static void unloadModule(Module module);
}
```

Each module utilizes a custom `ModuleClassLoader` that provides:
- **Isolation**: Prevents class conflicts between modules
- **Dependency Resolution**: Manages inter-module dependencies
- **Resource Access**: Controlled access to module resources and libraries

### Dependency Resolution

The module system implements sophisticated dependency management through the `ModuleUtil` class:

```java
public class ModuleUtil {
    public static List<Module> getModulesInStartupOrder(Collection<Module> modules);
    public static void checkRequiredModules(Module module) throws ModuleException;
    public static void checkOpenmrsVersion(Module module) throws ModuleException;
}
```

Dependencies are resolved using topological sorting to ensure modules start in the correct order, preventing runtime errors from missing dependencies.

## Database Integration

### Liquibase Integration

Modules seamlessly integrate with OpenMRS's database versioning system through Liquibase changesets:

```xml
<!-- Module's liquibase.xml -->
<databaseChangeLog>
    <changeSet id="basicmodule-1.0.0-1" author="developer">
        <createTable tableName="basicmodule_patient_data">
            <column name="id" type="int" autoIncrement="true">
                <constraints primaryKey="true" nullable="false"/>
            </column>
            <column name="patient_id" type="int">
                <constraints nullable="false"/>
            </column>
            <column name="data_value" type="varchar(255)"/>
        </createTable>
    </changeSet>
</databaseChangeLog>
```

### Hibernate Mapping Files

Modules can extend the data model through Hibernate mapping files (`.hbm.xml`) that are automatically discovered and loaded:

```xml
<hibernate-mapping package="org.openmrs.module.basicmodule">
    <class name="PatientData" table="basicmodule_patient_data">
        <id name="id" type="int" column="id">
            <generator class="native"/>
        </id>
        <property name="patientId" type="int" column="patient_id"/>
        <property name="dataValue" type="string" column="data_value"/>
    </class>
</hibernate-mapping>
```

## Spring Framework Integration

### Context Configuration

Modules integrate with OpenMRS's Spring application context through `moduleApplicationContext.xml`:

```xml
<beans xmlns="http://www.springframework.org/schema/beans">
    <bean id="basicModuleService" 
          class="org.openmrs.module.basicmodule.api.impl.BasicModuleServiceImpl">
        <property name="dao" ref="basicModuleDAO"/>
    </bean>
    
    <bean id="basicModuleDAO" 
          class="org.openmrs.module.basicmodule.api.db.hibernate.HibernateBasicModuleDAO">
        <property name="sessionFactory" ref="sessionFactory"/>
    </bean>
</beans>
```

### Service Layer Pattern

Modules follow OpenMRS's service layer architecture pattern:

```java
@Transactional
public interface BasicModuleService extends OpenmrsService {
    public PatientData savePatientData(PatientData data);
    public List<PatientData> getPatientDataByPatient(Patient patient);
    public void deletePatientData(PatientData data);
}
```

## Security and Permissions

### Privilege System Integration

Modules integrate with OpenMRS's privilege-based security system:

```xml
<!-- In config.xml -->
<privilege>
    <name>Manage Basic Module Data</name>
    <description>Allows user to manage basic module patient data</description>
</privilege>

<globalProperty>
    <property>basicmodule.defaultBehavior</property>
    <defaultValue>conservative</defaultValue>
    <description>Default behavior for basic module operations</description>
</globalProperty>
```

## Web Layer Integration

### Controller Registration

Modules can contribute web controllers that are automatically registered:

```java
@Controller
@RequestMapping("/module/basicmodule")
public class BasicModuleController {
    
    @Autowired
    private BasicModuleService service;
    
    @RequestMapping(value = "/patientData", method = RequestMethod.GET)
    public String showPatientData(Model model, @RequestParam("patientId") Integer patientId) {
        // Controller logic
        return "/module/basicmodule/patientData";
    }
}
```

### Resource Management

Static resources (CSS, JavaScript, images) are served through the module's web directory structure and automatically mapped to `/moduleResources/{moduleId}/` URLs.

## Best Practices and Patterns

### Version Compatibility

- Always specify minimum OpenMRS version requirements
- Use semantic versioning for module releases
- Implement backward compatibility checks in module activators

### Resource Management

- Properly clean up resources in the `stopped()` method
- Use dependency injection rather than static references
- Implement proper exception handling in lifecycle methods

### Database Considerations

- Use module-specific table prefixes to avoid conflicts
- Implement proper foreign key relationships to core tables
- Include rollback strategies in Liquibase changesets

The OpenMRS Module System represents a mature, production-ready plugin architecture that balances flexibility with stability, enabling the platform to serve diverse healthcare contexts while maintaining a consistent core foundation.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:53:09*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*