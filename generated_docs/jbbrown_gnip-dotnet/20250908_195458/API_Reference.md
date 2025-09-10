# API Reference

This API reference provides comprehensive documentation for the Gnip .NET API Client, a robust library designed to interact with Gnip's real-time data streaming services. The client follows an event-driven architecture pattern and provides a clean, intuitive interface for consuming social media data streams.

## Client Classes

### GnipClient

The `GnipClient` class serves as the primary entry point for all Gnip API interactions. It manages authentication, connection lifecycle, and provides methods for subscribing to data streams.

#### Constructor

```csharp
public GnipClient(string username, string password, string baseUrl = "https://api.gnip.com")
```

**Parameters:**
- `username` (string): Your Gnip account username
- `password` (string): Your Gnip account password  
- `baseUrl` (string, optional): The base URL for Gnip API endpoints

**Example:**
```csharp
var client = new GnipClient("your-username", "your-password");
```

#### Methods

##### ConnectAsync()
Establishes an asynchronous connection to the Gnip streaming API.

```csharp
public async Task<bool> ConnectAsync(CancellationToken cancellationToken = default)
```

**Returns:** `Task<bool>` - True if connection is successful, false otherwise

**Example:**
```csharp
var isConnected = await client.ConnectAsync();
if (isConnected)
{
    Console.WriteLine("Successfully connected to Gnip API");
}
```

##### SubscribeToStream()
Subscribes to a specific data stream with configurable filtering options.

```csharp
public void SubscribeToStream(string streamName, StreamConfiguration config, 
    Action<StreamData> onDataReceived, Action<Exception> onError = null)
```

**Parameters:**
- `streamName` (string): The name of the stream to subscribe to
- `config` (StreamConfiguration): Configuration object for stream parameters
- `onDataReceived` (Action<StreamData>): Callback function for processing received data
- `onError` (Action<Exception>, optional): Error handling callback

**Example:**
```csharp
var config = new StreamConfiguration
{
    MaxBackfillMinutes = 5,
    BufferSize = 1000,
    FilterRules = new[] { "keyword:technology", "lang:en" }
};

client.SubscribeToStream("powertrack", config, 
    data => ProcessStreamData(data),
    error => LogError(error));
```

##### DisconnectAsync()
Gracefully disconnects from all active streams and closes the connection.

```csharp
public async Task DisconnectAsync()
```

### StreamConfiguration

Configuration class for customizing stream behavior and filtering options.

#### Properties

```csharp
public class StreamConfiguration
{
    public int MaxBackfillMinutes { get; set; } = 0;
    public int BufferSize { get; set; } = 500;
    public string[] FilterRules { get; set; }
    public bool EnableHeartbeat { get; set; } = true;
    public TimeSpan ReconnectInterval { get; set; } = TimeSpan.FromSeconds(30);
    public int MaxRetryAttempts { get; set; } = 3;
}
```

**Property Descriptions:**
- `MaxBackfillMinutes`: Number of minutes of historical data to retrieve upon connection
- `BufferSize`: Internal buffer size for managing incoming data
- `FilterRules`: Array of filtering rules to apply to the stream
- `EnableHeartbeat`: Whether to enable heartbeat messages for connection monitoring
- `ReconnectInterval`: Time interval between reconnection attempts
- `MaxRetryAttempts`: Maximum number of retry attempts for failed connections

## Data Models

### StreamData

The primary data model representing a single item from a Gnip data stream.

```csharp
public class StreamData
{
    public string Id { get; set; }
    public DateTime CreatedAt { get; set; }
    public string Body { get; set; }
    public Actor Actor { get; set; }
    public string Verb { get; set; }
    public ActivityObject Object { get; set; }
    public Provider Provider { get; set; }
    public Matching[] MatchingRules { get; set; }
    public Dictionary<string, object> Extensions { get; set; }
}
```

**Usage Example:**
```csharp
client.SubscribeToStream("powertrack", config, data =>
{
    Console.WriteLine($"Received post: {data.Body}");
    Console.WriteLine($"Author: {data.Actor.DisplayName}");
    Console.WriteLine($"Created: {data.CreatedAt}");
    
    foreach (var rule in data.MatchingRules)
    {
        Console.WriteLine($"Matched rule: {rule.Tag}");
    }
});
```

### Actor

Represents the entity that performed the activity (e.g., the user who posted a tweet).

```csharp
public class Actor
{
    public string Id { get; set; }
    public string DisplayName { get; set; }
    public string PreferredUsername { get; set; }
    public string Summary { get; set; }
    public int FollowersCount { get; set; }
    public int FriendsCount { get; set; }
    public int StatusesCount { get; set; }
    public DateTime CreatedAt { get; set; }
    public string ProfileImageUrl { get; set; }
    public bool Verified { get; set; }
}
```

### ActivityObject

Represents the object of the activity (e.g., the content of a social media post).

```csharp
public class ActivityObject
{
    public string Id { get; set; }
    public string Summary { get; set; }
    public string ObjectType { get; set; }
    public string[] Tags { get; set; }
    public Geo Location { get; set; }
}
```

### Provider

Contains information about the data source provider.

```csharp
public class Provider
{
    public string ObjectType { get; set; }
    public string Id { get; set; }
    public string DisplayName { get; set; }
}
```

### Matching

Represents a rule that matched the current data item.

```csharp
public class Matching
{
    public string Tag { get; set; }
    public string Id { get; set; }
}
```

## Event Interfaces

### IStreamEventHandler

Interface for implementing custom stream event handlers with full lifecycle management.

```csharp
public interface IStreamEventHandler
{
    Task OnConnectedAsync(StreamConnectionEventArgs args);
    Task OnDataReceivedAsync(StreamDataEventArgs args);
    Task OnDisconnectedAsync(StreamDisconnectionEventArgs args);
    Task OnErrorAsync(StreamErrorEventArgs args);
    Task OnHeartbeatAsync(StreamHeartbeatEventArgs args);
}
```

**Implementation Example:**
```csharp
public class CustomStreamHandler : IStreamEventHandler
{
    public async Task OnConnectedAsync(StreamConnectionEventArgs args)
    {
        Console.WriteLine($"Connected to stream: {args.StreamName}");
        await LogConnectionAsync(args.StreamName, args.Timestamp);
    }

    public async Task OnDataReceivedAsync(StreamDataEventArgs args)
    {
        await ProcessDataAsync(args.Data);
        await UpdateMetricsAsync(args.StreamName, args.Data);
    }

    public async Task OnDisconnectedAsync(StreamDisconnectionEventArgs args)
    {
        Console.WriteLine($"Disconnected from stream: {args.StreamName}");
        if (args.Reason == DisconnectionReason.Error)
        {
            await HandleDisconnectionErrorAsync(args);
        }
    }

    public async Task OnErrorAsync(StreamErrorEventArgs args)
    {
        await LogErrorAsync(args.Exception, args.StreamName);
        
        if (args.Exception is RateLimitException)
        {
            await HandleRateLimitAsync(args);
        }
    }

    public async Task OnHeartbeatAsync(StreamHeartbeatEventArgs args)
    {
        await UpdateConnectionHealthAsync(args.StreamName, args.Timestamp);
    }
}
```

### IDataProcessor

Interface for implementing custom data processing logic with support for batch operations.

```csharp
public interface IDataProcessor
{
    Task<ProcessingResult> ProcessAsync(StreamData data);
    Task<BatchProcessingResult> ProcessBatchAsync(IEnumerable<StreamData> batch);
    bool CanProcess(StreamData data);
}
```

### Event Argument Classes

#### StreamDataEventArgs
```csharp
public class StreamDataEventArgs : EventArgs
{
    public string StreamName { get; set; }
    public StreamData Data { get; set; }
    public DateTime Timestamp { get; set; }
    public long SequenceNumber { get; set; }
}
```

#### StreamErrorEventArgs
```csharp
public class StreamErrorEventArgs : EventArgs
{
    public string StreamName { get; set; }
    public Exception Exception { get; set; }
    public DateTime Timestamp { get; set; }
    public bool CanRetry { get; set; }
    public int RetryAttempt { get; set; }
}
```

## Exception Types

### GnipException

Base exception class for all Gnip-related errors.

```csharp
public class GnipException : Exception
{
    public string ErrorCode { get; }
    public DateTime Timestamp { get; }
    
    public GnipException(string message, string errorCode = null) : base(message)
    {
        ErrorCode = errorCode;
        Timestamp = DateTime.UtcNow;
    }
}
```

### AuthenticationException

Thrown when authentication credentials are invalid or expired.

```csharp
public class AuthenticationException : GnipException
{
    public AuthenticationException(string message) : base(message, "AUTH_FAILED") { }
}
```

**Common Scenarios:**
- Invalid username/password combination
- Expired authentication tokens
- Insufficient permissions for requested stream

**Handling Example:**
```csharp
try
{
    await client.ConnectAsync();
}
catch (AuthenticationException ex)
{
    Console.WriteLine($"Authentication failed: {ex.Message}");
    // Prompt for new credentials or refresh tokens
}
```

### RateLimitException

Thrown when API rate limits are exceeded.

```csharp
public class RateLimitException : GnipException
{
    public TimeSpan RetryAfter { get; }
    public int RemainingRequests { get; }
    
    public RateLimitException(string message, TimeSpan retryAfter, int remaining) 
        : base(message, "RATE_LIMIT_EXCEEDED")
    {
        RetryAfter = retryAfter;
        RemainingRequests = remaining;
    }
}
```

### ConnectionException

Thrown when network connectivity issues occur.

```csharp
public class ConnectionException : GnipException
{
    public bool IsRetryable { get; }
    
    public ConnectionException(string message, bool isRetryable = true) 
        : base(message, "CONNECTION_ERROR")
    {
        IsRetryable = isRetryable;
    }
}
```

### StreamException

Thrown for stream-specific errors such as invalid configurations or stream unavailability.

```csharp
public class StreamException : GnipException
{
    public string StreamName { get; }
    
    public StreamException(string streamName, string message) 
        : base(message, "STREAM_ERROR")
    {
        StreamName = streamName;
    }
}
```

## Best Practices and Common Patterns

### Error Handling Strategy

Implement comprehensive error handling with exponential backoff:

```csharp
public async Task<bool> ConnectWithRetryAsync(int maxAttempts = 3)
{
    for (int attempt = 1; attempt <= maxAttempts; attempt++)
    {
        try
        {
            return await client.ConnectAsync();
        }
        catch (RateLimitException ex)
        {
            await Task.Delay(ex.RetryAfter);
        }
        catch (ConnectionException ex) when (ex.IsRetryable)
        {
            var delay = TimeSpan.FromSeconds(Math.Pow(2, attempt));
            await Task.Delay(delay);
        }
        catch (AuthenticationException)
        {
            // Don't retry authentication errors
            throw;
        }
    }
    return false;
}
```

### Resource Management

Always dispose of resources properly using the `using` statement or implementing `IDisposable`:

```csharp
using (var client = new GnipClient(username, password))
{
    await client.ConnectAsync();
    // Use client...
} // Automatically disconnects and disposes resources
```

## Troubleshooting

**Common Issues:**

1. **Connection Timeouts**: Increase the `ReconnectInterval` in `StreamConfiguration`
2. **Missing Data**: Check `FilterRules` syntax and ensure proper stream permissions
3. **High Memory Usage**: Reduce `BufferSize` or implement proper data processing disposal
4. **Authentication Failures**: Verify credentials and check account status

## Related Resources

- [Gnip API Documentation](https://developer.gnip.com/)
- [Activity Streams Specification](http://activitystrea.ms/)
- [.NET Async Programming Guide](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/async/)