# Security and Authentication

## Overview

Apache OFBiz implements a comprehensive security framework designed to protect enterprise data and ensure secure access control across all layers of the ERP system. The security architecture is built around a role-based access control (RBAC) model with fine-grained permissions, integrated authentication mechanisms, and robust data protection strategies that align with enterprise-grade security requirements.

## Authentication Framework

### User Authentication System

OFBiz employs a multi-layered authentication system that supports various authentication methods:

```xml
<!-- Example security configuration in security.xml -->
<security-config>
    <user-login-security>
        <password-policy>
            <min-length>8</min-length>
            <require-uppercase>true</require-uppercase>
            <require-numbers>true</require-numbers>
            <max-failed-attempts>3</max-failed-attempts>
        </password-policy>
    </user-login-security>
</security-config>
```

The authentication process integrates with the Entity Engine through the `UserLogin` entity, which stores encrypted credentials and authentication metadata. The system supports:

- **Database Authentication**: Primary method using encrypted passwords stored in the database
- **LDAP Integration**: Enterprise directory service integration for centralized authentication
- **Single Sign-On (SSO)**: Support for SAML and OAuth protocols
- **Certificate-based Authentication**: X.509 certificate validation for high-security environments

### Session Management

OFBiz implements secure session management through the `VisitHandler` and `LoginWorker` classes:

```java
// Example session validation in LoginWorker.java
public static String checkLogin(HttpServletRequest request, HttpServletResponse response) {
    HttpSession session = request.getSession();
    GenericValue userLogin = (GenericValue) session.getAttribute("userLogin");
    
    if (userLogin == null || !LoginWorker.hasBasePermission(userLogin, "COMMON_VIEW", request)) {
        return "error";
    }
    return "success";
}
```

Session security features include:
- Configurable session timeouts
- Secure cookie handling with HttpOnly and Secure flags
- Session fixation protection
- Cross-site request forgery (CSRF) token validation

## Authorization and Access Control

### Role-Based Access Control (RBAC)

The OFBiz security model implements a sophisticated RBAC system through several key entities:

- **SecurityGroup**: Defines groups of users with similar access needs
- **SecurityPermission**: Granular permissions for specific operations
- **SecurityGroupPermission**: Links groups to permissions
- **UserLoginSecurityGroup**: Associates users with security groups

```xml
<!-- Example permission definition in SecurityData.xml -->
<SecurityPermission permissionId="ACCOUNTING_VIEW" description="View accounting information"/>
<SecurityPermission permissionId="ACCOUNTING_CREATE" description="Create accounting entries"/>
<SecurityPermission permissionId="ACCOUNTING_UPDATE" description="Update accounting information"/>
<SecurityPermission permissionId="ACCOUNTING_DELETE" description="Delete accounting entries"/>

<SecurityGroup groupId="ACCOUNTING_USER" description="Accounting Users"/>
<SecurityGroupPermission groupId="ACCOUNTING_USER" permissionId="ACCOUNTING_VIEW"/>
<SecurityGroupPermission groupId="ACCOUNTING_USER" permissionId="ACCOUNTING_CREATE"/>
```

### Permission Checking

The framework provides multiple levels of permission checking:

```groovy
// Service-level security in services.xml
<service name="createPayment" engine="entity-auto" invoke="create" default-entity-name="Payment">
    <permission-service service-name="acctgPaymentPermissionCheck" main-action="CREATE"/>
    <auto-attributes include="pk" mode="INOUT" optional="true"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
</service>
```

```java
// Programmatic permission checking
if (security.hasPermission("ACCOUNTING_CREATE", userLogin)) {
    // Perform authorized operation
} else {
    return ServiceUtil.returnError("Insufficient permissions");
}
```

## Data Security

### Encryption and Data Protection

OFBiz implements multiple layers of data protection:

**Password Encryption**: Uses configurable hashing algorithms (SHA-256, bcrypt) with salt:

```java
// Password encryption in LoginServices.java
public static String getHashType() {
    return UtilProperties.getPropertyValue("security", "password.encrypt.hash.type", "SHA");
}

public static String encryptPassword(String password, String salt, String hashType) {
    return HashCrypt.cryptPassword(hashType, salt, password);
}
```

**Database Field Encryption**: Sensitive fields can be encrypted at the entity level:

```xml
<!-- Entity definition with encrypted fields -->
<entity entity-name="CreditCard">
    <field name="cardNumber" type="encrypted"/>
    <field name="securityCode" type="encrypted"/>
</entity>
```

### SQL Injection Prevention

The Entity Engine provides built-in protection against SQL injection through:

- Parameterized queries using prepared statements
- Input validation and sanitization
- Entity condition builders that escape special characters

```java
// Safe entity query construction
EntityCondition condition = EntityCondition.makeCondition(
    EntityCondition.makeCondition("partyId", EntityOperator.EQUALS, partyId),
    EntityOperator.AND,
    EntityCondition.makeCondition("statusId", EntityOperator.EQUALS, "PARTY_ENABLED")
);
```

## Web Security

### Cross-Site Scripting (XSS) Protection

OFBiz implements comprehensive XSS protection through:

```xml
<!-- Content Security Policy configuration -->
<web-app>
    <filter>
        <filter-name>ContentSecurityPolicyFilter</filter-name>
        <filter-class>org.apache.ofbiz.webapp.control.ContentSecurityPolicyFilter</filter-class>
        <init-param>
            <param-name>contentSecurityPolicy</param-name>
            <param-value>default-src 'self'; script-src 'self' 'unsafe-inline'</param-value>
        </init-param>
    </filter>
</web-app>
```

**FreeMarker Template Security**: Automatic HTML escaping and input sanitization:

```ftl
<!-- Safe output rendering -->
${productName?html}  <!-- Automatically escapes HTML -->
<#escape x as x?html>
    ${userInput}  <!-- All variables in this block are escaped -->
</#escape>
```

### HTTPS and Transport Security

OFBiz enforces secure transport through:

```xml
<!-- HTTPS configuration in web.xml -->
<security-constraint>
    <web-resource-collection>
        <web-resource-name>Secure Area</web-resource-name>
        <url-pattern>/control/*</url-pattern>
    </web-resource-collection>
    <user-data-constraint>
        <transport-guarantee>CONFIDENTIAL</transport-guarantee>
    </user-data-constraint>
</security-constraint>
```

## Integration Security

### Service Security

Services can be secured at multiple levels:

```xml
<!-- Service authentication requirements -->
<service name="updateParty" engine="simple" location="component://party/script/org/ofbiz/party/party/PartyServices.xml" invoke="updateParty">
    <description>Update a Party</description>
    <permission-service service-name="partyPermissionCheck" main-action="UPDATE"/>
    <attribute name="partyId" type="String" mode="IN" optional="false"/>
</service>
```

### API Security

RESTful API endpoints are secured through:

- OAuth 2.0 token validation
- Rate limiting and throttling
- Request/response logging and monitoring
- API key management

```java
// API authentication filter
public class ApiAuthenticationFilter implements Filter {
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        String apiKey = request.getParameter("api_key");
        if (!validateApiKey(apiKey)) {
            ((HttpServletResponse) response).setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }
        chain.doFilter(request, response);
    }
}
```

## Security Configuration

### Environment-Specific Security

Security configurations can be customized per environment:

```properties
# security.properties
password.encrypt.hash.type=SHA-256

## Subsections

- [User Management System](./User Management System.md)
- [Role-Based Access Control](./Role-Based Access Control.md)

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: Apache OFBiz is an open source enterprise resource planning (ERP) system
- **Business Domain**: Enterprise Resource Planning
- **Architecture Pattern**: Multi-tier Architecture
- **Key Components**: Presentation Layer, Business Logic Layer, Data Access Layer
- **Stars**: 1200
- **Forks**: 800
- **Size**: 50000 KB

## Technology Stack

### Languages
- Java
- Groovy
- JavaScript

### Frameworks
- Apache OFBiz Framework
- Spring
- Hibernate

### Databases
- MySQL
- PostgreSQL
- Derby

### Frontend
- React
- Angular
- Vue.js

### Devops
- Docker
- Jenkins
- Maven

## Quick Setup

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
./gradlew build
./gradlew ofbiz
```

## Related Documentation

This section is part of a comprehensive documentation structure. Related sections include:

- **User Management System**: Detailed coverage of user management system
- **Role-Based Access Control**: Detailed coverage of role-based access control

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:05:06*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*