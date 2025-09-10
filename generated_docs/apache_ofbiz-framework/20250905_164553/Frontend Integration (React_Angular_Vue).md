### Frontend Integration (React/Angular/Vue)

## Overview

Apache OFBiz's frontend integration capabilities enable modern JavaScript frameworks (React, Angular, Vue.js) to seamlessly interact with the ERP system's multi-tier architecture. This integration layer bridges the gap between OFBiz's traditional server-side rendering approach and contemporary single-page application (SPA) frameworks, providing RESTful APIs and WebSocket connections for real-time enterprise data management.

The frontend integration architecture leverages OFBiz's service engine and entity framework to expose business logic through standardized endpoints, allowing modern frontend frameworks to consume ERP functionalities while maintaining the system's robust security, transaction management, and data integrity features.

## Architecture Integration Points

### Service Layer Exposure

OFBiz exposes its service layer through REST endpoints that frontend frameworks can consume:

```java
// Example service definition in services.xml
<service name="getProductInventory" engine="groovy" 
         location="component://product/groovyScripts/inventory/InventoryServices.groovy" 
         invoke="getProductInventoryLevels">
    <description>Get product inventory levels for frontend display</description>
    <attribute name="productId" type="String" mode="IN" optional="false"/>
    <attribute name="facilityId" type="String" mode="IN" optional="true"/>
    <attribute name="inventoryData" type="Map" mode="OUT" optional="false"/>
</service>
```

### REST API Controller Configuration

Frontend integration requires specific controller configurations in the `controller.xml` files:

```xml
<!-- REST endpoint for React/Angular/Vue consumption -->
<request-map uri="api/product/inventory">
    <security https="true" auth="true"/>
    <event type="service" invoke="getProductInventory"/>
    <response name="success" type="request" value="json"/>
    <response name="error" type="request" value="json"/>
</request-map>

<view-map name="json" type="jsonrest">
    <view-map-parameter name="contentType" value="application/json"/>
</view-map>
```

## Framework-Specific Implementation

### React Integration

React applications integrate with OFBiz through custom hooks and service layers:

```javascript
// Custom React hook for OFBiz service calls
import { useState, useEffect } from 'react';

export const useOFBizService = (serviceName, params) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/service/${serviceName}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCSRFToken()
          },
          body: JSON.stringify(params)
        });
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [serviceName, params]);

  return { data, loading, error };
};

// React component using OFBiz data
const ProductInventory = ({ productId }) => {
  const { data, loading, error } = useOFBizService('getProductInventory', { productId });

  if (loading) return <div>Loading inventory...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="inventory-display">
      <h3>Product Inventory</h3>
      <p>Available: {data.inventoryData.availableToPromise}</p>
      <p>On Hand: {data.inventoryData.quantityOnHand}</p>
    </div>
  );
};
```

### Angular Integration

Angular services provide structured integration with OFBiz backend services:

```typescript
// Angular service for OFBiz integration
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OFBizService {
  private baseUrl = '/api/service';
  
  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'X-CSRF-Token': this.getCSRFToken()
    });
  }

  callService(serviceName: string, params: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/${serviceName}`, params, {
      headers: this.getHeaders()
    });
  }

  getProductCatalog(categoryId?: string): Observable<any> {
    return this.callService('getProductCategoryMembers', { 
      productCategoryId: categoryId 
    });
  }

  createOrder(orderData: any): Observable<any> {
    return this.callService('createOrder', orderData);
  }
}

// Angular component
@Component({
  selector: 'app-product-catalog',
  template: `
    <div *ngFor="let product of products">
      <h4>{{ product.productName }}</h4>
      <p>{{ product.description }}</p>
      <button (click)="addToCart(product.productId)">Add to Cart</button>
    </div>
  `
})
export class ProductCatalogComponent {
  products: any[] = [];

  constructor(private ofbizService: OFBizService) {}

  ngOnInit() {
    this.ofbizService.getProductCatalog('CATALOG_ROOT')
      .subscribe(response => {
        this.products = response.products;
      });
  }
}
```

### Vue.js Integration

Vue.js applications utilize composables and Pinia stores for state management:

```javascript
// Vue composable for OFBiz integration
import { ref, reactive } from 'vue';

export function useOFBizStore() {
  const state = reactive({
    user: null,
    cart: [],
    orders: []
  });

  const loading = ref(false);

  const callOFBizService = async (serviceName, params) => {
    loading.value = true;
    try {
      const response = await fetch(`/api/service/${serviceName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCSRFToken()
        },
        body: JSON.stringify(params)
      });
      return await response.json();
    } finally {
      loading.value = false;
    }
  };

  const addToCart = async (productId, quantity = 1) => {
    const result = await callOFBizService('addToCart', {
      productId,
      quantity,
      shoppingListId: state.user.defaultShoppingListId
    });
    
    if (result.success) {
      state.cart.push({ productId, quantity });
    }
  };

  return {
    state,
    loading,
    callOFBizService,
    addToCart
  };
}
```

## Security and Authentication

Frontend applications must handle OFBiz's security model through proper authentication flows:

```javascript
// Authentication service for frontend frameworks
class OFBizAuth {
  static async login(username, password) {
    const response = await fetch('/control/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        USERNAME: username,
        PASSWORD: password
      })
    });

    if (response.ok) {
      // Store session information
      localStorage.setItem('ofbiz-session', response.headers.get('Set-Cookie'));
      return true;
    }
    return false;
  }

  static getCSRFToken() {
    // Extract CSRF token from meta tag or cookie
    return document.querySelector

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

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 16:50:57*

*For the most up-to-date information, visit the [original repository](https://github.com/apache/ofbiz-framework)*