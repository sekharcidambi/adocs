# Database Setup

This section provides comprehensive guidance for setting up and configuring databases for the Apache OFBiz framework. OFBiz supports multiple database systems and provides flexible configuration options for different deployment scenarios.

## Overview

Apache OFBiz uses an entity engine that abstracts database operations and supports multiple database management systems (DBMS). The framework includes built-in support for popular databases and provides tools for schema generation, data loading, and database maintenance.

### Supported Database Systems

OFBiz officially supports the following database systems:

- **Apache Derby** (default, embedded)
- **PostgreSQL** (recommended for production)
- **MySQL/MariaDB**
- **Oracle Database**
- **Microsoft SQL Server**
- **H2 Database** (for testing)

## Quick Start with Derby

For development and testing purposes, OFBiz comes pre-configured with Apache Derby, which requires minimal setup.

### Default Derby Configuration

The default configuration uses an embedded Derby database that starts automatically with OFBiz:

```bash
# Start OFBiz with default Derby database
./gradlew ofbiz
```

The Derby database files are stored in:
```
runtime/data/derby/ofbiz/
```

## Production Database Setup

For production environments, it's recommended to use a dedicated database server like PostgreSQL or MySQL.

### PostgreSQL Setup

#### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
```

#### 2. Create Database and User

```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create database
CREATE DATABASE ofbiz;

-- Create user
CREATE USER ofbiz WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ofbiz TO ofbiz;
ALTER USER ofbiz CREATEDB;

-- Exit psql
\q
```

#### 3. Configure OFBiz for PostgreSQL

Edit the `framework/entity/config/entityengine.xml` file:

```xml
<delegator name="default" entity-model-reader="main" entity-group-reader="main" entity-eca-reader="main" distributed-cache-clear-enabled="false">
    <group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>
    <group-map group-name="org.apache.ofbiz.olap" datasource-name="localpostgresolap"/>
    <group-map group-name="org.apache.ofbiz.tenant" datasource-name="localpostgrestenant"/>
</delegator>

<datasource name="localpostgres"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    schema-name="public"
    field-type-name="postgres"
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
        jdbc-driver="org.postgresql.Driver"
        jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
        jdbc-username="ofbiz"
        jdbc-password="your_secure_password"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

### MySQL/MariaDB Setup

#### 1. Install MySQL/MariaDB

```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# CentOS/RHEL
sudo yum install mariadb-server mariadb
```

#### 2. Create Database and User

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE ofbiz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'ofbiz'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON ofbiz.* TO 'ofbiz'@'localhost';
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

#### 3. Configure OFBiz for MySQL

Update `framework/entity/config/entityengine.xml`:

```xml
<datasource name="localmysql"
    helper-class="org.apache.ofbiz.entity.datasource.GenericHelperDAO"
    field-type-name="mysql"
    check-on-start="true"
    add-missing-on-start="true"
    use-pk-constraint-names="false"
    use-indices-unique="false"
    alias-view-columns="false"
    drop-fk-use-foreign-key-keyword="true"
    table-type="InnoDB"
    character-set="utf8mb4"
    collate="utf8mb4_unicode_ci">
    <read-data reader-name="tenant"/>
    <read-data reader-name="seed"/>
    <read-data reader-name="seed-initial"/>
    <read-data reader-name="demo"/>
    <read-data reader-name="ext"/>
    <inline-jdbc
        jdbc-driver="com.mysql.cj.jdbc.Driver"
        jdbc-uri="jdbc:mysql://127.0.0.1:3306/ofbiz?characterEncoding=UTF-8&amp;useSSL=false&amp;serverTimezone=UTC"
        jdbc-username="ofbiz"
        jdbc-password="your_secure_password"
        isolation-level="ReadCommitted"
        pool-minsize="2"
        pool-maxsize="250"
        time-between-eviction-runs-millis="600000"/>
</datasource>
```

## Database Initialization

### Schema and Data Loading

After configuring your database connection, initialize the database schema and load initial data:

```bash
# Load all data (schema + seed + demo data)
./gradlew loadAll

# Load only schema and seed data (no demo data)
./gradlew "ofbiz --load-data readers=seed,seed-initial,ext"

# Load only schema
./gradlew "ofbiz --load-data readers=tenant"
```

### Data Types

OFBiz supports different data loading categories:

- **tenant**: Basic schema and tenant configuration
- **seed**: Essential system data required for operation
- **seed-initial**: Initial configuration data
- **demo**: Sample/demonstration data
- **ext**: Extension data from plugins

## Advanced Configuration

### Connection Pool Settings

Configure connection pool parameters for optimal performance:

```xml
<inline-jdbc
    jdbc-driver="org.postgresql.Driver"
    jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz"
    jdbc-username="ofbiz"
    jdbc-password="your_secure_password"
    isolation-level="ReadCommitted"
    pool-minsize="5"
    pool-maxsize="50"
    pool-sleeptime="300000"
    pool-lifetime="600000"
    pool-deadlock-maxwait="300000"
    pool-deadlock-retrywait="10000"
    time-between-eviction-runs-millis="600000"/>
```

### Multiple Database Configuration

OFBiz supports multiple databases for different purposes:

```xml
<!-- Main operational database -->
<group-map group-name="org.apache.ofbiz" datasource-name="localpostgres"/>

<!-- OLAP/Analytics database -->
<group-map group-name="org.apache.ofbiz.olap" datasource-name="localpostgresolap"/>

<!-- Tenant-specific database -->
<group-map group-name="org.apache.ofbiz.tenant" datasource-name="localpostgrestenant"/>
```

### SSL/TLS Configuration

For secure database connections, configure SSL parameters:

```xml
<inline-jdbc
    jdbc-driver="org.postgresql.Driver"
    jdbc-uri="jdbc:postgresql://127.0.0.1:5432/ofbiz?ssl=true&amp;sslmode=require"
    jdbc-username="ofbiz"
    jdbc-password="your_secure_password"
    isolation-level="ReadCommitted"/>
```

## Database Maintenance

### Backup and Restore

#### PostgreSQL Backup

```bash
# Create backup
pg_dump -U ofbiz -h localhost ofbiz > ofbiz_backup.sql

# Restore backup
psql -U ofbiz -h localhost ofbiz < ofbiz_backup.sql
```

#### MySQL Backup

```bash
# Create backup
mysqldump -u ofbiz -p ofbiz > ofbiz_backup.sql

# Restore backup
mysql -u ofbiz -p ofbiz < ofbiz_backup.sql
```

### Database Updates

When updating OFBiz versions, run database migration scripts:

```bash
# Check for database updates
./gradlew "ofbiz --load-data readers=seed,seed-initial,ext --load-data-update-mode=update"
```

## Troubleshooting

### Common Issues

#### Connection Timeout

If experiencing connection timeouts, adjust pool settings:

```xml
<inline-jdbc
    pool-sleeptime="300000"
    pool-lifetime="600000"
    time-between-eviction-runs-millis="300000"/>
```

#### Character Encoding Issues

Ensure proper UTF-8 configuration:

```xml
<!-- PostgreSQL -->
<datasource character-set="utf8" collate="utf8_general_ci">

<!-- MySQL -->
<datasource character-set="utf8mb4" collate="utf8mb4_unicode_ci">
```

#### Memory Issues

For large datasets, increase JVM memory:

```bash
export JAVA_OPTS="-Xms1024M -Xmx2048M"
./gradlew ofbiz
```

### Logging Configuration

Enable database logging for debugging:

```xml
<!-- In framework/base/config/log4j2.xml -->
<Logger name="org.apache.ofbiz.entity" level="DEBUG"/>
<Logger name="org.apache.ofbiz.entity.transaction" level="INFO"/>
```

## Performance Optimization

### Database Indexes

OFBiz automatically creates necessary indexes, but you can add custom indexes:

```sql
-- Example: Add index for frequently queried fields
CREATE INDEX idx_order_date ON order_header(order_date);
CREATE INDEX idx_party_id ON person(party_id);
```

### Query Optimization

Monitor slow queries and optimize entity definitions:

```xml
<!-- Example: Optimize view entity -->
<view-entity entity-name="OrderHeaderAndItems" package-name="org.apache.ofbiz.order.order">
    <member-entity entity-alias="OH" entity-name="OrderHeader"/>
    <member-entity entity-alias="OI" entity-name="OrderItem"/>
    <alias-all entity-alias="OH"/>
    <alias-all entity-alias="OI"/>
    <view-link entity-alias="OH" rel-entity-alias="OI">
        <key-map field-name="orderId"/>
    </view-link>
</view-entity>
```

## Security Considerations

### Database Security

1. **Use strong passwords** for database users
2. **Limit database user privileges** to only necessary operations
3. **Enable SSL/TLS** for database connections
4. **Regular security updates** for database software
5. **Network security** - restrict database access to application servers only

### Configuration Security

Store sensitive configuration in environment variables:

```xml
<inline-jdbc
    jdbc-username="${env:DB_USERNAME}"
    jdbc-password="${env:DB_PASSWORD}"/>
```

## References

- [OFBiz Entity Engine Documentation](https://cwiki.apache.org/confluence/display/OFBIZ/Entity+Engine+Guide)
- [Database Configuration Examples](https://github.com/apache/ofbiz-framework/tree/trunk/framework/entity/config)
- [Performance Tuning Guide](https://cwiki.apache.org/confluence/display/OFBIZ/Performance+Tips)