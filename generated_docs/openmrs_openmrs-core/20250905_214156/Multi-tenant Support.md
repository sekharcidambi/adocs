## Multi-tenant Support

## Overview

OpenMRS Core provides foundational multi-tenant architecture support that enables a single OpenMRS installation to serve multiple healthcare organizations or facilities while maintaining complete data isolation and customization capabilities. This multi-tenancy implementation is designed around the concept of "contexts" and database-level separation, allowing healthcare providers to share infrastructure costs while maintaining strict privacy and security boundaries.

The multi-tenant support in OpenMRS Core is built on a **database-per-tenant** model, where each tenant (healthcare facility, organization, or implementation) operates with its own dedicated database schema while sharing the same application codebase and server resources.

## Architecture Components

### Context Management

The multi-tenant architecture centers around the `Context` class and related components:

```java
// Core context switching for multi-tenant operations
Context.openSession();
Context.authenticate(username, password);
Context.getUserContext().setLocation(facility);
```

### Database Schema Isolation

Each tenant maintains complete database isolation through:

- **Separate Database Schemas**: Each tenant operates with its own MySQL/PostgreSQL database
- **Connection Pool Management**: Dynamic database connection routing based on tenant context
- **Schema Migration Independence**: Each tenant can maintain different OpenMRS versions and customizations

```properties
# Example tenant-specific database configuration
tenant.primary.database.url=jdbc:mysql://localhost:3306/openmrs_tenant1
tenant.secondary.database.url=jdbc:mysql://localhost:3306/openmrs_tenant2
```

### Tenant Resolution Strategy

OpenMRS Core implements tenant resolution through multiple strategies:

1. **Domain-based Resolution**: Different subdomains or domains route to specific tenants
2. **Header-based Resolution**: HTTP headers specify tenant context
3. **URL Path Resolution**: URL segments determine tenant routing

```java
// Custom tenant resolver implementation
public class OpenMRSTenantResolver implements TenantResolver {
    @Override
    public String resolveTenantIdentifier() {
        // Implementation-specific tenant resolution logic
        return extractTenantFromRequest();
    }
}
```

## Implementation Patterns

### Service Layer Multi-tenancy

OpenMRS services are designed to operate within tenant boundaries:

```java
// Patient service operating within tenant context
PatientService patientService = Context.getPatientService();
List<Patient> patients = patientService.getAllPatients(); // Tenant-scoped results
```

### Data Access Layer

The Hibernate-based data access layer automatically scopes queries to the current tenant's database:

```java
// DAO operations are automatically tenant-aware
@Repository
public class PatientDAOImpl implements PatientDAO {
    
    @Override
    public List<Patient> getPatients(String query) {
        // Queries execute against current tenant's database
        return sessionFactory.getCurrentSession()
            .createQuery("from Patient p where p.name like :query")
            .setParameter("query", "%" + query + "%")
            .list();
    }
}
```

### Module Multi-tenancy

OpenMRS modules inherit multi-tenant capabilities:

- **Module Installation**: Modules can be installed per-tenant or globally
- **Configuration Isolation**: Module configurations remain tenant-specific
- **Resource Separation**: Static resources and customizations are tenant-scoped

```xml
<!-- Module configuration with tenant awareness -->
<module configVersion="1.0">
    <id>reporting</id>
    <name>Reporting Module</name>
    <version>1.0.0</version>
    <require_version>2.0.0</require_version>
    <tenant-aware>true</tenant-aware>
</module>
```

## Configuration Management

### Global vs Tenant-Specific Settings

OpenMRS distinguishes between global system settings and tenant-specific configurations:

```properties
# Global application settings
application.global.timezone=UTC
application.global.locale=en

# Tenant-specific overrides
tenant.facility_a.timezone=America/New_York
tenant.facility_a.locale=en_US
tenant.facility_b.timezone=Europe/London
tenant.facility_b.locale=en_GB
```

### Runtime Configuration Switching

The platform supports dynamic configuration switching based on tenant context:

```java
// Configuration service with tenant awareness
@Service
public class ConfigurationService {
    
    public String getProperty(String key) {
        String tenantId = Context.getCurrentTenantId();
        return getPropertyForTenant(tenantId, key);
    }
}
```

## Security and Isolation

### Authentication and Authorization

Multi-tenant security ensures complete isolation between tenants:

- **User Isolation**: Users belong to specific tenants and cannot cross tenant boundaries
- **Role-Based Access**: Roles and privileges are tenant-scoped
- **Session Management**: User sessions are bound to specific tenant contexts

```java
// Tenant-aware authentication
public class OpenMRSAuthenticationProvider {
    
    public Authentication authenticate(Authentication auth, String tenantId) {
        // Authenticate user within specific tenant context
        Context.setCurrentTenant(tenantId);
        return performAuthentication(auth);
    }
}
```

### Data Privacy

The architecture ensures strict data privacy through:

- **Database-Level Isolation**: No shared tables between tenants
- **Query Scoping**: All database queries are automatically tenant-scoped
- **File System Separation**: Uploaded files and resources are tenant-isolated

## Deployment Strategies

### Single Application Instance

Deploy one OpenMRS instance serving multiple tenants:

```yaml
# Docker Compose example for multi-tenant deployment
version: '3.8'
services:
  openmrs:
    image: openmrs/openmrs-core:latest
    environment:
      - MULTI_TENANT_ENABLED=true
      - TENANT_RESOLVER_STRATEGY=domain
    volumes:
      - ./tenant-configs:/opt/openmrs/tenant-configs
```

### Load Balancer Configuration

Configure load balancing for tenant-aware routing:

```nginx
# Nginx configuration for tenant routing
upstream openmrs_backend {
    server openmrs:8080;
}

server {
    listen 80;
    server_name ~^(?<tenant>.+)\.openmrs\.example\.com$;
    
    location / {
        proxy_pass http://openmrs_backend;
        proxy_set_header X-Tenant-ID $tenant;
        proxy_set_header Host $host;
    }
}
```

## Best Practices

### Performance Optimization

- **Connection Pool Sizing**: Configure appropriate database connection pools per tenant
- **Caching Strategy**: Implement tenant-aware caching to prevent data leakage
- **Resource Monitoring**: Monitor per-tenant resource usage and performance metrics

### Maintenance Operations

- **Database Migrations**: Execute schema updates per tenant with rollback capabilities
- **Backup Strategies**: Implement tenant-specific backup and restore procedures
- **Monitoring**: Set up tenant-specific logging and monitoring dashboards

### Development Guidelines

- **Context Awareness**: Always ensure code operates within proper tenant context
- **Testing**: Write tests that validate multi-tenant isolation
- **Configuration**: Use tenant-aware configuration patterns throughout the application

The multi-tenant support in OpenMRS Core provides a robust foundation for healthcare organizations to share infrastructure while maintaining the security, privacy, and customization requirements essential in healthcare environments.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:51:26*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*