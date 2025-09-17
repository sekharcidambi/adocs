# Build System and Dependencies

## Overview

Apache OFBiz Framework utilizes a sophisticated build system based on Gradle, providing comprehensive dependency management, build automation, and deployment capabilities. The build system is designed to support the complex requirements of an enterprise-grade ERP and CRM framework, handling multi-module compilation, plugin management, and database operations.

## Build System Architecture

### Gradle Build System

OFBiz leverages Gradle as its primary build automation tool, replacing the legacy Ant-based system. The Gradle build provides:

- **Multi-project builds** for modular architecture
- **Dependency resolution** with Maven Central and custom repositories
- **Task automation** for development, testing, and deployment
- **Plugin ecosystem** integration for specialized functionality

```gradle
// Root build.gradle structure
plugins {
    id 'java'
    id 'groovy'
    id 'eclipse'
    id 'idea'
}

allprojects {
    apply plugin: 'java'
    apply plugin: 'groovy'
    
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}
```

### Build Configuration Files

#### Primary Build Files

- **`build.gradle`** - Root build configuration
- **`settings.gradle`** - Project structure definition
- **`gradle.properties`** - Build properties and JVM settings
- **`gradle/wrapper/`** - Gradle Wrapper configuration

#### Module-Specific Configuration

Each OFBiz component maintains its own build configuration:

```
framework/
├── base/build.gradle
├── entity/build.gradle
├── service/build.gradle
├── webapp/build.gradle
└── widget/build.gradle
```

## Core Dependencies

### Java Runtime Dependencies

OFBiz requires specific Java runtime components and libraries:

```gradle
dependencies {
    // Core Java EE APIs
    implementation 'javax.servlet:javax.servlet-api:4.0.1'
    implementation 'javax.transaction:javax.transaction-api:1.3'
    implementation 'javax.mail:javax.mail-api:1.6.2'
    
    // XML Processing
    implementation 'xerces:xercesImpl:2.12.2'
    implementation 'xml-apis:xml-apis:1.4.01'
    
    // Database Connectivity
    implementation 'org.apache.commons:commons-dbcp2:2.9.0'
    implementation 'commons-pool:commons-pool:1.6'
}
```

### Database Drivers

OFBiz supports multiple database systems through JDBC drivers:

```gradle
dependencies {
    // Database drivers (runtime scope)
    runtimeOnly 'org.apache.derby:derby:10.15.2.0'
    runtimeOnly 'org.postgresql:postgresql:42.3.1'
    runtimeOnly 'mysql:mysql-connector-java:8.0.28'
    runtimeOnly 'com.oracle.database.jdbc:ojdbc8:21.5.0.0'
    runtimeOnly 'com.microsoft.sqlserver:mssql-jdbc:9.4.1.jre11'
}
```

### Web Framework Dependencies

Essential libraries for web application functionality:

```gradle
dependencies {
    // Web framework components
    implementation 'org.apache.tomcat:tomcat-catalina:9.0.58'
    implementation 'org.apache.tomcat:tomcat-jasper:9.0.58'
    implementation 'org.freemarker:freemarker:2.3.31'
    
    // Security
    implementation 'org.apache.shiro:shiro-core:1.8.0'
    implementation 'org.apache.shiro:shiro-web:1.8.0'
    
    // HTTP Client
    implementation 'org.apache.httpcomponents:httpclient:4.5.13'
    implementation 'org.apache.httpcomponents:httpcore:4.4.15'
}
```

## Build Tasks and Commands

### Essential Build Commands

#### Initial Setup and Build

```bash
# Clean and build the entire framework
./gradlew clean build

# Load initial data and start OFBiz
./gradlew loadAll ofbiz

# Start OFBiz in development mode
./gradlew ofbiz --start-pos=both
```

#### Development Tasks

```bash
# Compile Java sources
./gradlew compileJava

# Run tests
./gradlew test

# Generate Eclipse project files
./gradlew eclipse

# Generate IntelliJ IDEA project files
./gradlew idea
```

#### Database Operations

```bash
# Load seed data
./gradlew "ofbiz --load-data"

# Load demo data
./gradlew "ofbiz --load-data --load-file=demo"

# Create database tables
./gradlew "ofbiz --create-tables"
```

### Custom Gradle Tasks

OFBiz defines specialized Gradle tasks for framework-specific operations:

```gradle
// Custom task definitions in build.gradle
task loadAll(group: ofbizServer, description: 'Load all data') {
    dependsOn 'ofbiz --load-data'
}

task createTables(group: ofbizServer, description: 'Create database tables') {
    dependsOn 'ofbiz --create-tables'
}

task runTests(type: Test, group: verification, description: 'Run OFBiz tests') {
    testClassesDirs = sourceSets.test.output.classesDirs
    classpath = sourceSets.test.runtimeClasspath
}
```

## Dependency Management

### Repository Configuration

OFBiz configures multiple repositories for dependency resolution:

```gradle
repositories {
    mavenCentral()
    
    // Apache repositories for snapshot versions
    maven {
        url "https://repository.apache.org/content/repositories/snapshots/"
    }
    
    // Local repository for custom JARs
    flatDir {
        dirs 'lib'
    }
}
```

### Version Management

Centralized version management through `gradle.properties`:

```properties
# Core dependency versions
commonsLangVersion=3.12.0
commonsCollectionsVersion=4.4
freemarkerVersion=2.3.31
groovyVersion=3.0.9
jacksonVersion=2.13.1
junitVersion=5.8.2
log4jVersion=2.17.1
```

### Plugin Dependencies

OFBiz supports a plugin architecture with independent dependency management:

```gradle
// Plugin-specific dependencies
project(':plugins:ecommerce') {
    dependencies {
        implementation project(':framework:base')
        implementation project(':framework:entity')
        implementation project(':framework:webapp')
        
        // Plugin-specific libraries
        implementation 'com.stripe:stripe-java:20.92.0'
        implementation 'com.paypal.sdk:paypal-core:1.7.2'
    }
}
```

## Build Optimization

### Performance Configuration

Optimize build performance through `gradle.properties`:

```properties
# JVM settings for build performance
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g -XX:+HeapDumpOnOutOfMemoryError

# Gradle daemon and parallel builds
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.configureondemand=true

# Build cache
org.gradle.caching=true
```

### Incremental Compilation

Configure incremental compilation for faster development cycles:

```gradle
compileJava {
    options.incremental = true
    options.compilerArgs += ['-Xlint:unchecked', '-Xlint:deprecation']
}

compileGroovy {
    options.incremental = true
}
```

## Testing Framework Integration

### Test Dependencies

OFBiz integrates comprehensive testing frameworks:

```gradle
dependencies {
    testImplementation 'org.junit.jupiter:junit-jupiter:5.8.2'
    testImplementation 'org.mockito:mockito-core:4.3.1'
    testImplementation 'org.mockito:mockito-junit-jupiter:4.3.1'
    testImplementation 'org.hamcrest:hamcrest:2.2'
    
    // OFBiz-specific test utilities
    testImplementation project(':framework:testtools')
}
```

### Test Configuration

```gradle
test {
    useJUnitPlatform()
    
    testLogging {
        events "passed", "skipped", "failed"
        exceptionFormat "full"
    }
    
    // Test JVM settings
    jvmArgs '-Xmx2g', '-XX:MaxMetaspaceSize=512m'
    
    // System properties for tests
    systemProperty 'ofbiz.home', project.projectDir
    systemProperty 'derby.system.home', "${project.projectDir}/runtime/data/derby"
}
```

## Deployment and Distribution

### WAR File Generation

Generate deployable WAR files for external application servers:

```gradle
task createWarFiles(type: Copy) {
    description 'Create WAR files for deployment'
    
    from 'build/libs'
    into 'runtime/wars'
    include '*.war'
}
```

### Docker Integration

Build configuration supports Docker containerization:

```gradle
task buildDockerImage(type: Exec) {
    description 'Build Docker image'
    commandLine 'docker', 'build', '-t', 'ofbiz:latest', '.'
}
```

## Troubleshooting Build Issues

### Common Build Problems

1. **Memory Issues**: Increase JVM heap size in `gradle.properties`
2. **Dependency Conflicts**: Use `./gradlew dependencies` to analyze dependency tree
3. **Compilation Errors**: Ensure Java 11+ compatibility
4. **Database Connection**: Verify database driver dependencies

### Diagnostic Commands

```bash
# Analyze dependency tree
./gradlew dependencies

# Check for dependency conflicts
./gradlew dependencyInsight --dependency commons-lang

# Verbose build output
./gradlew build --info --stacktrace

# Clean build cache
./gradlew clean cleanBuildCache
```

### Build Cache Management

```bash
# Clear Gradle cache
rm -rf ~/.gradle/caches/

# Refresh dependencies
./gradlew build --refresh-dependencies
```

This comprehensive build system ensures reliable, scalable development and deployment of the OFBiz framework while maintaining flexibility for customization and extension through its plugin architecture.