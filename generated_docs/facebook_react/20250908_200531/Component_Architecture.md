# Component Architecture

React's component architecture forms the foundation of modern web application development, providing a declarative, composable approach to building user interfaces. This architecture enables developers to create reusable, maintainable, and scalable applications through a well-defined component hierarchy and sophisticated state management patterns.

## Component-Based Design

### Core Principles

React's component-based design follows several fundamental principles that distinguish it from traditional imperative UI frameworks:

**Encapsulation**: Each component encapsulates its own state, logic, and rendering behavior, creating clear boundaries and reducing coupling between different parts of the application.

**Composition over Inheritance**: React favors composition patterns where complex components are built by combining simpler components, rather than extending base classes.

**Unidirectional Data Flow**: Data flows down through the component tree via props, while events bubble up through callback functions, creating predictable data patterns.

### Component Types and Patterns

#### Functional Components

Modern React applications primarily use functional components, which are JavaScript functions that return JSX:

```javascript
// Basic functional component
function UserProfile({ user, onEdit }) {
  return (
    <div className="user-profile">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <button onClick={() => onEdit(user.id)}>Edit Profile</button>
    </div>
  );
}

// TypeScript functional component with interface
interface UserProfileProps {
  user: {
    id: string;
    name: string;
    email: string;
    avatar: string;
  };
  onEdit: (userId: string) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onEdit }) => {
  return (
    <div className="user-profile">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <button onClick={() => onEdit(user.id)}>Edit Profile</button>
    </div>
  );
};
```

#### Higher-Order Components (HOCs)

HOCs provide a pattern for sharing logic between components:

```javascript
// Authentication HOC
function withAuth(WrappedComponent) {
  return function AuthenticatedComponent(props) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      checkAuthStatus()
        .then(setIsAuthenticated)
        .finally(() => setLoading(false));
    }, []);

    if (loading) return <LoadingSpinner />;
    if (!isAuthenticated) return <LoginForm />;

    return <WrappedComponent {...props} />;
  };
}

// Usage
const ProtectedDashboard = withAuth(Dashboard);
```

#### Render Props Pattern

The render props pattern enables flexible component composition:

```javascript
function DataFetcher({ url, render }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(response => response.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return render({ data, loading, error });
}

// Usage
<DataFetcher
  url="/api/users"
  render={({ data, loading, error }) => {
    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage error={error} />;
    return <UserList users={data} />;
  }}
/>
```

### Component Lifecycle and Performance

#### Memoization Strategies

React provides several mechanisms for optimizing component performance:

```javascript
// React.memo for component memoization
const ExpensiveComponent = React.memo(({ data, config }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      computed: expensiveCalculation(item, config)
    }));
  }, [data, config]);

  return (
    <div>
      {processedData.map(item => (
        <ItemComponent key={item.id} item={item} />
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function
  return (
    prevProps.data.length === nextProps.data.length &&
    prevProps.config.version === nextProps.config.version
  );
});
```

#### Error Boundaries

Error boundaries provide graceful error handling in component trees:

```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
    errorReportingService.captureException(error, { extra: errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Hooks System

### Built-in Hooks

React's hooks system revolutionized state management and side effects in functional components, providing a more intuitive and composable approach to component logic.

#### State Management Hooks

```javascript
// useState for local component state
function ShoppingCart() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);

  const addItem = useCallback((product) => {
    setItems(prevItems => [...prevItems, { ...product, id: Date.now() }]);
    setTotal(prevTotal => prevTotal + product.price);
  }, []);

  const removeItem = useCallback((itemId) => {
    setItems(prevItems => {
      const updatedItems = prevItems.filter(item => item.id !== itemId);
      const removedItem = prevItems.find(item => item.id === itemId);
      setTotal(prevTotal => prevTotal - removedItem.price);
      return updatedItems;
    });
  }, []);

  return (
    <div className="shopping-cart">
      <h2>Cart Total: ${total.toFixed(2)}</h2>
      {items.map(item => (
        <CartItem
          key={item.id}
          item={item}
          onRemove={() => removeItem(item.id)}
        />
      ))}
    </div>
  );
}
```

#### Effect Hooks

```javascript
// useEffect for side effects and lifecycle management
function UserDashboard({ userId }) {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);

  // Data fetching effect
  useEffect(() => {
    let cancelled = false;

    async function fetchUserData() {
      try {
        const [userData, notificationData] = await Promise.all([
          api.getUser(userId),
          api.getUserNotifications(userId)
        ]);

        if (!cancelled) {
          setUser(userData);
          setNotifications(notificationData);
        }
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to fetch user data:', error);
        }
      }
    }

    fetchUserData();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  // WebSocket connection effect
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080/users/${userId}`);

    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      setNotifications(prev => [notification, ...prev]);
    };

    return () => {
      ws.close();
    };
  }, [userId]);

  if (!user) return <LoadingSpinner />;

  return (
    <div className="user-dashboard">
      <UserProfile user={user} />
      <NotificationList notifications={notifications} />
    </div>
  );
}
```

### Custom Hooks

Custom hooks enable logic reuse across components:

```javascript
// Custom hook for API data fetching
function useApi(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [url, JSON.stringify(options)]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
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

  const setValue = useCallback((value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue];
}

// Usage in components
function UserPreferences() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');
  const { data: user, loading } = useApi('/api/user/profile');

  if (loading) return <LoadingSpinner />;

  return (
    <div className={`preferences-panel theme-${theme}`}>
      <h2>User Preferences</h2>
      <ThemeSelector value={theme} onChange={setTheme} />
      <UserSettings user={user} />
    </div>
  );
}
```

## Context and State Management

### React Context API

The Context API provides a way to share data across the component tree without prop drilling:

```javascript
// Theme context
const ThemeContext = createContext({
  theme: 'light',
  toggleTheme: () => {},
});

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');

  const toggleTheme = useCallback(() => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  }, []);

  const contextValue = useMemo(() => ({
    theme,
    toggleTheme,
  }), [theme, toggleTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook for consuming theme context
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
```

### Advanced State Management Patterns

#### useReducer for Complex State

```javascript
// Shopping cart reducer
const cartReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_ITEM':
      const existingItem = state.items.find(item => item.id === action.payload.id);
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          ),
          total: state.total + action.payload.price,
        };
      }
      return {
        ...state,
        items: [...state.items, { ...action.payload, quantity: 1 }],
        total: state.total + action.payload.price,
      };

    case 'REMOVE_ITEM':
      const itemToRemove = state.items.find(item => item.id === action.payload);
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload),
        total: state.total - (itemToRemove.price * itemToRemove.quantity),
      };

    case 'UPDATE_QUANTITY':
      const { itemId, quantity } = action.payload;
      const currentItem = state.items.find(item => item.id === itemId);
      const quantityDiff = quantity - currentItem.quantity;
      
      return {
        ...state,
        items: state.items.map(item =>
          item.id === itemId ? { ...item, quantity } : item
        ),
        total: state.total + (currentItem.price * quantityDiff),
      };

    case 'CLEAR_CART':
      return { items: [], total: 0 };

    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
};

function ShoppingCartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [], total: 0 });

  const addItem = useCallback((item) => {
    dispatch({ type: 'ADD_ITEM', payload: item });
  }, []);

  const removeItem = useCallback((itemId) => {
    dispatch({ type: 'REMOVE_ITEM', payload: itemId });
  }, []);

  const updateQuantity = useCallback((itemId, quantity) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { itemId, quantity } });
  }, []);

  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR_CART' });
  }, []);

  const contextValue = useMemo(() => ({
    ...state,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
  }), [state, addItem, removeItem, updateQuantity, clearCart]);

  return (
    <CartContext.Provider value={contextValue}>
      {children}
    </CartContext.Provider>
  );
}
```

### Best Practices and Common Pitfalls

#### Performance Considerations

- **Context Splitting**: Split contexts by update frequency to prevent unnecessary re-renders
- **Memoization**: Use `useMemo` and `useCallback` to prevent expensive recalculations
- **Lazy Loading**: Implement code splitting for large component trees

#### Common Anti-patterns

- **Prop Drilling**: Overusing props instead of context for deeply nested data
- **Massive Contexts**: Creating overly broad contexts that cause widespread re-renders
- **Missing Dependencies**: Forgetting to include dependencies in hook dependency arrays

#### Testing Strategies

```javascript
// Testing components with context
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from './ThemeContext';
import ThemedButton from './ThemedButton';

function renderWithTheme(ui, { theme = 'light' } = {}) {
  return render(
    <ThemeProvider initialTheme={theme}>
      {ui}
    </ThemeProvider>
  );
}

test('renders button with correct theme