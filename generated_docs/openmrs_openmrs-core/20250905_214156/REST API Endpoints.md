## REST API Endpoints

## Overview

OpenMRS Core provides a comprehensive RESTful API that serves as the primary interface for external applications, mobile clients, and third-party integrations to interact with the OpenMRS platform. The REST API endpoints are built using Spring MVC framework and follow RESTful conventions, enabling standardized access to clinical data, patient records, encounters, observations, and administrative functions.

The REST API is implemented through the `org.openmrs.module.webservices.rest` package structure and provides both read and write operations across all major OpenMRS domain objects. This API serves as the backbone for the OpenMRS Reference Application frontend and numerous community-developed modules.

## Architecture and Implementation

### Core REST Framework

The OpenMRS REST API is built on a modular architecture that leverages Spring's `@RestController` annotations and custom resource handlers. The framework implements a consistent pattern across all endpoints:

```java
@RestController
@RequestMapping("/rest/v1/patient")
public class PatientController extends BaseRestController {
    
    @RequestMapping(method = RequestMethod.GET)
    public SimpleObject getPatients(HttpServletRequest request) {
        // Implementation for retrieving patients
    }
    
    @RequestMapping(value = "/{uuid}", method = RequestMethod.GET)
    public Object getPatient(@PathVariable("uuid") String uuid) {
        // Implementation for retrieving specific patient
    }
}
```

### Resource Representation System

The API implements a sophisticated resource representation system that supports multiple levels of detail through the `v` (view) parameter:

- **ref**: Minimal representation with UUID and display name
- **default**: Standard representation with commonly used fields
- **full**: Complete representation including all relationships
- **custom**: User-defined field selection using dot notation

Example API calls demonstrating representation levels:

```bash
# Reference representation
GET /openmrs/ws/rest/v1/patient?v=ref

# Full representation with all patient data
GET /openmrs/ws/rest/v1/patient/{uuid}?v=full

# Custom representation with specific fields
GET /openmrs/ws/rest/v1/patient/{uuid}?v=custom:(uuid,display,person:(age,gender))
```

## Core Endpoint Categories

### Patient Management Endpoints

The patient endpoints provide comprehensive CRUD operations for patient records:

```bash
# Create new patient
POST /openmrs/ws/rest/v1/patient
Content-Type: application/json
{
  "person": {
    "names": [{"givenName": "John", "familyName": "Doe"}],
    "gender": "M",
    "birthdate": "1990-01-01"
  },
  "identifiers": [{
    "identifier": "12345",
    "identifierType": "05a29f94-c0ed-11e2-94be-8c13b969e334",
    "location": "8d6c993e-c2cc-11de-8d13-0010c6dffd0f"
  }]
}

# Search patients by name or identifier
GET /openmrs/ws/rest/v1/patient?q=John&v=custom:(uuid,display,identifiers)

# Update patient information
POST /openmrs/ws/rest/v1/patient/{uuid}
```

### Clinical Data Endpoints

#### Encounters and Observations

The encounter endpoints manage clinical visits and associated observations:

```bash
# Create encounter with observations
POST /openmrs/ws/rest/v1/encounter
{
  "patient": "patient-uuid",
  "encounterType": "encounter-type-uuid",
  "location": "location-uuid",
  "encounterDatetime": "2023-12-01T10:30:00.000+0000",
  "obs": [{
    "concept": "concept-uuid",
    "value": "120",
    "obsDatetime": "2023-12-01T10:30:00.000+0000"
  }]
}

# Retrieve patient encounters
GET /openmrs/ws/rest/v1/encounter?patient={uuid}&v=custom:(uuid,display,encounterDatetime,obs)
```

#### Concept Dictionary Access

The concept endpoints provide access to the OpenMRS concept dictionary:

```bash
# Search concepts by name
GET /openmrs/ws/rest/v1/concept?q=temperature&v=custom:(uuid,display,datatype,conceptClass)

# Get concept with answers (for coded concepts)
GET /openmrs/ws/rest/v1/concept/{uuid}?v=full
```

### Administrative Endpoints

#### User and Role Management

```bash
# Create new user
POST /openmrs/ws/rest/v1/user
{
  "username": "clinician1",
  "password": "TempPassword123",
  "person": {
    "names": [{"givenName": "Jane", "familyName": "Smith"}]
  },
  "roles": ["role-uuid"]
}

# Assign privileges to role
POST /openmrs/ws/rest/v1/role/{uuid}
{
  "privileges": ["privilege-uuid-1", "privilege-uuid-2"]
}
```

#### Location and Provider Management

```bash
# Create location hierarchy
POST /openmrs/ws/rest/v1/location
{
  "name": "Main Hospital",
  "description": "Primary care facility",
  "parentLocation": "parent-location-uuid"
}

# Register healthcare provider
POST /openmrs/ws/rest/v1/provider
{
  "person": "person-uuid",
  "identifier": "PROV001",
  "attributes": [{
    "attributeType": "attribute-type-uuid",
    "value": "Cardiology"
  }]
}
```

## Authentication and Security

The REST API implements session-based authentication with support for basic authentication and custom authentication schemes:

```bash
# Authenticate and establish session
GET /openmrs/ws/rest/v1/session
Authorization: Basic base64(username:password)

# Use session cookie for subsequent requests
GET /openmrs/ws/rest/v1/patient
Cookie: JSESSIONID=session-id
```

## Error Handling and Response Formats

The API implements standardized error responses with detailed error information:

```json
{
  "error": {
    "message": "The request is missing required parameters",
    "code": "webservices.rest.error.invalid.request",
    "detail": "Patient identifier is required"
  }
}
```

## Integration Patterns

### Module Extension Points

Custom modules can extend the REST API by implementing the `Resource` interface:

```java
@Resource(name = RestConstants.VERSION_1 + "/customresource", 
          supportedClass = CustomDomainObject.class, 
          supportedOpenmrsVersions = {"2.0.*", "2.1.*"})
public class CustomResource extends DataDelegatingCrudResource<CustomDomainObject> {
    // Custom resource implementation
}
```

### Bulk Operations and Batch Processing

The API supports batch operations for efficient data synchronization:

```bash
# Batch create multiple patients
POST /openmrs/ws/rest/v1/patient/batch
[
  {"person": {...}, "identifiers": [...]},
  {"person": {...}, "identifiers": [...]}
]
```

## Performance Considerations

The REST API implements several performance optimization strategies:

- **Lazy Loading**: Related objects are loaded on-demand based on representation level
- **Caching**: Frequently accessed metadata is cached using Spring's caching abstraction
- **Pagination**: Large result sets are automatically paginated with configurable page sizes
- **Field Selection**: Custom representations minimize data transfer

Example of optimized query with pagination:

```bash
GET /openmrs/ws/rest/v1/patient?startIndex=0&limit=50&v=custom:(uuid,display,identifiers:(identifier,identifierType:(display)))
```

This comprehensive REST API framework enables robust integration capabilities while maintaining the flexibility and extensibility that characterizes the OpenMRS platform architecture.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:52:37*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*