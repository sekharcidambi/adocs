## Quick Start Instructions

## Prerequisites

Before setting up Apache OFBiz, ensure your development environment meets the following requirements:

- **Java Development Kit (JDK) 8 or higher** - OFBiz is built on Java and requires JDK for compilation and runtime
- **Git** - For cloning the repository and version control
- **Minimum 4GB RAM** - Recommended 8GB+ for optimal performance during development
- **At least 2GB free disk space** - The framework and its dependencies require substantial storage

### System Compatibility

Apache OFBiz supports multiple operating systems:
- Linux (Ubuntu 18.04+, CentOS 7+, RHEL 7+)
- macOS 10.14+
- Windows 10+ (with PowerShell or WSL recommended)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

The repository structure follows OFBiz's multi-tier architecture pattern:
- `framework/` - Core framework components including entity engine, service engine, and web framework
- `applications/` - Standard business applications (accounting, catalog, order management)
- `plugins/` - Additional functionality and third-party integrations
- `themes/` - UI themes and presentation layer customizations

### 2. Build the Framework

```bash
./gradlew build
```

This Gradle command performs several critical operations:
- **Dependency Resolution**: Downloads required JAR files for Spring, Hibernate, and other framework dependencies
- **Java Compilation**: Compiles all Java source code across the multi-tier architecture
- **Groovy Script Compilation**: Processes business logic scripts in the service layer
- **Resource Processing**: Handles XML configurations, properties files, and static assets

The build process typically takes 5-15 minutes on first run, depending on your internet connection and system specifications.

### 3. Initialize and Start OFBiz

```bash
./gradlew ofbiz
```

This command initiates the complete OFBiz startup sequence:

1. **Database Initialization**: Creates the default Derby database with seed data
2. **Entity Engine Startup**: Initializes the data access layer with entity definitions
3. **Service Engine Loading**: Registers business services across all applications
4. **Web Container Startup**: Launches the embedded Tomcat server on default ports
5. **Application Deployment**: Deploys all web applications and REST endpoints

### 4. Verify Installation

Once startup completes (typically 2-5 minutes), verify your installation:

**Web Applications Access:**
- **eCommerce Store**: http://localhost:8080/ecommerce
- **Backend Management**: http://localhost:8080/webtools (admin/ofbiz)
- **Accounting Application**: http://localhost:8080/accounting (admin/ofbiz)
- **Catalog Management**: http://localhost:8080/catalog (admin/ofbiz)

**Default Credentials:**
- Username: `admin`
- Password: `ofbiz`

## Database Configuration

### Default Derby Setup

OFBiz ships with Apache Derby as the default embedded database, perfect for development and evaluation:

```bash
# Database files location
runtime/data/derby/ofbiz/
```

### Production Database Configuration

For production environments, configure external databases by modifying `framework/entity/config/entityengine.xml`:

**PostgreSQL Configuration:**
```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

**MySQL Configuration:**
```xml
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true">
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?autoReconnect=true&amp;useSSL=false"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"/>
</datasource>
```

## Development Environment Setup

### IDE Configuration

**IntelliJ IDEA Setup:**
1. Import project as Gradle project
2. Set Project SDK to Java 8+
3. Configure code style: `framework/documents/intellij-java-code-style.xml`
4. Enable Groovy plugin for service development

**Eclipse Setup:**
1. Import existing Gradle project
2. Install Groovy Development Tools (GDT)
3. Configure build path to include `framework/base/lib/` JARs

### Hot Deployment for Development

Enable hot deployment for rapid development cycles:

```bash
# Start in development mode with auto-reload
./gradlew "ofbiz --load-data --start"
```

This mode automatically reloads:
- Groovy service definitions
- Screen widget XML files
- Form widget definitions
- Menu configurations
- FreeMarker templates

## Architecture Integration Points

### Multi-Tier Architecture Access

The quick start setup provides immediate access to all architectural layers:

**Presentation Layer:**
- Web applications accessible via browser
- RESTful APIs available at `/rest/services/`
- JSON/XML data interchange formats

**Business Logic Layer:**
- Service definitions in `applications/*/servicedef/services*.xml`
- Groovy implementations in `applications/*/src/main/groovy/`
- Java services in `applications/*/src/main/java/`

**Data Access Layer:**
- Entity definitions in `applications/*/entitydef/entitymodel*.xml`
- Database access via Entity Engine
- Automatic CRUD operations and complex queries

### Framework Extension Points

Post-installation, leverage these integration capabilities:

**Custom Applications:**
```bash
# Create new application structure
mkdir -p hot-deploy/myapp/{config,data,entitydef,script,servicedef,webapp,widget}
```

**Plugin Development:**
```bash
# Generate plugin template
./gradlew createPlugin -PpluginId=myplugin
```

**Theme Customization:**
```bash
# Copy and modify existing theme
cp -r themes/common-theme themes/my-theme
```

This quick start foundation enables immediate development across OFBiz's comprehensive ERP functionality while maintaining the framework's architectural principles and integration patterns.

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:07:50*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*