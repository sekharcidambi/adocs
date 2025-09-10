# API Reference

This comprehensive API reference covers the core React library APIs that developers use to build modern web applications. React's API is designed to be minimal yet powerful, providing the essential building blocks for creating interactive user interfaces through a component-based architecture.

## React Core API

The React Core API provides the fundamental functions and classes for creating and managing React components, elements, and application state.

### React.Component

The base class for React components when using ES6 classes. Components defined as classes must extend `React.Component` and implement a `render()` method.

```javascript
import React, { Component } from 'react';

class UserProfile extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      userData: null
    };
  }

  componentDidMount() {
    this.fetchUserData();
  }

  fetchUserData = async () => {
    try {
      const response = await fetch(`/api/users/${this.props.userId}`);
      const userData = await response.json();
      this.setState({ userData, isLoading: false });
    } catch (error) {
      this.setState({ isLoading: false });
    }
  }

  render() {
    const { isLoading, userData } = this.state;
    
    if (isLoading) return <div>Loading...</div>;
    
    return (
      <div className="user-profile">
        <h2>{userData?.name}</h2>
        <p>{userData?.email}</p>
      </div>
    );
  }
}
```

**Key Methods:**
- `componentDidMount()`: Invoked after component is mounted
- `componentDidUpdate(prevProps, prevState)`: Invoked after updates
- `componentWillUnmount()`: Invoked before component is unmounted
- `setState(updater, callback)`: Updates component state
- `forceUpdate(callback)`: Forces a re-render

### React.createElement()

Creates and returns a new React element of the given type. This is the fundamental function that JSX compiles to.

```javascript
// JSX syntax
const element = <div className="container">Hello World</div>;

// Equivalent React.createElement call
const element = React.createElement(
  'div',
  { className: 'container' },
  'Hello World'
);

// Creating elements with multiple children
const complexElement = React.createElement(
  'div',
  { className: 'app' },
  React.createElement('h1', null, 'Welcome'),
  React.createElement('p', null, 'This is a React application')
);
```

**Parameters:**
- `type`: Element type (string for DOM elements, component for React components)
- `props`: Properties object (can be null)
- `...children`: Child elements

### React.Fragment

Allows grouping of multiple elements without adding extra DOM nodes. Essential for maintaining clean HTML structure.

```javascript
import React, { Fragment } from 'react';

// Using React.Fragment
function NavigationItems() {
  return (
    <Fragment>
      <li><a href="/home">Home</a></li>
      <li><a href="/about">About</a></li>
      <li><a href="/contact">Contact</a></li>
    </Fragment>
  );
}

// Using short syntax
function NavigationItemsShort() {
  return (
    <>
      <li><a href="/home">Home</a></li>
      <li><a href="/about">About</a></li>
      <li><a href="/contact">Contact</a></li>
    </>
  );
}
```

### React.memo()

Higher-order component that memoizes the result of a component, preventing unnecessary re-renders when props haven't changed.

```javascript
import React, { memo } from 'react';

const ExpensiveComponent = memo(function ExpensiveComponent({ data, onUpdate }) {
  console.log('Rendering ExpensiveComponent');
  
  return (
    <div>
      {data.map(item => (
        <div key={item.id} onClick={() => onUpdate(item.id)}>
          {item.name}
        </div>
      ))}
    </div>
  );
});

// Custom comparison function
const OptimizedComponent = memo(function OptimizedComponent(props) {
  return <div>{props.content}</div>;
}, (prevProps, nextProps) => {
  return prevProps.content === nextProps.content;
});
```

## Hooks API

React Hooks enable functional components to use state and lifecycle features previously available only in class components.

### useState

Manages local state in functional components. Returns a stateful value and a function to update it.

```javascript
import React, { useState } from 'react';

function ShoppingCart() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);

  const addItem = (item) => {
    setItems(prevItems => [...prevItems, item]);
    setTotal(prevTotal => prevTotal + item.price);
  };

  const removeItem = (itemId) => {
    setItems(prevItems => {
      const newItems = prevItems.filter(item => item.id !== itemId);
      const removedItem = prevItems.find(item => item.id === itemId);
      setTotal(prevTotal => prevTotal - removedItem.price);
      return newItems;
    });
  };

  return (
    <div className="shopping-cart">
      <h2>Cart Total: ${total.toFixed(2)}</h2>
      {items.map(item => (
        <div key={item.id}>
          {item.name} - ${item.price}
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
    </div>
  );
}
```

**Best Practices:**
- Use functional updates when new state depends on previous state
- Split state into multiple useState calls for unrelated data
- Use objects/arrays carefully to avoid mutation

### useEffect

Performs side effects in functional components. Combines `componentDidMount`, `componentDidUpdate`, and `componentWillUnmount`.

```javascript
import React, { useState, useEffect } from 'react';

function UserDashboard({ userId }) {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Effect with dependency array
  useEffect(() => {
    async function fetchUserData() {
      setLoading(true);
      try {
        const [userResponse, postsResponse] = await Promise.all([
          fetch(`/api/users/${userId}`),
          fetch(`/api/users/${userId}/posts`)
        ]);
        
        const userData = await userResponse.json();
        const postsData = await postsResponse.json();
        
        setUser(userData);
        setPosts(postsData);
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchUserData();
  }, [userId]); // Re-run when userId changes

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
  }, []); // Empty dependency array = run once

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{user?.name}</h1>
      <div className="posts">
        {posts.map(post => (
          <article key={post.id}>
            <h3>{post.title}</h3>
            <p>{post.content}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
```

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

// Component using context
function Header() {
  const { theme, setTheme } = useContext(ThemeContext);
  const { user } = useContext(UserContext);

  return (
    <header className={`header ${theme}`}>
      <h1>My App</h1>
      {user && <span>Welcome, {user.name}</span>}
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
    </header>
  );
}
```

### useReducer

Alternative to useState for complex state logic. Accepts a reducer function and returns current state with a dispatch method.

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
      return state;
  }
}

function TodoApp() {
  const initialState = {
    todos: [],
    filter: 'all'
  };

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
    <div className="todo-app">
      <input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && addTodo()}
      />
      <button onClick={addTodo}>Add Todo</button>
      
      <div className="filters">
        {['all', 'active', 'completed'].map(filter => (
          <button
            key={filter}
            className={state.filter === filter ? 'active' : ''}
            onClick={() => dispatch({ type: 'SET_FILTER', payload: filter })}
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
            <span className={todo.completed ? 'completed' : ''}>
              {todo.text}
            </span>
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

## ReactDOM API

ReactDOM provides DOM-specific methods for React applications, handling the bridge between React components and the browser DOM.

### ReactDOM.render()

Renders a React element into the DOM at the specified container and returns a reference to the component.

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

// Basic rendering
ReactDOM.render(<App />, document.getElementById('root'));

// With callback
ReactDOM.render(
  <App />,
  document.getElementById('root'),
  () => {
    console.log('App has been rendered');
  }
);

// Conditional rendering based on environment
const rootElement = document.getElementById('root');
if (process.env.NODE_ENV === 'development') {
  ReactDOM.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
    rootElement
  );
} else {
  ReactDOM.render(<App />, rootElement);
}
```

### ReactDOM.createPortal()

Creates a portal to render children into a DOM node outside the parent component's DOM hierarchy.

```javascript
import React, { useState } from 'react';
import ReactDOM from 'react-dom';

function Modal({ isOpen, onClose, children }) {
  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        {children}
      </div>
    </div>,
    document.getElementById('modal-root') // Portal target
  );
}

function App() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="app">
      <h1>Main Application</h1>
      <button onClick={() => setShowModal(true)}>
        Open Modal
      </button>
      
      <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
        <h2>Modal Content</h2>
        <p>This modal is rendered outside the main app tree!</p>
      </Modal>
    </div>
  );
}
```

### ReactDOM.hydrate()

Used for server-side rendering (SSR) to hydrate a container whose HTML was rendered by `ReactDOMServer`.

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

// For client-side hydration of server-rendered content
const rootElement = document.getElementById('root');

if (rootElement.hasChildNodes()) {
  // Hydrate server-rendered content
  ReactDOM.hydrate(<App />, rootElement);
} else {
  // Fallback to client-side rendering
  ReactDOM.render(<App />, rootElement);
}
```

### ReactDOM.unmountComponentAtNode()

Removes a mounted React component from the DOM and cleans up its event handlers and state.

```javascript
import ReactDOM from 'react-dom';

function cleanup() {
  const container = document.getElementById('root');
  const wasUnmounted = ReactDOM.unmountComponentAtNode(container);
  
  if (wasUnmounted) {
    console.log('Component successfully unmounted');
  } else {
    console.log('No component was mounted at this container');
  }
}

// Usage in testing or dynamic component mounting
window.addEventListener('beforeunload', cleanup);
```

### Best Practices and Common Pitfalls

**Performance Considerations:**
- Use `React.memo()` for expensive components that receive the same props frequently
- Implement proper dependency arrays in `useEffect` to avoid infinite loops
- Avoid creating objects/functions in render methods that cause unnecessary re-renders

**State Management:**
- Keep state as close to where it's used as possible
- Use `useReducer` for complex state logic instea