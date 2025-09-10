### ORM Integration (Hibernate)

## Overview

Apache OFBiz's ORM integration with Hibernate provides a sophisticated data persistence layer that complements the framework's native Entity Engine. While OFBiz traditionally relies on its own Entity Engine for database operations, Hibernate integration offers enhanced object-relational mapping capabilities, particularly beneficial for complex enterprise scenarios requiring advanced caching, lazy loading, and sophisticated query optimization.

The Hibernate integration in OFBiz follows the multi-tier architecture pattern, sitting within the Data Access Layer and providing seamless connectivity between the Business Logic Layer and various supported databases including MySQL, PostgreSQL, and Derby.

## Architecture Integration

### Entity Engine vs Hibernate Coexistence

OFBiz implements a dual-persistence strategy where both the native Entity Engine and Hibernate can coexist:

```java
// Native Entity Engine approach
GenericValue product = EntityQuery.use(delegator)
    .from("Product")
    .where("productId", productId)
    .queryOne();

// Hibernate integration approach
@Entity
@Table(name = "PRODUCT")
public class Product {
    @Id
    @Column(name = "PRODUCT_ID")
    private String productId;
    
    @Column(name = "PRODUCT_NAME")
    private String productName;
    
    // Hibernate-managed relationships
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private Set<ProductCategory> categories;
}
```

### Configuration Structure

The Hibernate integration is configured through multiple layers within the OFBiz framework:

```xml
<!-- framework/entity/config/entityengine.xml -->
<entity-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <resource-loader name="hibernate" class="org.apache.ofbiz.entity.hibernate.HibernateResourceLoader"/>
    
    <delegator name="hibernate-delegator" entity-model-reader="main" 
               entity-group-reader="main" entity-eca-reader="main">
        <group-map group-name="org.apache.ofbiz" datasource-name="hibernatelocal"/>
    </delegator>
    
    <datasource name="hibernatelocal"
                helper-class="org.apache.ofbiz.entity.hibernate.HibernateHelper"
                schema-name="public"
                check-on-start="true"
                add-missing-on-start="true">
        <read-data reader-name="tenant"/>
        <read-data reader-name="seed"/>
        <read-data reader-name="seed-initial"/>
    </datasource>
</entity-config>
```

## Implementation Patterns

### Entity Mapping Strategy

OFBiz employs a hybrid mapping strategy that leverages existing entity definitions while providing Hibernate-specific enhancements:

```java
// applications/product/src/main/java/org/apache/ofbiz/product/entity/
@Entity
@Table(name = "PRODUCT_STORE")
@NamedQueries({
    @NamedQuery(name = "ProductStore.findByCompany", 
                query = "SELECT ps FROM ProductStore ps WHERE ps.companyName = :companyName"),
    @NamedQuery(name = "ProductStore.findActive", 
                query = "SELECT ps FROM ProductStore ps WHERE ps.isActive = 'Y'")
})
public class ProductStore implements Serializable {
    
    @Id
    @Column(name = "PRODUCT_STORE_ID", length = 20)
    private String productStoreId;
    
    @Column(name = "STORE_NAME", length = 100)
    private String storeName;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "DEFAULT_CURRENCY_UOM_ID")
    private Uom defaultCurrency;
    
    @OneToMany(mappedBy = "productStore", cascade = CascadeType.ALL)
    private Set<ProductStoreCatalog> catalogs = new HashSet<>();
}
```

### Session Management Integration

The framework integrates Hibernate sessions with OFBiz's transaction management:

```java
// framework/entity/src/main/java/org/apache/ofbiz/entity/hibernate/
public class HibernateSessionManager {
    
    public static Session getCurrentSession(String delegatorName) {
        TransactionUtil transaction = TransactionUtil.getCurrentTransaction();
        SessionFactory sessionFactory = getSessionFactory(delegatorName);
        
        Session session = sessionFactory.getCurrentSession();
        if (transaction != null) {
            session.beginTransaction();
        }
        return session;
    }
    
    public static void closeSession(String delegatorName) {
        Session session = getCurrentSession(delegatorName);
        if (session != null && session.isOpen()) {
            if (session.getTransaction().isActive()) {
                session.getTransaction().commit();
            }
            session.close();
        }
    }
}
```

## Service Layer Integration

### Hibernate-Enabled Services

Services can leverage Hibernate for complex data operations while maintaining compatibility with existing OFBiz patterns:

```java
// applications/order/src/main/java/org/apache/ofbiz/order/order/
public class OrderServices {
    
    public static Map<String, Object> createOrderWithHibernate(DispatchContext dctx, 
                                                               Map<String, ? extends Object> context) {
        Delegator delegator = dctx.getDelegator();
        LocalDispatcher dispatcher = dctx.getDispatcher();
        
        try {
            Session session = HibernateUtil.getSessionFactory().getCurrentSession();
            session.beginTransaction();
            
            // Complex order creation with Hibernate relationships
            Order order = new Order();
            order.setOrderId(delegator.getNextSeqId("OrderHeader"));
            order.setOrderDate(UtilDateTime.nowTimestamp());
            
            // Leverage Hibernate's cascade operations
            Set<OrderItem> items = createOrderItems(context);
            order.setOrderItems(items);
            
            session.save(order);
            session.getTransaction().commit();
            
            return ServiceUtil.returnSuccess("Order created successfully");
            
        } catch (Exception e) {
            return ServiceUtil.returnError("Error creating order: " + e.getMessage());
        }
    }
}
```

## Performance Optimization

### Caching Strategy

OFBiz integrates Hibernate's second-level cache with its existing caching mechanisms:

```xml
<!-- framework/entity/config/hibernate.cfg.xml -->
<hibernate-configuration>
    <session-factory>
        <property name="hibernate.cache.use_second_level_cache">true</property>
        <property name="hibernate.cache.use_query_cache">true</property>
        <property name="hibernate.cache.region.factory_class">
            org.hibernate.cache.ehcache.EhCacheRegionFactory
        </property>
        
        <!-- Integration with OFBiz cache -->
        <property name="hibernate.cache.provider_configuration_file_resource_path">
            framework/base/config/cache.xml
        </property>
    </session-factory>
</hibernate-configuration>
```

### Query Optimization

The integration provides sophisticated querying capabilities for complex ERP operations:

```java
// Complex inventory query with Hibernate Criteria API
public List<InventoryItem> findLowStockItems(String facilityId, BigDecimal threshold) {
    Session session = HibernateUtil.getCurrentSession();
    
    CriteriaBuilder cb = session.getCriteriaBuilder();
    CriteriaQuery<InventoryItem> cq = cb.createQuery(InventoryItem.class);
    Root<InventoryItem> root = cq.from(InventoryItem.class);
    
    cq.select(root)
      .where(cb.and(
          cb.equal(root.get("facilityId"), facilityId),
          cb.lessThan(root.get("quantityOnHand"), threshold),
          cb.equal(root.get("statusId"), "INV_AVAILABLE")
      ))
      .orderBy(cb.asc(root.get("quantityOnHand")));
    
    return session.createQuery(

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:54:59*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*