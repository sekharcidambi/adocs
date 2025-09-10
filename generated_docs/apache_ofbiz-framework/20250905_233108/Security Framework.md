## Security Framework

## Overview

The Apache OFBiz Security Framework provides a comprehensive, multi-layered security architecture that protects the enterprise resource planning (ERP) and customer relationship management (CRM) functionalities. Built on Java Enterprise Edition principles, this framework implements role-based access control (RBAC), authentication mechanisms, authorization policies, and data protection measures specifically designed for business applications handling sensitive commercial data.

The security framework is deeply integrated into OFBiz's service-oriented architecture, providing security controls at the entity, service, and presentation layers. It leverages the framework's component-based structure to ensure consistent security policy enforcement across all business modules including accounting, inventory, manufacturing, and e-commerce.

## Core Security Components

### Authentication System

The authentication subsystem supports multiple authentication mechanisms through a pluggable provider architecture:

```xml
<!-- security.properties configuration -->
<property name="security.login.password.encrypt" value="true"/>
<property name="security.login.password.encrypt.hash.type" value="SHA"/>
<property name="security.ldap.enable" value="false"/>
<property name="security.login.tomcat.sso" value="false"/>
```

**Key Authentication Features:**
- **Password-based authentication** with configurable hashing algorithms (SHA-256, SHA-512, PBKDF2)
- **LDAP integration** for enterprise directory services
- **Single Sign-On (SSO)** support through Tomcat valve integration
- **Certificate-based authentication** for B2B communications
- **Token-based authentication** for REST API access

### Authorization Framework

The authorization system implements a sophisticated permission model based on security groups, permissions, and roles:

```java
// Example permission check in service context
public static Map<String, Object> checkPermission(DispatchContext dctx, Map<String, ? extends Object> context) {
    Security security = dctx.getSecurity();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    if (!security.hasPermission("ACCOUNTING_VIEW", userLogin)) {
        return ServiceUtil.returnError("Permission denied for accounting operations");
    }
    return ServiceUtil.returnSuccess();
}
```

**Permission Hierarchy:**
- **Base Permissions**: Fundamental access rights (e.g., `ENTITY_MAINT`, `SERVICE_INVOKE`)
- **Application Permissions**: Business function access (e.g., `ACCOUNTING_CREATE`, `ORDER_VIEW`)
- **Entity Permissions**: Data-level access control with CRUD granularity
- **Custom Permissions**: Domain-specific permissions for specialized business logic

### Security Groups and Roles

The framework implements a flexible role-based access control system:

```xml
<!-- Example security group definition -->
<SecurityGroup groupId="ACCOUNTING_ADMIN" description="Accounting Administrators"/>
<SecurityGroupPermission groupId="ACCOUNTING_ADMIN" permissionId="ACCOUNTING_ADMIN"/>
<SecurityGroupPermission groupId="ACCOUNTING_ADMIN" permissionId="ACCOUNTING_CREATE"/>
<SecurityGroupPermission groupId="ACCOUNTING_ADMIN" permissionId="ACCOUNTING_UPDATE"/>

<!-- User assignment to security group -->
<UserLoginSecurityGroup userLoginId="admin" groupId="ACCOUNTING_ADMIN" fromDate="2001-01-01 00:00:00"/>
```

## Data Security Implementation

### Entity-Level Security

The framework provides comprehensive data protection through entity-level security constraints:

```xml
<!-- Entity model with security constraints -->
<entity entity-name="Invoice" package-name="org.apache.ofbiz.accounting.invoice">
    <field name="invoiceId" type="id-ne"/>
    <field name="partyId" type="id"/>
    <!-- Security view entity for filtered access -->
    <view-entity entity-name="InvoiceAndParty" package-name="org.apache.ofbiz.accounting.invoice">
        <member-entity entity-alias="INV" entity-name="Invoice"/>
        <member-entity entity-alias="PTY" entity-name="Party"/>
        <alias entity-alias="INV" name="invoiceId"/>
        <view-condition>
            <condition-expr entity-alias="INV" field-name="partyId" operator="equals" 
                           env-name="userLogin.partyId"/>
        </view-condition>
    </view-entity>
</entity>
```

### Field-Level Encryption

Sensitive data fields support transparent encryption:

```java
// Encrypted field configuration
public class CreditCard extends GenericEntity {
    @EncryptedField(algorithm = "AES", keyName = "payment")
    private String cardNumber;
    
    @EncryptedField(algorithm = "AES", keyName = "payment")
    private String securityCode;
}
```

## Service Security Integration

### Service Definition Security

Services integrate security checks through declarative configuration:

```xml
<service name="createInvoice" engine="java" location="org.apache.ofbiz.accounting.invoice.InvoiceServices" 
         invoke="createInvoice" auth="true">
    <description>Create Invoice</description>
    <permission-service service-name="acctgInvoicePermissionCheck" main-action="CREATE"/>
    <auto-attributes entity-name="Invoice" include="pk" mode="OUT" optional="false"/>
    <auto-attributes entity-name="Invoice" include="nonpk" mode="IN" optional="true"/>
</service>
```

### Security Context Propagation

The framework ensures security context flows through service call chains:

```java
// Security context in service implementation
public static Map<String, Object> processPayment(DispatchContext dctx, Map<String, Object> context) {
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    // Security context automatically propagated to sub-services
    Map<String, Object> serviceContext = UtilMisc.toMap("userLogin", userLogin);
    Map<String, Object> result = dispatcher.runSync("validatePaymentMethod", serviceContext);
    
    return result;
}
```

## Web Application Security

### Request Security Filters

The framework implements comprehensive request filtering:

```xml
<!-- web.xml security filter configuration -->
<filter>
    <filter-name>ContextFilter</filter-name>
    <filter-class>org.apache.ofbiz.webapp.control.ContextFilter</filter-class>
    <init-param>
        <param-name>security-class</param-name>
        <param-value>org.apache.ofbiz.security.OFBizSecurity</param-value>
    </init-param>
</filter>
```

### Cross-Site Request Forgery (CSRF) Protection

Built-in CSRF protection through token validation:

```java
// CSRF token generation and validation
public class CSRFUtil {
    public static String generateToken(HttpSession session) {
        String token = UtilRandom.generateAlphaNumericString(32);
        session.setAttribute("_CSRF_TOKEN_", token);
        return token;
    }
    
    public static boolean validateToken(HttpServletRequest request) {
        String sessionToken = (String) request.getSession().getAttribute("_CSRF_TOKEN_");
        String requestToken = request.getParameter("_CSRF_TOKEN_");
        return sessionToken != null && sessionToken.equals(requestToken);
    }
}
```

## Integration Points

### Component Security Configuration

Each OFBiz component defines its security requirements:

```xml
<!-- component-load.xml security integration -->
<component name="accounting" location="applications/accounting">
    <security-config location="config/AccountingSecurity.xml"/>
    <permission-config location="data/AccountingPermissionData.xml"/>
</component>
```

### External System Integration

The framework supports secure integration with external systems:

```java
// Secure web service client configuration
public class SecureWebServiceClient {
    private void configureSSL() {
        System.setProperty("javax.net.ssl.trustStore", 
            UtilProperties.getPropertyValue("security", "ssl.truststore.path"));
        System.setProperty("javax.net.ssl.trustStorePassword", 
            UtilProperties.getPropertyValue("security", "ssl.truststore.password"));
    }
}
```

## Best Practices and Configuration

### Security

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:43:48*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*