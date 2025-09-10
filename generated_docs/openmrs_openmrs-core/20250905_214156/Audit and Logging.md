## Audit and Logging

## Overview

OpenMRS Core implements a comprehensive audit and logging framework designed to track system activities, user interactions, and data modifications within the healthcare information system. This framework is essential for maintaining regulatory compliance, debugging system issues, and ensuring data integrity in clinical environments where accountability and traceability are paramount.

The audit and logging system in OpenMRS Core operates on multiple levels, capturing both technical system events and clinical data changes through a combination of built-in logging mechanisms and custom audit trails.

## Core Logging Architecture

### Log4j Integration

OpenMRS Core utilizes Apache Log4j as its primary logging framework, configured through the `log4j2.xml` configuration file located in the application's runtime directory. The logging system supports multiple appenders and log levels:

```xml
<Configuration status="WARN">
    <Appenders>
        <File name="OPENMRS_FILE" fileName="${openmrs.application.data.directory}/openmrs.log">
            <PatternLayout pattern="%d{ISO8601} %-5p [%c{1}] %m%n"/>
        </File>
        <Console name="CONSOLE" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
        </Console>
    </Appenders>
    <Loggers>
        <Logger name="org.openmrs" level="INFO"/>
        <Logger name="org.hibernate.SQL" level="DEBUG"/>
        <Root level="WARN">
            <AppenderRef ref="OPENMRS_FILE"/>
            <AppenderRef ref="CONSOLE"/>
        </Root>
    </Loggers>
</Configuration>
```

### Logging Categories

The system categorizes logs into several key areas:

- **Application Logs**: General application behavior and system events
- **Security Logs**: Authentication, authorization, and security-related events
- **Database Logs**: SQL queries and database interactions via Hibernate
- **API Logs**: REST API calls and web service interactions
- **Module Logs**: Third-party module activities and custom extensions

## Audit Trail Implementation

### Database Audit Tables

OpenMRS Core maintains dedicated audit tables that mirror core data tables with additional metadata:

```sql
-- Example audit table structure
CREATE TABLE patient_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    operation_type VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    changed_by INT NOT NULL,
    date_changed DATETIME NOT NULL,
    old_values TEXT,
    new_values TEXT,
    change_reason VARCHAR(255)
);
```

### AOP-Based Auditing

The system employs Aspect-Oriented Programming (AOP) through Spring AOP to intercept service method calls and automatically generate audit entries:

```java
@Component
@Aspect
public class AuditAspect {
    
    @Autowired
    private AuditService auditService;
    
    @AfterReturning(pointcut = "@annotation(auditable)", returning = "result")
    public void auditServiceMethod(JoinPoint joinPoint, Auditable auditable, Object result) {
        String methodName = joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();
        
        AuditLog auditLog = new AuditLog();
        auditLog.setAction(methodName);
        auditLog.setObjectType(auditable.value());
        auditLog.setTimestamp(new Date());
        auditLog.setUserId(Context.getAuthenticatedUser().getId());
        
        auditService.saveAuditLog(auditLog);
    }
}
```

### Custom Audit Annotations

OpenMRS Core provides custom annotations for fine-grained audit control:

```java
@Service
@Transactional
public class PatientServiceImpl implements PatientService {
    
    @Auditable(type = "PATIENT", action = "CREATE")
    public Patient savePatient(Patient patient) throws APIException {
        // Patient creation logic
        return dao.savePatient(patient);
    }
    
    @Auditable(type = "PATIENT", action = "UPDATE", 
               includeVoided = true, sensitiveData = true)
    public Patient updatePatient(Patient patient) throws APIException {
        // Patient update logic with sensitive data tracking
        return dao.savePatient(patient);
    }
}
```

## Event-Driven Logging

### Application Events

The system publishes and listens to application events for comprehensive activity tracking:

```java
@Component
public class PatientEventListener {
    
    private static final Log log = LogFactory.getLog(PatientEventListener.class);
    
    @EventListener
    public void handlePatientCreated(PatientCreatedEvent event) {
        Patient patient = event.getPatient();
        log.info("Patient created: ID={}, UUID={}, Creator={}", 
                patient.getId(), patient.getUuid(), 
                event.getUser().getUsername());
        
        // Additional audit logic
        auditPatientActivity(patient, "CREATED", event.getUser());
    }
    
    @EventListener
    public void handlePatientUpdated(PatientUpdatedEvent event) {
        logPatientChanges(event.getOldPatient(), event.getNewPatient(), 
                         event.getUser());
    }
}
```

### Custom Event Publishing

Services can publish custom events for specialized audit requirements:

```java
@Service
public class EncounterService {
    
    @Autowired
    private ApplicationEventPublisher eventPublisher;
    
    public Encounter saveEncounter(Encounter encounter) {
        Encounter savedEncounter = encounterDAO.saveEncounter(encounter);
        
        // Publish audit event
        EncounterAuditEvent auditEvent = new EncounterAuditEvent(
            savedEncounter, Context.getAuthenticatedUser(), "ENCOUNTER_SAVED"
        );
        eventPublisher.publishEvent(auditEvent);
        
        return savedEncounter;
    }
}
```

## Security and Compliance Logging

### Authentication Audit

The system maintains detailed logs of authentication events:

```java
public class AuthenticationLogger {
    
    private static final Log securityLog = LogFactory.getLog("SECURITY");
    
    public void logSuccessfulLogin(User user, String sessionId, String ipAddress) {
        securityLog.info("LOGIN_SUCCESS: User={}, Session={}, IP={}, Timestamp={}", 
                        user.getUsername(), sessionId, ipAddress, new Date());
    }
    
    public void logFailedLogin(String username, String reason, String ipAddress) {
        securityLog.warn("LOGIN_FAILED: Username={}, Reason={}, IP={}, Timestamp={}", 
                        username, reason, ipAddress, new Date());
    }
    
    public void logPrivilegeEscalation(User user, String privilege, String resource) {
        securityLog.warn("PRIVILEGE_CHECK: User={}, Privilege={}, Resource={}, Result=DENIED", 
                        user.getUsername(), privilege, resource);
    }
}
```

### Data Access Logging

Critical data access operations are logged with contextual information:

```java
@Aspect
@Component
public class DataAccessAudit {
    
    @Around("execution(* org.openmrs.api.PatientService.getPatients(..))")
    public Object auditPatientQuery(ProceedingJoinPoint joinPoint) throws Throwable {
        User currentUser = Context.getAuthenticatedUser();
        String searchCriteria = Arrays.toString(joinPoint.getArgs());
        
        log.info("PATIENT_SEARCH: User={}, Criteria={}, Timestamp={}", 
                currentUser.getUsername(), searchCriteria, new Date());
        
        Object result = joinPoint.proceed();
        
        if (result instanceof List) {
            log.info("PATIENT_SEARCH_RESULT: User={}, ResultCount={}", 
                    currentUser.getUsername(), ((List<?>) result).size());
        }
        
        return result;
    }
}
```

## Configuration and Management

### Runtime Log Level Management

OpenMRS Core provides administrative interfaces

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:57:02*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*