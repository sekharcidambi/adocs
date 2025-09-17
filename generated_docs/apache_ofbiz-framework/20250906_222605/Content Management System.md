# Content Management System

The Apache OFBiz Content Management System (CMS) provides a comprehensive framework for managing digital content, documents, and media assets within enterprise applications. Built on OFBiz's robust entity engine and service framework, the CMS offers flexible content modeling, versioning, workflow management, and multi-channel publishing capabilities.

## Overview

OFBiz CMS is designed to handle diverse content types ranging from simple text documents to complex multimedia assets. It integrates seamlessly with other OFBiz applications including e-commerce, customer relationship management, and enterprise resource planning modules.

### Key Features

- **Flexible Content Modeling**: Define custom content types with arbitrary attributes
- **Version Control**: Track content changes with full revision history
- **Workflow Management**: Implement approval processes and content lifecycle management
- **Multi-channel Publishing**: Deliver content across web, mobile, and API channels
- **Security Integration**: Leverage OFBiz security framework for access control
- **Internationalization**: Support for multi-language content management
- **Template Engine**: Integration with FreeMarker for dynamic content rendering

## Architecture

### Core Components

The OFBiz CMS architecture consists of several interconnected components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Content API   │    │  Content Types  │    │   Templates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                    Content Engine                               │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Entity Engine  │ Service Engine  │      Security Framework     │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Entity Model

The CMS utilizes several key entities to model content:

#### Content Entity
```xml
<entity entity-name="Content" package-name="org.apache.ofbiz.content.content">
    <field name="contentId" type="id-ne"/>
    <field name="contentTypeId" type="id"/>
    <field name="ownerContentId" type="id"/>
    <field name="decoratorContentId" type="id"/>
    <field name="instanceOfContentId" type="id"/>
    <field name="dataResourceId" type="id"/>
    <field name="templateDataResourceId" type="id"/>
    <field name="dataSourceId" type="id"/>
    <field name="statusId" type="id"/>
    <field name="privilegeEnumId" type="id"/>
    <field name="serviceName" type="name"/>
    <field name="customMethodId" type="id"/>
    <field name="contentName" type="name"/>
    <field name="description" type="description"/>
    <field name="localeString" type="short-varchar"/>
    <field name="mimeTypeId" type="id"/>
    <field name="characterSetId" type="id"/>
    <field name="childLeafCount" type="numeric"/>
    <field name="childBranchCount" type="numeric"/>
    <field name="createdDate" type="date-time"/>
    <field name="createdByUserLogin" type="id-vlong"/>
    <field name="lastModifiedDate" type="date-time"/>
    <field name="lastModifiedByUserLogin" type="id-vlong"/>
    <prim-key field="contentId"/>
</entity>
```

#### DataResource Entity
```xml
<entity entity-name="DataResource" package-name="org.apache.ofbiz.content.data">
    <field name="dataResourceId" type="id-ne"/>
    <field name="dataResourceTypeId" type="id"/>
    <field name="dataTemplateTypeId" type="id"/>
    <field name="dataCategoryId" type="id"/>
    <field name="dataSourceId" type="id"/>
    <field name="statusId" type="id"/>
    <field name="dataResourceName" type="name"/>
    <field name="localeString" type="short-varchar"/>
    <field name="mimeTypeId" type="id"/>
    <field name="characterSetId" type="id"/>
    <field name="objectInfo" type="long-varchar"/>
    <field name="surveyId" type="id"/>
    <field name="surveyResponseId" type="id"/>
    <field name="relatedDetailId" type="id"/>
    <field name="isPublic" type="indicator"/>
    <field name="createdDate" type="date-time"/>
    <field name="createdByUserLogin" type="id-vlong"/>
    <field name="lastModifiedDate" type="date-time"/>
    <field name="lastModifiedByUserLogin" type="id-vlong"/>
    <prim-key field="dataResourceId"/>
</entity>
```

## Implementation Guide

### Creating Content Types

Content types define the structure and behavior of different content categories. Here's how to define a custom content type:

```xml
<!-- Define content type in ContentTypeData.xml -->
<ContentType contentTypeId="BLOG_POST" 
             description="Blog Post Content Type"
             hasTable="N"/>

<!-- Define associated data resource type -->
<DataResourceType dataResourceTypeId="BLOG_POST_DATA"
                  description="Blog Post Data Resource"
                  hasTable="N"/>
```

### Content Creation Service

Implement content creation using OFBiz services:

```java
// ContentServices.java
public static Map<String, Object> createContent(DispatchContext dctx, 
                                               Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    LocalDispatcher dispatcher = dctx.getDispatcher();
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    String contentId = delegator.getNextSeqId("Content");
    String contentTypeId = (String) context.get("contentTypeId");
    String contentName = (String) context.get("contentName");
    String description = (String) context.get("description");
    
    try {
        // Create DataResource first
        Map<String, Object> dataResourceContext = UtilMisc.toMap(
            "dataResourceTypeId", "ELECTRONIC_TEXT",
            "dataResourceName", contentName,
            "mimeTypeId", "text/html",
            "isPublic", "Y",
            "userLogin", userLogin
        );
        
        Map<String, Object> dataResourceResult = dispatcher.runSync(
            "createDataResource", dataResourceContext);
        
        if (ServiceUtil.isError(dataResourceResult)) {
            return dataResourceResult;
        }
        
        String dataResourceId = (String) dataResourceResult.get("dataResourceId");
        
        // Create Content
        GenericValue content = delegator.makeValue("Content", UtilMisc.toMap(
            "contentId", contentId,
            "contentTypeId", contentTypeId,
            "dataResourceId", dataResourceId,
            "contentName", contentName,
            "description", description,
            "statusId", "CTNT_INITIAL_DRAFT",
            "createdDate", UtilDateTime.nowTimestamp(),
            "createdByUserLogin", userLogin.getString("userLoginId")
        ));
        
        content.create();
        
        Map<String, Object> result = ServiceUtil.returnSuccess();
        result.put("contentId", contentId);
        return result;
        
    } catch (GenericEntityException | GenericServiceException e) {
        Debug.logError(e, "Error creating content", MODULE);
        return ServiceUtil.returnError("Error creating content: " + e.getMessage());
    }
}
```

### Content Rendering

Implement content rendering with FreeMarker templates:

```java
// ContentWorker.java
public static void renderContentAsText(LocalDispatcher dispatcher, 
                                      String contentId, 
                                      Appendable out, 
                                      Map<String, Object> templateContext,
                                      Locale locale, 
                                      String mimeTypeId, 
                                      boolean cache) throws GeneralException, IOException {
    
    Delegator delegator = dispatcher.getDelegator();
    
    // Get content
    GenericValue content = EntityQuery.use(delegator)
        .from("Content")
        .where("contentId", contentId)
        .cache(cache)
        .queryOne();
    
    if (content == null) {
        throw new GeneralException("Content not found: " + contentId);
    }
    
    // Get data resource
    String dataResourceId = content.getString("dataResourceId");
    if (UtilValidate.isNotEmpty(dataResourceId)) {
        GenericValue dataResource = EntityQuery.use(delegator)
            .from("DataResource")
            .where("dataResourceId", dataResourceId)
            .cache(cache)
            .queryOne();
        
        if (dataResource != null) {
            String dataResourceTypeId = dataResource.getString("dataResourceTypeId");
            
            // Handle different data resource types
            if ("ELECTRONIC_TEXT".equals(dataResourceTypeId)) {
                renderElectronicText(dispatcher, dataResource, out, 
                                   templateContext, locale, mimeTypeId, cache);
            } else if ("SHORT_TEXT".equals(dataResourceTypeId)) {
                renderShortText(dataResource, out, templateContext);
            } else if ("URL_RESOURCE".equals(dataResourceTypeId)) {
                renderUrlResource(dataResource, out, templateContext);
            }
        }
    }
}
```

### Content Workflow

Implement content approval workflow:

```xml
<!-- services.xml -->
<service name="updateContentStatus" engine="java"
         location="org.apache.ofbiz.content.content.ContentServices"
         invoke="updateContentStatus" auth="true">
    <description>Update Content Status</description>
    <attribute name="contentId" type="String" mode="IN" optional="false"/>
    <attribute name="statusId" type="String" mode="IN" optional="false"/>
    <attribute name="statusDate" type="Timestamp" mode="IN" optional="true"/>
</service>
```

```java
public static Map<String, Object> updateContentStatus(DispatchContext dctx, 
                                                     Map<String, ? extends Object> context) {
    Delegator delegator = dctx.getDelegator();
    String contentId = (String) context.get("contentId");
    String statusId = (String) context.get("statusId");
    Timestamp statusDate = (Timestamp) context.get("statusDate");
    GenericValue userLogin = (GenericValue) context.get("userLogin");
    
    if (statusDate == null) {
        statusDate = UtilDateTime.nowTimestamp();
    }
    
    try {
        // Update content status
        GenericValue content = EntityQuery.use(delegator)
            .from("Content")
            .where("contentId", contentId)
            .queryOne();
        
        if (content == null) {
            return ServiceUtil.returnError("Content not found: " + contentId);
        }
        
        String oldStatusId = content.getString("statusId");
        content.set("statusId", statusId);
        content.set("lastModifiedDate", statusDate);
        content.set("lastModifiedByUserLogin", userLogin.getString("userLoginId"));
        content.store();
        
        // Create status history
        GenericValue statusItem = delegator.makeValue("ContentStatus", UtilMisc.toMap(
            "contentId", contentId,
            "statusId", statusId,
            "statusDate", statusDate,
            "statusEndDate", null,
            "changeByUserLoginId", userLogin.getString("userLoginId")
        ));
        statusItem.create();
        
        // End previous status
        if (UtilValidate.isNotEmpty(oldStatusId)) {
            List<GenericValue> previousStatuses = EntityQuery.use(delegator)
                .from("ContentStatus")
                .where("contentId", contentId, "statusId", oldStatusId)
                .filterByDate()
                .queryList();
            
            for (GenericValue previousStatus : previousStatuses) {
                previousStatus.set("statusEndDate", statusDate);
                previousStatus.store();
            }
        }
        
        return ServiceUtil.returnSuccess();
        
    } catch (GenericEntityException e) {
        Debug.logError(e, "Error updating content status", MODULE);
        return ServiceUtil.returnError("Error updating content status: " + e.getMessage());
    }
}
```

## Content Types and Templates

### Built-in Content Types

OFBiz provides several predefined content types:

- **DOCUMENT**: General document content
- **WEB_SITE_PUB_PT**: Website publication point
- **SUB_CONTENT**: Sub-content for hierarchical structures
- **TEMPLATE**: Template content for rendering
- **DECORATOR**: Decorator content for layout
- **PAGE_TEMPLATE**: Page template content

### Template Integration

Content can be rendered using FreeMarker templates:

```ftl
<#-- content_template.ftl -->
<div class="content-wrapper">
    <h1>${content.contentName!}</h1>
    <div class="content-meta">
        <span class="created-date">${content.createdDate?string("yyyy-MM-dd")}</span>
        <span class="status">${content.statusId!}</span>
    </div>
    <div class="content-body">
        ${contentText!}
    </div>
</div>
```

### Custom Content Handlers

Implement custom content handlers for specialized content types:

```java
public class CustomContentHandler {
    
    public static String renderCustomContent(Delegator delegator, 
                                           String contentId, 
                                           Map<String, Object> context) {
        try {
            GenericValue content = EntityQuery.use(delegator)
                .from("Content")
                .where("contentId", contentId)
                .queryOne();
            
            if (content != null) {
                String contentTypeId = content.getString("contentTypeId");
                
                switch (contentTypeId) {
                    case "BLOG_POST":
                        return renderBlogPost(content, context);
                    case "PRODUCT_REVIEW":
                        return renderProductReview(content, context);
                    default:
                        return renderDefaultContent(content, context);
                }
            }
        } catch (GenericEntityException e) {
            Debug.logError(e, "Error rendering custom content", MODULE);
        }
        
        return "";
    }
    
    private static String renderBlogPost(GenericValue content, 
                                       Map<String, Object> context) {
        // Custom blog post rendering logic
        StringBuilder html = new StringBuilder();
        html.append("<article class='blog-post'>");
        html.append("<h2>").append(content.getString("contentName")).append("</h2>");
        html.append("<div class='blog-content'>");
        // Add content body
        html.append("</div>");
        html.append("</article>");
        return html.toString();
    }
}
```

## Security and Permissions

### Content Security

OFBiz CMS integrates with the security framework to control content access:

```xml
<!-- SecurityPermissionSeedData.xml -->
<SecurityPermission permissionId="CONTENTMGR_VIEW" 
                    description="Content Manager View"/>
<SecurityPermission permissionId="CONTENTMGR_CREATE" 
                    description="Content Manager Create"/>
<SecurityPermission permissionId="CONTENTMGR_UPDATE" 
                    description="Content Manager Update"/>
<SecurityPermission permissionId="CONTENTMGR_DELETE" 
                    description="Content Manager Delete"/>
<SecurityPermission permissionId="CONTENTMGR_PUBLISH" 
                    description="Content Manager Publish"/>
```

### Permission Checking