# Development Guide

This comprehensive guide provides developers with essential information for contributing to and working with the Apache OFBiz framework. OFBiz is a powerful, enterprise-grade suite of business applications built on a common architecture using best practices and open source approaches.

## Development Environment Setup

### Prerequisites

Before setting up your OFBiz development environment, ensure you have the following prerequisites installed:

#### Required Software
- **Java Development Kit (JDK) 8 or higher**
  ```bash
  java -version
  javac -version
  ```
- **Apache Ant 1.10.x or higher** (for build automation)
- **Git** (for version control)
- **Database System** (PostgreSQL, MySQL, or Derby for development)

#### Recommended Tools
- **IDE**: IntelliJ IDEA, Eclipse, or Visual Studio Code
- **Database Management Tool**: pgAdmin, MySQL Workbench, or DBeaver
- **HTTP Client**: Postman or curl for API testing

### Environment Configuration

#### 1. Clone the Repository
```bash
git clone https://github.com/apache/ofbiz-framework.git
cd ofbiz-framework
```

#### 2. Set Environment Variables
```bash
export JAVA_HOME=/path/to/your/jdk
export ANT_HOME=/path/to/your/ant
export PATH=$JAVA_HOME/bin:$ANT_HOME/bin:$PATH
```

#### 3. Configure Database Connection
Create or modify `framework/entity/config/entityengine.xml`:

```xml
<datasource name="localderby"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="derby"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    drop-fk-use-foreign-key-keyword="true"
    table-type="TABLE"
    character-set="utf8"
    collate="utf8_general_ci">
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
```

#### 4. IDE Setup

##### IntelliJ IDEA Configuration
1. Import project as Gradle/Ant project
2. Set Project SDK to your JDK version
3. Configure code style settings:
   ```
   File → Settings → Editor → Code Style → Java
   - Use 4 spaces for indentation
   - Line length: 120 characters
   ```

##### Eclipse Configuration
1. Import existing project
2. Set build path to include OFBiz libraries
3. Configure Java Build Path with required JARs

### Initial Build and Setup

#### 1. Load Initial Data
```bash
./gradlew loadDefault
# or using Ant
ant load-demo
```

#### 2. Start OFBiz
```bash
./gradlew ofbiz
# or
java -jar build/libs/ofbiz.jar
```

#### 3. Verify Installation
Navigate to `https://localhost:8443/webtools` and log in with:
- Username: `admin`
- Password: `ofbiz`

## Build System and Dependencies

### Gradle Build System

OFBiz uses Gradle as its primary build system, providing powerful dependency management and build automation capabilities.

#### Key Build Files
- `build.gradle`: Main build configuration
- `settings.gradle`: Project settings and module definitions
- `gradle.properties`: Build properties and JVM settings

#### Common Gradle Tasks

```bash
# Clean build artifacts
./gradlew clean

# Compile all components
./gradlew build

# Run tests
./gradlew test

# Load seed data
./gradlew loadDefault

# Start OFBiz
./gradlew ofbiz

# Create distribution
./gradlew distTar

# Generate Javadocs
./gradlew javadoc
```

#### Custom Gradle Tasks

```groovy
// build.gradle example for custom component
task loadComponentData(type: JavaExec) {
    main = "org.apache.ofbiz.base.start.Start"
    args = ["--load-data", "readers=seed,demo", "component=mycomponent"]
    classpath = sourceSets.main.runtimeClasspath
}
```

### Dependency Management

#### Core Dependencies
OFBiz manages dependencies through Gradle's dependency resolution:

```groovy
dependencies {
    implementation 'org.apache.tomcat:tomcat-catalina:9.0.x'
    implementation 'org.apache.derby:derby:10.14.x'
    implementation 'org.postgresql:postgresql:42.2.x'
    implementation 'mysql:mysql-connector-java:8.0.x'
    implementation 'org.apache.commons:commons-lang3:3.x'
    implementation 'com.fasterxml.jackson.core:jackson-core:2.x'
    
    testImplementation 'junit:junit:4.13.x'
    testImplementation 'org.mockito:mockito-core:3.x'
}
```

#### Plugin Dependencies
For component-specific dependencies, create a `build.gradle` in your plugin:

```groovy
dependencies {
    pluginLibsCompile 'com.example:custom-library:1.0.0'
    pluginLibsRuntime 'org.example:runtime-dependency:2.0.0'
}
```

### Component Structure

#### Standard Component Layout
```
component-name/
├── build.gradle
├── ofbiz-component.xml
├── config/
├── data/
├── entitydef/
├── groovyScripts/
├── minilang/
├── script/
├── servicedef/
├── src/
│   └── main/java/
├── testdef/
├── webapp/
└── widget/
```

#### Component Configuration
`ofbiz-component.xml` example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofbiz-component name="mycomponent"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://ofbiz.apache.org/dtds/ofbiz-component.xsd">
    
    <resource-loader name="main" type="component"/>
    
    <classpath type="jar" location="build/lib/*"/>
    <classpath type="dir" location="config"/>
    
    <entity-resource type="model" reader-name="main" loader="main" location="entitydef/entitymodel.xml"/>
    <entity-resource type="data" reader-name="seed" loader="main" location="data/MyComponentTypeData.xml"/>
    
    <service-resource type="model" loader="main" location="servicedef/services.xml"/>
    
    <webapp name="mycomponent"
        title="My Component"
        server="default-server"
        location="webapp/mycomponent"
        base-permission="MYCOMPONENT"
        mount-point="/mycomponent"/>
</ofbiz-component>
```

## Framework Development Patterns

### Entity Engine Patterns

#### Entity Definition
Define entities in `entitydef/entitymodel.xml`:

```xml
<entity entity-name="MyEntity" package-name="org.apache.ofbiz.mycomponent">
    <field name="myEntityId" type="id-ne"/>
    <field name="name" type="name"/>
    <field name="description" type="description"/>
    <field name="statusId" type="id"/>
    <field name="createdDate" type="date-time"/>
    <field name="lastModifiedDate" type="date-time"/>
    
    <prim-key field="myEntityId"/>
    
    <relation type="one" fk-name="MY_ENTITY_STATUS" rel-entity-name="StatusItem">
        <key-map field-name="statusId"/>
    </relation>
    
    <index name="MY_ENTITY_NAME_IDX">
        <index-field name="name"/>
    </index>
</entity>
```

#### Entity Operations in Java

```java
// Create
GenericValue myEntity = delegator.makeValue("MyEntity");
myEntity.set("myEntityId", delegator.getNextSeqId("MyEntity"));
myEntity.set("name", "Example Name");
myEntity.set("description", "Example Description");
myEntity.set("statusId", "ACTIVE");
myEntity.set("createdDate", UtilDateTime.nowTimestamp());
myEntity.create();

// Read
GenericValue entity = EntityQuery.use(delegator)
    .from("MyEntity")
    .where("myEntityId", entityId)
    .queryOne();

// Update
entity.set("description", "Updated Description");
entity.set("lastModifiedDate", UtilDateTime.nowTimestamp());
entity.store();

// Delete
entity.remove();

// Complex Query
List<GenericValue> entities = EntityQuery.use(delegator)
    .from("MyEntity")
    .where(EntityCondition.makeCondition("statusId", EntityOperator.EQUALS, "ACTIVE"))
    .orderBy("name")
    .queryList();
```

### Service Engine Patterns

#### Service Definition
Define services in `servicedef/services.xml`:

```xml
<service name="createMyEntity" default-entity-name="MyEntity" engine="java"
         location="org.apache.ofbiz.mycomponent.MyEntityServices" invoke="createMyEntity">
    <description>Create My Entity</description>
    <auto-attributes include="pk" mode="OUT" optional="false"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
    <attribute name="name" type="String" mode="IN" optional="false"/>
    <override name="description" optional="true"/>
</service>

<service name="updateMyEntity" default-entity-name="MyEntity" engine="java"
         location="org.apache.ofbiz.mycomponent.MyEntityServices" invoke="updateMyEntity">
    <description>Update My Entity</description>
    <auto-attributes include="pk" mode="IN" optional="false"/>
    <auto-attributes include="nonpk" mode="IN" optional="true"/>
</service>
```

#### Service Implementation

```java
public class MyEntityServices {
    
    public static final String module = MyEntityServices.class.getName();
    
    public static Map<String, Object> createMyEntity(DispatchContext dctx, Map<String, ? extends Object> context) {
        Delegator delegator = dctx.getDelegator();
        LocalDispatcher dispatcher = dctx.getDispatcher();
        GenericValue userLogin = (GenericValue) context.get("userLogin");
        
        try {
            // Validate input
            String name = (String) context.get("name");
            if (UtilValidate.isEmpty(name)) {
                return ServiceUtil.returnError("Name is required");
            }
            
            // Create entity
            GenericValue myEntity = delegator.makeValue("MyEntity");
            myEntity.setPKFields(context);
            myEntity.setNonPKFields(context);
            myEntity.set("myEntityId", delegator.getNextSeqId("MyEntity"));
            myEntity.set("createdDate", UtilDateTime.nowTimestamp());
            
            myEntity = delegator.createSetNextSeqId(myEntity);
            
            Map<String, Object> result = ServiceUtil.returnSuccess("Entity created successfully");
            result.put("myEntityId", myEntity.get("myEntityId"));
            return result;
            
        } catch (GenericEntityException e) {
            Debug.logError(e, "Error creating entity: " + e.getMessage(), module);
            return ServiceUtil.returnError("Error creating entity: " + e.getMessage());
        }
    }
    
    public static Map<String, Object> updateMyEntity(DispatchContext dctx, Map<String, ? extends Object> context) {
        Delegator delegator = dctx.getDelegator();
        String myEntityId = (String) context.get("myEntityId");
        
        try {
            GenericValue myEntity = EntityQuery.use(delegator)
                .from("MyEntity")
                .where("myEntityId", myEntityId)
                .queryOne();
                
            if (myEntity == null) {
                return ServiceUtil.returnError("Entity not found");
            }
            
            myEntity.setNonPKFields(context);
            myEntity.set("lastModifiedDate", UtilDateTime.nowTimestamp());
            myEntity.store();
            
            return ServiceUtil.returnSuccess("Entity updated successfully");
            
        } catch (GenericEntityException e) {
            Debug.logError(e, "Error updating entity: " + e.getMessage(), module);
            return ServiceUtil.returnError("Error updating entity: " + e.getMessage());
        }
    }
}
```

### Widget Framework Patterns

#### Screen Definition
Define screens in `widget/MyScreens.xml`:

```xml
<screens xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns="http://ofbiz.apache.org/Widget-Screen"
         xsi:schemaLocation="http://ofbiz.apache.org/Widget-Screen http://ofbiz.apache.org/dtds/widget-screen.xsd">
    
    <screen name="MyEntityList">
        <section>
            <actions>
                <entity-condition entity-name="MyEntity" list="myEntities">
                    <condition-expr field-name="statusId" value="ACTIVE"/>
                    <order-by field-name="name"/>
                </entity-condition>
            </actions>
            <widgets>
                <decorator-screen name="CommonDecorator" location="${parameters.mainDecoratorLocation}">
                    <decorator-section name="body">
                        <include-form name="ListMyEntities" location="component://mycomponent/widget/MyForms.xml"/>
                    </decorator-section>
                </decorator-screen>
            </widgets>
        </section>
    </screen>
</screens>
```

#### Form Definition
Define forms in `widget/MyForms.xml`:

```xml
<forms xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns="http://ofbiz.apache.org/Widget-Form"
       xsi:schemaLocation="http://ofbiz.apache.org/Widget-Form http://ofbiz.apache.org/dtds/widget-form.xsd">
    
    <form name="ListMyEntities" type="list" list-name="myEntities" paginate-target="MyEntityList">
        <actions>
            <service service-name="performFind" result-map="result" result-map-list="listIt">
                <field-map field-name="inputFields" from-field="myEntityCtx"/>
                <field-map field-name="entityName" value="MyEntity"/>
            </service>
        </actions>
        
        <field name="myEntityId" widget-style="buttontext">
            <hyperlink target="EditMyEntity" description="${myEntityId}">
                <parameter param-name="myEntityId"/>
            </hyperlink>
        </field>
        
        <field name="name" title="Name"><display/></field>
        <field name="description" title="Description"><display/></field>
        <field name="statusId" title="Status">
            <display-entity entity-name="StatusItem" description="${description}"/>
        </field>
        
        <field name="editAction" title