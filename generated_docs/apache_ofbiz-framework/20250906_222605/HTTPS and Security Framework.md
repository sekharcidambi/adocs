# HTTPS and Security Framework

## Overview

The Apache OFBiz framework implements a comprehensive security architecture that provides robust protection for enterprise applications. The HTTPS and Security Framework is a critical component that ensures secure communication, authentication, authorization, and data protection across all framework layers.

This framework integrates seamlessly with OFBiz's service-oriented architecture, providing security controls for web applications, REST APIs, and inter-service communications while maintaining the flexibility required for enterprise-grade business applications.

## Architecture Overview

### Security Layers

The OFBiz security framework operates across multiple layers:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│        (HTTPS, SSL/TLS, CSRF)          │
├─────────────────────────────────────────┤
│          Application Layer              │
│     (Authentication, Authorization)     │
├─────────────────────────────────────────┤
│            Service Layer                │
│      (Service Security, Permissions)    │
├─────────────────────────────────────────┤
│             Data Layer                  │
│    (Entity Security, Data Encryption)   │
└─────────────────────────────────────────┘
```

### Core Components

- **SSL/TLS Configuration**: Transport layer security implementation
- **Authentication Framework**: User identity verification
- **Authorization Engine**: Permission-based access control
- **Session Management**: Secure session handling
- **CSRF Protection**: Cross-site request forgery prevention
- **Data Encryption**: Sensitive data protection

## HTTPS Configuration

### SSL/TLS Setup

OFBiz supports comprehensive SSL/TLS configuration through the `framework/catalina/ofbiz-component.xml` and connector configurations.

#### Basic HTTPS Connector Configuration

```xml
<!-- framework/catalina/ofbiz-component.xml -->
<ofbiz-component name="catalina">
    <webapp name="ROOT"
            title="Apache OFBiz"
            server="default-server"
            location="webapp/ROOT"
            mount-point="/"
            app-bar-display="false"/>
    
    <!-- HTTPS Connector Configuration -->
    <container name="catalina-container" 
               loaders="main,rmi,pos"
               class="org.apache.ofbiz.catalina.container.CatalinaContainer">
        <property name="delegator-name" value="default"/>
        <property name="use-naming" value="false"/>
        <property name="debug" value="0"/>
        
        <!-- HTTPS Connector -->
        <property name="https-port" value="8443"/>
        <property name="https-host" value="0.0.0.0"/>
        <property name="ssl-accelerator-port" value="8443"/>
        <property name="keystore-file" value="framework/base/config/ofbizssl.jks"/>
        <property name="keystore-pass" value="changeit"/>
        <property name="keystore-type" value="JKS"/>
    </container>
</ofbiz-component>
```

#### Advanced SSL Configuration

```xml
<!-- Enhanced SSL configuration with modern security standards -->
<property name="ssl-enabled-protocols" value="TLSv1.2,TLSv1.3"/>
<property name="ssl-cipher-suites" value="
    TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384,
    TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256"/>
<property name="ssl-honor-cipher-order" value="true"/>
<property name="ssl-disable-compression" value="true"/>
```

### Certificate Management

#### Generating Self-Signed Certificates for Development

```bash
# Generate keystore for development
keytool -genkey -alias ofbiz -keyalg RSA -keysize 2048 \
        -keystore framework/base/config/ofbizssl.jks \
        -validity 365 -storepass changeit \
        -dname "CN=localhost, OU=OFBiz, O=Apache, L=City, ST=State, C=US"

# Export certificate for client trust
keytool -export -alias ofbiz \
        -keystore framework/base/config/ofbizssl.jks \
        -file ofbiz-cert.crt -storepass changeit
```

#### Production Certificate Configuration

```properties
# framework/base/config/security.properties
# Production SSL configuration
ssl.keystore.path=framework/base/config/production.jks
ssl.keystore.password=your_secure_password
ssl.keystore.type=JKS
ssl.key.alias=production-cert
ssl.truststore.path=framework/base/config/truststore.jks
ssl.truststore.password=truststore_password
```

## Authentication Framework

### User Authentication

OFBiz implements a flexible authentication system supporting multiple authentication methods:

#### Login Configuration

```xml
<!-- framework/security/config/security.xml -->
<security-config>
    <login-config>
        <login-module class="org.apache.ofbiz.security.login.DatabaseLoginModule"
                     control-flag="required">
            <property name="delegator-name" value="default"/>
            <property name="password-encrypt" value="true"/>
            <property name="hash-type" value="SHA-256"/>
        </login-module>
    </login-config>
</security-config>
```

#### Custom Authentication Implementation

```java
// Custom authentication service
public class CustomAuthenticationService {
    
    public static Map<String, Object> authenticateUser(DispatchContext dctx, 
                                                      Map<String, ?> context) {
        Delegator delegator = dctx.getDelegator();
        String username = (String) context.get("username");
        String password = (String) context.get("password");
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        
        try {
            // Custom authentication logic
            GenericValue userLogin = EntityQuery.use(delegator)
                .from("UserLogin")
                .where("userLoginId", username)
                .queryOne();
                
            if (userLogin != null && verifyPassword(password, userLogin)) {
                // Update last login timestamp
                userLogin.set("lastTimeZone", TimeZone.getDefault().getID());
                userLogin.set("lastLocale", Locale.getDefault().toString());
                userLogin.store();
                
                result.put("userLogin", userLogin);
                result.put("responseMessage", "Authentication successful");
            } else {
                return ServiceUtil.returnError("Invalid credentials");
            }
            
        } catch (GenericEntityException e) {
            Debug.logError(e, "Authentication error", MODULE);
            return ServiceUtil.returnError("Authentication system error");
        }
        
        return result;
    }
    
    private static boolean verifyPassword(String plainPassword, GenericValue userLogin) {
        String storedHash = userLogin.getString("currentPassword");
        String salt = userLogin.getString("passwordSalt");
        
        // Use OFBiz password encryption utilities
        return HashCrypt.comparePassword(storedHash, salt, plainPassword);
    }
}
```

### Multi-Factor Authentication (MFA)

```java
// MFA implementation service
public class MFAService {
    
    public static Map<String, Object> generateTOTP(DispatchContext dctx, 
                                                  Map<String, ?> context) {
        String userLoginId = (String) context.get("userLoginId");
        
        try {
            // Generate TOTP secret
            String secret = TOTPGenerator.generateSecret();
            
            // Store secret securely
            Delegator delegator = dctx.getDelegator();
            GenericValue mfaConfig = delegator.makeValue("UserMFAConfig");
            mfaConfig.set("userLoginId", userLoginId);
            mfaConfig.set("secretKey", EncryptionUtil.encrypt(secret));
            mfaConfig.set("isEnabled", "Y");
            mfaConfig.create();
            
            Map<String, Object> result = ServiceUtil.returnSuccess();
            result.put("qrCodeUrl", generateQRCodeUrl(userLoginId, secret));
            return result;
            
        } catch (Exception e) {
            return ServiceUtil.returnError("MFA setup failed: " + e.getMessage());
        }
    }
    
    public static Map<String, Object> verifyTOTP(DispatchContext dctx, 
                                               Map<String, ?> context) {
        String userLoginId = (String) context.get("userLoginId");
        String totpCode = (String) context.get("totpCode");
        
        try {
            // Retrieve and decrypt secret
            GenericValue mfaConfig = EntityQuery.use(dctx.getDelegator())
                .from("UserMFAConfig")
                .where("userLoginId", userLoginId)
                .queryOne();
                
            if (mfaConfig == null) {
                return ServiceUtil.returnError("MFA not configured");
            }
            
            String secret = EncryptionUtil.decrypt(mfaConfig.getString("secretKey"));
            boolean isValid = TOTPValidator.validate(secret, totpCode);
            
            Map<String, Object> result = ServiceUtil.returnSuccess();
            result.put("isValid", isValid);
            return result;
            
        } catch (Exception e) {
            return ServiceUtil.returnError("TOTP verification failed");
        }
    }
}
```

## Authorization and Permissions

### Permission-Based Access Control

OFBiz implements a sophisticated permission system based on security groups and permissions:

#### Security Group Configuration

```xml
<!-- framework/security/data/SecurityData.xml -->
<entity-engine-xml>
    <!-- Define security groups -->
    <SecurityGroup groupId="FULLADMIN" description="Full Admin group"/>
    <SecurityGroup groupId="BIZADMIN" description="Business Admin group"/>
    <SecurityGroup groupId="EMPLOYEE" description="Employee group"/>
    
    <!-- Define permissions -->
    <SecurityPermission permissionId="ACCOUNTING_ADMIN" 
                       description="Accounting Admin Permission"/>
    <SecurityPermission permissionId="CATALOG_ADMIN" 
                       description="Catalog Admin Permission"/>
    
    <!-- Assign permissions to groups -->
    <SecurityGroupPermission groupId="FULLADMIN" 
                           permissionId="ACCOUNTING_ADMIN"/>
    <SecurityGroupPermission groupId="BIZADMIN" 
                           permissionId="CATALOG_ADMIN"/>
</entity-engine-xml>
```

#### Service-Level Security

```java
// Service definition with security constraints
public class SecureBusinessService {
    
    @RequiredPermission("CATALOG_ADMIN")
    public static Map<String, Object> updateProductCatalog(DispatchContext dctx, 
                                                          Map<String, ?> context) {
        // Check permissions programmatically
        GenericValue userLogin = (GenericValue) context.get("userLogin");
        Security security = dctx.getSecurity();
        
        if (!security.hasPermission("CATALOG_ADMIN", userLogin)) {
            return ServiceUtil.returnError("Insufficient permissions");
        }
        
        // Business logic implementation
        String catalogId = (String) context.get("catalogId");
        String catalogName = (String) context.get("catalogName");
        
        try {
            Delegator delegator = dctx.getDelegator();
            GenericValue catalog = EntityQuery.use(delegator)
                .from("ProdCatalog")
                .where("prodCatalogId", catalogId)
                .queryOne();
                
            if (catalog != null) {
                catalog.set("catalogName", catalogName);
                catalog.store();
            }
            
            return ServiceUtil.returnSuccess("Catalog updated successfully");
            
        } catch (GenericEntityException e) {
            return ServiceUtil.returnError("Database error: " + e.getMessage());
        }
    }
}
```

### Dynamic Permission Checking

```java
// Dynamic permission evaluation
public class PermissionService {
    
    public static boolean hasEntityPermission(String entityName, 
                                            String operation, 
                                            GenericValue userLogin, 
                                            Delegator delegator) {
        try {
            // Check entity-specific permissions
            List<GenericValue> permissions = EntityQuery.use(delegator)
                .from("UserLoginSecurityGroup")
                .where("userLoginId", userLogin.getString("userLoginId"))
                .queryList();
                
            for (GenericValue permission : permissions) {
                String groupId = permission.getString("groupId");
                
                // Check if group has required entity permission
                if (hasGroupEntityPermission(groupId, entityName, operation, delegator)) {
                    return true;
                }
            }
            
            return false;
            
        } catch (GenericEntityException e) {
            Debug.logError(e, "Permission check failed", MODULE);
            return false;
        }
    }
    
    private static boolean hasGroupEntityPermission(String groupId, 
                                                   String entityName, 
                                                   String operation, 
                                                   Delegator delegator) 
                                                   throws GenericEntityException {
        String permissionId = entityName.toUpperCase() + "_" + operation.toUpperCase();
        
        GenericValue groupPermission = EntityQuery.use(delegator)
            .from("SecurityGroupPermission")
            .where("groupId", groupId, "permissionId", permissionId)
            .queryOne();
            
        return groupPermission != null;
    }
}
```

## Session Management

### Secure Session Configuration

```xml
<!-- framework/webapp/config/web.xml -->
<web-app>
    <session-config>
        <session-timeout>30</session-timeout>
        <cookie-config>
            <name>JSESSIONID</name>
            <http-only>true</http-only>
            <secure>true</secure>
            <max-age>1800</max-age>
            <same-site>Strict</same-site>
        </cookie-config>
        <tracking-mode>COOKIE</tracking-mode>
    </session-config>
</web-app>
```

### Session Security Implementation

```java
// Session security utilities
public class SessionSecurityUtil {
    
    public static void validateSession(HttpServletRequest request, 
                                     HttpServletResponse response) 
                                     throws SessionSecurityException {
        HttpSession session = request.getSession(false);
        
        if (session == null) {
            throw new SessionSecurityException("No valid session");
        }
        
        // Check session timeout
        long lastAccessed = session.getLastAccessedTime();
        long maxInactive = session.getMaxInactiveInterval() * 1000;
        
        if (System.currentTimeMillis() - lastAccessed > maxInactive) {
            session.invalidate();
            throw new SessionSecurityException("Session expired");
        }
        
        // Validate session token
        String sessionToken = (String) session.getAttribute("_SID_");
        if (!isValidSessionToken(sessionToken, request)) {
            session.invalidate();
            throw new SessionSecurityException("Invalid session token");
        }
        
        // Update session activity
        session.setAttribute("lastActivity", System.currentTimeMillis());
        
        // Regenerate session ID periodically
        if (shouldRegenerateSessionId(session)) {
            regenerateSessionId(request, response);
        }
    }
    
    private static boolean shouldRegenerateSessionId(HttpSession session) {
        Long lastRegeneration = (Long) session.getAttribute("lastRegeneration");
        if (lastRegeneration == null) {
            return true;
        }
        
        // Regenerate every 15 minutes
        return System.currentTimeMillis() - lastRegeneration > 900000;