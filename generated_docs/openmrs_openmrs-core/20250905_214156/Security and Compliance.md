# Security and Compliance

## Overview

OpenMRS Core implements a comprehensive security framework designed to protect patient health information and ensure compliance with healthcare regulations such as HIPAA, GDPR, and other regional privacy laws. The security architecture is built around role-based access control (RBAC), secure authentication mechanisms, and extensive audit logging capabilities that are essential for healthcare information systems.

## Authentication Framework

### User Authentication

OpenMRS Core provides a flexible authentication system that supports multiple authentication mechanisms:

```java
// Example of custom authentication implementation
public class CustomAuthenticationScheme implements AuthenticationScheme {
    @Override
    public Authenticated authenticate(AuthenticationCredentials credentials) {
        // Custom authentication logic
        return new Authenticated(user, authenticationScheme, credentialsType);
    }
}
```

The core authentication components include:

- **Password-based authentication** with configurable complexity requirements
- **LDAP integration** for enterprise directory services
- **Two-factor authentication (2FA)** support through extensible modules
- **Session management** with configurable timeout policies
- **Account lockout mechanisms** to prevent brute force attacks

### Security Configuration

Key security configurations are managed through global properties:

```properties
# Password security settings
security.passwordMinimumLength=8
security.passwordRequiresUpperAndLowerCase=true
security.passwordRequiresDigit=true
security.passwordCannotMatchUsername=true

# Session security
security.sessionTimeout=3600
security.forcePasswordChange=false
security.passwordExpirationDays=90
```

## Role-Based Access Control (RBAC)

### Privilege System

OpenMRS implements a granular privilege system where every system action requires specific privileges:

```java
// Example privilege check in service layer
@Authorized({"View Patients", "View Patient Identifiers"})
public Patient getPatient(Integer patientId) {
    return dao.getPatient(patientId);
}
```

Core privilege categories include:

- **Patient Management**: View Patients, Edit Patients, Delete Patients
- **Clinical Data**: View Observations, Edit Observations, View Encounters
- **Administrative**: Manage Users, Manage Roles, System Administration
- **Reporting**: View Reports, Run Reports, Manage Report Definitions

### Role Hierarchy

The system supports hierarchical role structures:

```sql
-- Example role hierarchy in database
INSERT INTO role (role, description) VALUES 
('System Developer', 'Full system access for development'),
('Data Manager', 'Manages patient data and clinical information'),
('Clinician', 'Provides patient care and enters clinical data'),
('Registration Clerk', 'Registers patients and manages demographics');
```

## Data Protection and Encryption

### Database Security

OpenMRS Core implements multiple layers of database security:

- **Connection encryption** using SSL/TLS for database connections
- **Sensitive data hashing** for passwords using BCrypt
- **Audit trail protection** with immutable log entries
- **Database user segregation** with minimal required privileges

```xml
<!-- Database connection security configuration -->
<property name="hibernate.connection.url">
    jdbc:mysql://localhost:3306/openmrs?useSSL=true&amp;requireSSL=true
</property>
<property name="hibernate.connection.useUnicode">true</property>
<property name="hibernate.connection.characterEncoding">UTF-8</property>
```

### Patient Data Anonymization

The system provides built-in capabilities for data anonymization:

```java
// Example of patient data anonymization
public class PatientDataAnonymizer {
    public void anonymizePatient(Patient patient) {
        patient.getPersonName().setGivenName(generateAnonymousName());
        patient.getPersonName().setFamilyName(generateAnonymousName());
        // Remove or hash sensitive identifiers
        patient.getPatientIdentifiers().clear();
    }
}
```

## Audit Logging and Compliance

### Comprehensive Audit Trail

OpenMRS maintains detailed audit logs for all system activities:

```java
// Audit logging implementation
@Component
public class AuditEventListener {
    
    @EventListener
    public void handlePatientAccess(PatientAccessEvent event) {
        AuditLog auditLog = new AuditLog();
        auditLog.setUser(event.getUser());
        auditLog.setAction("PATIENT_VIEWED");
        auditLog.setPatientId(event.getPatient().getId());
        auditLog.setTimestamp(new Date());
        auditLog.setIpAddress(event.getIpAddress());
        
        auditService.saveAuditLog(auditLog);
    }
}
```

### Compliance Reporting

The audit system supports compliance reporting requirements:

- **User access reports** showing who accessed what patient data
- **Data modification tracking** with before/after values
- **Login/logout tracking** with session duration
- **Failed access attempt logging** for security monitoring
- **Data export/import auditing** for data governance

## API Security

### REST API Protection

The REST API implements OAuth2 and basic authentication:

```java
// REST endpoint security annotation
@RestController
@RequestMapping("/ws/rest/v1/patient")
public class PatientRestController {
    
    @GetMapping("/{uuid}")
    @PreAuthorize("hasRole('ROLE_VIEW_PATIENTS')")
    public Patient getPatient(@PathVariable String uuid) {
        return patientService.getPatientByUuid(uuid);
    }
}
```

### Rate Limiting and Throttling

API endpoints implement rate limiting to prevent abuse:

```properties
# API rate limiting configuration
api.rateLimit.enabled=true
api.rateLimit.requestsPerMinute=100
api.rateLimit.burstCapacity=200
```

## Security Best Practices

### Input Validation and Sanitization

All user inputs undergo strict validation:

```java
// Example input validation
@Valid
public class PatientForm {
    @NotBlank(message = "Given name is required")
    @Size(max = 50, message = "Given name must not exceed 50 characters")
    @Pattern(regexp = "^[a-zA-Z\\s'-]+$", message = "Invalid characters in name")
    private String givenName;
}
```

### Cross-Site Scripting (XSS) Prevention

The system implements multiple XSS prevention mechanisms:

- **Output encoding** for all user-generated content
- **Content Security Policy (CSP)** headers
- **Input sanitization** using OWASP Java Encoder
- **Template auto-escaping** in view layers

### SQL Injection Prevention

All database queries use parameterized statements:

```java
// Safe database query example
public List<Patient> findPatientsByName(String name) {
    String hql = "FROM Patient p WHERE p.personName.givenName = :name";
    Query query = sessionFactory.getCurrentSession().createQuery(hql);
    query.setParameter("name", name);
    return query.list();
}
```

## Vulnerability Management

### Security Updates

The project maintains a security-focused update process:

- **Dependency scanning** using tools like OWASP Dependency Check
- **Regular security patches** for third-party libraries
- **Security advisory notifications** through GitHub Security Advisories
- **Coordinated disclosure process** for security vulnerabilities

### Penetration Testing

Regular security assessments include:

- **Automated vulnerability scanning** in CI/CD pipelines
- **Static code analysis** for security anti-patterns
- **Dynamic application security testing (DAST)**
- **Third-party security audits** for major releases

## Integration Security

### Module Security Framework

OpenMRS modules inherit the core security framework:

```java
// Module security configuration
@Component
public class ModuleSecurityConfig {
    
    @PostConstruct
    public void configureModuleSecurity() {
        // Register module-specific privileges
        Context.getUserService().savePrivilege(
            new Privilege("Manage Custom Module", "Allows management of custom module features")
        );
    }
}
```

### External System Integration

Security considerations for external integrations:

- **API key management** for third-party services
- **Certificate-based authentication** for HL7 FHIR endpoints
- **Secure message queuing** for asynchronous processing
- **Network segmentation** recommendations for deployment

This comprehensive security framework ensures that OpenMRS Core meets the stringent requirements of healthcare environments while maintaining flexibility for various deployment

## Subsections

- [Authentication Framework](./Authentication Framework.md)
- [Authorization Model](./Authorization Model.md)
- [Data Privacy Controls](./Data Privacy Controls.md)
- [Audit and Logging](./Audit and Logging.md)

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **Authentication Framework**: Detailed coverage of authentication framework
- **Authorization Model**: Detailed coverage of authorization model
- **Data Privacy Controls**: Detailed coverage of data privacy controls
- **Audit and Logging**: Detailed coverage of audit and logging

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:54:56*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*