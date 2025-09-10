# Core Concepts

React is built on several fundamental concepts that form the foundation of modern component-based web development. Understanding these core concepts is essential for building scalable, maintainable, and performant React applications. This section provides comprehensive coverage of the key concepts that every React developer must master.

## Components

Components are the building blocks of React applications. They encapsulate UI logic, state, and presentation into reusable, composable units that promote code reusability and maintainability.

### Component Types

React supports two primary types of components, each with distinct characteristics and use cases:

#### Functional Components

Functional components are JavaScript functions that return JSX. They are the modern standard for React development and support all React features through hooks.

```javascript
// Basic functional component
function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}

// Arrow function syntax
const Welcome = (props) => {
  return <h1>Hello, {props.name}!</h1>;
};

// With hooks for state and lifecycle
import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId)
      .then(userData => {
        setUser(userData);
        setLoading(false);
      })
      .catch(error => {
        console.error('Failed to fetch user:', error);
        setLoading(false);
      });
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
};
```

#### Class Components

Class components extend `React.Component` and use class methods for lifecycle management. While less common in modern React development, they're still important for understanding legacy codebases.

```javascript
import React, { Component } from 'react';

class UserProfile extends Component {
  constructor(props) {
    super(props);
    this.state = {
      user: null,
      loading: true
    };
  }

  async componentDidMount() {
    try {
      const user = await fetchUser(this.props.userId);
      this.setState({ user, loading: false });
    } catch (error) {
      console.error('Failed to fetch user:', error);
      this.setState({ loading: false });
    }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUserData();
    }
  }

  render() {
    const { user, loading } = this.state;
    
    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;

    return (
      <div className="user-profile">
        <h2>{user.name}</h2>
        <p>{user.email}</p>
      </div>
    );
  }
}
```

### Component Best Practices

- **Single Responsibility**: Each component should have one clear purpose
- **Composition over Inheritance**: Favor component composition over class inheritance
- **Pure Components**: Strive for components that produce the same output given the same props
- **Proper Naming**: Use PascalCase for component names and descriptive, meaningful names
- **File Organization**: Keep related components, styles, and tests in the same directory

## JSX

JSX (JavaScript XML) is a syntax extension for JavaScript that allows you to write HTML-like code within JavaScript. It provides a declarative way to describe the UI structure and is transpiled to regular JavaScript function calls.

### JSX Fundamentals

JSX combines the power of JavaScript with the familiarity of HTML syntax:

```javascript
// JSX syntax
const element = <h1>Hello, World!</h1>;

// Transpiled JavaScript (what React actually executes)
const element = React.createElement('h1', null, 'Hello, World!');
```

### JSX Rules and Syntax

#### 1. Single Root Element
JSX expressions must have exactly one parent element:

```javascript
// ❌ Invalid - multiple root elements
return (
  <h1>Title</h1>
  <p>Content</p>
);

// ✅ Valid - single root element
return (
  <div>
    <h1>Title</h1>
    <p>Content</p>
  </div>
);

// ✅ Valid - React Fragment
return (
  <>
    <h1>Title</h1>
    <p>Content</p>
  </>
);
```

#### 2. JavaScript Expressions
Use curly braces to embed JavaScript expressions:

```javascript
const UserGreeting = ({ user, isLoggedIn }) => {
  const currentTime = new Date().toLocaleTimeString();
  
  return (
    <div>
      <h1>{isLoggedIn ? `Welcome back, ${user.name}!` : 'Please log in'}</h1>
      <p>Current time: {currentTime}</p>
      <p>You have {user.notifications.length} notifications</p>
      {user.notifications.length > 0 && (
        <button onClick={() => markAllAsRead()}>
          Mark all as read
        </button>
      )}
    </div>
  );
};
```

#### 3. Attributes and Props
JSX attributes use camelCase naming and can accept strings or JavaScript expressions:

```javascript
const Button = ({ onClick, disabled, children }) => {
  return (
    <button
      className="btn btn-primary"
      onClick={onClick}
      disabled={disabled}
      aria-label="Submit form"
      data-testid="submit-button"
    >
      {children}
    </button>
  );
};
```

#### 4. Conditional Rendering
JSX supports various patterns for conditional rendering:

```javascript
const Dashboard = ({ user, isLoading, error }) => {
  // Early return pattern
  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <div className="dashboard">
      {/* Logical AND operator */}
      {user.isAdmin && <AdminPanel />}
      
      {/* Ternary operator */}
      {user.notifications.length > 0 ? (
        <NotificationList notifications={user.notifications} />
      ) : (
        <p>No new notifications</p>
      )}
      
      {/* Immediately Invoked Function Expression (IIFE) */}
      {(() => {
        switch (user.role) {
          case 'admin':
            return <AdminDashboard />;
          case 'moderator':
            return <ModeratorDashboard />;
          default:
            return <UserDashboard />;
        }
      })()}
    </div>
  );
};
```

### JSX Best Practices

- **Readable Formatting**: Use proper indentation and line breaks for complex JSX
- **Fragment Usage**: Use React Fragments to avoid unnecessary wrapper elements
- **Key Props**: Always provide unique keys when rendering lists
- **Event Handling**: Use arrow functions or bind methods properly to maintain context
- **Accessibility**: Include proper ARIA attributes and semantic HTML elements

## Props

Props (properties) are the mechanism for passing data from parent components to child components. They enable component reusability and establish a unidirectional data flow that makes applications predictable and easier to debug.

### Props Fundamentals

Props are read-only and should never be modified by the receiving component:

```javascript
// Parent component
const App = () => {
  const user = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    avatar: '/images/john-avatar.jpg'
  };

  return (
    <div>
      <UserCard 
        user={user}
        showEmail={true}
        onEdit={(userId) => handleUserEdit(userId)}
        className="featured-user"
      />
    </div>
  );
};

// Child component
const UserCard = ({ user, showEmail, onEdit, className }) => {
  return (
    <div className={`user-card ${className}`}>
      <img src={user.avatar} alt={`${user.name}'s avatar`} />
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
      <button onClick={() => onEdit(user.id)}>
        Edit Profile
      </button>
    </div>
  );
};
```

### Props Patterns and Techniques

#### 1. Destructuring Props
Destructuring makes component signatures clearer and code more readable:

```javascript
// ✅ Destructured props (recommended)
const ProductCard = ({ product, onAddToCart, isInCart, discount = 0 }) => {
  const finalPrice = product.price * (1 - discount);
  
  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p className="price">
        {discount > 0 && (
          <span className="original-price">${product.price}</span>
        )}
        <span className="final-price">${finalPrice.toFixed(2)}</span>
      </p>
      <button 
        onClick={() => onAddToCart(product.id)}
        disabled={isInCart}
      >
        {isInCart ? 'In Cart' : 'Add to Cart'}
      </button>
    </div>
  );
};

// ❌ Non-destructured props (less readable)
const ProductCard = (props) => {
  return (
    <div className="product-card">
      <h3>{props.product.name}</h3>
      <p>${props.product.price}</p>
      <button onClick={() => props.onAddToCart(props.product.id)}>
        Add to Cart
      </button>
    </div>
  );
};
```

#### 2. Default Props
Provide fallback values for optional props:

```javascript
// Using default parameters (modern approach)
const Avatar = ({ 
  src, 
  alt, 
  size = 'medium', 
  shape = 'circle',
  fallbackIcon = 'user' 
}) => {
  const sizeClasses = {
    small: 'w-8 h-8',
    medium: 'w-12 h-12',
    large: 'w-16 h-16'
  };

  return (
    <div className={`avatar ${shape} ${sizeClasses[size]}`}>
      {src ? (
        <img src={src} alt={alt} />
      ) : (
        <Icon name={fallbackIcon} />
      )}
    </div>
  );
};

// Using defaultProps (legacy approach)
Avatar.defaultProps = {
  size: 'medium',
  shape: 'circle',
  fallbackIcon: 'user'
};
```

#### 3. Props Validation with TypeScript
TypeScript provides excellent props validation and developer experience:

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'user' | 'moderator';
}

interface UserCardProps {
  user: User;
  showEmail?: boolean;
  onEdit: (userId: number) => void;
  className?: string;
}

const UserCard: React.FC<UserCardProps> = ({ 
  user, 
  showEmail = false, 
  onEdit, 
  className = '' 
}) => {
  return (
    <div className={`user-card ${className}`}>
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
      <span className={`role-badge role-${user.role}`}>
        {user.role}
      </span>
      <button onClick={() => onEdit(user.id)}>
        Edit
      </button>
    </div>
  );
};
```

#### 4. Render Props Pattern
Pass functions as props to share code between components:

```javascript
const DataFetcher = ({ url, children }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(response => response.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, [url]);

  return children({ data, loading, error });
};

// Usage
const UserList = () => {
  return (
    <DataFetcher url="/api/users">
      {({ data, loading, error }) => {
        if (loading) return <LoadingSpinner />;
        if (error) return <ErrorMessage error={error} />;
        
        return (
          <ul>
            {data.map(user => (
              <li key={user.id}>{user.name}</li>
            ))}
          </ul>
        );
      }}
    </DataFetcher>
  );
};
```

## State Management

State management is crucial for building interactive React applications. React provides built-in state management capabilities through hooks, and the ecosystem offers various solutions for complex state management needs.

### Local State with useState

The `useState` hook is the primary way to manage local component state:

```javascript
import React, { useState } from 'react';

const ContactForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
      setFormData({ name: '', email: '', message: '' });
    } catch (error) {
      setErrors({ submit: 'Failed to send message. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="contact-form">
      <div className="form-group">
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={handleInputChange('name')}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && <span className="error-message">{errors.name}</span>}
      </div>
      
      <div className="