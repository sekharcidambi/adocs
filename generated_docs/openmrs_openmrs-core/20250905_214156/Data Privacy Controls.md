## Data Privacy Controls

## Overview

OpenMRS Core implements comprehensive data privacy controls to ensure compliance with healthcare data protection regulations such as HIPAA, GDPR, and other regional privacy laws. As a medical record system handling sensitive patient information, the platform provides multiple layers of privacy protection through configurable access controls, data anonymization capabilities, audit logging, and secure data handling mechanisms.

The privacy control framework is deeply integrated into the OpenMRS architecture, spanning across the service layer, data access objects (DAOs), and API endpoints to ensure consistent privacy enforcement throughout the application lifecycle.

## Core Privacy Components

### Patient Data Access Controls

OpenMRS implements role-based access control (RBAC) through the `UserService` and `PrivilegeService` components to restrict access to patient data based on user roles and privileges:

```java
// Example privilege check for patient data access
@Authorized(PrivilegeConstants.GET_PATIENTS)
public Patient getPatient(Integer patientId) throws APIException {
    return dao.getPatient(patientId);
}

// Location-based access control
@Authorized(PrivilegeConstants.GET_PATIENTS)
public List<Patient> getPatients(Location location) throws APIException {
    if (!Context.hasPrivilege(PrivilegeConstants.VIEW_PATIENT_COHORTS)) {
        // Filter patients based on user's assigned locations
        return filterPatientsByUserLocation(location);
    }
    return dao.getPatients(location);
}
```

### Data Anonymization Framework

The platform provides built-in data anonymization capabilities through the `PatientService` and custom anonymization utilities:

```java
// Patient data anonymization
public class PatientAnonymizer {
    
    public Patient anonymizePatient(Patient patient) {
        Patient anonymized = patient.copy();
        
        // Remove direct identifiers
        anonymized.getNames().clear();
        anonymized.getIdentifiers().clear();
        anonymized.getAddresses().clear();
        
        // Generalize quasi-identifiers
        anonymized.setBirthdate(generalizeDate(patient.getBirthdate()));
        anonymized.setGender(generalizeGender(patient.getGender()));
        
        return anonymized;
    }
    
    private Date generalizeDate(Date birthdate) {
        // Generalize to year only for patients over 89
        Calendar cal = Calendar.getInstance();
        cal.setTime(birthdate);
        if (getAge(birthdate) > 89) {
            cal.set(Calendar.MONTH, 0);
            cal.set(Calendar.DAY_OF_MONTH, 1);
        }
        return cal.getTime();
    }
}
```

### Audit Trail Implementation

OpenMRS maintains comprehensive audit logs through the `AuditLogService` to track all access and modifications to patient data:

```java
@Component
public class PatientAuditInterceptor implements Interceptor {
    
    @Override
    public boolean onLoad(Object entity, Serializable id, Object[] state, String[] propertyNames, Type[] types) {
        if (entity instanceof Patient) {
            auditLogService.createAuditLog(
                AuditLog.Action.VIEWED,
                entity.getClass().getSimpleName(),
                id.toString(),
                Context.getAuthenticatedUser()
            );
        }
        return true;
    }
}
```

## Configuration and Global Properties

Privacy controls are configured through OpenMRS global properties, allowing administrators to customize privacy behavior:

```properties
# Enable/disable patient data export restrictions
privacy.patient.export.enabled=true

# Minimum privilege level for patient data export
privacy.patient.export.required_privilege=Export Patient Data

# Data retention period (in days)
privacy.data.retention.period=2555

# Enable automatic data anonymization for research
privacy.research.auto_anonymize=true

# Audit log retention period
privacy.audit.retention.days=2555
```

## API Privacy Endpoints

The REST API includes specific endpoints for privacy-related operations:

```java
@RestController
@RequestMapping("/ws/rest/v1/privacy")
public class PrivacyController {
    
    @PostMapping("/anonymize/patient/{uuid}")
    @Authorized(PrivilegeConstants.ANONYMIZE_PATIENTS)
    public ResponseEntity<Patient> anonymizePatient(@PathVariable String uuid) {
        Patient patient = patientService.getPatientByUuid(uuid);
        Patient anonymized = privacyService.anonymizePatient(patient);
        return ResponseEntity.ok(anonymized);
    }
    
    @GetMapping("/audit/patient/{uuid}")
    @Authorized(PrivilegeConstants.VIEW_AUDIT_LOGS)
    public ResponseEntity<List<AuditLog>> getPatientAuditTrail(@PathVariable String uuid) {
        List<AuditLog> auditTrail = auditLogService.getAuditLogsByPatient(uuid);
        return ResponseEntity.ok(auditTrail);
    }
    
    @PostMapping("/consent/patient/{uuid}")
    @Authorized(PrivilegeConstants.MANAGE_PATIENT_CONSENT)
    public ResponseEntity<ConsentForm> recordConsent(
            @PathVariable String uuid, 
            @RequestBody ConsentForm consent) {
        ConsentForm recorded = consentService.recordConsent(uuid, consent);
        return ResponseEntity.ok(recorded);
    }
}
```

## Database Privacy Patterns

### Encrypted Storage

Sensitive patient data fields utilize database-level encryption through custom Hibernate user types:

```java
@Entity
@Table(name = "patient")
public class Patient extends BaseOpenmrsData {
    
    @Column(name = "ssn")
    @Type(type = "org.openmrs.util.EncryptedStringType")
    private String socialSecurityNumber;
    
    @Column(name = "phone")
    @Type(type = "org.openmrs.util.EncryptedStringType")
    private String phoneNumber;
}
```

### Soft Delete Implementation

OpenMRS implements soft deletes to maintain audit trails while allowing data to be logically removed:

```java
@Entity
@SQLDelete(sql = "UPDATE patient SET voided = true, date_voided = NOW(), voided_by = ? WHERE patient_id = ?")
@Where(clause = "voided = false")
public class Patient extends BaseOpenmrsData implements Voidable {
    // Patient implementation with soft delete support
}
```

## Integration with External Systems

### HL7 Privacy Segments

When integrating with external systems via HL7, OpenMRS respects privacy indicators:

```java
public class HL7PrivacyHandler {
    
    public void processPrivacySegment(PID pid, Patient patient) {
        // Process PID-12 (Patient Death Indicator)
        if (pid.getPatientDeathIndicator().getValue() != null) {
            patient.setDead(Boolean.parseBoolean(pid.getPatientDeathIndicator().getValue()));
        }
        
        // Handle restricted access indicators
        if (hasRestrictedAccess(pid)) {
            patient.addAttribute(createRestrictedAccessAttribute());
        }
    }
}
```

## Best Practices and Compliance

### GDPR Compliance Features

- **Right to Access**: API endpoints provide structured patient data export
- **Right to Rectification**: Audit trails track all data modifications
- **Right to Erasure**: Soft delete with configurable hard delete policies
- **Data Portability**: Standardized export formats (JSON, XML, HL7)
- **Privacy by Design**: Default restrictive permissions with explicit privilege grants

### Implementation Guidelines

1. **Principle of Least Privilege**: Grant minimum necessary permissions for user roles
2. **Data Minimization**: Collect and retain only necessary patient information
3. **Purpose Limitation**: Restrict data usage to stated medical purposes
4. **Consent Management**: Implement explicit consent tracking for data processing
5. **Regular Audits**: Schedule periodic reviews of access logs and privilege assignments

The privacy control framework in OpenMRS Core provides a robust foundation for healthcare organizations to maintain compliance while delivering effective patient care through secure, auditable, and privacy-preserving data management practices.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:56:31*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*