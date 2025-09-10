# Core Architecture

React's core architecture is built around a sophisticated system of interconnected components that work together to provide a declarative, efficient, and flexible framework for building user interfaces. The architecture is designed with separation of concerns in mind, allowing different parts of the system to evolve independently while maintaining a cohesive developer experience.

At its foundation, React's architecture consists of three primary subsystems: the **React Reconciler** (the core algorithm that manages component updates), the **Component System** (the abstraction layer for building UI elements), and the **Renderer Architecture** (the platform-specific rendering implementations). This modular design enables React to support multiple platforms while maintaining a consistent programming model.

## React Reconciler

The React Reconciler is the heart of React's architecture, responsible for determining what changes need to be made to the UI when component state or props change. It implements the core diffing algorithm and manages the component lifecycle, making it one of the most critical and complex parts of the React ecosystem.

### Fiber Architecture

The current reconciler implementation, known as **React Fiber**, was introduced in React 16 to address performance limitations of the previous stack-based reconciler. Fiber introduces several key architectural improvements:

**Incremental Rendering**: Unlike the previous synchronous reconciler, Fiber can pause, abort, or restart rendering work, allowing React to maintain responsive user interfaces even during complex updates.

```javascript
// Example of how Fiber enables time-slicing
function WorkLoop(deadline) {
  let shouldYield = false;
  while (nextUnitOfWork && !shouldYield) {
    nextUnitOfWork = performUnitOfWork(nextUnitOfWork);
    shouldYield = deadline.timeRemaining() < 1;
  }
  
  if (nextUnitOfWork) {
    // More work to do, schedule continuation
    requestIdleCallback(WorkLoop);
  }
}
```

**Priority-Based Scheduling**: Fiber assigns different priorities to different types of updates, ensuring that high-priority updates (like user interactions) are processed before low-priority ones (like data fetching).

```javascript
// Priority levels in React Fiber
const priorities = {
  ImmediatePriority: 1,    // User interactions, animations
  UserBlockingPriority: 2, // User input, hover effects  
  NormalPriority: 3,       // Data fetching, network responses
  LowPriority: 4,          // Analytics, logging
  IdlePriority: 5          // Background tasks
};
```

### Reconciliation Process

The reconciliation process follows a predictable pattern that developers can reason about:

1. **Trigger Phase**: A state update or prop change triggers a re-render
2. **Render Phase**: React builds a new virtual DOM tree
3. **Commit Phase**: React applies changes to the actual DOM

```javascript
// Simplified reconciliation workflow
function reconcileChildren(current, workInProgress, nextChildren) {
  if (current === null) {
    // Mount new children
    workInProgress.child = mountChildFibers(
      workInProgress,
      null,
      nextChildren
    );
  } else {
    // Reconcile existing children
    workInProgress.child = reconcileChildFibers(
      workInProgress,
      current.child,
      nextChildren
    );
  }
}
```

### Diffing Algorithm

React's diffing algorithm makes assumptions to achieve O(n) complexity:

- **Element Type Changes**: When an element changes type, React destroys the old tree and builds a new one
- **Keys for List Items**: Keys help React identify which items have changed, been added, or removed
- **Component Instance Preservation**: React preserves component instances when possible to maintain state

```javascript
// Example demonstrating key importance in reconciliation
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        // Without key, React may incorrectly reconcile items
        <TodoItem 
          key={todo.id}  // Key helps React track items correctly
          todo={todo} 
        />
      ))}
    </ul>
  );
}
```

### Error Boundaries and Recovery

The reconciler includes sophisticated error handling mechanisms:

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    console.error('Component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

## Component System

React's component system provides the primary abstraction for building user interfaces. It's designed around the principle of composition over inheritance, enabling developers to build complex UIs from simple, reusable pieces.

### Component Types and Patterns

**Functional Components**: The modern standard for React components, leveraging hooks for state and lifecycle management:

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const userData = await api.getUser(userId);
        setUser(userData);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchUser();
  }, [userId]);

  if (loading) return <LoadingSpinner />;
  if (!user) return <ErrorMessage />;
  
  return (
    <div className="user-profile">
      <Avatar src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
    </div>
  );
}
```

**Class Components**: Still supported for legacy code and specific use cases:

```javascript
class DataFetcher extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: null,
      error: null,
      loading: true
    };
  }

  async componentDidMount() {
    try {
      const data = await this.props.fetchData();
      this.setState({ data, loading: false });
    } catch (error) {
      this.setState({ error, loading: false });
    }
  }

  render() {
    const { data, error, loading } = this.state;
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    
    return this.props.children(data);
  }
}
```

### Hooks Architecture

Hooks represent a fundamental shift in React's component model, providing a way to use state and lifecycle features in functional components:

**Built-in Hooks**:
- `useState`: Local component state management
- `useEffect`: Side effects and lifecycle events
- `useContext`: Context consumption
- `useReducer`: Complex state logic
- `useMemo` and `useCallback`: Performance optimization

```javascript
// Custom hook example demonstrating composition
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url);
        const result = await response.json();
        
        if (!cancelled) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchData();
    
    return () => {
      cancelled = true;
    };
  }, [url]);

  return { data, loading, error };
}
```

### Context and State Management

React's Context API provides a way to share data across component trees without prop drilling:

```javascript
// Theme context example
const ThemeContext = React.createContext();

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  const value = useMemo(() => ({
    theme,
    toggleTheme
  }), [theme, toggleTheme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook for consuming theme context
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

### Component Composition Patterns

**Higher-Order Components (HOCs)**:

```javascript
function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const { user, loading } = useAuth();
    
    if (loading) return <LoadingSpinner />;
    if (!user) return <LoginForm />;
    
    return <WrappedComponent {...props} user={user} />;
  };
}
```

**Render Props Pattern**:

```javascript
function DataProvider({ children, url }) {
  const { data, loading, error } = useApi(url);
  
  return children({ data, loading, error });
}

// Usage
<DataProvider url="/api/users">
  {({ data, loading, error }) => {
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    return <UserList users={data} />;
  }}
</DataProvider>
```

## Renderer Architecture

React's renderer architecture enables the library to target multiple platforms while maintaining a consistent component model. The separation between the reconciler and renderers is a key architectural decision that provides flexibility and extensibility.

### Renderer Abstraction

The renderer architecture is built around a host configuration that defines how React interacts with the target platform:

```javascript
// Simplified renderer host configuration
const HostConfig = {
  // Create instance of a host element
  createInstance(type, props, rootContainer, hostContext, internalHandle) {
    const element = document.createElement(type);
    // Apply props to element
    Object.keys(props).forEach(key => {
      if (key === 'children') return;
      if (key === 'style') {
        Object.assign(element.style, props.style);
      } else {
        element.setAttribute(key, props[key]);
      }
    });
    return element;
  },

  // Append child to parent
  appendChild(parent, child) {
    parent.appendChild(child);
  },

  // Update instance properties
  commitUpdate(instance, updatePayload, type, oldProps, newProps) {
    updatePayload.forEach(([key, value]) => {
      if (key === 'style') {
        Object.assign(instance.style, value);
      } else {
        instance.setAttribute(key, value);
      }
    });
  }
};
```

### React DOM Renderer

The DOM renderer is the most commonly used renderer, responsible for translating React components into DOM elements:

**Event System**: React implements a synthetic event system that normalizes browser differences:

```javascript
// Synthetic event handling
function Button({ onClick, children }) {
  const handleClick = useCallback((syntheticEvent) => {
    // syntheticEvent is normalized across browsers
    syntheticEvent.preventDefault();
    
    // Access native event if needed
    const nativeEvent = syntheticEvent.nativeEvent;
    
    onClick?.(syntheticEvent);
  }, [onClick]);

  return (
    <button onClick={handleClick}>
      {children}
    </button>
  );
}
```

**Portal Support**: Rendering components outside the normal component tree:

```javascript
function Modal({ children, isOpen }) {
  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div className="modal-overlay">
      <div className="modal-content">
        {children}
      </div>
    </div>,
    document.getElementById('modal-root')
  );
}
```

### Server-Side Rendering (SSR)

React's SSR capabilities are implemented through specialized renderers:

```javascript
// Server-side rendering setup
import { renderToString } from 'react-dom/server';

function renderApp(req, res) {
  const context = {};
  
  const html = renderToString(
    <StaticRouter location={req.url} context={context}>
      <App />
    </StaticRouter>
  );

  if (context.url) {
    // Handle redirects
    res.redirect(301, context.url);
    return;
  }

  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>My App</title>
      </head>
      <body>
        <div id="root">${html}</div>
        <script src="/bundle.js"></script>
      </body>
    </html>
  `);
}
```

### Concurrent Features

React 18 introduced concurrent features that leverage the renderer architecture:

**Suspense for Data Fetching**:

```javascript
function UserProfile({ userId }) {
  // This component "suspends" until data is available
  const user = use(fetchUser(userId));
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

function App() {
  return (
    <Suspense fallback={<div>Loading user...</div>}>
      <UserProfile userId="123" />
    </Suspense>
  );
}
```

**Streaming SSR**:

```javascript
import { renderToPipeableStream } from 'react-dom/server';

function handleRequest(req, res) {
  const { pipe } = renderToPipeableStream(
    <App />,
    {
      onShellReady() {
        res.statusCode = 200;
        res.setHeader('Content-type', 'text/html');
        pipe(res);
      },
      onError(error) {
        console.error('SSR Error:', error);
        res.statusCode = 500;
        res.send('Internal Server Error');
      }
    }
  );
}
```

### Performance Considerations

The renderer architecture includes several performance optimizations:

- **Batching**: Multiple state updates are batched together
- **Time Slicing**: Long-running renders are broken into chunks
- **Selective Hydration**: Only interactive parts are hydrated first
- **Lazy Loading**: Components can be loaded on demand

```javascript
// Performance optimization example
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <div>
      <Header />
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
      <Footer />
    </div>
  );
}
```

This architecture enables React to maintain high performance while providing a flexible and powerful development experience across multiple platforms and use cases.