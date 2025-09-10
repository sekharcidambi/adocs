## Installation and Setup

## Prerequisites

Before installing Apache OFBiz, ensure your system meets the following requirements:

### System Requirements
- **Java Development Kit (JDK)**: Java 11 or higher (OpenJDK or Oracle JDK)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for production)
- **Disk Space**: At least 2GB free space for installation and data
- **Operating System**: Linux, Windows, or macOS

### Required Tools
- **Git**: For cloning the repository
- **Gradle**: Bundled with OFBiz (uses Gradle Wrapper)
- **Database**: H2 (embedded, default), PostgreSQL, MySQL, or other supported databases

## Installation Methods

### Method 1: Quick Start Installation

The fastest way to get OFBiz running is using the embedded H2 database:

```bash
# Clone the repository
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework

# Load initial data and start OFBiz
./gradlew loadAll ofbiz
```

This command performs several critical operations:
- Downloads and installs all dependencies via Gradle
- Initializes the embedded H2 database
- Loads seed data, demo data, and security configurations
- Starts the OFBiz server on default ports

### Method 2: Production Installation

For production environments, follow these detailed steps:

```bash
# Clone the stable release branch
git clone -b release22.01 https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework

# Build the framework without loading demo data
./gradlew build

# Load only essential data (no demo data)
./gradlew "ofbiz --load-data readers=seed,seed-initial,ext"

# Start OFBiz
./gradlew ofbiz
```

## Database Configuration

### Using External Database (PostgreSQL Example)

OFBiz's entity engine supports multiple databases through its flexible datasource configuration:

1. **Install PostgreSQL** and create a database:
```sql
CREATE DATABASE ofbiz_production;
CREATE USER ofbiz WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ofbiz_production TO ofbiz;
```

2. **Configure the datasource** by editing `framework/entity/config/entityengine.xml`:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    join-style="ansi"
    result-fetch-size="50">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz_production"
        jdbc-username="ofbiz"
        jdbc-password="your_secure_password"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

3. **Update the default delegator** in the same file:
```xml
<delegator name="default" entity-model-reader="main" 
    entity-group-reader="main" entity-eca-reader="main" 
    distributed-cache-clear-enabled="false">
    <group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>
</delegator>
```

## Configuration Files

### Core Configuration Structure

OFBiz follows a hierarchical configuration pattern with several key files:

#### `framework/start/src/main/java/org/apache/ofbiz/base/start/Config.java`
Controls startup parameters and JVM settings. Key configurations include:

```properties
# In start.properties
ofbiz.admin.port=10523
ofbiz.admin.key=so3du5kasd5dn
ofbiz.enable.hook=true
ofbiz.start.loader1=org.apache.ofbiz.base.container.ContainerLoader
ofbiz.start.loader2=org.apache.ofbiz.base.start.StartupControlPanel
```

#### `framework/webapp/config/url.properties`
Defines URL patterns and security configurations:

```properties
# Port configuration
port.https=8443
port.http=8080

# Host configuration  
default.https.host=localhost
default.http.host=localhost

# Force HTTPS for secure areas
force.https.host=localhost
```

### Application-Specific Configuration

#### `applications/*/config/` directories
Each OFBiz application maintains its own configuration:

- **Accounting**: `applications/accounting/config/AccountingUiLabels.xml`
- **Party Manager**: `applications/party/config/PartyEntityLabels.xml`
- **Order Management**: `applications/order/config/OrderErrorUiLabels.xml`

## Environment Setup

### Development Environment

For development work, configure your IDE and development tools:

```bash
# Generate IDE project files
./gradlew eclipse  # For Eclipse
./gradlew idea     # For IntelliJ IDEA

# Enable debug mode
./gradlew ofbizDebug

# Run with specific JVM options
export JAVA_OPTS="-Xms1024M -Xmx2048M -XX:MaxPermSize=1024m"
./gradlew ofbiz
```

### Production Environment Tuning

Configure JVM parameters for production in `gradle.properties`:

```properties
# Memory settings
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# Garbage collection
systemProp.java.awt.headless=true
systemProp.file.encoding=UTF-8

# OFBiz specific
systemProp.ofbiz.home=/opt/ofbiz
systemProp.derby.system.home=/opt/ofbiz/runtime/data/derby
```

## Security Configuration

### Initial Security Setup

After installation, immediately secure your OFBiz instance:

1. **Change default passwords**:
```bash
# Access the webtools application
# https://localhost:8443/webtools/control/main
# Default: admin/ofbiz
```

2. **Configure HTTPS certificates**:
```bash
# Generate keystore for HTTPS
keytool -genkey -alias ofbiz -keyalg RSA -keystore framework/base/config/ofbizssl.jks
```

3. **Update security configuration** in `framework/security/config/security.properties`:
```properties
# Password encryption
password.encrypt=true
password.encrypt.hash.type=SHA-256

# Login security
max.failed.logins=3
login.disable.minutes=30
```

## Verification and Testing

### Installation Verification

Verify your installation by checking these endpoints:

```bash
# Check if OFBiz is running
curl -k https://localhost:8443/catalog/control/main

# Verify database connectivity
./gradlew "ofbiz --status"

# Run integration tests
./gradlew testIntegration
```

### Log File Locations

Monitor these log files for troubleshooting:

- **Runtime logs**: `runtime/logs/ofbiz.log`
- **Console output**: `runtime/logs/console.log`  
- **Error logs**: `runtime/logs/error.log`
- **Access logs**: `runtime/logs/access.log`

The logging configuration is managed through `framework/base/config/log4j2.xml`, allowing fine-grained control over log levels and output formats for different OFBiz components.

This installation approach leverages OFBiz's modular architecture, where the framework provides core services (entity engine, service engine, webapp framework) while applications build upon these foundations to deliver business functionality.

## Repository Context

- **Repository**: [https://github.com/apache/ofbiz-framework](https://github.com/apache/ofbiz-framework)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 23:46:45*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*