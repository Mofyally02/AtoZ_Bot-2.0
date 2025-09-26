# Enhanced Job Monitoring Features

This document describes the enhanced job monitoring functionality added to the AtoZ Bot, including 10-second job checking and 5-second results reporting.

## Overview

The bot now supports two enhanced monitoring features:

1. **10-Second Job Checking**: Monitors for jobs matching a selected category every 10 seconds (or any custom interval). This is separate from the main bot processing cycle and provides faster detection of relevant jobs.

2. **5-Second Results Reporting**: Provides detailed reports of accepted jobs every 5 seconds (or any custom interval), including statistics, language distribution, and time period analysis.

## New Configuration Parameters

### Environment Variables

Add these to your `.env` file:

```bash
# Quick check configuration
QUICK_CHECK_INTERVAL_SEC=10          # Interval in seconds (default: 10)
ENABLE_QUICK_CHECK=false             # Enable/disable quick checking (default: false)

# Results reporting configuration
RESULTS_REPORT_INTERVAL_SEC=5        # Interval in seconds (default: 5)
ENABLE_RESULTS_REPORTING=true        # Enable/disable results reporting (default: true)

# Main bot configuration
REFRESH_INTERVAL_SEC=0.5             # Main bot interval (default: 0.5)
```

### Configuration in Code

The following parameters are available in `BOT_CONFIG`:

- `quick_check_interval`: Float value for check interval in seconds (default: 10)
- `enable_quick_check`: Boolean to enable/disable the feature (default: false)
- `results_report_interval`: Float value for results reporting interval in seconds (default: 5)
- `enable_results_reporting`: Boolean to enable/disable results reporting (default: true)
- `check_interval`: Main bot processing interval (default: 0.5)

## Usage

### 1. Enable Quick Checking

Set the environment variable or modify the config:

```python
# In your .env file
ENABLE_QUICK_CHECK=true
QUICK_CHECK_INTERVAL_SEC=10

# Or in code
BOT_CONFIG["enable_quick_check"] = True
BOT_CONFIG["quick_check_interval"] = 10
```

### 2. Run with Quick Checking

#### Option A: Use the Persistent Bot (Recommended)
```bash
python persistent_bot.py
```

#### Option B: Use the Bot Orchestrator
```bash
python bot_orchestrator.py
```

#### Option C: Use the Standalone Quick Checker
```bash
# Run for 5 minutes
python quick_checker.py "Telephone interpreting" 5

# Run indefinitely
python quick_checker.py "Telephone interpreting"
```

### 3. Test the Features
```bash
# Show current configuration
python test_quick_check.py config

# Run a 2-minute test for quick checking
python test_quick_check.py

# Test results reporting
python test_results_reporting.py

# Test manual job addition
python test_results_reporting.py manual

# Show results reporting configuration
python test_results_reporting.py config
```

## How It Works

### Quick Check Process

1. **Job Extraction**: The bot navigates to the job board and extracts all available jobs
2. **Category Filtering**: For each "matched" job, it checks the job details page to verify the category
3. **Matching**: Jobs that match the selected category (e.g., "Telephone interpreting") are identified
4. **Reporting**: Found jobs are logged with their details (reference, language, date, time)

### Results Reporting Process

1. **Job Tracking**: Every time a job is accepted, it's automatically tracked with timestamp and details
2. **Interval Reporting**: Every 5 seconds (or configured interval), a summary report is generated
3. **Statistics**: The system tracks total accepted jobs, jobs since last report, session duration, and more
4. **Detailed Analysis**: Provides language distribution, time period analysis, and performance metrics

### Integration with Main Bot

- Both quick check and results reporting run independently of the main bot processing cycle
- They use the same login session to avoid re-authentication overhead
- Results are logged separately from main bot activities
- The main bot continues to process jobs normally

## Files Modified/Added

### New Files
- `quick_checker.py`: Standalone quick checking module
- `results_tracker.py`: Results tracking and reporting module
- `test_quick_check.py`: Test script for quick checking functionality
- `test_results_reporting.py`: Test script for results reporting functionality
- `QUICK_CHECK_README.md`: This documentation

### Modified Files
- `config.py`: Added quick check and results reporting configuration parameters
- `data_processor.py`: Added `check_jobs_for_category()` and `quick_job_check_cycle()` functions
- `persistent_bot.py`: Integrated quick checking and results tracking into the main bot loop
- `bot_orchestrator.py`: Added quick check and results reporting scheduling support
- `env.example`: Added new environment variable examples

## Example Output

### Quick Checking Output
When quick checking is enabled, you'll see output like:

```
[AtoZBot] Quick check enabled: checking every 10s for category 'Telephone interpreting'
[AtoZBot] Quick check found 2 jobs matching category 'Telephone interpreting'
Found 2 jobs matching category 'Telephone interpreting':
  - Job 12345: Spanish - 2024-01-15 14:30
  - Job 12346: French - 2024-01-15 15:00
```

### Results Reporting Output
When results reporting is enabled, you'll see output like:

```
============================================================
📊 RESULTS REPORT - 2024-01-15T14:35:22.123456
============================================================
⏱️  Session Duration: 12.5 minutes
✅ Total Accepted: 8 jobs
🆕 Since Last Report: 2 jobs

📋 Recently Accepted Jobs:
  1. Job 12345: Spanish - 2024-01-15 14:30
     Accepted at: 2024-01-15T14:34:15.123456
  2. Job 12346: French - 2024-01-15 15:00
     Accepted at: 2024-01-15T14:34:45.789012
============================================================
```

### Detailed Statistics Output
At the end of a session, you'll see detailed statistics:

```
============================================================
📈 DETAILED STATISTICS
============================================================
📊 Total Jobs Accepted: 15
⏱️  Session Duration: 2.5 hours
📈 Average per Hour: 6.0 jobs

🌍 Language Distribution:
  Spanish: 6 jobs
  French: 4 jobs
  German: 3 jobs
  Italian: 2 jobs

🕐 Time Period Distribution:
  Morning: 3 jobs
  Afternoon: 8 jobs
  Evening: 4 jobs
  Night: 0 jobs
============================================================
```

## Performance Considerations

- Quick checking adds minimal overhead as it reuses the existing browser session
- The 10-second interval provides a good balance between responsiveness and resource usage
- You can adjust the interval based on your needs (shorter for more frequent checks, longer to reduce load)

## Troubleshooting

### Quick Check Not Running
1. Verify `ENABLE_QUICK_CHECK=true` in your environment
2. Check that `BOT_CONFIG["bot_running"]` is `True`
3. Ensure the bot is logged in successfully

### No Jobs Found
1. Verify the selected category matches exactly (case-sensitive in job details)
2. Check that there are actually "matched" jobs available
3. Ensure the job board is accessible and loading properly

### Performance Issues
1. Increase `QUICK_CHECK_INTERVAL_SEC` to reduce frequency
2. Check browser resources and consider running headless
3. Monitor network connectivity to the job portal

## Future Enhancements

Potential improvements for the quick checking feature:

1. **Multiple Categories**: Support checking for multiple job categories simultaneously
2. **Custom Filters**: Add more sophisticated filtering criteria
3. **Notifications**: Send alerts when matching jobs are found
4. **Statistics**: Track and report quick check performance metrics
5. **Webhook Integration**: Send job matches to external services
