## Gradle Build Configuration

## Overview

Apache OFBiz utilizes Gradle as its primary build automation tool, replacing the legacy Ant-based build system to provide more flexible dependency management and streamlined build processes. The Gradle configuration in OFBiz is specifically designed to handle the complex multi-module architecture of an enterprise ERP system, managing dependencies across presentation, business logic, and data access layers while supporting multiple deployment scenarios.

The build configuration supports OFBiz's modular plugin architecture, allowing for dynamic loading of business components, custom applications, and third-party extensions. This approach aligns with the framework's goal of providing a flexible, scalable ERP solution that can be customized for various business domains.

## Core Build Files Structure

### Root Build Configuration

The primary `build.gradle` file at the repository root orchestrates the entire build process:

```gradle
plugins {
    id 'java-library'
    id 'groovy'
    id 'eclipse'
    id 'idea'
}

allprojects {
    apply plugin: 'java-library'
    apply plugin: 'groovy'
    
    repositories {
        mavenCentral()
        jcenter()
    }
    
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}
```

### Component Module Configuration

Each OFBiz component (accounting, manufacturing, order, etc.) maintains its own `build.gradle` file that defines:

- Component-specific dependencies
- Resource compilation requirements
- Entity and service definitions
- Web application configurations

```gradle
dependencies {
    implementation project(':framework:base')
    implementation project(':framework:entity')
    implementation project(':framework:service')
    implementation project(':framework:webapp')
    
    // Component-specific dependencies
    implementation 'org.apache.commons:commons-csv:1.8'
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.12.3'
}
```

## Dependency Management Strategy

### Framework Dependencies

OFBiz's Gradle configuration manages complex dependency relationships between framework layers:

- **Base Framework**: Core utilities, configuration management, and logging
- **Entity Engine**: Database abstraction and ORM functionality
- **Service Engine**: Business logic execution and transaction management
- **Widget Framework**: UI component rendering and form handling

### External Library Management

The build system handles integration with enterprise-grade libraries:

```gradle
ext {
    commonsCodecVersion = '1.15'
    commonsCollectionsVersion = '4.4'
    freemarkerVersion = '2.3.31'
    log4jVersion = '2.14.1'
    tomcatVersion = '9.0.46'
}

dependencies {
    implementation "org.apache.commons:commons-collections4:${commonsCollectionsVersion}"
    implementation "org.freemarker:freemarker:${freemarkerVersion}"
    implementation "org.apache.logging.log4j:log4j-core:${log4jVersion}"
    implementation "org.apache.tomcat:tomcat-catalina:${tomcatVersion}"
}
```

## Multi-Database Support Configuration

The Gradle build accommodates OFBiz's multi-database architecture through conditional dependency loading:

```gradle
configurations {
    derby
    mysql
    postgresql
}

dependencies {
    derby 'org.apache.derby:derby:10.14.2.0'
    derby 'org.apache.derby:derbytools:10.14.2.0'
    
    mysql 'mysql:mysql-connector-java:8.0.25'
    
    postgresql 'org.postgresql:postgresql:42.2.20'
}
```

## Custom Tasks for ERP Operations

### Data Loading Tasks

OFBiz includes specialized Gradle tasks for enterprise data management:

```gradle
task loadSeedData(type: JavaExec) {
    description = 'Load seed data for OFBiz components'
    classpath = sourceSets.main.runtimeClasspath
    main = 'org.apache.ofbiz.base.start.Start'
    args = ['--load-data', 'readers=seed']
}

task loadDemoData(type: JavaExec) {
    description = 'Load demo data for testing and development'
    classpath = sourceSets.main.runtimeClasspath
    main = 'org.apache.ofbiz.base.start.Start'
    args = ['--load-data', 'readers=seed,demo']
}
```

### Component Management Tasks

```gradle
task createComponent(type: JavaExec) {
    description = 'Create a new OFBiz component'
    classpath = sourceSets.main.runtimeClasspath
    main = 'org.apache.ofbiz.base.component.ComponentConfig'
    
    doFirst {
        if (!project.hasProperty('componentName')) {
            throw new GradleException('Component name must be specified with -PcomponentName=<name>')
        }
        args = ['--create-component', project.componentName]
    }
}
```

## Plugin and Extension Support

### Hot Deployment Configuration

The build system supports OFBiz's hot deployment capabilities for development environments:

```gradle
task hotDeploy(type: Copy) {
    description = 'Deploy component changes without full restart'
    from 'src/main/java'
    into "${buildDir}/hot-deploy/classes"
    
    doLast {
        // Trigger component reload
        ant.touch(file: "${buildDir}/hot-deploy/.reload")
    }
}
```

### Custom Plugin Integration

```gradle
subprojects { project ->
    if (project.file('plugin.xml').exists()) {
        apply plugin: 'ofbiz-plugin'
        
        dependencies {
            implementation project(':framework:base')
            implementation project(':framework:entity')
            implementation project(':framework:service')
        }
        
        jar {
            manifest {
                attributes(
                    'OFBiz-Plugin': 'true',
                    'Plugin-Version': project.version,
                    'Plugin-Dependencies': getPluginDependencies()
                )
            }
        }
    }
}
```

## Build Optimization and Performance

### Parallel Execution

The Gradle configuration leverages parallel execution for OFBiz's multi-module structure:

```gradle
org.gradle.parallel=true
org.gradle.configureondemand=true
org.gradle.caching=true
org.gradle.workers.max=4
```

### Incremental Compilation

Component-specific incremental compilation reduces build times during development:

```gradle
compileJava {
    options.incremental = true
    options.compilerArgs += ['-Xlint:unchecked', '-Xlint:deprecation']
}

compileGroovy {
    options.incremental = true
}
```

## Integration with Development Workflow

The Gradle build integrates seamlessly with OFBiz development practices, supporting continuous integration through Jenkins pipelines, Docker containerization for deployment, and IDE integration for Eclipse and IntelliJ IDEA. The configuration automatically handles resource compilation, including Freemarker templates, XML entity definitions, and JavaScript/CSS assets for the web presentation layer.

This comprehensive build system ensures that OFBiz maintains its position as a robust, enterprise-ready ERP solution while providing developers with modern build tooling and practices.

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 17:01:26*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*