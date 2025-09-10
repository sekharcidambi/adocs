# Advanced Topics

This section covers advanced React concepts and features that enable developers to build sophisticated, high-performance applications. These topics represent the cutting edge of React development and require a solid understanding of React fundamentals.

## Concurrent Features

React's Concurrent Features represent a fundamental shift in how React handles rendering and updates, enabling better user experiences through improved performance and responsiveness.

### Understanding Concurrency in React

Concurrent React allows the framework to interrupt, pause, and resume rendering work to keep the main thread responsive. This is achieved through time-slicing and prioritization of updates.

#### Key Concepts

- **Time Slicing**: Breaking rendering work into small chunks that can be interrupted
- **Priority-based Updates**: Different updates have different priorities (urgent vs. non-urgent)
- **Interruptible Rendering**: React can pause work on low-priority updates to handle high-priority ones

### Concurrent Mode APIs

#### Suspense for Data Fetching

Suspense allows components to "wait" for something before rendering, providing a declarative way to handle asynchronous operations.

```jsx
import { Suspense, lazy } from 'react';

// Lazy loading components
const LazyComponent = lazy(() => import('./LazyComponent'));

// Data fetching with Suspense
function ProfilePage({ userId }) {
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <ProfileDetails userId={userId} />
      <Suspense fallback={<PostsSkeleton />}>
        <ProfilePosts userId={userId} />
      </Suspense>
    </Suspense>
  );
}

// Custom hook with Suspense integration
function useUserData(userId) {
  const [user, setUser] = useState(null);
  
  if (!user) {
    throw fetchUser(userId).then(setUser); // Suspense boundary will catch this
  }
  
  return user;
}
```

#### Transitions and useTransition

The `useTransition` hook allows you to mark updates as non-urgent, preventing them from blocking urgent updates.

```jsx
import { useTransition, useState } from 'react';

function SearchResults() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (newQuery) => {
    setQuery(newQuery); // Urgent update
    
    startTransition(() => {
      // Non-urgent update - won't block typing
      setResults(performExpensiveSearch(newQuery));
    });
  };

  return (
    <div>
      <input 
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search..."
      />
      {isPending && <div>Searching...</div>}
      <ResultsList results={results} />
    </div>
  );
}
```

#### useDeferredValue

This hook allows you to defer updates to less critical parts of the UI.

```jsx
import { useDeferredValue, useMemo } from 'react';

function ProductList({ query }) {
  const deferredQuery = useDeferredValue(query);
  
  const filteredProducts = useMemo(() => {
    return products.filter(product => 
      product.name.toLowerCase().includes(deferredQuery.toLowerCase())
    );
  }, [deferredQuery]);

  return (
    <div>
      {query !== deferredQuery && <div>Updating results...</div>}
      {filteredProducts.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

### Best Practices for Concurrent Features

- **Identify Update Priorities**: Distinguish between urgent (user input) and non-urgent (search results) updates
- **Use Suspense Boundaries Strategically**: Place them at appropriate levels to provide good loading states
- **Avoid Overusing Transitions**: Not all updates need to be wrapped in transitions
- **Test Performance**: Use React DevTools Profiler to measure the impact of concurrent features

## Server Components

React Server Components (RSC) enable rendering components on the server, reducing bundle size and improving performance by moving computation to the server.

### Understanding Server Components

Server Components run exclusively on the server and never hydrate on the client. They can access server-side resources directly and don't increase the client bundle size.

#### Types of Components

```jsx
// Server Component (default in app directory)
// This runs only on the server
async function ServerComponent() {
  const data = await fetch('https://api.example.com/data');
  const posts = await data.json();
  
  return (
    <div>
      {posts.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  );
}

// Client Component (marked with 'use client')
'use client';
import { useState } from 'react';

function ClientComponent() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}

// Mixed usage
function MixedPage() {
  return (
    <div>
      <ServerComponent /> {/* Rendered on server */}
      <ClientComponent /> {/* Hydrated on client */}
    </div>
  );
}
```

### Server Component Patterns

#### Data Fetching in Server Components

```jsx
// Direct database access in Server Components
import { db } from '@/lib/database';

async function UserProfile({ userId }) {
  // This runs on the server - no API route needed
  const user = await db.user.findUnique({
    where: { id: userId },
    include: { posts: true }
  });

  if (!user) {
    return <div>User not found</div>;
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <UserPosts posts={user.posts} />
    </div>
  );
}

// Streaming with Suspense
function UserDashboard({ userId }) {
  return (
    <div>
      <UserProfile userId={userId} />
      <Suspense fallback={<AnalyticsSkeleton />}>
        <UserAnalytics userId={userId} />
      </Suspense>
    </div>
  );
}
```

#### Server Actions

Server Actions allow you to run server-side code directly from client components.

```jsx
// app/actions.js
'use server';

export async function createPost(formData) {
  const title = formData.get('title');
  const content = formData.get('content');
  
  await db.post.create({
    data: { title, content }
  });
  
  revalidatePath('/posts');
}

// Client Component using Server Action
'use client';
import { createPost } from './actions';

function PostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Post title" required />
      <textarea name="content" placeholder="Post content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

### Server Component Architecture

#### File Structure in Next.js App Router

```
app/
├── layout.js          # Root layout (Server Component)
├── page.js           # Home page (Server Component)
├── globals.css
├── posts/
│   ├── page.js       # Posts list (Server Component)
│   ├── [id]/
│   │   └── page.js   # Post detail (Server Component)
│   └── components/
│       ├── PostList.js      # Server Component
│       └── PostInteraction.js # Client Component
└── components/
    ├── Header.js     # Server Component
    └── Navigation.js # Client Component ('use client')
```

#### Component Composition Patterns

```jsx
// Server Component that composes other components
function BlogPost({ postId }) {
  return (
    <article>
      <PostContent postId={postId} /> {/* Server Component */}
      <PostInteractions postId={postId} /> {/* Client Component */}
      <RelatedPosts postId={postId} /> {/* Server Component */}
    </article>
  );
}

// Passing Server Components as children to Client Components
function Layout({ children }) {
  return (
    <div>
      <ClientSidebar>
        {children} {/* Server Components can be passed as children */}
      </ClientSidebar>
    </div>
  );
}
```

### Best Practices for Server Components

- **Keep Client Components Minimal**: Only use 'use client' when necessary for interactivity
- **Leverage Server-Side Data Access**: Access databases and APIs directly in Server Components
- **Use Streaming**: Implement Suspense boundaries for better perceived performance
- **Optimize Bundle Size**: Server Components don't contribute to client bundle size

## Custom Renderers

Custom renderers allow React to target different platforms and environments beyond the DOM, enabling React's component model for various output targets.

### Understanding React's Reconciliation

React's core reconciliation algorithm is separate from the rendering target, enabling custom renderers through the React Reconciler package.

#### Reconciler Architecture

```jsx
import Reconciler from 'react-reconciler';

// Host config defines how to interact with the target platform
const hostConfig = {
  // Environment-specific implementations
  createInstance(type, props, rootContainer, hostContext, internalHandle) {
    // Create a platform-specific instance
  },
  
  appendChild(parent, child) {
    // Add child to parent in the target environment
  },
  
  removeChild(parent, child) {
    // Remove child from parent
  },
  
  commitUpdate(instance, updatePayload, type, oldProps, newProps) {
    // Apply updates to the instance
  }
  
  // ... many more methods
};

const CustomRenderer = Reconciler(hostConfig);
```

### Building a Custom Renderer

#### Example: Console Renderer

```jsx
import Reconciler from 'react-reconciler';

// Simple console-based renderer
const hostConfig = {
  supportsMutation: true,
  supportsPersistence: false,
  supportsHydration: false,

  createInstance(type, props) {
    return {
      type,
      props,
      children: []
    };
  },

  createTextInstance(text) {
    return { text };
  },

  appendChild(parent, child) {
    parent.children.push(child);
  },

  removeChild(parent, child) {
    const index = parent.children.indexOf(child);
    if (index !== -1) {
      parent.children.splice(index, 1);
    }
  },

  commitUpdate(instance, updatePayload, type, oldProps, newProps) {
    instance.props = newProps;
  },

  commitTextUpdate(textInstance, oldText, newText) {
    textInstance.text = newText;
  },

  finalizeInitialChildren() {
    return false;
  },

  getChildHostContext() {
    return {};
  },

  getPublicInstance(instance) {
    return instance;
  },

  getRootHostContext() {
    return {};
  },

  prepareForCommit() {
    return null;
  },

  prepareUpdate(instance, type, oldProps, newProps) {
    return true; // Always update
  },

  resetAfterCommit(containerInfo) {
    // Render the tree to console
    console.clear();
    renderToConsole(containerInfo.children[0], 0);
  },

  shouldSetTextContent(type, props) {
    return false;
  }
};

function renderToConsole(node, depth) {
  const indent = '  '.repeat(depth);
  
  if (node.text) {
    console.log(indent + node.text);
  } else {
    console.log(indent + `<${node.type}>`);
    node.children.forEach(child => renderToConsole(child, depth + 1));
  }
}

const ConsoleRenderer = Reconciler(hostConfig);

// Usage
function render(element, container) {
  const root = ConsoleRenderer.createContainer(container, 0, false, null);
  ConsoleRenderer.updateContainer(element, root, null, null);
}

// Example usage
function App() {
  return (
    <div>
      <h1>Hello Console!</h1>
      <p>This renders to the console</p>
    </div>
  );
}

render(<App />, { children: [] });
```

#### Canvas Renderer Example

```jsx
// Canvas-specific renderer for 2D graphics
const canvasHostConfig = {
  createInstance(type, props) {
    const instance = {
      type,
      props,
      children: []
    };
    
    // Define drawing functions for different types
    switch (type) {
      case 'rect':
        instance.draw = (ctx) => {
          ctx.fillStyle = props.fill || 'black';
          ctx.fillRect(props.x, props.y, props.width, props.height);
        };
        break;
      case 'circle':
        instance.draw = (ctx) => {
          ctx.fillStyle = props.fill || 'black';
          ctx.beginPath();
          ctx.arc(props.x, props.y, props.radius, 0, 2 * Math.PI);
          ctx.fill();
        };
        break;
    }
    
    return instance;
  },

  resetAfterCommit(containerInfo) {
    const canvas = containerInfo.canvas;
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Render all instances
    function renderInstance(instance) {
      if (instance.draw) {
        instance.draw(ctx);
      }
      instance.children.forEach(renderInstance);
    }
    
    containerInfo.children.forEach(renderInstance);
  }
  
  // ... other required methods
};

// Usage
function CanvasApp() {
  return (
    <div>
      <rect x={10} y={10} width={50} height={50} fill="red" />
      <circle x={100} y={50} radius={25} fill="blue" />
    </div>
  );
}
```

### Real-World Custom Renderer Examples

#### React Native Architecture

```jsx
// Simplified React Native renderer concept
const ReactNativeRenderer = {
  createInstance(type, props) {
    switch (type) {
      case 'View':
        return new NativeView(props);
      case 'Text':
        return new NativeText(props);
      case 'Image':
        return new NativeImage(props);
      default:
        throw new Error(`Unknown component type: ${type}`);
    }
  }
};

// Bridge communication
function NativeView(props) {
  this.nativeId = generateUniqueId();
  NativeBridge.createView(this.nativeId, props);
}
```

#### Testing Renderer

```jsx
// Custom renderer for testing React components
const TestRenderer = {
  createInstance(type, props) {
    return {
      type,
      props: { ...props },
      children: []
    };
  },
  
  // Provides methods for testing
  toJSON() {
    return this.getInstance();
  },
  
  findByType(type) {
    // Find components by type
  },
  
  findByProps(props) {
    // Find components by props
  }
};
```

### Best Practices for Custom Renderers

- **Understand the Host Config**: Implement all required methods properly
- **Handle Updates Efficiently**: Optimize the update and commit phases
- **Provide Developer Tools**: Consider React DevTools integration
- **Error Handling**: Implement robust error boundaries and reporting
- **Performance Considerations**: Minimize work in the commit phase
- **Testing Strategy**: Build comprehensive tests for your renderer

### Common Pitfalls

- **Incomplete Host Config**: Missing required methods can cause