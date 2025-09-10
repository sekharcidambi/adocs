# Getting Started

Welcome to React, the powerful JavaScript library for building user interfaces. This comprehensive guide will walk you through everything you need to know to start developing with React, from initial setup to creating your first application. Whether you're new to React or transitioning from another framework, this documentation will provide you with the foundation needed to build modern, interactive web applications.

React's component-based architecture allows you to build encapsulated components that manage their own state, then compose them to make complex user interfaces. With its declarative nature, React makes it painless to create interactive UIs by designing simple views for each state in your application.

## Installation and Setup

### Prerequisites

Before installing React, ensure your development environment meets the following requirements:

- **Node.js**: Version 14.0.0 or later (LTS version recommended)
- **npm**: Version 6.14.0 or later (comes with Node.js)
- **Git**: For version control and cloning repositories
- **Code Editor**: VS Code, WebStorm, or your preferred editor with JavaScript/TypeScript support

To verify your Node.js and npm installation:

```bash
node --version
npm --version
```

### Installation Methods

#### Method 1: Create React App (Recommended for Beginners)

Create React App is the officially supported way to create single-page React applications. It offers a modern build setup with no configuration required.

```bash
# Using npx (recommended)
npx create-react-app my-react-app

# Using npm
npm init react-app my-react-app

# Using Yarn
yarn create react-app my-react-app

# For TypeScript support
npx create-react-app my-react-app --template typescript
```

#### Method 2: Manual Installation

For more control over your build configuration:

```bash
# Initialize a new project
mkdir my-react-project
cd my-react-project
npm init -y

# Install React and React DOM
npm install react react-dom

# Install development dependencies
npm install --save-dev @babel/core @babel/preset-env @babel/preset-react
npm install --save-dev webpack webpack-cli webpack-dev-server
npm install --save-dev babel-loader css-loader style-loader html-webpack-plugin
```

#### Method 3: Next.js (For Production Applications)

Next.js provides a complete framework built on top of React with additional features like server-side rendering:

```bash
npx create-next-app@latest my-next-app
cd my-next-app

# With TypeScript
npx create-next-app@latest my-next-app --typescript
```

### Package Manager Considerations

**npm vs Yarn vs pnpm:**

- **npm**: Default package manager, widely supported
- **Yarn**: Faster installation, better dependency resolution
- **pnpm**: Most efficient disk usage, fastest installation

Choose based on your team's preferences and project requirements. All examples in this documentation use npm, but commands are easily translatable.

## Creating Your First React App

### Using Create React App

Let's create a new React application step by step:

```bash
# Create the application
npx create-react-app my-first-react-app
cd my-first-react-app

# Start the development server
npm start
```

This command creates a new directory with the following structure:

```
my-first-react-app/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── App.js
│   ├── App.css
│   ├── App.test.js
│   ├── index.js
│   ├── index.css
│   └── logo.svg
├── package.json
└── README.md
```

### Understanding the Project Structure

**Key Files and Directories:**

- **`public/index.html`**: The HTML template where your React app will be mounted
- **`src/index.js`**: The entry point of your React application
- **`src/App.js`**: The main App component
- **`package.json`**: Project dependencies and scripts
- **`node_modules/`**: Installed dependencies (auto-generated)

### Available Scripts

Create React App provides several built-in scripts:

```bash
# Start development server (http://localhost:3000)
npm start

# Create production build
npm run build

# Run tests
npm test

# Eject from Create React App (irreversible)
npm run eject
```

**Important Note on Ejecting:** The `eject` command is irreversible and gives you full control over the build configuration. Only eject if you need advanced customization that Create React App doesn't support.

### Customizing Your App

#### Adding Dependencies

```bash
# UI Libraries
npm install @mui/material @emotion/react @emotion/styled
npm install react-bootstrap bootstrap

# Routing
npm install react-router-dom

# State Management
npm install redux react-redux @reduxjs/toolkit

# HTTP Client
npm install axios

# Styling
npm install styled-components sass
```

#### Environment Variables

Create a `.env` file in your project root:

```env
REACT_APP_API_URL=https://api.example.com
REACT_APP_VERSION=1.0.0
```

Access in your components:

```javascript
const apiUrl = process.env.REACT_APP_API_URL;
```

## Development Environment Setup

### Code Editor Configuration

#### VS Code Extensions (Recommended)

Install these essential extensions for React development:

- **ES7+ React/Redux/React-Native snippets**: Code snippets
- **Prettier - Code formatter**: Automatic code formatting
- **ESLint**: JavaScript linting
- **Auto Rename Tag**: Automatically rename paired HTML/JSX tags
- **Bracket Pair Colorizer**: Color matching brackets
- **GitLens**: Enhanced Git capabilities

#### VS Code Settings

Create `.vscode/settings.json` in your project:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  },
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

### Linting and Formatting

#### ESLint Configuration

Create `.eslintrc.json`:

```json
{
  "extends": [
    "react-app",
    "react-app/jest"
  ],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "warn",
    "prefer-const": "error"
  }
}
```

#### Prettier Configuration

Create `.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

### Git Configuration

#### .gitignore

Ensure your `.gitignore` includes:

```gitignore
# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/build

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
```

#### Pre-commit Hooks

Install Husky for Git hooks:

```bash
npm install --save-dev husky lint-staged

# Add to package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "src/**/*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

### Browser Developer Tools

#### React Developer Tools

Install the React Developer Tools browser extension:

- **Chrome**: React Developer Tools
- **Firefox**: React Developer Tools

These tools provide:
- Component tree inspection
- Props and state debugging
- Performance profiling
- Hook debugging

#### Debugging Techniques

```javascript
// Console debugging
console.log('Component rendered:', props);

// React DevTools debugging
const MyComponent = (props) => {
  // This will be visible in React DevTools
  React.useDebugValue(props.userId ? 'Logged In' : 'Logged Out');
  
  return <div>{/* component content */}</div>;
};
```

## Hello World Example

### Basic Hello World

Let's create a simple Hello World component to understand React fundamentals:

```javascript
// src/HelloWorld.js
import React from 'react';

function HelloWorld() {
  return (
    <div>
      <h1>Hello, World!</h1>
      <p>Welcome to React development!</p>
    </div>
  );
}

export default HelloWorld;
```

Update `src/App.js`:

```javascript
import React from 'react';
import HelloWorld from './HelloWorld';
import './App.css';

function App() {
  return (
    <div className="App">
      <HelloWorld />
    </div>
  );
}

export default App;
```

### Interactive Hello World with State

Let's enhance our example with state and interactivity:

```javascript
// src/InteractiveHello.js
import React, { useState } from 'react';

function InteractiveHello() {
  const [name, setName] = useState('World');
  const [count, setCount] = useState(0);

  const handleNameChange = (event) => {
    setName(event.target.value);
  };

  const incrementCount = () => {
    setCount(count + 1);
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Hello, {name}!</h1>
      
      <div style={{ margin: '20px 0' }}>
        <label htmlFor="nameInput">Enter your name: </label>
        <input
          id="nameInput"
          type="text"
          value={name}
          onChange={handleNameChange}
          placeholder="Your name here"
        />
      </div>

      <div style={{ margin: '20px 0' }}>
        <p>You've clicked the button {count} times</p>
        <button onClick={incrementCount}>
          Click me!
        </button>
      </div>
    </div>
  );
}

export default InteractiveHello;
```

### Component with Props

Create a reusable greeting component:

```javascript
// src/Greeting.js
import React from 'react';

function Greeting({ name, age, isStudent = false }) {
  return (
    <div className="greeting-card">
      <h2>Hello, {name}!</h2>
      <p>Age: {age}</p>
      {isStudent && <p>👨‍🎓 Student</p>}
    </div>
  );
}

// Usage in App.js
function App() {
  return (
    <div className="App">
      <Greeting name="Alice" age={25} isStudent={true} />
      <Greeting name="Bob" age={30} />
      <Greeting name="Charlie" age={22} isStudent={true} />
    </div>
  );
}
```

### Class Component Example

While functional components are preferred, understanding class components is valuable:

```javascript
// src/ClassHello.js
import React, { Component } from 'react';

class ClassHello extends Component {
  constructor(props) {
    super(props);
    this.state = {
      message: 'Hello from Class Component!',
      timestamp: new Date().toLocaleTimeString()
    };
  }

  componentDidMount() {
    this.timer = setInterval(() => {
      this.setState({
        timestamp: new Date().toLocaleTimeString()
      });
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.timer);
  }

  render() {
    return (
      <div>
        <h2>{this.state.message}</h2>
        <p>Current time: {this.state.timestamp}</p>
      </div>
    );
  }
}

export default ClassHello;
```

### Best Practices Demonstrated

The examples above demonstrate several React best practices:

1. **Functional Components**: Preferred over class components for simplicity
2. **Hooks**: Using `useState` for state management
3. **Props**: Passing data between components
4. **Event Handling**: Proper event handler implementation
5. **Conditional Rendering**: Using logical operators for conditional display
6. **Component Composition**: Building complex UIs from simple components

### Common Pitfalls to Avoid

1. **Direct State Mutation**:
```javascript
// ❌ Wrong
state.items.push(newItem);

// ✅ Correct
setItems([...items, newItem]);
```

2. **Missing Keys in Lists**:
```javascript
// ❌ Wrong
{items.map(item => <div>{item.name}</div>)}

// ✅ Correct
{items.map(item => <div key={item.id}>{item.name}</div>)}
```

3. **Incorrect Event Handler Binding**:
```javascript
// ❌ Wrong (calls immediately)
<button onClick={handleClick()}>Click</button>

// ✅ Correct
<button onClick={handleClick}>Click</button>
```

### Next Steps

After completing this getting started guide, consider exploring:

- **React Router** for navigation
- **State Management** with Context API or Redux
- **Styling Solutions** like CSS Modules or Styled Components
- **Testing** with Jest and React Testing Library
- **Performance Optimization** techniques
- **TypeScript** integration for better development experience

## Additional Resources

- [Official React Documentation](https://reactjs.org/docs)
- [Create React App Documentation](https://create-react-app.dev/)
- [React Developer Tools](https://github.com/facebook/react/tree/main/packages/react-devtools)
- [React Community Resources](https://reactjs.org/community/support.html)

This comprehensive getting started guide provides the foundation you need to begin your React development journey. The examples and configurations shown here represent current best practices and will help you build maintainable, scalable React applications.