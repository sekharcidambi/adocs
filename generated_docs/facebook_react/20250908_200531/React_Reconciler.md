# React Reconciler

The React Reconciler is the core engine that powers React's ability to efficiently update the user interface. It serves as the heart of React's rendering system, responsible for determining what changes need to be made to the DOM and executing those changes in the most optimal way possible. Understanding the reconciler is crucial for React developers who want to build performant applications and debug complex rendering issues.

The reconciler operates on the principle of comparing (or "reconciling") the current state of the component tree with the desired new state, then applying only the necessary changes to bring the actual DOM in sync with the virtual representation. This process involves sophisticated algorithms and data structures that have evolved significantly since React's inception.

## Fiber Architecture

### Overview of Fiber

Fiber represents a complete rewrite of React's reconciliation algorithm, introduced in React 16. It replaced the previous stack-based reconciler with a more flexible, interruptible architecture that enables advanced features like time-slicing, suspense, and concurrent rendering.

The Fiber architecture treats each component as a "fiber" - a JavaScript object that represents a unit of work. These fibers form a linked list structure that can be traversed, paused, and resumed, giving React unprecedented control over the rendering process.

### Fiber Node Structure

Each fiber node contains essential information about a component and its relationship to other components:

```javascript
// Simplified Fiber node structure
const fiberNode = {
  // Component information
  type: 'div', // Component type (string for DOM elements, function for components)
  key: 'unique-key',
  props: { className: 'container', children: [...] },
  
  // Tree structure
  child: null,      // First child fiber
  sibling: null,    // Next sibling fiber
  parent: null,     // Parent fiber (also called 'return')
  
  // State and effects
  memoizedState: null,    // Current state
  pendingProps: null,     // New props
  memoizedProps: null,    // Previous props
  updateQueue: null,      // Queue of state updates
  
  // Work tracking
  effectTag: 'NoEffect',  // What type of work needs to be done
  nextEffect: null,       // Linked list of effects
  
  // Scheduling
  expirationTime: 0,      // When this work should be completed
  childExpirationTime: 0, // Earliest expiration time of children
  
  // Alternate fiber for double buffering
  alternate: null
};
```

### Double Buffering with Alternate Trees

Fiber implements a double buffering technique using two fiber trees:

- **Current Tree**: Represents the current state of the UI
- **Work-in-Progress Tree**: Represents the future state being constructed

```javascript
// Example of how alternate fibers work
function createWorkInProgress(current, pendingProps) {
  let workInProgress = current.alternate;
  
  if (workInProgress === null) {
    // Create new fiber if alternate doesn't exist
    workInProgress = createFiber(current.tag, pendingProps, current.key);
    workInProgress.type = current.type;
    workInProgress.stateNode = current.stateNode;
    
    // Link the alternates
    workInProgress.alternate = current;
    current.alternate = workInProgress;
  } else {
    // Reuse existing alternate
    workInProgress.pendingProps = pendingProps;
    workInProgress.effectTag = NoEffect;
    workInProgress.nextEffect = null;
    workInProgress.firstEffect = null;
    workInProgress.lastEffect = null;
  }
  
  return workInProgress;
}
```

### Work Loop and Scheduling

The Fiber architecture enables interruptible rendering through its work loop mechanism:

```javascript
// Simplified work loop implementation
function workLoop(isYieldy) {
  if (!isYieldy) {
    // Synchronous rendering - don't yield
    while (nextUnitOfWork !== null) {
      nextUnitOfWork = performUnitOfWork(nextUnitOfWork);
    }
  } else {
    // Concurrent rendering - yield when time slice expires
    while (nextUnitOfWork !== null && !shouldYield()) {
      nextUnitOfWork = performUnitOfWork(nextUnitOfWork);
    }
  }
}

function performUnitOfWork(workInProgress) {
  // Process current fiber
  const next = beginWork(workInProgress);
  
  if (next === null) {
    // No child work, complete this unit
    completeUnitOfWork(workInProgress);
  }
  
  return next;
}
```

### Priority Levels and Expiration Times

Fiber introduces a sophisticated priority system to ensure important updates are processed first:

```javascript
// Priority levels in React Fiber
const ImmediatePriority = 1;      // 250ms - user interactions
const UserBlockingPriority = 2;   // 5s - user input, hover
const NormalPriority = 3;         // 5s - network responses
const LowPriority = 4;            // 10s - analytics
const IdlePriority = 5;           // Never expires - offscreen content

// Example of priority-based scheduling
function scheduleWork(fiber, expirationTime) {
  const root = scheduleWorkToRoot(fiber, expirationTime);
  
  if (expirationTime === Sync) {
    // Synchronous work - render immediately
    performSyncWork();
  } else {
    // Asynchronous work - schedule based on priority
    scheduleCallbackWithExpirationTime(root, expirationTime);
  }
}
```

## Virtual DOM and Diffing

### Virtual DOM Concepts

The Virtual DOM is React's in-memory representation of the real DOM. It's a programming concept where a "virtual" representation of the UI is kept in memory and synced with the "real" DOM through a process called reconciliation.

```javascript
// Virtual DOM representation
const virtualElement = {
  type: 'div',
  props: {
    className: 'container',
    children: [
      {
        type: 'h1',
        props: {
          children: 'Hello World'
        }
      },
      {
        type: 'p',
        props: {
          children: 'This is a paragraph'
        }
      }
    ]
  }
};

// JSX creates virtual DOM elements
const element = (
  <div className="container">
    <h1>Hello World</h1>
    <p>This is a paragraph</p>
  </div>
);
```

### Diffing Algorithm

React's diffing algorithm compares the new virtual DOM tree with the previous one to determine the minimal set of changes needed. The algorithm makes three key assumptions to achieve O(n) complexity:

1. **Different element types produce different trees**
2. **Elements with stable keys maintain identity across renders**
3. **Subtrees can be compared level by level**

```javascript
// Simplified diffing logic
function reconcileChildren(current, workInProgress, nextChildren) {
  if (current === null) {
    // Mount new children
    workInProgress.child = mountChildFibers(
      workInProgress,
      null,
      nextChildren
    );
  } else {
    // Reconcile existing children
    workInProgress.child = reconcileChildFibers(
      workInProgress,
      current.child,
      nextChildren
    );
  }
}

function reconcileChildFibers(returnFiber, currentFirstChild, newChild) {
  // Handle different types of children
  if (typeof newChild === 'object' && newChild !== null) {
    switch (newChild.$$typeof) {
      case REACT_ELEMENT_TYPE:
        return placeSingleChild(
          reconcileSingleElement(returnFiber, currentFirstChild, newChild)
        );
      case REACT_FRAGMENT_TYPE:
        return reconcileChildrenArray(returnFiber, currentFirstChild, newChild.props.children);
    }
    
    if (isArray(newChild)) {
      return reconcileChildrenArray(returnFiber, currentFirstChild, newChild);
    }
  }
  
  // Delete remaining children
  return deleteRemainingChildren(returnFiber, currentFirstChild);
}
```

### Key-based Reconciliation

Keys help React identify which items have changed, been added, or removed:

```javascript
// Without keys - inefficient reconciliation
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li>{todo.text}</li> // React can't track identity
      ))}
    </ul>
  );
}

// With keys - efficient reconciliation
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>{todo.text}</li> // React can track identity
      ))}
    </ul>
  );
}

// Key-based reconciliation algorithm
function reconcileChildrenArray(returnFiber, currentFirstChild, newChildren) {
  let resultingFirstChild = null;
  let previousNewFiber = null;
  let oldFiber = currentFirstChild;
  let newIdx = 0;
  
  // First pass: handle updates with same keys
  for (; oldFiber !== null && newIdx < newChildren.length; newIdx++) {
    if (oldFiber.key === newChildren[newIdx].key) {
      // Keys match - update existing fiber
      const newFiber = updateElement(returnFiber, oldFiber, newChildren[newIdx]);
      // Link fibers...
    } else {
      break; // Keys don't match - handle in second pass
    }
  }
  
  // Second pass: handle insertions and deletions
  // ... complex logic for handling remaining children
}
```

### Effect Processing

The reconciler tracks side effects that need to be applied to the DOM:

```javascript
// Effect tags indicate what work needs to be done
const NoEffect = 0b000000000000;
const PerformedWork = 0b000000000001;
const Placement = 0b000000000010;      // Insert
const Update = 0b000000000100;         // Update props
const PlacementAndUpdate = 0b000000000110;
const Deletion = 0b000000001000;       // Remove
const ContentReset = 0b000000010000;   // Reset text content
const Callback = 0b000000100000;       // componentDidUpdate, etc.
const Ref = 0b000010000000;            // Ref updates

// Effect list processing
function commitRoot(root) {
  const finishedWork = root.finishedWork;
  
  // Process effects in three phases
  commitBeforeMutationEffects(finishedWork);
  commitMutationEffects(finishedWork);
  commitLayoutEffects(finishedWork);
}

function commitMutationEffects(firstChild) {
  let fiber = firstChild;
  while (fiber !== null) {
    const effectTag = fiber.effectTag;
    
    if (effectTag & Placement) {
      commitPlacement(fiber);
    }
    
    if (effectTag & Update) {
      commitWork(fiber);
    }
    
    if (effectTag & Deletion) {
      commitDeletion(fiber);
    }
    
    fiber = fiber.nextEffect;
  }
}
```

## Concurrent Features

### Time Slicing

Time slicing allows React to break rendering work into chunks and spread it across multiple frames, preventing the main thread from being blocked:

```javascript
// Time slicing implementation
const FRAME_DEADLINE = 5; // 5ms per frame

function shouldYield() {
  return getCurrentTime() >= deadline;
}

function scheduleCallback(callback, options) {
  const currentTime = getCurrentTime();
  const timeout = options?.timeout ?? 5000;
  const expirationTime = currentTime + timeout;
  
  const newTask = {
    callback,
    expirationTime,
    startTime: currentTime
  };
  
  if (currentTime >= expirationTime) {
    // Immediate priority
    flushWork(newTask);
  } else {
    // Schedule for later
    push(taskQueue, newTask);
    requestHostCallback(flushWork);
  }
}

// Example component that benefits from time slicing
function ExpensiveList({ items }) {
  return (
    <div>
      {items.map(item => (
        <ExpensiveItem key={item.id} data={item} />
      ))}
    </div>
  );
}

// React can interrupt rendering of this list to handle user interactions
```

### Suspense and Error Boundaries

Suspense enables components to "wait" for something before rendering:

```javascript
// Suspense implementation concepts
function throwException(root, returnFiber, sourceFiber, value) {
  sourceFiber.effectTag |= Incomplete;
  sourceFiber.firstEffect = sourceFiber.lastEffect = null;
  
  if (value !== null && typeof value === 'object' && typeof value.then === 'function') {
    // This is a promise - handle suspense
    const thenable = value;
    
    // Find the nearest Suspense boundary
    let workInProgress = returnFiber;
    do {
      if (workInProgress.tag === SuspenseComponent) {
        // Found Suspense boundary
        const suspenseState = workInProgress.memoizedState;
        if (suspenseState === null) {
          // First time suspending
          const primaryChildren = workInProgress.child;
          const fallbackChildren = workInProgress.child.sibling;
          
          // Switch to fallback
          workInProgress.memoizedState = { dehydrated: null };
          workInProgress.child = fallbackChildren;
        }
        
        // Attach retry listener
        thenable.then(
          () => scheduleWork(workInProgress, Sync),
          () => scheduleWork(workInProgress, Sync)
        );
        
        return;
      }
      workInProgress = workInProgress.return;
    } while (workInProgress !== null);
  }
}

// Usage example
function AsyncComponent() {
  const data = useSuspenseData(); // This might throw a promise
  return <div>{data.content}</div>;
}

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <AsyncComponent />
    </Suspense>
  );
}
```

### Concurrent Mode and useTransition

Concurrent Mode enables React to prepare multiple versions of the UI at the same time:

```javascript
// useTransition hook implementation concepts
function useTransition() {
  const [isPending, setIsPending] = useState(false);
  
  const startTransition = useCallback((callback) => {
    setIsPending(true);
    
    // Schedule update with lower priority
    unstable_scheduleCallback(unstable_NormalPriority, () => {
      callback();
      setIsPending(false);
    });
  }, []);
  
  return [isPending, startTransition];
}

// Usage example
function SearchResults() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();
  
  const handleSearch = (newQuery) => {
    setQuery(newQuery); // Urgent update
    
    startTransition(() => {
      // Non-urgent update - can be interrupted
      setResults(searchData(newQuery));
    });
  };
  
  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => handleSearch(e.target.value)} 
      />
      <div style={{ opacity: isPending ? 0.7 : 1 }}>
        {results.map(result => (
          <SearchResult key={result.id} data={result} />
        ))}
      </div>
    </div>
  );
}
```

### Best Practices and Performance Considerations

1. **Optimize Component Updates**:
   ```javascript
   // Use React.memo for expensive components
   const ExpensiveComponent = React.memo(({ data }) => {
     return <ComplexVisualization data={data