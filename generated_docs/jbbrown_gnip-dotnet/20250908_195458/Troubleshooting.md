# Troubleshooting

This section provides comprehensive guidance for diagnosing and resolving common issues encountered when working with the Gnip .NET API Client. The troubleshooting information is organized by problem category to help you quickly identify and resolve issues in your event-driven applications.

## Common Issues

### Invalid Stream Configuration

**Problem**: Stream fails to initialize or returns unexpected data formats.

**Symptoms**:
- Stream connection established but no data received
- Malformed JSON responses
- Unexpected HTTP status codes (400, 422)

**Solutions**:

1. **Verify Stream Configuration**:
```csharp
var config = new GnipStreamConfig
{
    Url = "https://gnip-api.twitter.com/publishers/twitter/streams/track/prod.json",
    Username = "your-username",
    Password = "your-password",
    Rules = new List<string> { "keyword1", "keyword2" }
};

// Validate configuration before use
if (string.IsNullOrEmpty(config.Url) || string.IsNullOrEmpty(config.Username))
{
    throw new ArgumentException("Stream configuration is incomplete");
}
```

2. **Check Rule Syntax**:
```csharp
// Correct rule format
var validRules = new List<string>
{
    "twitter OR social",
    "lang:en has:links",
    "(cats OR dogs) -puppies"
};

// Avoid common syntax errors
var invalidRules = new List<string>
{
    "twitter OR",  // Incomplete operator
    "lang:",       // Missing value
    "((cats)"      // Unmatched parentheses
};
```

### Event Handler Registration Issues

**Problem**: Events not firing or handlers not receiving data.

**Symptoms**:
- Silent failures in event processing
- Missing event notifications
- Memory leaks from unregistered handlers

**Solutions**:

1. **Proper Event Handler Registration**:
```csharp
public class StreamManager
{
    private GnipStream _stream;
    
    public void InitializeStream()
    {
        _stream = new GnipStream(config);
        
        // Register handlers before starting stream
        _stream.OnActivityReceived += HandleActivity;
        _stream.OnError += HandleError;
        _stream.OnDisconnected += HandleDisconnection;
        
        _stream.Start();
    }
    
    private void HandleActivity(object sender, ActivityEventArgs e)
    {
        try
        {
            // Process activity data
            ProcessActivity(e.Activity);
        }
        catch (Exception ex)
        {
            // Log but don't throw to prevent handler chain interruption
            Logger.Error($"Error processing activity: {ex.Message}");
        }
    }
    
    public void Cleanup()
    {
        if (_stream != null)
        {
            // Always unregister handlers to prevent memory leaks
            _stream.OnActivityReceived -= HandleActivity;
            _stream.OnError -= HandleError;
            _stream.OnDisconnected -= HandleDisconnection;
            _stream.Dispose();
        }
    }
}
```

### JSON Deserialization Failures

**Problem**: Unable to parse incoming JSON data into .NET objects.

**Symptoms**:
- JsonException or similar parsing errors
- Null or incomplete object properties
- Type conversion errors

**Solutions**:

1. **Robust JSON Handling**:
```csharp
public class ActivityProcessor
{
    private readonly JsonSerializerSettings _jsonSettings;
    
    public ActivityProcessor()
    {
        _jsonSettings = new JsonSerializerSettings
        {
            NullValueHandling = NullValueHandling.Ignore,
            DateFormatHandling = DateFormatHandling.IsoDateFormat,
            Error = HandleDeserializationError
        };
    }
    
    private void HandleDeserializationError(object sender, ErrorEventArgs e)
    {
        Logger.Warning($"JSON deserialization error: {e.ErrorContext.Error.Message}");
        e.ErrorContext.Handled = true; // Continue processing
    }
    
    public Activity ParseActivity(string json)
    {
        try
        {
            return JsonConvert.DeserializeObject<Activity>(json, _jsonSettings);
        }
        catch (JsonException ex)
        {
            Logger.Error($"Failed to parse activity JSON: {ex.Message}");
            return null;
        }
    }
}
```

## Connection Problems

### Network Connectivity Issues

**Problem**: Unable to establish or maintain connection to Gnip endpoints.

**Diagnostic Steps**:

1. **Test Basic Connectivity**:
```csharp
public async Task<bool> TestConnectivity(string endpoint)
{
    try
    {
        using (var client = new HttpClient())
        {
            client.Timeout = TimeSpan.FromSeconds(30);
            var response = await client.GetAsync(endpoint);
            return response.IsSuccessStatusCode;
        }
    }
    catch (HttpRequestException ex)
    {
        Logger.Error($"Connectivity test failed: {ex.Message}");
        return false;
    }
    catch (TaskCanceledException ex)
    {
        Logger.Error($"Connection timeout: {ex.Message}");
        return false;
    }
}
```

2. **Implement Connection Retry Logic**:
```csharp
public class ConnectionManager
{
    private const int MaxRetries = 3;
    private const int BaseDelayMs = 1000;
    
    public async Task<bool> ConnectWithRetry(GnipStream stream)
    {
        for (int attempt = 1; attempt <= MaxRetries; attempt++)
        {
            try
            {
                await stream.ConnectAsync();
                Logger.Info($"Connected successfully on attempt {attempt}");
                return true;
            }
            catch (Exception ex)
            {
                Logger.Warning($"Connection attempt {attempt} failed: {ex.Message}");
                
                if (attempt < MaxRetries)
                {
                    var delay = TimeSpan.FromMilliseconds(BaseDelayMs * Math.Pow(2, attempt - 1));
                    await Task.Delay(delay);
                }
            }
        }
        
        Logger.Error($"Failed to connect after {MaxRetries} attempts");
        return false;
    }
}
```

### Firewall and Proxy Configuration

**Problem**: Corporate firewalls or proxies blocking Gnip API access.

**Solutions**:

1. **Configure Proxy Settings**:
```csharp
public class ProxyConfiguration
{
    public static HttpClientHandler CreateProxyHandler(string proxyUrl, string username, string password)
    {
        var proxy = new WebProxy(proxyUrl)
        {
            Credentials = new NetworkCredential(username, password)
        };
        
        return new HttpClientHandler()
        {
            Proxy = proxy,
            UseProxy = true
        };
    }
}

// Usage in stream configuration
var handler = ProxyConfiguration.CreateProxyHandler(
    "http://proxy.company.com:8080", 
    "proxyuser", 
    "proxypass"
);

var httpClient = new HttpClient(handler);
```

2. **Whitelist Required Endpoints**:
```
Required Gnip API endpoints for firewall whitelist:
- gnip-api.twitter.com (port 443)
- stream.gnip.com (port 443)
- api.gnip.com (port 443)
```

### SSL/TLS Certificate Issues

**Problem**: SSL handshake failures or certificate validation errors.

**Solutions**:

1. **Certificate Validation Handling**:
```csharp
public class SslConfiguration
{
    public static void ConfigureCertificateValidation()
    {
        ServicePointManager.ServerCertificateValidationCallback = 
            (sender, certificate, chain, sslPolicyErrors) =>
            {
                if (sslPolicyErrors == SslPolicyErrors.None)
                    return true;
                
                // Log certificate issues for debugging
                Logger.Warning($"SSL Policy Error: {sslPolicyErrors}");
                Logger.Warning($"Certificate Subject: {certificate.Subject}");
                
                // In production, implement proper certificate validation
                // For development only: return true;
                return false;
            };
    }
}
```

## Authentication Errors

### Invalid Credentials

**Problem**: HTTP 401 Unauthorized responses from Gnip API.

**Diagnostic Steps**:

1. **Validate Credentials Format**:
```csharp
public class CredentialValidator
{
    public static bool ValidateCredentials(string username, string password)
    {
        if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
        {
            Logger.Error("Username or password is empty");
            return false;
        }
        
        // Gnip usernames typically follow email format
        if (!username.Contains("@"))
        {
            Logger.Warning("Username should be in email format");
        }
        
        // Check for common encoding issues
        if (username.Contains("%") || password.Contains("%"))
        {
            Logger.Warning("Credentials may be incorrectly URL encoded");
        }
        
        return true;
    }
}
```

2. **Test Authentication Separately**:
```csharp
public async Task<bool> TestAuthentication(string username, string password)
{
    try
    {
        var credentials = Convert.ToBase64String(
            Encoding.ASCII.GetBytes($"{username}:{password}")
        );
        
        using (var client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Basic", credentials);
            
            var response = await client.GetAsync("https://gnip-api.twitter.com/accounts/publishers/twitter.json");
            
            if (response.StatusCode == HttpStatusCode.Unauthorized)
            {
                Logger.Error("Authentication failed - check credentials");
                return false;
            }
            
            return response.IsSuccessStatusCode;
        }
    }
    catch (Exception ex)
    {
        Logger.Error($"Authentication test error: {ex.Message}");
        return false;
    }
}
```

### Token Expiration and Refresh

**Problem**: Authentication tokens expiring during long-running streams.

**Solutions**:

1. **Implement Token Refresh Logic**:
```csharp
public class TokenManager
{
    private string _currentToken;
    private DateTime _tokenExpiry;
    private readonly object _tokenLock = new object();
    
    public string GetValidToken()
    {
        lock (_tokenLock)
        {
            if (DateTime.UtcNow >= _tokenExpiry.AddMinutes(-5)) // Refresh 5 minutes early
            {
                RefreshToken();
            }
            
            return _currentToken;
        }
    }
    
    private void RefreshToken()
    {
        try
        {
            // Implement token refresh logic based on your authentication method
            var newToken = RequestNewToken();
            _currentToken = newToken;
            _tokenExpiry = DateTime.UtcNow.AddHours(1); // Adjust based on token lifetime
            
            Logger.Info("Authentication token refreshed successfully");
        }
        catch (Exception ex)
        {
            Logger.Error($"Token refresh failed: {ex.Message}");
            throw;
        }
    }
}
```

## Performance Issues

### High Memory Usage

**Problem**: Application consuming excessive memory during stream processing.

**Diagnostic Approaches**:

1. **Implement Memory Monitoring**:
```csharp
public class MemoryMonitor
{
    private readonly Timer _monitorTimer;
    private long _lastGcMemory;
    
    public MemoryMonitor()
    {
        _monitorTimer = new Timer(CheckMemoryUsage, null, TimeSpan.Zero, TimeSpan.FromMinutes(1));
    }
    
    private void CheckMemoryUsage(object state)
    {
        var currentMemory = GC.GetTotalMemory(false);
        var workingSet = Process.GetCurrentProcess().WorkingSet64;
        
        Logger.Info($"Memory Usage - GC: {currentMemory / 1024 / 1024} MB, Working Set: {workingSet / 1024 / 1024} MB");
        
        if (currentMemory > _lastGcMemory * 1.5) // 50% increase
        {
            Logger.Warning("Significant memory increase detected, forcing GC");
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();
        }
        
        _lastGcMemory = currentMemory;
    }
}
```

2. **Optimize Object Lifecycle**:
```csharp
public class OptimizedActivityProcessor : IDisposable
{
    private readonly ObjectPool<StringBuilder> _stringBuilderPool;
    private readonly ConcurrentQueue<Activity> _activityQueue;
    private bool _disposed;
    
    public OptimizedActivityProcessor()
    {
        _stringBuilderPool = new DefaultObjectPool<StringBuilder>(
            new StringBuilderPooledObjectPolicy());
        _activityQueue = new ConcurrentQueue<Activity>();
    }
    
    public void ProcessActivity(string json)
    {
        var sb = _stringBuilderPool.Get();
        try
        {
            // Use pooled StringBuilder for processing
            var processedData = ProcessWithStringBuilder(json, sb);
            
            // Queue for batch processing instead of immediate processing
            if (_activityQueue.Count < 1000) // Prevent unbounded growth
            {
                _activityQueue.Enqueue(ParseActivity(processedData));
            }
        }
        finally
        {
            _stringBuilderPool.Return(sb);
        }
    }
    
    public void Dispose()
    {
        if (!_disposed)
        {
            // Clean up resources
            while (_activityQueue.TryDequeue(out _)) { }
            _disposed = true;
        }
    }
}
```

### Slow Processing Performance

**Problem**: Stream processing cannot keep up with incoming data rate.

**Solutions**:

1. **Implement Parallel Processing**:
```csharp
public class ParallelStreamProcessor
{
    private readonly ActionBlock<Activity> _processingBlock;
    
    public ParallelStreamProcessor(int maxDegreeOfParallelism = Environment.ProcessorCount)
    {
        _processingBlock = new ActionBlock<Activity>(
            ProcessActivityAsync,
            new ExecutionDataflowBlockOptions
            {
                MaxDegreeOfParallelism = maxDegreeOfParallelism,
                BoundedCapacity = 1000 // Prevent memory issues
            });
    }
    
    public async Task<bool> QueueActivity(Activity activity)
    {
        return await _processingBlock.SendAsync(activity);
    }
    
    private async Task ProcessActivityAsync(Activity activity)
    {
        try
        {
            // Perform CPU-intensive processing
            await ProcessActivity(activity);
        }
        catch (Exception ex)
        {
            Logger.Error($"Error processing activity {activity.Id}: {ex.Message}");
        }
    }
}
```

2. **Batch Processing Optimization**:
```csharp
public class BatchProcessor
{
    private readonly List<Activity> _batch = new List<Activity>();
    private readonly Timer _flushTimer;
    private const int BatchSize = 100;
    
    public BatchProcessor()
    {
        _flushTimer = new Timer(FlushBatch, null, TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(5));
    }
    
    public void AddActivity(Activity activity)
    {
        lock (_batch)
        {
            _batch.Add(activity);
            
            if (_batch.Count >= BatchSize)
            {
                ProcessBatch(_batch.ToList());
                _batch.Clear();
            }
        }
    }
    
    private void FlushBatch(object state)
    {
        lock (_batch)
        {
            if (_batch.Count > 0)
            