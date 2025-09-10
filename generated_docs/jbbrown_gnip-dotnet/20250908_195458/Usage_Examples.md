# Usage Examples

This section provides comprehensive examples demonstrating how to effectively use the Gnip .NET API Client in various scenarios. The examples cover common use cases from basic streaming operations to advanced event processing patterns, helping developers integrate Gnip's social media data streams into their .NET applications.

## Real-time Streaming

Real-time streaming is the core functionality of the Gnip .NET client, enabling applications to receive live social media data as it becomes available. The following examples demonstrate how to establish and manage streaming connections effectively.

### Basic Streaming Setup

```csharp
using Gnip.Client;
using Gnip.Client.Models;

// Initialize the Gnip client with authentication credentials
var config = new GnipConfiguration
{
    Username = "your-username",
    Password = "your-password",
    Account = "your-account-name",
    StreamLabel = "your-stream-label"
};

var client = new GnipStreamClient(config);

// Set up event handlers for incoming data
client.OnActivityReceived += (sender, activity) =>
{
    Console.WriteLine($"Received activity: {activity.Id}");
    Console.WriteLine($"Content: {activity.Body}");
    Console.WriteLine($"Posted at: {activity.PostedTime}");
};

client.OnError += (sender, error) =>
{
    Console.WriteLine($"Stream error: {error.Message}");
};

// Start the streaming connection
await client.StartStreamAsync();
```

### Advanced Streaming with Buffering

For high-volume streams, implementing proper buffering and batch processing is crucial for maintaining performance:

```csharp
using System.Collections.Concurrent;
using System.Threading.Tasks.Dataflow;

public class BufferedStreamProcessor
{
    private readonly GnipStreamClient _client;
    private readonly ActionBlock<Activity> _processor;
    private readonly ConcurrentQueue<Activity> _buffer;
    private readonly Timer _flushTimer;
    
    public BufferedStreamProcessor(GnipConfiguration config)
    {
        _client = new GnipStreamClient(config);
        _buffer = new ConcurrentQueue<Activity>();
        
        // Configure processing pipeline with bounded capacity
        _processor = new ActionBlock<Activity>(
            ProcessActivity,
            new ExecutionDataflowBlockOptions
            {
                BoundedCapacity = 1000,
                MaxDegreeOfParallelism = Environment.ProcessorCount
            });
        
        // Set up periodic buffer flushing
        _flushTimer = new Timer(FlushBuffer, null, 
            TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(5));
        
        _client.OnActivityReceived += OnActivityReceived;
    }
    
    private void OnActivityReceived(object sender, Activity activity)
    {
        _buffer.Enqueue(activity);
        
        // Process immediately if buffer is getting full
        if (_buffer.Count >= 100)
        {
            FlushBuffer(null);
        }
    }
    
    private void FlushBuffer(object state)
    {
        var activities = new List<Activity>();
        
        while (_buffer.TryDequeue(out var activity) && activities.Count < 100)
        {
            activities.Add(activity);
        }
        
        foreach (var activity in activities)
        {
            _processor.Post(activity);
        }
    }
    
    private async Task ProcessActivity(Activity activity)
    {
        // Your processing logic here
        await SaveToDatabase(activity);
        await UpdateAnalytics(activity);
    }
}
```

### Connection Management and Resilience

Implementing robust connection management ensures your streaming application can handle network interruptions and service outages:

```csharp
public class ResilientStreamManager
{
    private readonly GnipStreamClient _client;
    private readonly ILogger _logger;
    private CancellationTokenSource _cancellationTokenSource;
    private int _reconnectAttempts = 0;
    private readonly int _maxReconnectAttempts = 10;
    
    public async Task StartWithRetryAsync()
    {
        while (_reconnectAttempts < _maxReconnectAttempts)
        {
            try
            {
                _cancellationTokenSource = new CancellationTokenSource();
                await _client.StartStreamAsync(_cancellationTokenSource.Token);
                
                // Reset reconnect counter on successful connection
                _reconnectAttempts = 0;
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Stream connection failed. Attempt {_reconnectAttempts + 1}");
                _reconnectAttempts++;
                
                // Exponential backoff
                var delay = TimeSpan.FromSeconds(Math.Pow(2, _reconnectAttempts));
                await Task.Delay(delay);
            }
        }
    }
}
```

## Historical Data Retrieval

Historical data retrieval allows you to access past social media activities within specified time ranges. This is particularly useful for backfilling data, conducting historical analysis, or recovering from downtime.

### Basic Historical Search

```csharp
using Gnip.Client.Historical;

var historicalClient = new GnipHistoricalClient(config);

var searchRequest = new HistoricalSearchRequest
{
    Query = "keyword OR #hashtag",
    FromDate = DateTime.UtcNow.AddDays(-7),
    ToDate = DateTime.UtcNow.AddDays(-1),
    MaxResults = 1000,
    Format = DataFormat.ActivityStreams
};

var results = await historicalClient.SearchAsync(searchRequest);

foreach (var activity in results.Activities)
{
    Console.WriteLine($"Historical activity: {activity.Body}");
    Console.WriteLine($"Posted: {activity.PostedTime}");
}
```

### Paginated Historical Data Processing

For large historical datasets, implement pagination to manage memory usage and processing time:

```csharp
public async Task ProcessHistoricalDataAsync(HistoricalSearchRequest baseRequest)
{
    var pageSize = 500;
    var currentPage = 0;
    var totalProcessed = 0;
    
    do
    {
        var pagedRequest = new HistoricalSearchRequest
        {
            Query = baseRequest.Query,
            FromDate = baseRequest.FromDate,
            ToDate = baseRequest.ToDate,
            MaxResults = pageSize,
            Next = currentPage > 0 ? GetNextToken() : null
        };
        
        var results = await historicalClient.SearchAsync(pagedRequest);
        
        if (results.Activities?.Any() != true)
            break;
            
        // Process the current page
        await ProcessActivitiesBatch(results.Activities);
        
        totalProcessed += results.Activities.Count();
        currentPage++;
        
        // Store pagination token for next request
        StoreNextToken(results.Next);
        
        // Rate limiting - respect API limits
        await Task.Delay(1000);
        
    } while (totalProcessed < baseRequest.MaxResults);
}
```

### Time-based Data Segmentation

When dealing with large time ranges, segment requests to optimize performance and reliability:

```csharp
public async Task ProcessTimeSegmentedDataAsync(
    string query, 
    DateTime startDate, 
    DateTime endDate)
{
    var segmentDuration = TimeSpan.FromHours(6);
    var currentStart = startDate;
    
    while (currentStart < endDate)
    {
        var currentEnd = currentStart.Add(segmentDuration);
        if (currentEnd > endDate)
            currentEnd = endDate;
            
        var segmentRequest = new HistoricalSearchRequest
        {
            Query = query,
            FromDate = currentStart,
            ToDate = currentEnd,
            MaxResults = 10000
        };
        
        try
        {
            var results = await historicalClient.SearchAsync(segmentRequest);
            await ProcessHistoricalSegment(results, currentStart, currentEnd);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, 
                $"Failed to process segment {currentStart} to {currentEnd}");
            // Implement retry logic or error handling as needed
        }
        
        currentStart = currentEnd;
    }
}
```

## Rule Management

Rules define the filtering criteria for your data streams. Effective rule management ensures you receive relevant data while optimizing performance and staying within API limits.

### Creating and Managing Rules

```csharp
using Gnip.Client.Rules;

var rulesClient = new GnipRulesClient(config);

// Create new rules
var newRules = new List<Rule>
{
    new Rule 
    { 
        Value = "keyword1 OR keyword2", 
        Tag = "marketing-campaign" 
    },
    new Rule 
    { 
        Value = "#hashtag lang:en", 
        Tag = "english-hashtag" 
    },
    new Rule 
    { 
        Value = "from:username OR mention:username", 
        Tag = "user-monitoring" 
    }
};

// Add rules to the stream
var addResult = await rulesClient.AddRulesAsync(newRules);

if (addResult.Success)
{
    Console.WriteLine($"Successfully added {addResult.Rules.Count} rules");
}
else
{
    Console.WriteLine($"Failed to add rules: {addResult.Error}");
}
```

### Rule Validation and Testing

Before deploying rules to production, validate their syntax and test their effectiveness:

```csharp
public async Task<bool> ValidateRulesAsync(IEnumerable<Rule> rules)
{
    var validationClient = new GnipRulesValidationClient(config);
    
    foreach (var rule in rules)
    {
        var validationResult = await validationClient.ValidateRuleAsync(rule);
        
        if (!validationResult.IsValid)
        {
            _logger.LogWarning(
                $"Rule validation failed: {rule.Value} - {validationResult.Error}");
            return false;
        }
        
        // Check estimated volume
        if (validationResult.EstimatedVolume > 1000)
        {
            _logger.LogWarning(
                $"Rule may generate high volume: {rule.Value} " +
                $"(estimated: {validationResult.EstimatedVolume} activities/hour)");
        }
    }
    
    return true;
}
```

### Dynamic Rule Updates

Implement dynamic rule management to adapt to changing requirements without service interruption:

```csharp
public class DynamicRuleManager
{
    private readonly GnipRulesClient _rulesClient;
    private readonly Dictionary<string, Rule> _activeRules;
    
    public async Task UpdateRulesAsync(
        IEnumerable<Rule> newRules, 
        bool replaceAll = false)
    {
        if (replaceAll)
        {
            // Remove all existing rules
            var currentRules = await _rulesClient.GetRulesAsync();
            if (currentRules.Any())
            {
                await _rulesClient.DeleteRulesAsync(currentRules);
            }
        }
        
        // Validate new rules before applying
        if (!await ValidateRulesAsync(newRules))
        {
            throw new InvalidOperationException("Rule validation failed");
        }
        
        // Add new rules
        var result = await _rulesClient.AddRulesAsync(newRules);
        
        if (result.Success)
        {
            // Update local cache
            foreach (var rule in newRules)
            {
                _activeRules[rule.Tag] = rule;
            }
        }
    }
    
    public async Task RemoveRulesByTagAsync(params string[] tags)
    {
        var rulesToRemove = _activeRules
            .Where(kvp => tags.Contains(kvp.Key))
            .Select(kvp => kvp.Value)
            .ToList();
            
        if (rulesToRemove.Any())
        {
            await _rulesClient.DeleteRulesAsync(rulesToRemove);
            
            foreach (var tag in tags)
            {
                _activeRules.Remove(tag);
            }
        }
    }
}
```

## Event Processing Patterns

Implementing robust event processing patterns ensures your application can handle high-volume data streams efficiently while maintaining data integrity and system performance.

### Event-Driven Architecture with Message Queues

```csharp
using Azure.ServiceBus;
using System.Text.Json;

public class EventDrivenProcessor
{
    private readonly ServiceBusClient _serviceBusClient;
    private readonly ServiceBusSender _sender;
    private readonly GnipStreamClient _streamClient;
    
    public EventDrivenProcessor(GnipConfiguration gnipConfig, string serviceBusConnection)
    {
        _streamClient = new GnipStreamClient(gnipConfig);
        _serviceBusClient = new ServiceBusClient(serviceBusConnection);
        _sender = _serviceBusClient.CreateSender("gnip-activities");
        
        _streamClient.OnActivityReceived += OnActivityReceived;
    }
    
    private async void OnActivityReceived(object sender, Activity activity)
    {
        try
        {
            // Enrich activity with metadata
            var enrichedActivity = await EnrichActivity(activity);
            
            // Create message for service bus
            var message = new ServiceBusMessage(JsonSerializer.Serialize(enrichedActivity))
            {
                MessageId = activity.Id,
                ContentType = "application/json",
                Subject = "gnip-activity"
            };
            
            // Add custom properties for routing
            message.ApplicationProperties["source"] = activity.Provider?.DisplayName;
            message.ApplicationProperties["language"] = activity.TwitterLang;
            message.ApplicationProperties["timestamp"] = activity.PostedTime;
            
            await _sender.SendMessageAsync(message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, $"Failed to process activity {activity.Id}");
            // Implement dead letter handling
            await HandleFailedActivity(activity, ex);
        }
    }
    
    private async Task<EnrichedActivity> EnrichActivity(Activity activity)
    {
        return new EnrichedActivity
        {
            OriginalActivity = activity,
            ProcessedAt = DateTime.UtcNow,
            Sentiment = await AnalyzeSentiment(activity.Body),
            Keywords = ExtractKeywords(activity.Body),
            Location = await ResolveLocation(activity.Location)
        };
    }
}
```

### CQRS Pattern Implementation

Implement Command Query Responsibility Segregation (CQRS) to separate read and write operations:

```csharp
public class ActivityCommandHandler
{
    private readonly IActivityWriteRepository _writeRepository;
    private readonly IEventBus _eventBus;
    
    public async Task HandleActivityReceived(Activity activity)
    {
        // Command: Store raw activity
        await _writeRepository.StoreActivityAsync(activity);
        
        // Publish events for different processing pipelines
        await _eventBus.PublishAsync(new ActivityStoredEvent
        {
            ActivityId = activity.Id,
            Timestamp = DateTime.UtcNow
        });
        
        // Trigger specific processing based on content
        if (ContainsKeywords(activity.Body, _monitoredKeywords))
        {
            await _eventBus.PublishAsync(new KeywordMatchedEvent
            {
                ActivityId = activity.Id,
                MatchedKeywords = ExtractMatchedKeywords(activity.Body)
            });
        }
        
        if (activity.Verb == "share" && activity.RetweetCount > 100)
        {
            await _eventBus.PublishAsync(new ViralContentDetectedEvent
            {
                ActivityId = activity.Id,
                ShareCount = activity.RetweetCount.Value
            });
        }
    }
}

public class ActivityQueryHandler
{
    private readonly IActivityReadRepository _readRepository;
    
    public async Task<ActivitySummary> GetActivitySummaryAsync(
        DateTime from, 
        DateTime to)
    