# API Reference

This comprehensive API reference provides detailed documentation for React's core functionality, including fundamental APIs, Hooks, and advanced features. React's declarative, component-based architecture enables developers to build complex user interfaces through a well-designed set of APIs that promote reusability, maintainability, and performance.

## Core APIs

### React.Component

The base class for React components when using ES6 classes. Components defined as classes have access to lifecycle methods and local state management.

```javascript
import React, { Component } from 'react';

class MyComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      count: 0
    };
  }

  componentDidMount() {
    console.log('Component mounted');
  }

  render() {
    return (
      <div>
        <h1>Count: {this.state.count}</h1>
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
- `componentDidMount()`: Called after component is mounted to DOM
- `componentDidUpdate(prevProps, prevState)`: Called after component updates
- `componentWillUnmount()`: Called before component is removed from DOM
- `setState(updater, callback)`: Updates component state and triggers re-render

### React.createElement()

Creates and returns a new React element of the given type. This is the underlying function that JSX compiles to.

```javascript
// JSX syntax
const element = <h1 className="greeting">Hello, world!</h1>;

// Equivalent createElement call
const element = React.createElement(
  'h1',
  { className: 'greeting' },
  'Hello, world!'
);

// Creating component elements
const componentElement = React.createElement(
  MyComponent,
  { prop1: 'value1', prop2: 'value2' },
  'Child content'
);
```

**Parameters:**
- `type`: String (HTML tag) or React component
- `props`: Object containing properties and attributes
- `...children`: Child elements or content

### React.Fragment

Allows grouping of multiple elements without adding extra DOM nodes. Essential for maintaining clean HTML structure.

```javascript
import React, { Fragment } from 'react';

// Using React.Fragment
function MyComponent() {
  return (
    <Fragment>
      <h1>Title</h1>
      <p>Description</p>
    </Fragment>
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

// With key prop for lists
function ListComponent({ items }) {
  return (
    <ul>
      {items.map(item => (
        <Fragment key={item.id}>
          <li>{item.name}</li>
          <li>{item.description}</li>
        </Fragment>
      ))}
    </ul>
  );
}
```

### React.memo()

Higher-order component that memoizes the result of a component, preventing unnecessary re-renders when props haven't changed.

```javascript
import React, { memo } from 'react';

const ExpensiveComponent = memo(function ExpensiveComponent({ data, config }) {
  // Expensive calculations or rendering logic
  const processedData = processLargeDataset(data);
  
  return (
    <div>
      <h2>{config.title}</h2>
      <DataVisualization data={processedData} />
    </div>
  );
});

// Custom comparison function
const MyComponent = memo(function MyComponent(props) {
  return <div>{props.name}</div>;
}, (prevProps, nextProps) => {
  // Return true if props are equal (skip re-render)
  return prevProps.name === nextProps.name;
});
```

## Hooks API

### useState

Manages local state in functional components. Returns current state value and a setter function.

```javascript
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [user, setUser] = useState({ name: '', email: '' });

  // Functional updates for complex state logic
  const increment = () => {
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
      <button onClick={increment}>Increment</button>
      
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
- Initialize state with functions for expensive computations

### useEffect

Handles side effects in functional components, replacing lifecycle methods from class components.

```javascript
import React, { useState, useEffect } from 'react';

function DataFetcher({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Effect with dependency array
  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        
        if (!cancelled) {
          setData(userData);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchData();

    // Cleanup function
    return () => {
      cancelled = true;
    };
  }, [userId]); // Re-run when userId changes

  // Effect for subscriptions
  useEffect(() => {
    const subscription = subscribeToUpdates(userId, (update) => {
      setData(prevData => ({ ...prevData, ...update }));
    });

    return () => subscription.unsubscribe();
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  return <div>{JSON.stringify(data, null, 2)}</div>;
}
```

**Effect Patterns:**
- Empty dependency array `[]`: Run once on mount
- No dependency array: Run on every render
- With dependencies `[dep1, dep2]`: Run when dependencies change

### useContext

Consumes context values without nesting Consumer components.

```javascript
import React, { createContext, useContext, useState } from 'react';

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

// Custom hooks for context consumption
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
}

// Component using context
function ThemedButton() {
  const { theme, setTheme } = useTheme();
  const { user } = useUser();

  return (
    <button
      className={`btn btn-${theme}`}
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {user ? `Hello, ${user.name}` : 'Login'}
    </button>
  );
}
```

### useReducer

Manages complex state logic through reducer functions, similar to Redux patterns.

```javascript
import React, { useReducer } from 'react';

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
  const [inputValue, setInputValue] = useState('');

  const addTodo = () => {
    if (inputValue.trim()) {
      dispatch({ type: 'ADD_TODO', payload: inputValue });
      setInputValue('');
    }
  };

  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === 'completed') return todo.completed;
    if (state.filter === 'active') return !todo.completed;
    return true;
  });

  return (
    <div>
      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && addTodo()}
      />
      <button onClick={addTodo}>Add Todo</button>
      
      <div>
        {['all', 'active', 'completed'].map(filter => (
          <button
            key={filter}
            onClick={() => dispatch({ type: 'SET_FILTER', payload: filter })}
            className={state.filter === filter ? 'active' : ''}
          >
            {filter}
          </button>
        ))}
      </div>

      <ul>
        {filteredTodos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
            />
            <span className={todo.completed ? 'completed' : ''}>{todo.text}</span>
            <button onClick={() => dispatch({ type: 'DELETE_TODO', payload: todo.id })}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Advanced APIs

### React.lazy() and Suspense

Enables code splitting and lazy loading of components for improved performance.

```javascript
import React, { Suspense, lazy } from 'react';

// Lazy load components
const Dashboard = lazy(() => import('./Dashboard'));
const Profile = lazy(() => import('./Profile'));
const Settings = lazy(() => import('./Settings'));

// Loading component
function LoadingSpinner() {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p>Loading...</p>
    </div>
  );
}

// Error boundary for lazy loading
class LazyLoadErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong while loading the component.</div>;
    }

    return this.props.children;
  }
}

// App with lazy loading
function App() {
  const [currentView, setCurrentView] = useState('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'profile':
        return <Profile />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <nav>
        <button onClick={() => setCurrentView('dashboard')}>Dashboard</button>
        <button onClick={() => setCurrentView('profile')}>Profile</button>
        <button onClick={() => setCurrentView('settings')}>Settings</button>
      </nav>

      <main>
        <LazyLoadErrorBoundary>
          <Suspense fallback={<LoadingSpinner />}>
            {renderView()}
          </Suspense>
        </LazyLoadErrorBoundary>
      </main>
    </div>
  );
}
```

### Error Boundaries

Components that catch JavaScript errors in their component tree and display fallback UI.

```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state to show fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
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
          <details style={{ whiteSpace: 'pre-wrap' }}>
            <summary>Error Details</summary>
            <p><strong>Error:</strong> {this.state.error && this.state.error.toString()}</p>
            <p><strong>Stack Trace:</strong></p>
            <pre>{this.state.errorInfo.componentStack}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage with multiple error boundaries
function App() {
  return (
    <div>
      <ErrorBoundary>
        <Header />
      </ErrorBoundary>
      
      <ErrorBoundary>
        <Sidebar />
      </ErrorBoundary>
      
      <ErrorBoundary>
        <MainContent />
      </ErrorBoundary>
    </div>
  );
}
```

### Custom Hooks

Reusable stateful logic that can be shared between components.

```javascript
import { useState, useEffect, useCallback, useRef } from 'react