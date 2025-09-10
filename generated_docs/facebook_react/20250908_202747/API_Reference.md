# API Reference

This comprehensive API reference provides detailed documentation for React's core APIs, hooks, and utility functions. React is a declarative, efficient, and flexible JavaScript library for building user interfaces, particularly web applications with complex state management and component hierarchies.

## React API

### React.Component

The base class for React components when defined as ES6 classes. Provides the fundamental lifecycle methods and state management capabilities.

```javascript
class MyComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }

  componentDidMount() {
    // Component has mounted
    console.log('Component mounted');
  }

  componentDidUpdate(prevProps, prevState) {
    // Component has updated
    if (prevState.count !== this.state.count) {
      console.log('Count updated:', this.state.count);
    }
  }

  componentWillUnmount() {
    // Cleanup before component unmounts
    console.log('Component will unmount');
  }

  render() {
    return (
      <div>
        <p>Count: {this.state.count}</p>
        <button onClick={() => this.setState({ count: this.state.count + 1 })}>
          Increment
        </button>
      </div>
    );
  }
}
```

**Key Methods:**
- `render()`: Required method that returns JSX elements
- `setState(updater, callback)`: Updates component state and triggers re-render
- `forceUpdate(callback)`: Forces a re-render bypassing shouldComponentUpdate

### React.PureComponent

An optimized version of React.Component that implements `shouldComponentUpdate` with shallow prop and state comparison.

```javascript
class OptimizedComponent extends React.PureComponent {
  render() {
    return <div>{this.props.title}</div>;
  }
}
```

**Best Practices:**
- Use for components with simple props and state
- Avoid when props contain complex objects or arrays
- Consider React.memo for functional components instead

### React.createElement

Creates and returns a new React element of the given type. This is the underlying function that JSX compiles to.

```javascript
// JSX
const element = <div className="container">Hello World</div>;

// Equivalent React.createElement call
const element = React.createElement(
  'div',
  { className: 'container' },
  'Hello World'
);

// With multiple children
const complexElement = React.createElement(
  'div',
  { className: 'container' },
  React.createElement('h1', null, 'Title'),
  React.createElement('p', null, 'Description')
);
```

**Parameters:**
- `type`: String (HTML tag) or React component
- `props`: Object containing properties and attributes
- `...children`: Child elements or text content

### React.Fragment

Allows grouping of multiple elements without adding extra DOM nodes.

```javascript
// Using React.Fragment
function MyComponent() {
  return (
    <React.Fragment>
      <h1>Title</h1>
      <p>Description</p>
    </React.Fragment>
  );
}

// Using short syntax
function MyComponent() {
  return (
    <>
      <h1>Title</h1>
      <p>Description</p>
    </>
  );
}

// With key prop (useful in lists)
function ListItems({ items }) {
  return items.map(item => (
    <React.Fragment key={item.id}>
      <dt>{item.term}</dt>
      <dd>{item.description}</dd>
    </React.Fragment>
  ));
}
```

### React.memo

Higher-order component that memoizes functional components, preventing unnecessary re-renders when props haven't changed.

```javascript
const ExpensiveComponent = React.memo(function ExpensiveComponent({ data, options }) {
  // Expensive calculations or rendering
  const processedData = expensiveCalculation(data);
  
  return (
    <div>
      {processedData.map(item => (
        <div key={item.id}>{item.value}</div>
      ))}
    </div>
  );
});

// With custom comparison function
const CustomMemoComponent = React.memo(function CustomMemoComponent(props) {
  return <div>{props.content}</div>;
}, (prevProps, nextProps) => {
  // Return true if props are equal (skip re-render)
  return prevProps.content === nextProps.content;
});
```

## Hooks API

### useState

Manages local state in functional components. Returns current state value and a setter function.

```javascript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState({ name: '', email: '' });

  // Functional update for complex state logic
  const incrementCount = () => {
    setCount(prevCount => prevCount + 1);
  };

  // Updating object state
  const updateUser = (field, value) => {
    setUser(prevUser => ({
      ...prevUser,
      [field]: value
    }));
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={incrementCount}>Increment</button>
      
      <input
        value={user.name}
        onChange={(e) => updateUser('name', e.target.value)}
        placeholder="Name"
      />
    </div>
  );
}
```

**Best Practices:**
- Use functional updates when new state depends on previous state
- Split state into multiple useState calls for unrelated data
- Initialize with function for expensive initial state: `useState(() => expensiveComputation())`

### useEffect

Handles side effects in functional components, replacing lifecycle methods from class components.

```javascript
import { useEffect, useState } from 'react';

function DataFetcher({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Effect with cleanup
  useEffect(() => {
    let cancelled = false;
    
    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        
        if (!cancelled) {
          setData(userData);
          setLoading(false);
        }
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to fetch user data:', error);
          setLoading(false);
        }
      }
    }

    fetchData();

    // Cleanup function
    return () => {
      cancelled = true;
    };
  }, [userId]); // Dependency array

  // Effect for event listeners
  useEffect(() => {
    function handleResize() {
      console.log('Window resized');
    }

    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []); // Empty dependency array - runs once

  if (loading) return <div>Loading...</div>;
  return <div>{data?.name}</div>;
}
```

**Effect Patterns:**
- **No dependency array**: Runs after every render
- **Empty dependency array `[]`**: Runs once after initial render
- **With dependencies `[dep1, dep2]`**: Runs when dependencies change

### useContext

Consumes context values without nesting Consumer components.

```javascript
import { createContext, useContext, useState } from 'react';

// Create context
const ThemeContext = createContext();
const UserContext = createContext();

// Provider component
function AppProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const [user, setUser] = useState(null);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <UserContext.Provider value={{ user, setUser }}>
        {children}
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
}

// Consumer component
function ThemedButton() {
  const { theme, setTheme } = useContext(ThemeContext);
  const { user } = useContext(UserContext);

  return (
    <button
      className={`btn btn-${theme}`}
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {user ? `Hello, ${user.name}` : 'Sign In'}
    </button>
  );
}

// Custom hook for theme context
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
```

### useReducer

Manages complex state logic with a reducer function, similar to Redux patterns.

```javascript
import { useReducer } from 'react';

// Reducer function
function todoReducer(state, action) {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [...state.todos, {
          id: Date.now(),
          text: action.payload,
          completed: false
        }]
      };
    
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload
            ? { ...todo, completed: !todo.completed }
            : todo
        )
      };
    
    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload)
      };
    
    case 'SET_FILTER':
      return {
        ...state,
        filter: action.payload
      };
    
    default:
      throw new Error(`Unknown action type: ${action.type}`);
  }
}

// Initial state
const initialState = {
  todos: [],
  filter: 'all'
};

function TodoApp() {
  const [state, dispatch] = useReducer(todoReducer, initialState);

  const addTodo = (text) => {
    dispatch({ type: 'ADD_TODO', payload: text });
  };

  const toggleTodo = (id) => {
    dispatch({ type: 'TOGGLE_TODO', payload: id });
  };

  return (
    <div>
      <TodoInput onAdd={addTodo} />
      <TodoList 
        todos={state.todos} 
        onToggle={toggleTodo}
        filter={state.filter}
      />
    </div>
  );
}
```

### Custom Hooks

Create reusable stateful logic by combining built-in hooks.

```javascript
// Custom hook for API data fetching
function useApi(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
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

// Custom hook for local storage
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}

// Usage example
function UserProfile() {
  const { data: user, loading, error } = useApi('/api/user/profile');
  const [preferences, setPreferences] = useLocalStorage('userPreferences', {});

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>{user.name}</h1>
      <UserPreferences 
        preferences={preferences}
        onUpdate={setPreferences}
      />
    </div>
  );
}
```

## Utilities

### React.lazy

Enables code splitting by dynamically importing components, reducing initial bundle size.

```javascript
import { lazy, Suspense } from 'react';

// Lazy load components
const Dashboard = lazy(() => import('./Dashboard'));
const Profile = lazy(() => import('./Profile'));
const Settings = lazy(() => import('./Settings'));

// With named exports
const Analytics = lazy(() => 
  import('./Analytics').then(module => ({ default: module.Analytics }))
);

function App() {
  return (
    <div>
      <nav>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/profile">Profile</Link>
      </nav>
      
      <Suspense fallback={<div className="loading-spinner">Loading...</div>}>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Suspense>
    </div>
  );
}

// Advanced loading component
function LoadingFallback({ message = "Loading..." }) {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  );
}

// Error boundary for lazy components
class LazyErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Lazy component loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong loading this component.</div>;
    }

    return this.props.children;
  }
}
```

### React.Suspense

Handles loading states for lazy components and concurrent features.

```javascript
import { Suspense, lazy } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <div>
      <h1>My App</h1>
      
      {/* Basic suspense */}
      <Suspense fallback={<div>Loading component...</div>}>
        <HeavyComponent />
      </Suspense>

      {/* Nested suspense boundaries */}
      <Suspense fallback={<PageLoader />}>
        <MainContent>
          <Suspense fallback={<SectionLoader />}>
            <DynamicSection />
          </Suspense>
        </MainContent>
      </Suspense>
    </div>
  );
}

// Custom loading components
function PageLoader() {
  return (
    <div className="page-loader">
      <div className="skeleton-header" />
      