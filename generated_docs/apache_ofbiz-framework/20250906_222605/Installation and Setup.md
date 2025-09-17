# Installation and Setup

This comprehensive guide covers the installation and setup process for the Apache OFBiz framework, a powerful enterprise resource planning (ERP) and customer relationship management (CRM) suite built on Java technologies.

## System Requirements

### Hardware Requirements

**Minimum Requirements:**
- **CPU**: 2-core processor (2.0 GHz or higher)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free disk space for basic installation
- **Network**: Internet connection for dependency downloads

**Recommended Requirements:**
- **CPU**: 4-core processor (2.5 GHz or higher)
- **RAM**: 16 GB or more for production environments
- **Storage**: 10 GB+ free disk space (includes database storage)
- **Network**: High-speed internet connection

### Software Requirements

**Java Development Kit (JDK)**
- **Required**: OpenJDK 11 or Oracle JDK 11
- **Supported**: OpenJDK 17 (recommended for new installations)
- **Not Supported**: JDK 8 or earlier versions

```bash
# Verify Java installation
java -version
javac -version

# Expected output format:
# openjdk version "11.0.x" or "17.0.x"
```

**Operating System Support**
- **Linux**: Ubuntu 18.04+, CentOS 7+, RHEL 7+, Debian 9+
- **Windows**: Windows 10, Windows Server 2016+
- **macOS**: macOS 10.14+ (Mojave or later)

**Additional Software**
- **Git**: Version 2.0 or higher for source code management
- **Gradle**: Bundled with OFBiz (no separate installation required)
- **Database**: Derby (embedded, default), PostgreSQL, MySQL, or Oracle

### Browser Compatibility

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Installation Guide

### Quick Start Installation

#### 1. Clone the Repository

```bash
# Clone the official Apache OFBiz repository
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework

# Alternatively, download a specific release
git clone --branch release18.12 https://github.com/apache/ofbiz-framework.git
```

#### 2. Initial Setup and Build

```bash
# Make the Gradle wrapper executable (Linux/macOS)
chmod +x gradlew

# Windows users use gradlew.bat instead of ./gradlew

# Load initial data and start OFBiz
./gradlew cleanAll loadDefault
```

#### 3. Start the Server

```bash
# Start OFBiz server
./gradlew ofbiz

# Alternative: Start with specific run-time arguments
./gradlew "ofbiz --start"
```

#### 4. Verify Installation

Once the server starts successfully, access the applications:

- **Webtools**: https://localhost:8443/webtools/
- **eCommerce**: https://localhost:8443/ecommerce/
- **Accounting**: https://localhost:8443/accounting/
- **Default Credentials**: admin/ofbiz

### Advanced Installation Options

#### Custom Installation Directory

```bash
# Set custom installation path
export OFBIZ_HOME=/opt/ofbiz
git clone https://github.com/apache/ofbiz-framework.git $OFBIZ_HOME
cd $OFBIZ_HOME
```

#### Development Environment Setup

```bash
# Clone with development branches
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework

# Switch to trunk for latest development version
git checkout trunk

# Build without data loading for development
./gradlew build
```

#### Production Installation

```bash
# Production-optimized build
./gradlew build -x test

# Load production seed data only
./gradlew "ofbiz --load-data readers=seed,seed-initial"

# Start in production mode
./gradlew "ofbiz --start --portoffset=0"
```

### Docker Installation

#### Using Official Docker Image

```dockerfile
# docker-compose.yml
version: '3.8'
services:
  ofbiz:
    image: apache/ofbiz:latest
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - OFBIZ_ADMIN_PASSWORD=admin123
    volumes:
      - ofbiz-data:/opt/ofbiz/runtime
volumes:
  ofbiz-data:
```

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f ofbiz
```

#### Custom Docker Build

```dockerfile
# Dockerfile
FROM openjdk:11-jdk-slim

WORKDIR /opt/ofbiz
COPY . .

RUN chmod +x gradlew && \
    ./gradlew build -x test

EXPOSE 8080 8443

CMD ["./gradlew", "ofbiz"]
```

## Configuration Management

### Core Configuration Files

#### 1. General Configuration (`framework/start/src/main/java/org/apache/ofbiz/base/start/`)

**start.properties**
```properties
# JVM Arguments
java.awt.headless=true
user.timezone=UTC

# Memory settings
ofbiz.start.loader1=-Xms128M
ofbiz.start.loader2=-Xmx1024M
ofbiz.start.loader3=-XX:MaxPermSize=512m
```

#### 2. Server Configuration (`framework/base/config/`)

**general.properties**
```properties
# Default server ports
default.http.port=8080
default.https.port=8443
default.ajp.port=8009

# Force HTTPS for secure pages
force.https.host=localhost
force.https.port=8443

# Session timeout (in minutes)
default.http.session.timeout=60
```

**security.properties**
```properties
# Password encryption settings
password.encrypt=true
password.encrypt.hash.type=SHA-256

# Login security
max.failed.logins=3
login.disable.minutes=5

# CSRF protection
csrf.defense.strategy=token
```

#### 3. Entity Engine Configuration (`framework/entity/config/`)

**entityengine.xml**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/entity-config.xsd">
    
    <!-- Default Derby Configuration -->
    <datasource name="localderby"
                helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
                field-type-name="derby"
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
                jdbc-driver="org.apache.derby.jdbc.EmbeddedDriver"
                jdbc-uri="jdbc:derby:runtime/data/derby/ofbiz;create=true"
                jdbc-username="ofbiz"
                jdbc-password="ofbiz"
                isolation-level="ReadCommitted"
                pool-minsize="2"
                pool-maxsize="250"
                time-between-eviction-runs-millis="600000"/>
    </datasource>
</entity-config>
```

### Environment-Specific Configuration

#### Development Environment

```bash
# Set development properties
export JAVA_OPTS="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"
export OFBIZ_LOG_LEVEL=DEBUG

# Start with development settings
./gradlew "ofbiz --start --load-data"
```

#### Production Environment

**production.properties**
```properties
# Production optimizations
cache.properties.url=cache-production.properties
debug.log.level=WARN
enable.debug.mode=false

# Performance settings
entity.default.operation.timeout=300
service.default.timeout=300

# Security hardening
security.login.password.change.history.limit=12
security.login.password.min.length=8
```

#### SSL/TLS Configuration

**Generate SSL Certificate:**
```bash
# Generate keystore for HTTPS
keytool -genkey -alias ofbiz -keyalg RSA -keystore ofbiz.keystore \
        -keysize 2048 -validity 365 -storepass changeit

# Configure in general.properties
ssl.keystore.type=JKS
ssl.keystore.path=framework/base/config/ofbiz.keystore
ssl.keystore.password=changeit
ssl.keystore.alias=ofbiz
```

### Plugin Configuration

#### Installing Plugins

```bash
# Install a plugin from repository
./gradlew pullPlugin -PpluginId=ecommerce-plugin

# Install local plugin
./gradlew installPlugin -PpluginPath=/path/to/plugin

# List installed plugins
./gradlew listPlugins
```

#### Plugin Configuration Example

**plugin.xml**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<plugin xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/plugin.xsd">
    
    <name>Custom Business Plugin</name>
    <description>Custom business logic plugin</description>
    <version>1.0.0</version>
    <vendor>Your Company</vendor>
    
    <depends-on plugin-id="base"/>
    <depends-on plugin-id="entity"/>
    
    <webapp name="custombusiness"
            title="Custom Business"
            server="default-server"
            location="webapp/custombusiness"
            mount-point="/custombusiness"/>
</plugin>
```

## Database Setup

### Default Derby Database

OFBiz comes with Apache Derby as the default embedded database, requiring no additional setup for development and testing.

**Derby Configuration Benefits:**
- Zero configuration required
- Embedded database (no separate server)
- Suitable for development and small deployments
- Automatic database creation

**Derby Limitations:**
- Single-user access
- Limited performance for large datasets
- Not recommended for production

### PostgreSQL Setup

#### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS (using Homebrew)
brew install postgresql
brew services start postgresql
```

#### 2. Create Database and User

```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE ofbiz;
CREATE USER ofbiz WITH PASSWORD 'ofbiz123';
GRANT ALL PRIVILEGES ON DATABASE ofbiz TO ofbiz;

-- Enable required extensions
\c ofbiz
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";  -- If using geospatial features

\q
```

#### 3. Configure OFBiz for PostgreSQL

**entityengine.xml** (PostgreSQL configuration):
```xml
<datasource name="localpostgres"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="postgres"
            check-on-start="true"
            add-missing-on-start="true">
    
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    
    <inline-jdbc
            jdbc-driver="org.postgresql.Driver"
            jdbc-uri="jdbc:postgresql://localhost:5432/ofbiz"
            jdbc-username="ofbiz"
            jdbc-password="ofbiz123"
            isolation-level="ReadCommitted"
            pool-minsize="5"
            pool-maxsize="50"
            time-between-eviction-runs-millis="600000"/>
</datasource>
```

#### 4. Load Data into PostgreSQL

```bash
# Clean and load data
./gradlew cleanAll loadDefault

# Or load specific data sets
./gradlew "ofbiz --load-data readers=seed,seed-initial,demo"
```

### MySQL Setup

#### 1. Install MySQL

```bash
# Ubuntu/Debian
sudo apt-get install mysql-server mysql-client

# CentOS/RHEL
sudo yum install mysql-server mysql
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Secure installation
sudo mysql_secure_installation
```

#### 2. Create Database and User

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database and user
CREATE DATABASE ofbiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ofbiz'@'localhost' IDENTIFIED BY 'ofbiz123';
GRANT ALL PRIVILEGES ON ofbiz.* TO 'ofbiz'@'localhost';
FLUSH PRIVILEGES;

EXIT;
```

#### 3. Configure OFBiz for MySQL

**entityengine.xml** (MySQL configuration):
```xml
<datasource name="localmysql"
            helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
            field-type-name="mysql"
            check-on-start="true"
            add-missing-on-start="true">
    
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    
    <inline-jdbc
            jdbc-driver="com.mysql.cj.jdbc.Driver"
            jdbc-uri="jdbc:mysql://localhost:3306/ofbiz?useSSL=false&amp;serverTimezone=UTC&amp;allowPublicKeyRetrieval=true"
            jdbc-username="ofbiz"
            jdbc-password="ofbiz123"
            isolation-level="ReadCommitted"
            pool-minsize="5"
            pool-maxsize="50"
            time-between-eviction-runs-millis="600000"/>
</datasource>
```

### Database Migration and Backup

#### Data Export/Import

```bash
# Export data to XML
./gradlew "ofbiz --export-data --export-file=backup.xml"

# Import data from XML
./gradlew "ofbiz --import-data --import-file=backup.xml"

# Export specific entities
./gradlew "ofbiz --export-data --export-file=users.xml --entity-name=UserLogin"
```

#### Database Backup Scripts

**PostgreSQL Backup:**
```bash
#!/bin/bash
# backup-postgres.sh
BACKUP_DIR="/opt/backups/ofbiz"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ofbiz_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U ofbiz -d ofbiz > $BACKUP_FILE
gzip $BACKUP_FILE

echo "Backup completed: $BACKUP_FILE.gz"
```

**MySQL Backup:**
```bash
#!/bin/bash
# backup-mysql.sh
BACKUP_DIR="/opt/backups/ofbiz"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/of