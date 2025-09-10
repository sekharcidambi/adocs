# Installation and Setup Guide

## Prerequisites

Before installing Apache OFBiz, ensure your system meets the following requirements:

### System Requirements
- **Java Development Kit (JDK)**: Version 8 or higher (OpenJDK or Oracle JDK)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for production)
- **Disk Space**: At least 2GB free space for installation and data
- **Operating System**: Linux, Windows, or macOS

### Required Software
```bash
# Verify Java installation
java -version
javac -version

# Ensure JAVA_HOME is set
echo $JAVA_HOME
```

## Quick Start Installation

### 1. Clone the Repository

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

### 2. Build the Framework

Apache OFBiz uses Gradle as its build system. The framework includes a Gradle wrapper that automatically downloads the correct Gradle version:

```bash
# Make the Gradle wrapper executable (Linux/macOS)
chmod +x gradlew

# Build the entire framework
./gradlew build
```

The build process compiles all Java and Groovy sources across the multi-tier architecture, including:
- **Entity Engine**: Data access layer components
- **Service Engine**: Business logic layer services
- **Widget Framework**: Presentation layer components
- **Web Applications**: Individual OFBiz applications

### 3. Initial System Setup

```bash
# Load seed and demo data
./gradlew "ofbiz --load-data"

# Start OFBiz
./gradlew ofbiz
```

## Database Configuration

Apache OFBiz supports multiple database systems through its Entity Engine abstraction layer.

### Default Derby Configuration

OFBiz ships with Apache Derby as the default embedded database, requiring no additional configuration:

```bash
# Start with Derby (default)
./gradlew ofbiz
```

### MySQL Configuration

For production environments, configure MySQL by modifying the entity engine configuration:

1. **Install MySQL** and create a database:
```sql
CREATE DATABASE ofbiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ofbiz'@'localhost' IDENTIFIED BY 'ofbiz_password';
GRANT ALL PRIVILEGES ON ofbiz.* TO 'ofbiz'@'localhost';
```

2. **Configure the datasource** in `framework/entity/config/entityengine.xml`:
```xml
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    join-style="ansi-no-parenthesis"
    result-fetch-size="50">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?autoReconnect=true&amp;useSSL=false&amp;serverTimezone=UTC"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz_password"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

3. **Update the default delegator** to use MySQL:
```xml
<delegator name="default" entity-model-reader="main" entity-group-reader="main" entity-eca-reader="main" distributed-cache-clear-enabled="false">
    <group-map group-name="org.apache.ofbiz" datasource-name="localmysql"/>
</delegator>
```

### PostgreSQL Configuration

For PostgreSQL integration:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true">
    <inline-jdbc
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz_password"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"/>
</datasource>
```

## Advanced Configuration

### Memory and Performance Tuning

Configure JVM parameters for optimal performance:

```bash
# Create or modify gradle.properties
echo "org.gradle.jvmargs=-Xmx2048m -XX:MaxPermSize=512m" >> gradle.properties

# For production environments, modify the start script
export JAVA_OPTS="-Xms1024m -Xmx4096m -XX:MaxPermSize=512m -Dfile.encoding=UTF-8"
./gradlew ofbiz
```

### Multi-tenant Setup

OFBiz supports multi-tenancy through its Entity Engine:

1. **Enable multi-tenancy** in `framework/entity/config/entityengine.xml`:
```xml
<delegator name="default#TENANT_ID" entity-model-reader="main" entity-group-reader="main" entity-eca-reader="main" distributed-cache-clear-enabled="false">
    <group-map group-name="org.apache.ofbiz.tenant" datasource-name="localderbyTenant"/>
    <group-map group-name="org.apache.ofbiz" datasource-name="localderby"/>
</delegator>
```

2. **Create tenant-specific data**:
```bash
./gradlew "ofbiz --load-data --load-data-readers=tenant"
```

### Docker Deployment

For containerized deployment:

```dockerfile
FROM openjdk:8-jdk-alpine
WORKDIR /opt/ofbiz
COPY . .
RUN ./gradlew build
EXPOSE 8080 8443
CMD ["./gradlew", "ofbiz"]
```

```bash
# Build and run Docker container
docker build -t ofbiz-framework .
docker run -p 8080:8080 -p 8443:8443 ofbiz-framework
```

## Verification and Testing

### System Health Check

After installation, verify the system is running correctly:

```bash
# Check if OFBiz is responding
curl -I http://localhost:8080/

# Access the web interface
# Navigate to: https://localhost:8443/webtools/
# Default credentials: admin/ofbiz
```

### Running Tests

Execute the comprehensive test suite:

```bash
# Run all tests
./gradlew test

# Run specific component tests
./gradlew :applications:accounting:test
./gradlew :framework:entity:test
```

## Integration with Development Tools

### IDE Setup

For development with IntelliJ IDEA or Eclipse:

```bash
# Generate IDE project files
./gradlew idea     # For IntelliJ IDEA
./gradlew eclipse  # For Eclipse
```

### Maven Integration

While OFBiz primarily uses Gradle, Maven integration is available for specific components:

```xml
<dependency>
    <groupId>org.apache.ofbiz</groupId>
    <artifactId>ofbiz-framework</artifactId>
    <version>17.12.01</version>
</dependency>
```

This installation guide provides the foundation for deploying Apache OFBiz's comprehensive ERP system, leveraging its multi-tier architecture to deliver scalable enterprise solutions across the presentation, business logic, and data access layers.

## Subsections

- [System Requirements](./System Requirements.md)
- [Quick Start Instructions](./Quick Start Instructions.md)
- [Configuration Management](./Configuration Management.md)

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

- **System Requirements**: Detailed coverage of system requirements
- **Quick Start Instructions**: Detailed coverage of quick start instructions
- **Configuration Management**: Detailed coverage of configuration management

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:06:43*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*