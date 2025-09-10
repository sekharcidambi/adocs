# Hooks

React Hooks are a powerful feature introduced in React 16.8 that allow you to use state and other React features in functional components. Hooks provide a more direct API to the React concepts you already know, enabling you to write more concise and reusable code while maintaining the same functionality as class components.

Hooks fundamentally changed how React applications are built by allowing developers to:
- Use state and lifecycle methods in functional components
- Share stateful logic between components without complex patterns like higher-order components or render props
- Split one component into smaller functions based on related pieces
- Optimize performance through fine-grained control over re-renders

## Built-in Hooks

React provides several built-in hooks that cover the most common use cases in component development. These hooks are divided into basic hooks and additional hooks for more advanced scenarios.

### Basic Hooks

#### useState

The `useState` hook allows you to add state to functional components. It returns an array with two elements: the current state value and a function to update it.

```javascript
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
      <button onClick={() => setCount(prevCount => prevCount + 1)}>
        Increment (functional update)
      </button>
      
      <input 
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter name"
      />
    </div>
  );
}
```

**Best Practices:**
- Use functional updates when the new state depends on the previous state
- Initialize state with the appropriate data type
- Consider using multiple state variables for unrelated data instead of a single object

#### useEffect

The `useEffect` hook lets you perform side effects in functional components. It serves the same purpose as `componentDidMount`, `componentDidUpdate`, and `componentWillUnmount` combined.

```javascript
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Effect with dependency array
  useEffect(() => {
    async function fetchUser() {
      setLoading(true);
      try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, [userId]); // Only re-run when userId changes

  // Effect with cleanup
  useEffect(() => {
    const handleResize = () => {
      console.log('Window resized');
    };

    window.addEventListener('resize', handleResize);
    
    // Cleanup function
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []); // Empty dependency array means this runs once

  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{user?.name}</h1>
      <p>{user?.email}</p>
    </div>
  );
}
```

#### useContext

The `useContext` hook provides a way to consume context values without nesting Consumer components.

```javascript
import React, { createContext, useContext, useState } from 'react';

// Create context
const ThemeContext = createContext();

// Provider component
function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Consumer component using useContext
function ThemedButton() {
  const { theme, toggleTheme } = useContext(ThemeContext);
  
  return (
    <button 
      onClick={toggleTheme}
      style={{
        backgroundColor: theme === 'light' ? '#fff' : '#333',
        color: theme === 'light' ? '#333' : '#fff'
      }}
    >
      Toggle Theme (Current: {theme})
    </button>
  );
}
```

### Additional Hooks

#### useReducer

The `useReducer` hook is an alternative to `useState` for managing complex state logic. It's particularly useful when state transitions are complex or when the next state depends on the previous one.

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
    default:
      return state;
  }
}

function TodoApp() {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: [],
    filter: 'all'
  });

  const addTodo = (text) => {
    dispatch({ type: 'ADD_TODO', payload: text });
  };

  const toggleTodo = (id) => {
    dispatch({ type: 'TOGGLE_TODO', payload: id });
  };

  return (
    <div>
      <input 
        onKeyPress={(e) => {
          if (e.key === 'Enter' && e.target.value.trim()) {
            addTodo(e.target.value.trim());
            e.target.value = '';
          }
        }}
        placeholder="Add todo..."
      />
      <ul>
        {state.todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{
              textDecoration: todo.completed ? 'line-through' : 'none'
            }}>
              {todo.text}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

#### useMemo and useCallback

These hooks help optimize performance by memoizing expensive calculations and function references.

```javascript
import React, { useState, useMemo, useCallback } from 'react';

function ExpensiveComponent({ items, onItemClick }) {
  // Memoize expensive calculation
  const expensiveValue = useMemo(() => {
    console.log('Calculating expensive value...');
    return items.reduce((sum, item) => sum + item.value, 0);
  }, [items]);

  // Memoize callback to prevent unnecessary re-renders
  const handleClick = useCallback((item) => {
    onItemClick(item);
  }, [onItemClick]);

  return (
    <div>
      <p>Total Value: {expensiveValue}</p>
      {items.map(item => (
        <button key={item.id} onClick={() => handleClick(item)}>
          {item.name}
        </button>
      ))}
    </div>
  );
}
```

#### useRef

The `useRef` hook provides a way to access DOM elements directly and persist values across renders without causing re-renders.

```javascript
import React, { useRef, useEffect, useState } from 'react';

function FocusInput() {
  const inputRef = useRef(null);
  const renderCount = useRef(0);
  const [value, setValue] = useState('');

  useEffect(() => {
    renderCount.current += 1;
    inputRef.current?.focus();
  });

  return (
    <div>
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="This input will auto-focus"
      />
      <p>Render count: {renderCount.current}</p>
    </div>
  );
}
```

## Custom Hooks

Custom hooks are JavaScript functions that start with "use" and can call other hooks. They allow you to extract component logic into reusable functions, promoting code reuse and separation of concerns.

### Creating Custom Hooks

```javascript
import { useState, useEffect } from 'react';

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

// Usage of custom hooks
function UserDashboard() {
  const { data: users, loading, error } = useApi('/api/users');
  const [preferences, setPreferences] = useLocalStorage('userPreferences', {
    theme: 'light',
    notifications: true
  });

  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>User Dashboard</h1>
      <p>Theme: {preferences.theme}</p>
      <button onClick={() => 
        setPreferences(prev => ({ 
          ...prev, 
          theme: prev.theme === 'light' ? 'dark' : 'light' 
        }))
      }>
        Toggle Theme
      </button>
      <ul>
        {users?.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Advanced Custom Hook Patterns

```javascript
// Custom hook with cleanup and cancellation
function useAsyncOperation() {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(async (asyncFunction) => {
    setState({ data: null, loading: true, error: null });
    
    try {
      const result = await asyncFunction();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      setState({ data: null, loading: false, error });
      throw error;
    }
  }, []);

  return { ...state, execute };
}

// Custom hook for form handling
function useForm(initialValues, validationSchema) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const handleChange = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  }, [errors]);

  const handleBlur = useCallback((name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    
    // Validate field on blur
    if (validationSchema[name]) {
      const error = validationSchema[name](values[name]);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  }, [values, validationSchema]);

  const validate = useCallback(() => {
    const newErrors = {};
    Object.keys(validationSchema).forEach(key => {
      const error = validationSchema[key](values[key]);
      if (error) newErrors[key] = error;
    });
    
    setErrors(newErrors);
    setTouched(Object.keys(validationSchema).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {}));
    
    return Object.keys(newErrors).length === 0;
  }, [values, validationSchema]);

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validate,
    isValid: Object.keys(errors).length === 0
  };
}
```

## Rules of Hooks

The Rules of Hooks are essential guidelines that must be followed to ensure hooks work correctly. These rules are enforced by the ESLint plugin `eslint-plugin-react-hooks`.

### Rule 1: Only Call Hooks at the Top Level

**✅ Correct:**
```javascript
function MyComponent() {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');
  
  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);

  return <div>{count}</div>;
}
```

**❌ Incorrect:**
```javascript
function MyComponent() {
  if (someCondition) {
    const [count, setCount] = useState(0); // ❌ Don't call hooks inside conditions
  }

  for (let i = 0; i < 10; i++) {
    useEffect(() => {}); // ❌ Don't call hooks inside loops
  }

  function handleClick() {
    const [state, setState] = useState(); // ❌ Don't call hooks inside nested functions
  }

  return <div>Content</div>;
}
```

### Rule 2: Only Call Hooks from React Functions

**✅ Correct:**
```javascript
// ✅ Call hooks from React function components
function MyComponent() {
  const [state, setState] = useState();
  return <div />;
}

// ✅ Call hooks from custom hooks
function useCustomHook() {
  const [state, setState] = useState();
  return state;
}
```

**❌ Incorrect:**
```javascript
// ❌ Don't call hooks from regular JavaScript functions
function regularFunction() {
  const [state, setState] = useState(); // ❌ This