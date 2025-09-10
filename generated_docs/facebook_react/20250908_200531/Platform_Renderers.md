# Platform Renderers

Platform renderers are the core abstraction layer that enables React to target different environments and platforms beyond the traditional web browser. React's architecture separates the reconciliation logic (React Core) from the rendering logic (Platform Renderers), allowing the same component-based programming model to work across web, mobile, desktop, and even custom environments.

This architectural decision makes React a truly universal library, where developers can write components once and render them to multiple platforms using different renderers. Each renderer implements the same interface but provides platform-specific implementations for creating, updating, and managing UI elements.

## React DOM

React DOM is the most widely used platform renderer, responsible for rendering React components to the browser's Document Object Model (DOM). It serves as the bridge between React's virtual representation of the UI and the actual DOM elements that browsers can display.

### Core Architecture

React DOM operates through a sophisticated reconciliation process that efficiently updates the DOM by comparing virtual DOM trees and applying only the necessary changes. This process involves several key phases:

**Render Phase**: During this phase, React DOM builds a new virtual DOM tree representing the desired state of the UI. This phase is pure and can be interrupted, paused, or restarted as needed.

**Commit Phase**: In this synchronous phase, React DOM applies all changes to the actual DOM, ensuring consistency and triggering lifecycle methods and effects.

### Implementation Details

React DOM provides several entry points for different use cases:

```javascript
// Modern concurrent rendering (React 18+)
import { createRoot } from 'react-dom/client';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);

// Legacy rendering (React 17 and below)
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// Server-side rendering
import { renderToString } from 'react-dom/server';
const html = renderToString(<App />);
```

### Advanced Features

**Concurrent Features**: React DOM supports concurrent rendering features that improve user experience by allowing React to interrupt rendering work to handle high-priority updates:

```javascript
import { startTransition } from 'react';

// Mark updates as non-urgent
startTransition(() => {
  setSearchResults(filteredResults);
});
```

**Selective Hydration**: For server-side rendered applications, React DOM can selectively hydrate parts of the page based on user interactions:

```javascript
import { hydrateRoot } from 'react-dom/client';

const container = document.getElementById('root');
hydrateRoot(container, <App />);
```

**Portal Rendering**: React DOM supports rendering components outside their parent hierarchy using portals:

```javascript
import { createPortal } from 'react-dom';

function Modal({ children }) {
  return createPortal(
    children,
    document.getElementById('modal-root')
  );
}
```

### Performance Optimizations

React DOM implements several optimization strategies:

- **Batching**: Multiple state updates are batched together to reduce DOM manipulations
- **Event Delegation**: A single event listener at the document root handles all events
- **Fiber Architecture**: Enables incremental rendering and better scheduling
- **Tree Shaking**: Unused code is eliminated during the build process

### Best Practices

When working with React DOM, consider these best practices:

1. **Use React.StrictMode** in development to catch potential issues:
```javascript
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

2. **Optimize bundle size** by importing only necessary functions:
```javascript
import { createRoot } from 'react-dom/client';
// Instead of: import ReactDOM from 'react-dom';
```

3. **Handle errors gracefully** with error boundaries:
```javascript
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('React DOM Error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}
```

## React Native Integration

React Native represents one of the most successful implementations of React's platform renderer concept, enabling developers to build native mobile applications using React components and JavaScript. Unlike React DOM, which targets web browsers, React Native renders to native platform components on iOS and Android.

### Architecture Overview

React Native's architecture consists of three main layers:

**JavaScript Layer**: Contains React components, business logic, and application state management. This layer runs on a JavaScript engine (Hermes on newer versions, JavaScriptCore on older versions).

**Bridge Layer**: Facilitates communication between JavaScript and native code through asynchronous message passing. This layer serializes data and method calls between the two environments.

**Native Layer**: Contains platform-specific implementations for iOS (Objective-C/Swift) and Android (Java/Kotlin), handling actual UI rendering and system interactions.

### Component Mapping

React Native provides a set of core components that map to native platform equivalents:

```javascript
import React from 'react';
import {
  View,        // Maps to UIView (iOS) / ViewGroup (Android)
  Text,        // Maps to UILabel (iOS) / TextView (Android)
  ScrollView,  // Maps to UIScrollView (iOS) / ScrollView (Android)
  TextInput,   // Maps to UITextField (iOS) / EditText (Android)
  TouchableOpacity,
  FlatList,
  Image
} from 'react-native';

function UserProfile({ user }) {
  return (
    <View style={styles.container}>
      <Image source={{ uri: user.avatar }} style={styles.avatar} />
      <Text style={styles.name}>{user.name}</Text>
      <Text style={styles.email}>{user.email}</Text>
    </View>
  );
}
```

### Styling System

React Native uses a subset of CSS properties implemented through JavaScript objects:

```javascript
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  text: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  }
});
```

### Platform-Specific Code

React Native allows developers to write platform-specific code when needed:

```javascript
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.OS === 'ios' ? 20 : 0,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 4,
      },
      android: {
        elevation: 5,
      },
    }),
  },
});

// Platform-specific file extensions
// Button.ios.js
// Button.android.js
// Button.js (fallback)
```

### Native Module Integration

React Native enables integration with native platform APIs through native modules:

```javascript
// JavaScript side
import { NativeModules } from 'react-native';
const { CustomNativeModule } = NativeModules;

// Usage
CustomNativeModule.performNativeOperation()
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### Performance Considerations

React Native applications require specific performance optimizations:

1. **FlatList for Large Lists**: Use FlatList instead of ScrollView for large datasets:
```javascript
<FlatList
  data={items}
  renderItem={({ item }) => <ItemComponent item={item} />}
  keyExtractor={item => item.id}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>
```

2. **Image Optimization**: Properly handle image loading and caching:
```javascript
<Image
  source={{ uri: imageUrl }}
  style={styles.image}
  resizeMode="cover"
  loadingIndicatorSource={require('./loading.png')}
/>
```

3. **Navigation Optimization**: Use React Navigation with proper screen optimization:
```javascript
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

function AppNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyleInterpolator: CardStyleInterpolators.forHorizontalIOS,
      }}
    >
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
    </Stack.Navigator>
  );
}
```

## Custom Renderer Development

Creating custom renderers allows React to target new platforms and environments beyond web and mobile. This advanced topic involves implementing the React Reconciler interface to define how React components should be rendered in your target environment.

### Reconciler Architecture

The React Reconciler is the core engine that manages component lifecycle, state updates, and tree reconciliation. Custom renderers implement a host configuration that defines platform-specific operations:

```javascript
import Reconciler from 'react-reconciler';

const hostConfig = {
  // Environment
  supportsMutation: true,
  supportsPersistence: false,
  supportsHydration: false,
  
  // Context
  getRootHostContext(rootContainerInstance) {
    return {};
  },
  
  getChildHostContext(parentHostContext, type, rootContainerInstance) {
    return parentHostContext;
  },
  
  // Instance creation
  createInstance(type, props, rootContainerInstance, hostContext, internalInstanceHandle) {
    // Create and return a platform-specific instance
    return new PlatformElement(type, props);
  },
  
  createTextInstance(text, rootContainerInstance, hostContext, internalInstanceHandle) {
    return new PlatformTextElement(text);
  },
  
  // Instance updates
  commitUpdate(instance, updatePayload, type, oldProps, newProps, internalInstanceHandle) {
    instance.update(newProps);
  },
  
  commitTextUpdate(textInstance, oldText, newText) {
    textInstance.setText(newText);
  },
  
  // Tree operations
  appendChild(parentInstance, child) {
    parentInstance.appendChild(child);
  },
  
  removeChild(parentInstance, child) {
    parentInstance.removeChild(child);
  },
  
  insertBefore(parentInstance, child, beforeChild) {
    parentInstance.insertBefore(child, beforeChild);
  },
  
  // Commit hooks
  commitMount(instance, type, newProps, internalInstanceHandle) {
    // Called after instance is attached to tree
  },
  
  finalizeInitialChildren(instance, type, props, rootContainerInstance, hostContext) {
    return false; // Return true if commitMount should be called
  },
  
  // Scheduling
  scheduleTimeout: setTimeout,
  cancelTimeout: clearTimeout,
  noTimeout: -1,
  
  // Misc
  shouldSetTextContent(type, props) {
    return false;
  },
  
  getPublicInstance(instance) {
    return instance;
  },
  
  prepareForCommit(containerInfo) {
    return null;
  },
  
  resetAfterCommit(containerInfo) {
    // Perform any cleanup after commit
  },
};

const CustomRenderer = Reconciler(hostConfig);
```

### Example: Canvas Renderer

Here's a simplified example of a custom renderer that targets HTML5 Canvas:

```javascript
class CanvasElement {
  constructor(type, props) {
    this.type = type;
    this.props = props;
    this.children = [];
    this.parent = null;
  }
  
  appendChild(child) {
    child.parent = this;
    this.children.push(child);
  }
  
  removeChild(child) {
    const index = this.children.indexOf(child);
    if (index !== -1) {
      this.children.splice(index, 1);
      child.parent = null;
    }
  }
  
  render(ctx) {
    // Platform-specific rendering logic
    switch (this.type) {
      case 'rect':
        ctx.fillStyle = this.props.fill || '#000';
        ctx.fillRect(
          this.props.x || 0,
          this.props.y || 0,
          this.props.width || 100,
          this.props.height || 100
        );
        break;
      case 'circle':
        ctx.beginPath();
        ctx.arc(
          this.props.x || 0,
          this.props.y || 0,
          this.props.radius || 50,
          0,
          2 * Math.PI
        );
        ctx.fillStyle = this.props.fill || '#000';
        ctx.fill();
        break;
    }
    
    // Render children
    this.children.forEach(child => child.render(ctx));
  }
}

const canvasHostConfig = {
  supportsMutation: true,
  
  createInstance(type, props) {
    return new CanvasElement(type, props);
  },
  
  createTextInstance(text) {
    return new CanvasElement('text', { content: text });
  },
  
  appendChild(parent, child) {
    parent.appendChild(child);
    // Trigger re-render
    requestAnimationFrame(() => renderCanvas());
  },
  
  commitUpdate(instance, updatePayload, type, oldProps, newProps) {
    instance.props = newProps;
    requestAnimationFrame(() => renderCanvas());
  },
  
  // ... other required methods
};

const CanvasRenderer = Reconciler(canvasHostConfig);

// Usage
function CanvasApp() {
  const [x, setX] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setX(x => (x + 1) % 400);
    }, 16);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <rect x={x} y={100} width={50} height={50} fill="blue">
      <circle x={25} y={25} radius={10} fill="red" />
    </rect>
  );
}

// Render to canvas
const canvas = document.getElementById('canvas');
const container = CanvasRenderer.createContainer(canvas, 0, false, null);
CanvasRenderer.updateContainer(<CanvasApp />, container, null, null);
```

### Testing Custom Renderers

Testing custom renderers requires careful consideration of both React behavior and platform-specific functionality:

```javascript
import { act } from 'react-test-renderer';

describe('Custom Renderer', () => {
  let container;
  
  beforeEach(() => {
    container = CustomRenderer.createContainer(
      new MockPlatformContainer(),
      0,
      false,
      null
    );
  });
  
  test('renders components correctly', () => {
    act(() => {
      CustomRenderer.updateContainer(
        <rect width={100} height={100} />,
        container,
        null,
        null
      );
    });
    
    expect(container.children).toHaveLength(1);
    expect(container.children[0].type).toBe('rect');
  });
  
  test('handles updates properly', () => {
    act(() => {
      CustomRenderer.updateContainer(
        <rect width={100} height={100} />,
        container,
        null,
        null
      );
    });
    
    act(() => {
      CustomRenderer.updateContainer(
        <rect width={200} height={100} />,
        container,
        null,
        null
      );
    });
    
    expect(container.children[0].props.width).toBe(200);
  });
});
```

### Best Practices for Custom Renderers

1.