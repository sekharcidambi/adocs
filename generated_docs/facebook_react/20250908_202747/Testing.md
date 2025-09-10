# Testing

## Overview

Testing is a critical aspect of React application development that ensures code reliability, maintainability, and user experience quality. This comprehensive guide covers testing strategies, methodologies, and best practices specifically tailored for React applications built with modern JavaScript/TypeScript, component-based architecture, and associated tooling like Webpack and Next.js.

## Testing Philosophy

### Core Principles

React testing philosophy centers around **confidence-driven testing** rather than coverage-driven approaches. The primary goal is to test applications the way users interact with them, focusing on behavior over implementation details.

#### Key Tenets

- **User-Centric Testing**: Write tests that simulate real user interactions
- **Implementation Independence**: Tests should not break when refactoring internal component logic
- **Confidence Over Coverage**: Prioritize tests that provide the highest confidence in application functionality
- **Test Pyramid Balance**: Maintain appropriate ratios of unit, integration, and end-to-end tests

#### Testing Strategy Hierarchy

```
    /\
   /  \    E2E Tests (Few)
  /____\   - Full user workflows
 /      \  - Critical business paths
/________\ Integration Tests (Some)
          - Component interactions
          - API integrations
          - State management flows
          
          Unit Tests (Many)
          - Individual components
          - Utility functions
          - Custom hooks
```

### Testing Tools Ecosystem

**Primary Testing Framework**: Jest
- Built-in test runner, assertion library, and mocking capabilities
- Snapshot testing for component output verification
- Code coverage reporting

**React Testing Utilities**:
- **React Testing Library**: Preferred for component testing with user-focused queries
- **Enzyme** (Legacy): Shallow rendering and implementation testing (being phased out)

**Additional Tools**:
- **@testing-library/jest-dom**: Custom Jest matchers for DOM assertions
- **@testing-library/user-event**: Realistic user interaction simulation
- **MSW (Mock Service Worker)**: API mocking for integration tests

## Unit Testing Components

### Component Testing Fundamentals

Unit testing React components involves testing individual components in isolation, focusing on their rendered output and behavior in response to props and user interactions.

#### Basic Component Test Structure

```javascript
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import '@testing-library/jest-dom';
import Button from '../Button';

describe('Button Component', () => {
  test('renders button with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  test('calls onClick handler when clicked', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await user.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies custom className', () => {
    render(<Button className="custom-btn">Test</Button>);
    expect(screen.getByRole('button')).toHaveClass('custom-btn');
  });
});
```

#### Testing Component Props and State

```javascript
import { render, screen } from '@testing-library/react';
import Counter from '../Counter';

describe('Counter Component', () => {
  test('displays initial count from props', () => {
    render(<Counter initialCount={5} />);
    expect(screen.getByText('Count: 5')).toBeInTheDocument();
  });

  test('increments count when increment button is clicked', async () => {
    const user = userEvent.setup();
    render(<Counter initialCount={0} />);
    
    const incrementButton = screen.getByRole('button', { name: /increment/i });
    await user.click(incrementButton);
    
    expect(screen.getByText('Count: 1')).toBeInTheDocument();
  });

  test('handles disabled state correctly', () => {
    render(<Counter disabled />);
    const incrementButton = screen.getByRole('button', { name: /increment/i });
    expect(incrementButton).toBeDisabled();
  });
});
```

#### Snapshot Testing

```javascript
import { render } from '@testing-library/react';
import ProductCard from '../ProductCard';

describe('ProductCard Snapshots', () => {
  const mockProduct = {
    id: 1,
    name: 'Test Product',
    price: 29.99,
    image: '/test-image.jpg'
  };

  test('renders correctly with product data', () => {
    const { container } = render(<ProductCard product={mockProduct} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  test('renders correctly in loading state', () => {
    const { container } = render(<ProductCard loading />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

### Testing Component Variants

#### Conditional Rendering Tests

```javascript
import { render, screen } from '@testing-library/react';
import UserProfile from '../UserProfile';

describe('UserProfile Conditional Rendering', () => {
  test('shows login prompt when user is not authenticated', () => {
    render(<UserProfile user={null} />);
    expect(screen.getByText(/please log in/i)).toBeInTheDocument();
    expect(screen.queryByText(/welcome/i)).not.toBeInTheDocument();
  });

  test('shows user information when authenticated', () => {
    const user = { name: 'John Doe', email: 'john@example.com' };
    render(<UserProfile user={user} />);
    
    expect(screen.getByText(/welcome, john doe/i)).toBeInTheDocument();
    expect(screen.queryByText(/please log in/i)).not.toBeInTheDocument();
  });
});
```

#### Form Component Testing

```javascript
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import ContactForm from '../ContactForm';

describe('ContactForm', () => {
  test('submits form with correct data', async () => {
    const mockSubmit = jest.fn();
    const user = userEvent.setup();
    
    render(<ContactForm onSubmit={mockSubmit} />);
    
    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.type(screen.getByLabelText(/message/i), 'Test message');
    
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(mockSubmit).toHaveBeenCalledWith({
      name: 'John Doe',
      email: 'john@example.com',
      message: 'Test message'
    });
  });

  test('displays validation errors for invalid input', async () => {
    const user = userEvent.setup();
    render(<ContactForm onSubmit={jest.fn()} />);
    
    await user.click(screen.getByRole('button', { name: /submit/i }));
    
    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  });
});
```

## Testing Hooks

### Custom Hook Testing Strategies

Testing custom hooks requires special consideration since hooks cannot be called outside of React components. The `@testing-library/react-hooks` library (now integrated into React Testing Library) provides utilities for testing hooks in isolation.

#### Basic Hook Testing

```javascript
import { renderHook, act } from '@testing-library/react';
import useCounter from '../useCounter';

describe('useCounter Hook', () => {
  test('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  test('initializes with custom initial value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  test('increments count', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });

  test('decrements count', () => {
    const { result } = renderHook(() => useCounter(5));
    
    act(() => {
      result.current.decrement();
    });
    
    expect(result.current.count).toBe(4);
  });
});
```

#### Testing Hooks with Dependencies

```javascript
import { renderHook, act } from '@testing-library/react';
import useLocalStorage from '../useLocalStorage';

describe('useLocalStorage Hook', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('returns initial value when localStorage is empty', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default'));
    expect(result.current[0]).toBe('default');
  });

  test('returns stored value from localStorage', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));
    const { result } = renderHook(() => useLocalStorage('test-key', 'default'));
    expect(result.current[0]).toBe('stored-value');
  });

  test('updates localStorage when value changes', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));
    
    act(() => {
      result.current[1]('updated-value');
    });
    
    expect(result.current[0]).toBe('updated-value');
    expect(localStorage.getItem('test-key')).toBe('"updated-value"');
  });
});
```

#### Testing Async Hooks

```javascript
import { renderHook, waitFor } from '@testing-library/react';
import useFetch from '../useFetch';

// Mock fetch
global.fetch = jest.fn();

describe('useFetch Hook', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('handles successful API call', async () => {
    const mockData = { id: 1, name: 'Test User' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useFetch('/api/user/1'));

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
  });

  test('handles API error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useFetch('/api/user/1'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toEqual(new Error('Network error'));
  });
});
```

#### Testing Hooks with Context

```javascript
import React from 'react';
import { renderHook } from '@testing-library/react';
import { ThemeProvider } from '../ThemeContext';
import useTheme from '../useTheme';

describe('useTheme Hook', () => {
  const wrapper = ({ children }) => (
    <ThemeProvider value={{ theme: 'dark', toggleTheme: jest.fn() }}>
      {children}
    </ThemeProvider>
  );

  test('returns theme context value', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });
    
    expect(result.current.theme).toBe('dark');
    expect(typeof result.current.toggleTheme).toBe('function');
  });

  test('throws error when used outside provider', () => {
    const { result } = renderHook(() => useTheme());
    
    expect(result.error).toEqual(
      Error('useTheme must be used within a ThemeProvider')
    );
  });
});
```

## Integration Testing

### Component Integration Testing

Integration tests verify that multiple components work together correctly, including their interactions with external dependencies like APIs, routing, and state management.

#### Testing Component Interactions

```javascript
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import ProductList from '../ProductList';
import { CartProvider } from '../CartContext';

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <CartProvider>
        {component}
      </CartProvider>
    </BrowserRouter>
  );
};

describe('ProductList Integration', () => {
  test('adds product to cart and updates cart count', async () => {
    const user = userEvent.setup();
    const mockProducts = [
      { id: 1, name: 'Product 1', price: 10.99 },
      { id: 2, name: 'Product 2', price: 15.99 }
    ];

    renderWithProviders(<ProductList products={mockProducts} />);

    const addToCartButtons = screen.getAllByText(/add to cart/i);
    await user.click(addToCartButtons[0]);

    expect(screen.getByText(/cart \(1\)/i)).toBeInTheDocument();
  });
});
```

#### API Integration Testing with MSW

```javascript
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen, waitFor } from '@testing-library/react';
import UserDashboard from '../UserDashboard';

const server = setupServer(
  rest.get('/api/user/profile', (req, res, ctx) => {
    return res(ctx.json({
      id: 1,
      name: 'John Doe',
      email: 'john@example.com'
    }));
  }),
  
  rest.get('/api/user/orders', (req, res, ctx) => {
    return res(ctx.json([
      { id: 1, total: 29.99, status: 'completed' },
      { id: 2, total: 45.50, status: 'pending' }
    ]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserDashboard Integration', () => {
  test('loads and displays user data', async () => {
    render(<UserDashboard />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText(/2 orders/i)).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    server.use(
      rest.get('/api/user/profile', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<UserDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/error loading profile/i)).toBeInTheDocument();
    });
  });
});
```

### Next.js Integration Testing

```javascript
import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/router';
import ProductPage from '../pages/product/[id]