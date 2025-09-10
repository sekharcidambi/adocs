## User Management System

## Overview

The User Management System in Apache OFBiz is a comprehensive security and access control framework that handles authentication, authorization, and user lifecycle management across the entire ERP platform. Built on OFBiz's multi-tier architecture, this system provides enterprise-grade security features essential for managing complex organizational structures and role-based access patterns typical in ERP environments.

The system operates through OFBiz's entity-relationship model, leveraging the framework's built-in security components to manage users, security groups, permissions, and authentication mechanisms. It integrates seamlessly with all OFBiz applications including accounting, manufacturing, e-commerce, and human resources modules.

## Architecture Integration

### Data Access Layer
The User Management System utilizes OFBiz's entity engine with several core entities:

```xml
<!-- Core user entities in framework/security/entitydef/entitymodel.xml -->
<entity entity-name="UserLogin" package-name="org.apache.ofbiz.security.login">
    <field name="userLoginId" type="id-ne"/>
    <field name="currentPassword" type="long-varchar"/>
    <field name="passwordHint" type="description"/>
    <field name="isSystem" type="indicator"/>
    <field name="enabled" type="indicator"/>
    <field name="hasLoggedOut" type="indicator"/>
    <field name="requirePasswordChange" type="indicator"/>
    <prim-key field="userLoginId"/>
</entity>

<entity entity-name="SecurityGroup" package-name="org.apache.ofbiz.security.securitygroup">
    <field name="groupId" type="id-ne"/>
    <field name="description" type="description"/>
    <prim-key field="groupId"/>
</entity>
```

### Business Logic Layer
User management services are implemented in Groovy and Java, following OFBiz's service-oriented architecture:

```groovy
// Example from framework/security/src/main/groovy/org/apache/ofbiz/security/
def createUserLogin() {
    Map result = success()
    
    // Validate input parameters
    if (!parameters.userLoginId) {
        return error("User Login ID is required")
    }
    
    // Check for existing user
    GenericValue existingUser = from("UserLogin")
        .where("userLoginId", parameters.userLoginId)
        .queryOne()
    
    if (existingUser) {
        return error("User Login ID already exists")
    }
    
    // Create new user with encrypted password
    Map createUserMap = [
        userLoginId: parameters.userLoginId,
        currentPassword: LoginServices.getHashedPassword(parameters.currentPassword),
        enabled: parameters.enabled ?: "Y",
        requirePasswordChange: parameters.requirePasswordChange ?: "N"
    ]
    
    GenericValue newUser = makeValue("UserLogin", createUserMap)
    newUser.create()
    
    return result
}
```

### Presentation Layer
The user interface components are built using OFBiz's widget system and can be extended with modern frontend frameworks:

```xml
<!-- Screen definition in framework/security/widget/SecurityScreens.xml -->
<screen name="UserLoginList">
    <section>
        <actions>
            <entity-condition entity-name="UserLogin" list="userLogins">
                <condition-expr field-name="enabled" value="Y"/>
                <order-by field-name="userLoginId"/>
            </entity-condition>
        </actions>
        <widgets>
            <decorator-screen name="CommonSecurityDecorator">
                <decorator-section name="body">
                    <include-grid name="ListUserLogins" location="component://security/widget/SecurityForms.xml"/>
                </decorator-section>
            </decorator-screen>
        </widgets>
    </section>
</screen>
```

## Key Components

### Authentication Mechanisms

OFBiz supports multiple authentication methods configurable through `security.properties`:

```properties
# Password encryption settings
password.encrypt=true
password.encrypt.hash.type=SHA-256
password.encrypt.salt.type=RANDOM

# Login attempt restrictions
max.failed.logins=3
login.disable.minutes=30

# Session management
security.login.password.allow.reuse=false
security.login.password.change.history.limit=5
```

### Authorization Framework

The permission system uses a hierarchical model with security groups and individual permissions:

```java
// Example permission check in Java service
public static Map<String, Object> checkUserPermission(DispatchContext dctx, Map<String, ?> context) {
    Security security = dctx.getSecurity();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    String permission = (String) context.get("permission");
    String action = (String) context.get("action");
    
    boolean hasPermission = security.hasPermission(permission, userLogin);
    if (!hasPermission && action != null) {
        hasPermission = security.hasEntityPermission(permission, action, userLogin);
    }
    
    Map<String, Object> result = ServiceUtil.returnSuccess();
    result.put("hasPermission", hasPermission);
    return result;
}
```

### Role-Based Access Control (RBAC)

Security groups define roles with specific permissions:

```xml
<!-- Security group data in framework/security/data/SecurityData.xml -->
<SecurityGroup groupId="ACCOUNTING" description="Accounting Users"/>
<SecurityGroup groupId="MANUFACTURING" description="Manufacturing Users"/>
<SecurityGroup groupId="ADMIN" description="System Administrators"/>

<SecurityPermission permissionId="ACCOUNTING_VIEW" description="View Accounting"/>
<SecurityPermission permissionId="ACCOUNTING_CREATE" description="Create Accounting"/>
<SecurityPermission permissionId="MANUFACTURING_VIEW" description="View Manufacturing"/>

<SecurityGroupPermission groupId="ACCOUNTING" permissionId="ACCOUNTING_VIEW"/>
<SecurityGroupPermission groupId="ACCOUNTING" permissionId="ACCOUNTING_CREATE"/>
<SecurityGroupPermission groupId="ADMIN" permissionId="ACCOUNTING_VIEW"/>
```

## Integration Points

### Party Management Integration
User accounts are linked to the Party entity, enabling rich profile management:

```groovy
// Service to create user with party information
def createUserLoginAndPerson() {
    // Create Party first
    Map createPersonResult = run service: "createPerson", with: [
        firstName: parameters.firstName,
        lastName: parameters.lastName,
        birthDate: parameters.birthDate
    ]
    
    // Create UserLogin linked to Party
    Map createUserResult = run service: "createUserLogin", with: [
        userLoginId: parameters.userLoginId,
        currentPassword: parameters.currentPassword,
        partyId: createPersonResult.partyId
    ]
    
    return success([partyId: createPersonResult.partyId, userLoginId: parameters.userLoginId])
}
```

### Single Sign-On (SSO) Support
OFBiz supports LDAP and external authentication providers:

```properties
# LDAP configuration in security.properties
ldap.enable=true
ldap.url=ldap://your-ldap-server:389
ldap.username=cn=admin,dc=company,dc=com
ldap.password=adminpassword
ldap.search.base=ou=users,dc=company,dc=com
ldap.search.filter=(uid={0})
```

## Best Practices

### Security Hardening
1. **Password Policies**: Configure strong password requirements in `security.properties`
2. **Session Management**: Implement proper session timeout and cleanup
3. **Audit Logging**: Enable comprehensive user activity logging

```groovy
// Custom password validation service
def validatePasswordStrength() {
    String password = parameters.newPassword
    List<String> errors = []
    
    if (password.length() < 8) {
        errors.add("Password must be at least 8 characters long")
    }
    if (!password.matches(".*[A-Z].*")) {
        errors.add("Password must contain uppercase letters")
    }
    if (!password.matches(".*[0-9].*")) {
        errors.add("Password must contain numbers")
    }
    if (!password.matches(".*[!@#$%^&*].*")) {
        errors.ad

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

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:05:38*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*