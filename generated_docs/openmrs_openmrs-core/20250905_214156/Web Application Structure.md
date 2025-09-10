## Web Application Structure

## Overview

The OpenMRS Core web application follows a traditional Java web application structure built on the Spring MVC framework. The web layer serves as the primary interface for healthcare data management, providing both REST APIs and web-based user interfaces for clinical workflows, patient management, and administrative functions.

## Directory Structure

The web application components are organized within the `webapp` module of the OpenMRS Core repository:

```
webapp/
├── src/main/webapp/
│   ├── WEB-INF/
│   │   ├── web.xml                 # Servlet configuration
│   │   ├── applicationContext-*.xml # Spring context configurations
│   │   ├── view/                   # JSP view templates
│   │   └── tags/                   # Custom JSP tag libraries
│   ├── scripts/                    # JavaScript files
│   ├── images/                     # Static image resources
│   └── css/                        # Stylesheet resources
└── src/main/java/
    └── org/openmrs/web/
        ├── controller/             # Spring MVC controllers
        ├── filter/                 # Servlet filters
        ├── servlet/                # Custom servlets
        └── taglib/                 # JSP tag implementations
```

## Spring MVC Architecture

### Controller Layer

OpenMRS implements a comprehensive controller architecture using Spring MVC annotations. Controllers are organized by functional domain:

```java
@Controller
@RequestMapping("/admin/patients")
public class PatientController {
    
    @Autowired
    private PatientService patientService;
    
    @RequestMapping(method = RequestMethod.GET)
    public String listPatients(ModelMap model) {
        model.addAttribute("patients", patientService.getAllPatients());
        return "/admin/patients/patientList";
    }
}
```

Key controller packages include:
- `org.openmrs.web.controller.patient` - Patient management operations
- `org.openmrs.web.controller.encounter` - Clinical encounter handling
- `org.openmrs.web.controller.concept` - Medical concept management
- `org.openmrs.web.controller.admin` - Administrative functions

### View Resolution

The application uses JSP-based view resolution with a hierarchical template structure:

```xml
<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">
    <property name="prefix" value="/WEB-INF/view/" />
    <property name="suffix" value=".jsp" />
    <property name="order" value="1" />
</bean>
```

Views are organized by module functionality:
- `/WEB-INF/view/admin/` - Administrative interfaces
- `/WEB-INF/view/portlets/` - Reusable UI components
- `/WEB-INF/view/scripts/` - JavaScript includes

## REST API Structure

### RESTful Web Services

OpenMRS Core provides extensive REST API capabilities through the `org.openmrs.module.webservices.rest` package structure:

```java
@Resource(name = "v1/patient", supportedClass = Patient.class, supportedOpenmrsVersions = {"1.8.*", "1.9.*"})
public class PatientResource extends DelegatingCrudResource<Patient> {
    
    @Override
    public Patient newDelegate() {
        return new Patient();
    }
    
    @Override
    public Patient save(Patient patient) {
        return Context.getPatientService().savePatient(patient);
    }
}
```

The REST architecture follows OpenMRS conventions:
- **Base URL Pattern**: `/ws/rest/v1/{resource}`
- **Standard HTTP Methods**: GET, POST, PUT, DELETE
- **Response Format**: JSON with standardized structure
- **Authentication**: Session-based or Basic Authentication

### API Versioning

The web services implement version management through URL path versioning:

```
/ws/rest/v1/patient          # Version 1 API
/ws/rest/v2/patient          # Version 2 API (future)
```

## Security Integration

### Authentication Filters

The web application integrates with OpenMRS security through custom servlet filters:

```java
@Component
public class OpenmrsFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                        FilterChain chain) throws IOException, ServletException {
        
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        
        // Check authentication status
        if (!Context.isAuthenticated()) {
            // Redirect to login or return 401
        }
        
        chain.doFilter(request, response);
    }
}
```

### Authorization Patterns

Controllers implement role-based access control using Spring Security annotations:

```java
@Controller
@RequestMapping("/admin/users")
@PreAuthorize("hasRole('ROLE_ADMIN')")
public class UserController {
    
    @RequestMapping(value = "/delete", method = RequestMethod.POST)
    @PreAuthorize("hasPrivilege('Delete Users')")
    public String deleteUser(@RequestParam Integer userId) {
        // Implementation
    }
}
```

## Session Management

### Context Handling

OpenMRS maintains application context through the `Context` class, which provides thread-local access to services and user sessions:

```java
// In web controllers
User authenticatedUser = Context.getAuthenticatedUser();
PatientService patientService = Context.getPatientService();
```

### Session Lifecycle

The web application manages session lifecycle through:
- **Login Process**: Authentication via `/login.htm`
- **Session Timeout**: Configurable timeout with automatic cleanup
- **Logout Handling**: Proper context cleanup and session invalidation

## Static Resource Management

### Resource Organization

Static resources are organized for optimal caching and delivery:

```
webapp/src/main/webapp/
├── scripts/
│   ├── jquery/              # Third-party libraries
│   ├── openmrs.js          # Core OpenMRS JavaScript
│   └── custom/             # Module-specific scripts
├── css/
│   ├── openmrs_default.css # Default theme
│   └── style.css           # Base styles
└── images/
    ├── openmrs_logo_*.png  # Branding assets
    └── icons/              # UI icons
```

### Performance Optimization

The application implements several performance optimizations:
- **Resource Compression**: Gzip compression for CSS/JS
- **Caching Headers**: Appropriate cache control for static resources
- **Minification**: JavaScript and CSS minification in production builds

## Integration Points

### Module System Integration

The web layer integrates seamlessly with OpenMRS modules through:
- **Controller Discovery**: Automatic registration of module controllers
- **Resource Mapping**: Dynamic resource path resolution
- **Tag Library Extensions**: Module-specific JSP tags

### Database Connectivity

Web controllers access data through the service layer, maintaining proper transaction boundaries:

```java
@Transactional
@RequestMapping(value = "/save", method = RequestMethod.POST)
public String savePatient(@ModelAttribute Patient patient) {
    Context.getPatientService().savePatient(patient);
    return "redirect:/admin/patients/patient.form?patientId=" + patient.getId();
}
```

This architecture ensures proper separation of concerns while maintaining the flexibility required for healthcare application development and module extensibility.

## Repository Context

- **Repository**: [https://github.com/openmrs/openmrs-core](https://github.com/openmrs/openmrs-core)
- **Description**: No description available
- **Business Domain**: Software Development
- **Architecture Pattern**: Library/Utility

## Technology Stack

---

*Generated by ADocS (Automated Documentation Structure) on 2025-09-05 21:44:51*

*For the most up-to-date information, visit the [original repository](https://github.com/openmrs/openmrs-core)*