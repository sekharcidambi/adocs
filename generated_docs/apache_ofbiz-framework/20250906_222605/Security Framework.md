## Security Framework

## Overview

The Apache OFBiz Security Framework provides a comprehensive, multi-layered security architecture that protects the enterprise application platform through authentication, authorization, data encryption, and security policy enforcement. Built on Java EE security principles, the framework integrates deeply with OFBiz's service-oriented architecture to ensure secure access to business services, entities, and web resources across all application modules.

The security framework operates as a foundational layer that spans the entire OFBiz stack, from the entity engine data access layer through the service engine to the web presentation layer. It implements role-based access control (RBAC), supports multiple authentication mechanisms, and provides fine-grained permission controls that can be applied at the service, entity, and UI component levels.

## Core Security Components

### Authentication System

The authentication subsystem handles user identity verification through multiple configurable mechanisms:

```java
// Primary authentication interface
public interface Authenticator {
    boolean authenticate(String username, String password, boolean isServiceAuth) throws AuthenticatorException;
    void logout(HttpServletRequest request, HttpServletResponse response);
    boolean isUserLoggedIn(HttpServletRequest request);
}
```

**Supported Authentication Methods:**
- **Database Authentication**: Default mechanism using UserLogin entity with encrypted passwords
- **LDAP Integration**: Enterprise directory service authentication with configurable LDAP servers
- **Single Sign-On (SSO)**: Support for external authentication providers
- **Certificate-based Authentication**: X.509 client certificate validation

### Authorization and Permission Framework

The authorization system implements a hierarchical permission model with the following key entities:

```xml
<!-- Core security entities in security/entitydef/entitymodel.xml -->
<entity entity-name="UserLogin" package-name="org.apache.ofbiz.security.login">
    <field name="userLoginId" type="id-ne"/>
    <field name="currentPassword" type="short-varchar" encrypt="true"/>
    <field name="passwordHint" type="description"/>
    <field name="enabled" type="indicator"/>
    <field name="hasLoggedOut" type="indicator"/>
    <prim-key field="userLoginId"/>
</entity>

<entity entity-name="SecurityGroup" package-name="org.apache.ofbiz.security.securitygroup">
    <field name="groupId" type="id-ne"/>
    <field name="description" type="description"/>
    <prim-key field="groupId"/>
</entity>

<entity entity-name="SecurityPermission" package-name="org.apache.ofbiz.security.securitygroup">
    <field name="permissionId" type="id-ne"/>
    <field name="description" type="description"/>
    <prim-key field="permissionId"/>
</entity>
```

**Permission Hierarchy:**
- **Security Groups**: Logical groupings of users with similar access needs
- **Security Permissions**: Atomic permission units (e.g., ACCOUNTING_VIEW, CATALOG_ADMIN)
- **User-Group Associations**: Many-to-many relationships between users and groups
- **Group-Permission Mappings**: Assignment of specific permissions to security groups

### Service-Level Security

OFBiz implements security at the service definition level, allowing fine-grained control over business logic access:

```xml
<!-- Example service definition with security constraints -->
<service name="createProduct" engine="entity-auto" invoke="create" default-entity-name="Product">
    <description>Create a Product</description>
    <permission-service service-name="catalogPermissionCheck" main-action="CREATE"/>
    <auto-attributes include="pk" mode="INOUT" optional="true"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
</service>

<!-- Permission service implementation -->
<service name="catalogPermissionCheck" engine="simple" 
         location="component://product/script/org/apache/ofbiz/product/catalog/CatalogServices.xml" 
         invoke="catalogPermissionCheck">
    <description>Catalog Permission Checking Logic</description>
    <attribute name="mainAction" type="String" mode="IN" optional="true"/>
    <attribute name="primaryPermission" type="String" mode="IN" optional="true"/>
    <attribute name="altPermission" type="String" mode="IN" optional="true"/>
    <attribute name="resourceDescription" type="String" mode="IN" optional="true"/>
    <attribute name="hasPermission" type="Boolean" mode="OUT"/>
    <attribute name="failMessage" type="String" mode="OUT" optional="true"/>
</service>
```

### Web Security Integration

The framework integrates with Java servlet security through custom filters and interceptors:

```xml
<!-- web.xml security configuration -->
<filter>
    <filter-name>ContextFilter</filter-name>
    <filter-class>org.apache.ofbiz.webapp.control.ContextFilter</filter-class>
    <init-param>
        <param-name>security</param-name>
        <param-value>true</param-value>
    </init-param>
</filter>

<!-- Controller request mapping with security -->
<request-map uri="createProduct">
    <security https="true" auth="true"/>
    <event type="service" invoke="createProduct"/>
    <response name="success" type="view" value="ProductCreated"/>
    <response name="error" type="view" value="ProductForm"/>
</request-map>
```

## Data Protection and Encryption

### Entity Field Encryption

OFBiz provides transparent field-level encryption for sensitive data:

```xml
<!-- Entity definition with encrypted fields -->
<entity entity-name="CreditCard" package-name="org.apache.ofbiz.accounting.payment">
    <field name="cardNumber" type="credit-card-number" encrypt="true"/>
    <field name="cardSecurityCode" type="short-varchar" encrypt="true"/>
    <field name="expireDate" type="date-time"/>
</entity>
```

The encryption system uses configurable algorithms and key management:

```properties
# security.properties configuration
password.encrypt.hash.type=SHA
password.encrypt.pbkdf2.iterations=10000
entity.crypto.key.supplier=org.apache.ofbiz.entity.crypto.EntityCryptoKeySupplier
```

### Secure Communication

**HTTPS Configuration:**
- SSL/TLS termination at the application server level
- Configurable cipher suites and protocol versions
- Certificate management through standard Java keystore mechanisms

**API Security:**
- REST API authentication through token-based mechanisms
- SOAP web service security headers
- Rate limiting and request validation

## Security Policy Configuration

### Global Security Settings

The framework provides centralized security configuration through properties files:

```properties
# framework/security/config/security.properties
security.login.password.change.history.limit=5
security.login.password.min.length=8
security.login.password.max.age.days=90
security.login.max.failed.logins=3
security.login.disable.minutes=30
```

### Component-Specific Security

Individual OFBiz components can define their own security policies:

```xml
<!-- Component security configuration -->
<ofbiz-component name="accounting" enabled="true">
    <security-config>
        <permission-group name="ACCOUNTING" description="Accounting Module Permissions">
            <permission name="ACCOUNTING_VIEW" description="View accounting information"/>
            <permission name="ACCOUNTING_CREATE" description="Create accounting transactions"/>
            <permission name="ACCOUNTING_UPDATE" description="Update accounting information"/>
            <permission name="ACCOUNTING_DELETE" description="Delete accounting information"/>
        </permission-group>
    </security-config>
</ofbiz-component>
```

## Integration with OFBiz Architecture

### Service Engine Integration

The security framework seamlessly integrates with OFBiz's service-oriented architecture:

- **Pre-service Security Checks**: Authentication and authorization validation before service execution
- **Security Context Propagation**: User context maintained across service calls
- **Audit Trail Integration**: Security events logged through the standard logging framework

### Entity Engine Security

Database-level security integration provides:

- **Row-level Security**: Entity-specific access controls based on user context
- **Field-level Permissions**: Granular control over entity field access
- **Data Filtering**: Automatic filtering of query results based on user permissions

### Widget Framework Security

The screen widget system integrates security at the presentation layer:

```xml
<!-- Screen definition with security constraints -->
<screen

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-06 22:40:37*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*