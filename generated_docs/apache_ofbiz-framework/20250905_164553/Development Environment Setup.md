## Development Environment Setup

## Prerequisites

Before setting up your Apache OFBiz development environment, ensure your system meets the following requirements:

### System Requirements
- **Java Development Kit (JDK)**: Version 11 or higher (OpenJDK recommended)
- **Memory**: Minimum 4GB RAM (8GB+ recommended for optimal performance)
- **Storage**: At least 2GB free disk space for the framework and dependencies
- **Operating System**: Linux, macOS, or Windows with proper shell support

### Required Tools
- **Git**: For version control and repository management
- **Gradle**: Bundled with the project (Gradle Wrapper)
- **Database**: One of the supported databases (Derby included by default)

## Initial Setup

### 1. Repository Clone and Basic Setup

```bash
# Clone the repository
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework

# Make gradlew executable (Linux/macOS)
chmod +x gradlew

# Initial build and setup
./gradlew build
```

The initial build process downloads all necessary dependencies, compiles the multi-tier architecture components, and prepares the embedded Derby database. This process typically takes 5-10 minutes on first run.

### 2. Database Configuration

Apache OFBiz supports multiple database backends. The default Derby configuration works out-of-the-box for development:

#### Default Derby Setup (Recommended for Development)
```bash
# Load seed data and demo data
./gradlew "ofbiz --load-data"
```

#### PostgreSQL Configuration
For production-like development environments, configure PostgreSQL:

```bash
# Create entityengine.xml configuration
cp framework/entity/config/entityengine.xml.example framework/entity/config/entityengine.xml
```

Edit `framework/entity/config/entityengine.xml`:
```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="public"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    constraint-name-clip-length="30">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="demo"/>
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

## Development Environment Configuration

### 1. IDE Setup

#### IntelliJ IDEA Configuration
```bash
# Generate IntelliJ project files
./gradlew idea
```

Configure the following in IntelliJ:
- **Project SDK**: Set to your JDK 11+ installation
- **Module Structure**: Verify all OFBiz modules are recognized
- **Run Configuration**: Create a new Application configuration
  - Main class: `org.apache.ofbiz.base.start.Start`
  - VM options: `-Xms1024M -Xmx2048M -XX:MaxPermSize=1024m`
  - Working directory: `[PROJECT_ROOT]`

#### Eclipse Configuration
```bash
# Generate Eclipse project files
./gradlew eclipse
```

### 2. Framework Configuration

#### Component Loading Configuration
Edit `framework/base/config/component-load.xml` to control which components load during development:

```xml
<!-- Core framework components (always required) -->
<load-component component-location="framework/start"/>
<load-component component-location="framework/base"/>
<load-component component-location="framework/entity"/>
<load-component component-location="framework/service"/>
<load-component component-location="framework/webapp"/>

<!-- Business applications (customize as needed) -->
<load-component component-location="applications/party"/>
<load-component component-location="applications/product"/>
<load-component component-location="applications/order"/>
<load-component component-location="applications/accounting"/>
```

#### Debug Configuration
Enable debug logging by modifying `framework/base/config/log4j2.xml`:

```xml
<Logger name="org.apache.ofbiz" level="DEBUG"/>
<Logger name="org.apache.ofbiz.entity.GenericEntity" level="INFO"/>
<Logger name="org.apache.ofbiz.service.ServiceDispatcher" level="DEBUG"/>
```

## Multi-Tier Architecture Development Setup

### 1. Data Access Layer Development
For entity engine development, configure the entity debugging:

```bash
# Enable entity engine debugging
export JAVA_OPTS="-Dofbiz.entity.debug=true"
./gradlew ofbiz
```

Create custom entity definitions in your component's `entitydef` directory:
```xml
<!-- Example: hot-deploy/mycomponent/entitydef/entitymodel.xml -->
<entitymodel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entitymodel.xsd">
    <entity entity-name="MyCustomEntity" package-name="org.apache.ofbiz.mycomponent">
        <field name="myEntityId" type="id-ne"/>
        <field name="description" type="description"/>
        <prim-key field="myEntityId"/>
    </entity>
</entitymodel>
```

### 2. Business Logic Layer Development
Service engine development requires proper service definition:

```xml
<!-- Example: hot-deploy/mycomponent/servicedef/services.xml -->
<services xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/services.xsd">
    <service name="createMyEntity" engine="groovy"
        location="component://mycomponent/groovyScripts/MyEntityServices.groovy"
        invoke="createMyEntity">
        <description>Create My Entity</description>
        <attribute name="description" type="String" mode="IN" optional="false"/>
        <attribute name="myEntityId" type="String" mode="OUT" optional="false"/>
    </service>
</services>
```

### 3. Presentation Layer Development
For frontend development with modern frameworks, configure the webapp structure:

```bash
# Create component webapp structure
mkdir -p hot-deploy/mycomponent/webapp/mycomponent/WEB-INF
mkdir -p hot-deploy/mycomponent/webapp/mycomponent/js
mkdir -p hot-deploy/mycomponent/webapp/mycomponent/css
```

Configure React/Vue.js build integration:
```javascript
// package.json for frontend assets
{
  "name": "ofbiz-mycomponent-frontend",
  "scripts": {
    "build": "webpack --mode production",
    "dev": "webpack --mode development --watch"
  },
  "devDependencies": {
    "webpack": "^5.0.0",
    "babel-loader": "^8.0.0"
  }
}
```

## Hot Deployment and Development Workflow

### 1. Hot Deployment Setup
Enable hot deployment for rapid development:

```bash
# Start OFBiz in development mode
./gradlew "ofbiz --start --portoffset 10000"

# In another terminal, deploy changes
./gradlew "ofbiz --load-component=hot-deploy/mycomponent"
```

### 2. Automated Development Tasks
Create Gradle tasks for common development operations:

```gradle
// In your component's build.gradle
task deployComponent {
    doLast {
        exec {
            commandLine './gradlew', 'ofbiz', '--load-component=hot-deploy/mycomponent'
        }
    }
}

task runTests {
    doLast {
        exec {
            commandLine './gradlew', 'test', '--tests', 'MyComponentTests'
        }

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:09:33*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*