## Data Access Layer

## Overview

The Data Access Layer (DAL) in OpenMRS Core serves as the foundational abstraction layer that manages all interactions between the application logic and the underlying database. This layer implements a sophisticated repository pattern combined with Hibernate ORM to provide consistent, secure, and efficient data access across the entire OpenMRS platform. The DAL is designed to handle the complex medical data structures inherent in healthcare information systems while maintaining ACID compliance and supporting multi-tenant deployments.

## Architecture Components

### DAO Pattern Implementation

OpenMRS Core implements a comprehensive Data Access Object (DAO) pattern with interface-based contracts and Hibernate-backed implementations:

```java
// Base DAO interface
public interface OpenmrsObjectDAO<T extends OpenmrsObject> {
    T saveOrUpdate(T object);
    T getById(Integer id);
    void delete(T object);
    List<T> getAll(boolean includeRetired);
}

// Example implementation for Patient data access
@Repository
public class HibernatePatientDAO extends HibernateOpenmrsObjectDAO<Patient> 
    implements PatientDAO {
    
    @Override
    public List<Patient> getPatients(String query, List<PatientIdentifierType> identifierTypes, 
                                   boolean matchIdentifierExactly, Integer start, Integer length) {
        Criteria criteria = sessionFactory.getCurrentSession().createCriteria(Patient.class);
        // Complex query building logic for patient search
        return criteria.list();
    }
}
```

### Hibernate Integration

The DAL leverages Hibernate as the primary ORM framework, configured through Spring's session management:

```xml
<!-- hibernate.cfg.xml configuration -->
<hibernate-configuration>
    <session-factory>
        <property name="hibernate.dialect">org.hibernate.dialect.MySQLDialect</property>
        <property name="hibernate.connection.driver_class">com.mysql.cj.jdbc.Driver</property>
        <property name="hibernate.show_sql">false</property>
        <property name="hibernate.format_sql">true</property>
        <property name="hibernate.cache.use_second_level_cache">true</property>
        <property name="hibernate.cache.region.factory_class">
            org.hibernate.cache.ehcache.EhCacheRegionFactory
        </property>
    </session-factory>
</hibernate-configuration>
```

### Entity Mapping Strategy

OpenMRS employs a sophisticated entity mapping strategy that handles complex medical data relationships:

```java
@Entity
@Table(name = "encounter")
public class Encounter extends BaseOpenmrsData {
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "patient_id")
    private Patient patient;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "encounter_type")
    private EncounterType encounterType;
    
    @OneToMany(mappedBy = "encounter", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private Set<Obs> obs = new HashSet<>();
    
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(name = "encounter_provider",
               joinColumns = @JoinColumn(name = "encounter_id"),
               inverseJoinColumns = @JoinColumn(name = "provider_id"))
    private Set<Provider> encounterProviders;
}
```

## Core DAO Services

### Patient Data Access

The `PatientDAO` handles complex patient data operations including identifier management, demographic searches, and relationship mapping:

```java
public interface PatientDAO extends OpenmrsObjectDAO<Patient> {
    List<Patient> getPatients(String query, List<PatientIdentifierType> identifierTypes,
                            boolean matchIdentifierExactly, Integer start, Integer length);
    
    Patient getPatient(Integer patientId);
    
    List<Patient> getDuplicatePatientsByAttributes(List<String> attributes);
    
    boolean isIdentifierInUseByAnotherPatient(PatientIdentifier patientIdentifier);
}
```

### Concept Dictionary Access

The concept dictionary serves as OpenMRS's medical terminology backbone, with specialized DAO operations:

```java
@Repository
public class HibernateConceptDAO implements ConceptDAO {
    
    public List<ConceptSearchResult> getConcepts(String phrase, List<Locale> locales,
                                                boolean includeRetired, 
                                                List<ConceptClass> requireClasses,
                                                List<ConceptDatatype> excludeDatatypes) {
        
        Criteria criteria = sessionFactory.getCurrentSession()
            .createCriteria(ConceptName.class, "cn")
            .createAlias("cn.concept", "concept")
            .add(Restrictions.ilike("cn.name", phrase, MatchMode.ANYWHERE));
            
        // Apply locale-specific filtering
        if (locales != null && !locales.isEmpty()) {
            criteria.add(Restrictions.in("cn.locale", locales));
        }
        
        return criteria.list();
    }
}
```

## Transaction Management

### Declarative Transaction Boundaries

OpenMRS implements declarative transaction management through Spring's `@Transactional` annotations:

```java
@Service
@Transactional
public class PatientServiceImpl extends BaseOpenmrsService implements PatientService {
    
    @Transactional(readOnly = true)
    public Patient getPatient(Integer patientId) {
        return dao.getPatient(patientId);
    }
    
    @Transactional
    public Patient savePatient(Patient patient) throws PatientIdentifierException {
        // Validation logic
        if (patient.getPatientId() == null) {
            // New patient creation logic
        }
        return dao.savePatient(patient);
    }
}
```

### Connection Pool Management

The DAL utilizes HikariCP for efficient connection pooling:

```properties
# Database connection pool configuration
hibernate.hikari.connectionTimeout=20000
hibernate.hikari.minimumIdle=10
hibernate.hikari.maximumPoolSize=20
hibernate.hikari.idleTimeout=300000
hibernate.hikari.maxLifetime=1200000
hibernate.hikari.leakDetectionThreshold=60000
```

## Caching Strategy

### Second-Level Cache Implementation

OpenMRS implements a comprehensive caching strategy using Ehcache for frequently accessed medical reference data:

```java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE, region = "concept")
public class Concept extends BaseOpenmrsMetadata {
    
    @OneToMany(mappedBy = "concept", fetch = FetchType.LAZY)
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    private Collection<ConceptName> names;
    
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "datatype_id")
    private ConceptDatatype datatype;
}
```

### Query Result Caching

Critical queries are cached to improve performance in high-volume clinical environments:

```java
@Cacheable(value = "conceptSearchResults", key = "#phrase + #locales.hashCode()")
public List<ConceptSearchResult> getConceptsByName(String phrase, List<Locale> locales) {
    return hibernateConceptDAO.getConcepts(phrase, locales, false, null, null);
}
```

## Database Migration and Liquibase Integration

### Schema Evolution Management

OpenMRS uses Liquibase for database schema versioning and migration:

```xml
<!-- Example changeset for adding new clinical data structure -->
<changeSet id="add-allergy-severity-concept-20231201" author="openmrs">
    <preConditions onFail="MARK_RAN">
        <not>
            <tableExists tableName="allergy_reaction"/>
        </not>
    </preConditions>
    
    <createTable tableName="allergy_reaction">
        <column name="allergy_reaction_id" type="int" autoIncrement="true">
            <constraints primaryKey="true" nullable="false"/>
        </column>
        <column name="allergy_i

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:48:06*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*