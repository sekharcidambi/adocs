## Authorization Model

## Overview

The OpenMRS authorization model implements a comprehensive role-based access control (RBAC) system that governs user permissions throughout the medical record system. This security framework ensures that healthcare workers can only access and modify data appropriate to their roles while maintaining strict compliance with healthcare privacy regulations.

The authorization system is built around four core entities: **Users**, **Roles**, **Privileges**, and **Context** (location-based permissions). This hierarchical model allows for granular control over system functionality while maintaining flexibility for different healthcare environments.

## Core Authorization Components

### User Management
Users represent individual system accounts with authentication credentials and associated metadata. Each user can be assigned multiple roles, creating a flexible permission inheritance model:

```java
public class User extends BaseOpenmrsObject implements java.io.Serializable {
    private Set<Role> roles;
    private Person person;
    private String username;
    // Authentication and profile management
}
```

### Role-Based Access Control
Roles serve as permission containers that group related privileges together. The system includes several built-in roles:

- **System Developer**: Full system access including administrative functions
- **Provider**: Clinical data access and patient care functionality  
- **Data Manager**: Data entry and reporting capabilities
- **Anonymous**: Limited read-only access for public interfaces

```java
public class Role extends BaseOpenmrsObject {
    private String role;
    private String description;
    private Set<Privilege> privileges;
    private Set<Role> inheritedRoles;
}
```

### Privilege System
Privileges define atomic permissions for specific system operations. They follow a hierarchical naming convention using dot notation:

```java
// Core system privileges
public static final String PRIV_VIEW_PATIENTS = "View Patients";
public static final String PRIV_ADD_PATIENTS = "Add Patients";
public static final String PRIV_EDIT_PATIENTS = "Edit Patients";
public static final String PRIV_DELETE_PATIENTS = "Delete Patients";

// Administrative privileges
public static final String PRIV_MANAGE_USERS = "Manage Users";
public static final String PRIV_MANAGE_ROLES = "Manage Roles";
public static final String PRIV_MANAGE_PRIVILEGES = "Manage Privileges";
```

## Implementation Architecture

### Security Interceptors
The authorization model integrates with Spring Security through custom interceptors that evaluate permissions before method execution:

```java
@Component
public class AuthorizationAdvice implements MethodInterceptor {
    
    public Object invoke(MethodInvocation invocation) throws Throwable {
        Method method = invocation.getMethod();
        Authorized authorized = method.getAnnotation(Authorized.class);
        
        if (authorized != null) {
            Context.requirePrivilege(authorized.value());
        }
        
        return invocation.proceed();
    }
}
```

### Annotation-Based Security
Service methods use the `@Authorized` annotation to declare required privileges:

```java
@Service
public class PatientServiceImpl implements PatientService {
    
    @Authorized(PrivilegeConstants.GET_PATIENTS)
    public Patient getPatient(Integer patientId) {
        return dao.getPatient(patientId);
    }
    
    @Authorized({PrivilegeConstants.ADD_PATIENTS, PrivilegeConstants.EDIT_PATIENTS})
    public Patient savePatient(Patient patient) {
        return dao.savePatient(patient);
    }
}
```

### Context-Aware Authorization
The `Context` class provides the runtime authorization framework, maintaining the current user session and evaluating permissions:

```java
public class Context {
    private static final ThreadLocal<UserContext> userContext = new ThreadLocal<>();
    
    public static boolean hasPrivilege(String privilege) {
        User user = getAuthenticatedUser();
        return user != null && user.hasPrivilege(privilege);
    }
    
    public static void requirePrivilege(String privilege) throws APIException {
        if (!hasPrivilege(privilege)) {
            throw new APIException("Privilege required: " + privilege);
        }
    }
}
```

## Location-Based Security

OpenMRS implements location-based access control for multi-site deployments. Users can be restricted to specific locations, limiting their access to patients and data within those boundaries:

```java
public class User extends BaseOpenmrsObject {
    // Location restrictions for user access
    private Set<Location> allowedLocations;
    
    public boolean hasAccessToLocation(Location location) {
        return allowedLocations == null || 
               allowedLocations.isEmpty() || 
               allowedLocations.contains(location);
    }
}
```

## Database Schema Integration

The authorization model persists through several database tables with foreign key relationships:

```sql
-- Core authorization tables
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    person_id INT,
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

CREATE TABLE role (
    role VARCHAR(50) PRIMARY KEY,
    description TEXT
);

CREATE TABLE privilege (
    privilege VARCHAR(50) PRIMARY KEY,
    description TEXT
);

CREATE TABLE user_role (
    user_id INT,
    role VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (role) REFERENCES role(role)
);
```

## Module Extension Points

The authorization system provides extension mechanisms for custom modules:

### Custom Privilege Registration
Modules can register new privileges during startup:

```java
@Component
public class MyModuleActivator implements ModuleActivator {
    
    public void started() {
        AdministrationService adminService = Context.getAdministrationService();
        
        // Register custom privileges
        adminService.savePrivilege(new Privilege("My Module: View Data"));
        adminService.savePrivilege(new Privilege("My Module: Edit Data"));
    }
}
```

### Role Inheritance
Complex permission structures use role inheritance to avoid privilege duplication:

```java
// Clinical roles inherit from base provider role
Role provider = Context.getUserService().getRole("Provider");
Role nurse = new Role("Nurse", "Nursing staff");
nurse.getInheritedRoles().add(provider);
```

## Best Practices and Security Considerations

### Principle of Least Privilege
Always assign the minimum privileges necessary for user functions. Use role inheritance to build complex permission sets from simpler base roles.

### Privilege Granularity
Design privileges at the appropriate level of granularity. Too broad privileges create security risks, while overly specific privileges become difficult to manage.

### Session Management
The authorization system integrates with HTTP session management to maintain security context across requests:

```java
// Proper session handling in web controllers
@RequestMapping("/patient")
public String viewPatient(@RequestParam Integer patientId, Model model) {
    Context.requirePrivilege(PrivilegeConstants.GET_PATIENTS);
    Patient patient = Context.getPatientService().getPatient(patientId);
    model.addAttribute("patient", patient);
    return "patientView";
}
```

This authorization model provides the security foundation for OpenMRS deployments worldwide, ensuring that sensitive medical data remains protected while enabling efficient healthcare delivery workflows.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:55:56*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*