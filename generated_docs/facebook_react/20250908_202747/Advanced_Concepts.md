# Advanced Concepts

This section covers advanced React patterns and techniques that enable developers to build sophisticated, maintainable, and performant applications. These concepts are essential for creating complex user interfaces and managing application state effectively.

## Context API

The Context API provides a way to share data between components without explicitly passing props through every level of the component tree. This pattern is particularly useful for global state management, theming, and user authentication.

### Creating and Using Context

```javascript
import React, { createContext, useContext, useReducer } from 'react';

// Create context
const ThemeContext = createContext();
const UserContext = createContext();

// Context provider component
const AppProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [user, setUser] = useState(null);

  const themeValue = {
    theme,
    setTheme,
    toggleTheme: () => setTheme(prev => prev === 'light' ? 'dark' : 'light')
  };

  const userValue = {
    user,
    setUser,
    login: (userData) => setUser(userData),
    logout: () => setUser(null)
  };

  return (
    <ThemeContext.Provider value={themeValue}>
      <UserContext.Provider value={userValue}>
        {children}
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
};

// Custom hooks for consuming context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
```

### Advanced Context Patterns

For complex state management, combine Context API with useReducer:

```javascript
const AppStateContext = createContext();

const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_DATA':
      return { ...state, data: action.payload, loading: false, error: null };
    default:
      return state;
  }
};

const AppStateProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, {
    data: null,
    loading: false,
    error: null
  });

  return (
    <AppStateContext.Provider value={{ state, dispatch }}>
      {children}
    </AppStateContext.Provider>
  );
};
```

### Best Practices

- **Avoid Context Hell**: Don't nest too many providers; consider combining related contexts
- **Performance Optimization**: Split contexts by update frequency to prevent unnecessary re-renders
- **Type Safety**: Use TypeScript interfaces for context values
- **Error Boundaries**: Always provide fallback values and error handling

## Error Boundaries

Error boundaries are React components that catch JavaScript errors anywhere in their child component tree, log those errors, and display a fallback UI instead of crashing the entire application.

### Basic Error Boundary Implementation

```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('Error caught by boundary:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Report to error tracking service
    if (typeof window !== 'undefined' && window.errorTracker) {
      window.errorTracker.captureException(error, {
        extra: errorInfo,
        tags: {
          component: 'ErrorBoundary'
        }
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          {process.env.NODE_ENV === 'development' && (
            <details style={{ whiteSpace: 'pre-wrap' }}>
              <summary>Error Details (Development Only)</summary>
              {this.state.error && this.state.error.toString()}
              <br />
              {this.state.errorInfo.componentStack}
            </details>
          )}
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Hook-Based Error Boundary (React 18+)

```javascript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert" className="error-fallback">
      <h2>Oops! Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function MyApp() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        console.log('Error logged:', error, errorInfo);
      }}
      onReset={() => {
        // Reset app state if needed
        window.location.reload();
      }}
    >
      <App />
    </ErrorBoundary>
  );
}
```

### Strategic Error Boundary Placement

- **Route Level**: Wrap entire routes to prevent navigation failures
- **Feature Level**: Isolate complex features or third-party components
- **Component Level**: Protect critical UI components

## Refs and DOM Manipulation

Refs provide a way to access DOM nodes or React elements directly, enabling imperative DOM manipulation when declarative approaches aren't sufficient.

### useRef Hook Patterns

```javascript
import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react';

// Basic DOM manipulation
const FocusInput = () => {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleClear = () => {
    if (inputRef.current) {
      inputRef.current.value = '';
      inputRef.current.focus();
    }
  };

  return (
    <div>
      <input ref={inputRef} type="text" />
      <button onClick={handleClear}>Clear</button>
    </div>
  );
};

// Forward refs for component composition
const CustomInput = forwardRef((props, ref) => {
  const internalRef = useRef();
  
  useImperativeHandle(ref, () => ({
    focus: () => internalRef.current?.focus(),
    clear: () => {
      if (internalRef.current) {
        internalRef.current.value = '';
      }
    },
    getValue: () => internalRef.current?.value || ''
  }));

  return <input ref={internalRef} {...props} />;
});

// Usage of forwarded ref
const ParentComponent = () => {
  const customInputRef = useRef();

  const handleAction = () => {
    customInputRef.current?.focus();
    console.log('Current value:', customInputRef.current?.getValue());
  };

  return (
    <div>
      <CustomInput ref={customInputRef} placeholder="Enter text" />
      <button onClick={handleAction}>Focus & Log</button>
    </div>
  );
};
```

### Advanced Ref Patterns

```javascript
// Callback refs for dynamic elements
const DynamicList = ({ items }) => {
  const itemRefs = useRef({});

  const setItemRef = (id) => (element) => {
    if (element) {
      itemRefs.current[id] = element;
    } else {
      delete itemRefs.current[id];
    }
  };

  const scrollToItem = (id) => {
    itemRefs.current[id]?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div>
      {items.map(item => (
        <div
          key={item.id}
          ref={setItemRef(item.id)}
          onClick={() => scrollToItem(item.id)}
        >
          {item.content}
        </div>
      ))}
    </div>
  );
};

// Measuring DOM elements
const useMeasure = () => {
  const ref = useRef();
  const [bounds, setBounds] = useState({});

  useEffect(() => {
    if (ref.current) {
      const resizeObserver = new ResizeObserver(entries => {
        const { width, height } = entries[0].contentRect;
        setBounds({ width, height });
      });
      
      resizeObserver.observe(ref.current);
      return () => resizeObserver.disconnect();
    }
  }, []);

  return [ref, bounds];
};
```

## Higher-Order Components (HOCs)

Higher-Order Components are functions that take a component and return a new component with enhanced functionality. They're useful for cross-cutting concerns like authentication, logging, and data fetching.

### Basic HOC Pattern

```javascript
// Authentication HOC
const withAuth = (WrappedComponent) => {
  return function AuthenticatedComponent(props) {
    const { user, loading } = useUser();

    if (loading) {
      return <div>Loading...</div>;
    }

    if (!user) {
      return <div>Please log in to access this content.</div>;
    }

    return <WrappedComponent {...props} user={user} />;
  };
};

// Usage
const Dashboard = ({ user, ...props }) => (
  <div>
    <h1>Welcome, {user.name}!</h1>
    {/* Dashboard content */}
  </div>
);

const AuthenticatedDashboard = withAuth(Dashboard);
```

### Advanced HOC Patterns

```javascript
// Data fetching HOC with loading states
const withData = (url, propName = 'data') => (WrappedComponent) => {
  return function DataComponent(props) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      const fetchData = async () => {
        try {
          setLoading(true);
          const response = await fetch(url);
          if (!response.ok) throw new Error('Failed to fetch');
          const result = await response.json();
          setData(result);
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };

      fetchData();
    }, [url]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    const enhancedProps = {
      ...props,
      [propName]: data,
      loading,
      error
    };

    return <WrappedComponent {...enhancedProps} />;
  };
};

// Composable HOCs
const enhance = compose(
  withAuth,
  withData('/api/user-data', 'userData'),
  withErrorBoundary
);

const EnhancedComponent = enhance(MyComponent);
```

### HOC Best Practices

- **Don't Mutate the Original Component**: Always return a new component
- **Copy Static Methods**: Use `hoist-non-react-statics` to preserve static methods
- **Pass Through Props**: Ensure all props are passed to the wrapped component
- **Use Display Names**: Set meaningful display names for debugging

## Render Props

Render props is a pattern where a component accepts a function as a prop and calls that function to determine what to render. This pattern provides maximum flexibility for component composition.

### Basic Render Props Pattern

```javascript
// Mouse tracker with render props
const MouseTracker = ({ render }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event) => {
      setPosition({ x: event.clientX, y: event.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return render(position);
};

// Usage
const App = () => (
  <MouseTracker
    render={({ x, y }) => (
      <div>
        <h1>Mouse position: ({x}, {y})</h1>
        <div
          style={{
            position: 'absolute',
            left: x,
            top: y,
            width: 10,
            height: 10,
            backgroundColor: 'red',
            borderRadius: '50%'
          }}
        />
      </div>
    )}
  />
);
```

### Advanced Render Props Patterns

```javascript
// Data fetcher with render props
const DataFetcher = ({ url, children }) => {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true }));
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        if (!cancelled) {
          setState({ data, loading: false, error: null });
        }
      } catch (error) {
        if (!cancelled) {
          setState({ data: null, loading: false, error: error.message });
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [url]);

  return children(state);
};

// Toggle component with render props
const Toggle = ({ initial = false, children }) => {
  const [on, setOn] = useState(initial);

  const toggle = () => setOn(prev => !prev);
  const turnOn = () => setOn(true);
  const turnOff = () => setOn(false);

  return children({ on, toggle, turnOn, turnOff });
};

// Usage examples
const MyApp = () => (
  <div>
    <DataFetcher url="/api/users">
      {({ data, loading, error }) => {
        if (loading) return <div>Loading...</div>;
        if (error) return <div>Error: {error}</div>;
        return (
          <ul>
            {data.map(user => (
              <li key={user.id}>{user.name}</li>
            ))}
          </ul>
        );
      }}
    </DataFetcher>

    <Toggle initial={false}>
      {({ on, toggle }) => (
        <div>
          <button onClick={toggle}>
            {on ? 'Turn Off' : 'Turn On'}
          </button>
          {on && <div>The toggle is on!</div>}
        </div>
      )}
    </Toggle>
  </div>
);
```

## Code Splitting and Lazy Loading

Code splitting allows you to split your bundle into smaller chunks that can be loaded on demand, improving initial load times and overall performance.

### React.lazy and Suspense

```javascript
import React, { Suspense, lazy } from 'react';

// Lazy load components
const Dashboard = lazy(() => import('./Dashboard'));
const Profile = lazy(() => import('./Profile'));
const Settings = lazy(() => import('./Settings'));

// Loading component
const LoadingSpinner = () =>