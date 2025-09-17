# Development Environment Setup

This guide provides comprehensive instructions for setting up a development environment for the Apache OFBiz framework. OFBiz is a powerful enterprise automation software that includes framework components and business applications for ERP, CRM, E-Business/E-Commerce, Supply Chain Management, and Manufacturing Resource Planning.

## Prerequisites

### System Requirements

Before setting up your OFBiz development environment, ensure your system meets the following requirements:

- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB, recommended 8GB or more
- **Disk Space**: At least 2GB free space for OFBiz installation
- **Network**: Internet connection for downloading dependencies

### Required Software

#### Java Development Kit (JDK)

OFBiz requires Java 8 or higher. We recommend using OpenJDK or Oracle JDK.

**Installation on Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install openjdk-11-jdk
```

**Installation on macOS (using Homebrew):**
```bash
brew install openjdk@11
```

**Installation on Windows:**
Download and install from [OpenJDK website](https://openjdk.java.net/) or [Oracle JDK](https://www.oracle.com/java/technologies/downloads/).

**Verify Installation:**
```bash
java -version
javac -version
```

#### Apache Ant (Optional but Recommended)

While OFBiz includes Gradle as the primary build tool, Ant is still useful for certain tasks.

```bash
# Ubuntu/Debian
sudo apt install ant

# macOS
brew install ant

# Verify installation
ant -version
```

#### Git

Git is essential for version control and cloning the OFBiz repository.

```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows: Download from https://git-scm.com/
```

## Environment Setup

### Setting Environment Variables

Create or modify your shell profile file (`~/.bashrc`, `~/.zshrc`, or equivalent):

```bash
# Java Environment
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Adjust path as needed
export PATH=$JAVA_HOME/bin:$PATH

# OFBiz Environment (set after cloning)
export OFBIZ_HOME=/path/to/ofbiz-framework
export PATH=$OFBIZ_HOME:$PATH

# Database Configuration (if using PostgreSQL)
export PGHOST=localhost
export PGPORT=5432
export PGUSER=ofbiz
export PGPASSWORD=ofbiz
```

Reload your shell configuration:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Cloning the Repository

Clone the official OFBiz repository:

```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

For development, create your own fork first:

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/ofbiz-framework.git
cd ofbiz-framework

# Add upstream remote
git remote add upstream https://github.com/apache/ofbiz-framework.git
```

## Database Configuration

### Default Derby Database

OFBiz comes with Apache Derby as the default database, which requires no additional setup for development:

```bash
# The Derby database will be automatically created during first run
# Database files will be stored in runtime/data/derby/
```

### PostgreSQL Setup (Recommended for Development)

For a more production-like environment, configure PostgreSQL:

#### Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Create OFBiz database and user
sudo -u postgres createuser -P ofbiz
sudo -u postgres createdb -O ofbiz ofbiz
```

#### Configure OFBiz for PostgreSQL

Create or modify `framework/entity/config/entityengine.xml`:

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
    result-fetch-size="50">
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

## IDE Configuration

### IntelliJ IDEA Setup

#### Import Project

1. Open IntelliJ IDEA
2. Select "Open or Import"
3. Navigate to your OFBiz directory
4. Select the root `ofbiz-framework` folder
5. Choose "Import project from external model" → "Gradle"

#### Configure Project Settings

```groovy
// In build.gradle, ensure proper Java version
sourceCompatibility = '11'
targetCompatibility = '11'
```

#### Recommended Plugins

- **Groovy**: For Groovy script support
- **XML Tools**: For XML configuration files
- **Database Tools**: For database management
- **Git Integration**: Built-in Git support

#### Code Style Configuration

Create `.editorconfig` in the project root:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.java]
indent_style = space
indent_size = 4

[*.{xml,groovy}]
indent_style = space
indent_size = 4

[*.{js,html,css}]
indent_style = space
indent_size = 2
```

### Eclipse Setup

#### Import Project

1. Open Eclipse
2. File → Import → Existing Projects into Workspace
3. Select root directory: your OFBiz folder
4. Import as Gradle project

#### Configure Build Path

1. Right-click project → Properties
2. Java Build Path → Libraries
3. Add External JARs from `build/libs/` directory

### Visual Studio Code Setup

#### Required Extensions

```json
{
  "recommendations": [
    "vscjava.vscode-java-pack",
    "redhat.vscode-xml",
    "ms-vscode.vscode-groovy",
    "eamodio.gitlens"
  ]
}
```

#### Workspace Settings

Create `.vscode/settings.json`:

```json
{
  "java.configuration.updateBuildConfiguration": "automatic",
  "java.compile.nullAnalysis.mode": "automatic",
  "files.exclude": {
    "build/": true,
    "runtime/logs/": true,
    "runtime/data/derby/": true
  }
}
```

## Build and Initial Setup

### Building OFBiz

Use the Gradle wrapper for building:

```bash
# Make gradlew executable (Linux/macOS)
chmod +x gradlew

# Clean and build
./gradlew cleanAll loadDefault

# On Windows
gradlew.bat cleanAll loadDefault
```

### Loading Sample Data

```bash
# Load seed data (required)
./gradlew loadDefault

# Load demo data (optional, for testing)
./gradlew loadDemo

# Load specific data types
./gradlew "loadData --load-file=framework/security/data/SecurityData.xml"
```

### Starting OFBiz

```bash
# Start OFBiz
./gradlew ofbiz

# Start with specific arguments
./gradlew "ofbizDebug --start --portoffset 10000"

# Start in background
nohup ./gradlew ofbiz &
```

## Development Tools and Utilities

### Gradle Tasks

Common Gradle tasks for development:

```bash
# View all available tasks
./gradlew tasks

# Run tests
./gradlew test

# Generate documentation
./gradlew javadoc

# Create distribution
./gradlew createOfbizCommandZip

# Clean build artifacts
./gradlew clean
```

### Hot Deployment

For rapid development, enable hot deployment:

```bash
# Start OFBiz in development mode
./gradlew "ofbiz --load-data --start --portoffset 10000"

# In another terminal, deploy changes
./gradlew "ofbiz --shutdown --portoffset 10000"
./gradlew "ofbiz --start --portoffset 10000"
```

### Debugging Configuration

#### Remote Debugging

Start OFBiz with debugging enabled:

```bash
./gradlew "ofbizDebug --start"
```

#### IDE Debug Configuration

**IntelliJ IDEA:**
1. Run → Edit Configurations
2. Add new "Remote JVM Debug"
3. Host: localhost, Port: 5005
4. Use module classpath: ofbiz-framework

**Eclipse:**
1. Run → Debug Configurations
2. Remote Java Application → New
3. Host: localhost, Port: 5005

### Log Configuration

Configure logging in `framework/base/config/log4j2.xml`:

```xml
<Configuration>
    <Appenders>
        <Console name="stdout" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{ISO8601} |%-5p| %c{1} |%t| %m%n"/>
        </Console>
        <RollingFile name="main-log" fileName="runtime/logs/ofbiz.log"
                     filePattern="runtime/logs/ofbiz.log.%i">
            <PatternLayout pattern="%d{ISO8601} |%-5p| %c{1} |%t| %m%n"/>
            <Policies>
                <SizeBasedTriggeringPolicy size="10MB"/>
            </Policies>
            <DefaultRolloverStrategy max="5"/>
        </RollingFile>
    </Appenders>
    
    <Loggers>
        <Logger name="org.apache.ofbiz" level="INFO"/>
        <Logger name="org.apache.ofbiz.entity" level="WARN"/>
        <Root level="WARN">
            <AppenderRef ref="stdout"/>
            <AppenderRef ref="main-log"/>
        </Root>
    </Loggers>
</Configuration>
```

## Testing Environment

### Unit Testing

Run unit tests:

```bash
# Run all tests
./gradlew test

# Run specific test class
./gradlew test --tests "org.apache.ofbiz.entity.test.*"

# Run tests with detailed output
./gradlew test --info
```

### Integration Testing

```bash
# Run integration tests
./gradlew integrationTest

# Run specific integration test
./gradlew "ofbiz --test component=entity"
```

### Test Configuration

Create test-specific configuration in `framework/entity/config/entityengine-test.xml`:

```xml
<entity-config>
    <resource-loader name="testdata" class="org.apache.ofbiz.base.config.FileLoader"
                    prepend-env="ofbiz.home" prefix="/framework/entity/testdata/"/>
    
    <delegator name="test" entity-model-reader="main" 
               entity-group-reader="main" entity-eca-reader="main">
        <group-map group-name="org.apache.ofbiz" datasource-name="localderbytest"/>
    </delegator>
</entity-config>
```

## Performance Optimization

### JVM Tuning

Create `framework/start/src/main/java/org/apache/ofbiz/base/start/start.properties`:

```properties
# JVM Arguments for development
java.vm.runArgs=-Xms512M -Xmx2048M -XX:MaxPermSize=512m \
    -Dfile.encoding=UTF-8 \
    -Djava.awt.headless=true \
    -Djava.net.preferIPv4Stack=true
```

### Database Performance

For PostgreSQL development database:

```sql
-- Optimize PostgreSQL for development
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
SELECT pg_reload_conf();
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080
# or
netstat -tulpn | grep 8080

# Kill the process
kill -9 <PID>
```

#### Memory Issues

```bash
# Increase heap size
export JAVA_OPTS="-Xmx2048m -Xms1024m"
./gradlew ofbiz
```

#### Database Connection Issues

```bash
# Test database connectivity
./gradlew "ofbiz --test component=entity testcase=entity-query"

# Reset database
./gradlew cleanAll loadDefault
```

### Debug Logging

Enable debug logging for specific components:

```bash
# Enable entity engine debug logging
./gradlew "ofbiz --start" -Dlog4j.logger.org.apache.ofbiz.entity=DEBUG
```

## Best Practices

### Development Workflow

1. **Branch Strategy**: Use feature branches for development
   ```bash
   git checkout -b feature/new-component
   git push -u origin feature/new-component
   ```

2. **Code Quality**: Use static analysis tools
   ```bash
   ./gradlew checkstyleMain
   ./gradlew spotbugsMain
   ```

3. **Testing**: Write tests for new functionality
   ```bash
   # Create test class in appropriate test directory
   mkdir -p applications/myapp/src/test/java/org/apache/ofbiz/myapp
   ```

4. **Documentation**: Update documentation for changes
   ```bash
   ./gradlew javadoc
   ```

### Security Considerations

- Never commit sensitive configuration files
- Use environment variables for database credentials
- Regularly update dependencies
- Enable HTTPS in development when testing security features

```bash
# Generate self-signed certificate for HTTPS testing
keytool -genkey -alias ofbizssl -keyalg RSA -keystore framework/base/config/ofbizssl.jks
```

This comprehensive setup guide should get you started with OFBiz development. Remember to regularly update your development environment and follow the project's contribution guidelines when submitting changes.