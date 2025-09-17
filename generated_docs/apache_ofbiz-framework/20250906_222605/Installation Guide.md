# Installation Guide

This comprehensive guide will walk you through the installation and setup process for Apache OFBiz, a powerful open-source enterprise automation software suite built on Java.

## Prerequisites

### System Requirements

Before installing OFBiz, ensure your system meets the following minimum requirements:

#### Hardware Requirements
- **RAM**: Minimum 2GB, recommended 4GB or more
- **Disk Space**: At least 2GB free space for installation and data
- **CPU**: Multi-core processor recommended for production environments

#### Software Requirements
- **Java Development Kit (JDK)**: Version 8 or higher (OpenJDK or Oracle JDK)
- **Operating System**: 
  - Linux (Ubuntu 16.04+, CentOS 7+, RHEL 7+)
  - Windows 10/Server 2016+
  - macOS 10.12+
- **Database** (Optional): PostgreSQL, MySQL, or other supported databases
- **Git**: For cloning the repository

### Java Installation Verification

Verify your Java installation by running:

```bash
java -version
javac -version
```

Expected output should show Java version 8 or higher:
```
java version "11.0.12" 2021-07-20 LTS
Java(TM) SE Runtime Environment 18.9 (build 11.0.12+8-LTS-237)
Java HotSpot(TM) 64-Bit Server VM 18.9 (build 11.0.12+8-LTS-237, mixed mode)
```

## Installation Methods

### Method 1: Source Code Installation (Recommended)

#### Step 1: Clone the Repository

Clone the OFBiz repository from GitHub:

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

#### Step 2: Choose a Branch

For production use, checkout a stable release branch:

```bash
# List available branches
git branch -r

# Checkout a stable release (replace with desired version)
git checkout release18.12
```

For development, you can use the trunk branch:

```bash
git checkout trunk
```

#### Step 3: Initial Setup

Run the initial setup to download dependencies and prepare the system:

```bash
# On Linux/macOS
./gradlew cleanAll loadDefault

# On Windows
gradlew.bat cleanAll loadDefault
```

This command will:
- Download required dependencies
- Compile the source code
- Initialize the embedded Derby database
- Load default data including demo data

### Method 2: Binary Distribution Installation

#### Step 1: Download Binary Release

Download the latest binary release from the [Apache OFBiz website](https://ofbiz.apache.org/download.html):

```bash
wget https://archive.apache.org/dist/ofbiz/apache-ofbiz-18.12.07.zip
unzip apache-ofbiz-18.12.07.zip
cd apache-ofbiz-18.12.07
```

#### Step 2: Initialize the System

```bash
# On Linux/macOS
./gradlew loadDefault

# On Windows
gradlew.bat loadDefault
```

## Database Configuration

### Using Default Derby Database

OFBiz comes with an embedded Apache Derby database that's ready to use out of the box. No additional configuration is required for development or testing purposes.

### Configuring External Database

For production environments, it's recommended to use an external database.

#### PostgreSQL Configuration

1. **Install PostgreSQL** and create a database:

```sql
CREATE DATABASE ofbiz;
CREATE USER ofbiz WITH PASSWORD 'ofbiz';
GRANT ALL PRIVILEGES ON DATABASE ofbiz TO ofbiz;
```

2. **Configure OFBiz** by editing `framework/entity/config/entityengine.xml`:

```xml
<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="postgres"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    join-style="ansi-no-parenthesis"
    result-fetch-size="50"
    get-all-fields="true">
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

3. **Update the default delegator** in the same file:

```xml
<delegator name="default" entity-model-reader="main" entity-group-reader="main" entity-eca-reader="main" distributed-cache-clear-enabled="false">
    <group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>
    <group-map group-name="org.apache.ofbiz.olap" datasource-name="localpostgres"/>
    <group-map group-name="org.apache.ofbiz.tenant" datasource-name="localpostgres"/>
</delegator>
```

#### MySQL Configuration

1. **Create MySQL database**:

```sql
CREATE DATABASE ofbiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ofbiz'@'localhost' IDENTIFIED BY 'ofbiz';
GRANT ALL PRIVILEGES ON ofbiz.* TO 'ofbiz'@'localhost';
FLUSH PRIVILEGES;
```

2. **Configure datasource** in `entityengine.xml`:

```xml
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true"
    use-fk-initially-deferred="false"
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
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?characterEncoding=UTF-8&amp;characterSetResults=UTF-8&amp;autoReconnect=true&amp;useSSL=false&amp;allowPublicKeyRetrieval=true"
        jdbc-username="ofbiz"
        jdbc-password="ofbiz"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

## Configuration

### Basic Configuration Files

#### Server Configuration

Edit `framework/base/config/ofbiz-containers.xml` to configure server settings:

```xml
<container name="catalina-container" loaders="main,rmi,test" class="org.apache.ofbiz.catalina.container.CatalinaContainer">
    <property name="delegator-name" value="default"/>
    <property name="use-naming" value="false"/>
    <property name="debug" value="0"/>
    <property name="catalina-runtime-home" value="runtime/catalina"/>
    <property name="apps-context-reloadable" value="false"/>
    <property name="apps-cross-context" value="false"/>
    <property name="apps-distributable" value="false"/>
    <property name="default-server" value="default-server"/>
</container>
```

#### HTTPS Configuration

To enable HTTPS, modify `framework/webapp/config/url.properties`:

```properties
# HTTPS Configuration
port.https=8443
port.https.enabled=true
keystore.file=framework/base/config/ofbizssl.jks
keystore.password=changeit
keystore.type=JKS
```

Generate or import SSL certificates:

```bash
keytool -genkey -alias ofbiz -keyalg RSA -keystore framework/base/config/ofbizssl.jks -keysize 2048
```

### Memory Configuration

For production environments, configure JVM memory settings by creating or editing `tools/gradle/init.gradle`:

```groovy
allprojects {
    gradle.projectsEvaluated {
        tasks.withType(JavaExec) {
            jvmArgs '-Xms2048M', '-Xmx4096M', '-XX:MaxPermSize=1024m'
        }
    }
}
```

## Starting OFBiz

### Development Mode

Start OFBiz in development mode:

```bash
# On Linux/macOS
./gradlew ofbiz

# On Windows
gradlew.bat ofbiz
```

### Production Mode

For production deployment, start OFBiz as a background service:

```bash
# Start OFBiz
./gradlew "ofbiz --start"

# Check status
./gradlew "ofbiz --status"

# Stop OFBiz
./gradlew "ofbiz --shutdown"
```

### Service Configuration (Linux)

Create a systemd service file `/etc/systemd/system/ofbiz.service`:

```ini
[Unit]
Description=Apache OFBiz
After=network.target

[Service]
Type=forking
User=ofbiz
Group=ofbiz
WorkingDirectory=/opt/ofbiz-framework
ExecStart=/opt/ofbiz-framework/gradlew "ofbiz --start"
ExecStop=/opt/ofbiz-framework/gradlew "ofbiz --shutdown"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable ofbiz
sudo systemctl start ofbiz
sudo systemctl status ofbiz
```

## Verification

### Access Web Applications

Once OFBiz is running, verify the installation by accessing these URLs:

- **eCommerce Store**: http://localhost:8080/ecommerce
- **Backend Applications**: http://localhost:8080/webtools
- **Accounting**: http://localhost:8080/accounting
- **Manufacturing**: http://localhost:8080/manufacturing
- **Human Resources**: http://localhost:8080/humanres

### Default Login Credentials

Use these default credentials for initial access:

| Application | Username | Password |
|-------------|----------|----------|
| Admin | admin | ofbiz |
| Demo Customer | DemoCustomer | ofbiz |
| Demo Employee | flexadmin | ofbiz |

### Health Check

Verify system health using the webtools application:

1. Navigate to http://localhost:8080/webtools
2. Login with admin/ofbiz
3. Check "Entity Data Maintenance" for database connectivity
4. Review "Cache Maintenance" for system performance
5. Monitor "Service Engine Tools" for service status

## Plugin Management

### Installing Plugins

OFBiz supports a plugin architecture. Install plugins using Gradle:

```bash
# Install a plugin from the plugins directory
./gradlew installPlugin -PpluginId=example

# Install external plugin
./gradlew pullPluginSource -PpluginId=mycompany-plugin -PpluginRepoUrl=https://github.com/mycompany/ofbiz-plugin.git
```

### Managing Plugin Dependencies

Edit `plugins/component-load.xml` to control plugin loading order:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component-loader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://ofbiz.apache.org/dtds/component-loader.xsd">
    <load-component component-location="example"/>
    <load-component component-location="mycompany-plugin"/>
</component-loader>
```

## Troubleshooting

### Common Issues

#### Port Already in Use

If port 8080 is already in use, modify `framework/webapp/config/url.properties`:

```properties
port.http=8081
port.https=8444
```

#### Memory Issues

Increase JVM heap size for large datasets:

```bash
export JAVA_OPTS="-Xms2048m -Xmx4096m -XX:MaxPermSize=512m"
./gradlew ofbiz
```

#### Database Connection Issues

Check database connectivity and credentials:

```bash
# Test database connection
./gradlew "ofbiz --test component=entity"

# Reload database schema
./gradlew "ofbiz --load-data readers=seed,seed-initial"
```

### Log Files

Monitor OFBiz logs for troubleshooting:

```bash
# Main application log
tail -f runtime/logs/ofbiz.log

# Error log
tail -f runtime/logs/error.log

# Console output
tail -f runtime/logs/console.log
```

### Performance Tuning

#### Database Optimization

For PostgreSQL, add these settings to `postgresql.conf`:

```
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

#### JVM Tuning

Optimize JVM settings for production:

```bash
export JAVA_OPTS="-server -Xms2048m -Xmx4096m -XX:NewRatio=2 -XX:+UseG1GC -XX:+UseStringDeduplication"
```

## Next Steps

After successful installation:

1. **Security Configuration**: Change default passwords and configure security settings
2. **Data Loading**: Import your business data using the Entity Data Maintenance tools
3. **Customization**: Develop custom components or modify existing ones
4. **Integration**: Configure external system integrations
5. **Monitoring**: Set up monitoring and logging for production environments

For detailed configuration and customization guides, refer to the [Configuration Guide](./configuration-guide.md) and [Development Guide](./development-guide.md).

## Additional Resources

- [Apache OFBiz Official Documentation](https://ofbiz.apache.org/documentation.html)
- [Community Wiki](https://cwiki.apache.org/confluence/display/OFBIZ)
- [Mailing Lists](https://ofbiz.apache.org/mailing-lists.html)
- [Issue Tracker](https://issues.apache.org/jira/browse/OFBIZ)