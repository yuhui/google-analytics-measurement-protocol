# google-analytics-measurement-protocol

Send hits to Google Analytics through its Measurement Protocol API.

The architecture is inspired by [Google Analytics' `analytics.js` library](https://developers.google.com/analytics/devguides/collection/analyticsjs/).

## Installation

Install from git:
```
pip install -e git+https://github.com/yuhui/google-analytics-measurement-protocol.git#egg=google-analytics-measurement-protocol
```

## Usage

```
from google.analytics.measurement_protocol import GoogleAnalytics

# create a tracker
ga = GoogleAnalytics('UA-12345-6')

# set common fields
ga.set(user_id='abc123')

# send data
ga.send_pageview('/page', 'domain.com')
ga.send_event('menu', 'click', 'about')
```

## Setting data
Use the `set()` method to set data that can be sent with all hits:

- `custom_dimensions`
- `custom_metrics`
- `user_id`
- `app_name`
- `app_id`
- `app_version`
- `app_installer_id`

## Sending data
Send hit data with the appropriate methods:

- `send_pageview(page, hostname, title, content_groups)`
- `send_screenview(screen_name)`
- `send_event(event_category, event_action, event_label, event_value, non_interaction)`
- `send_social(social_network, social_action, social_target)`
- `send_exception(ex_description, ex_fatal)`
- `send_timing(timing_category, timing_var, timing_value, timing_label)`

Not available:
- `transaction`
- `item`
- Traffic Sources
- Enhanced Ecommerce

**Note about Content Experiments**

Support for Content Experiment tracking will *never* be available because Google Analytics has deprecated this feature.

## Debugging
Use `debug=True` when creating the tracker, e.g.

```
# create a debugger tracker
ga_debug = GoogleAnalytics('UA-12345-6', debug=True)
```

This prevents hits from being sent to your Analytics property. Instead, your hits are validated against the [Measurement Protocol Validation Server](https://developers.google.com/analytics/devguides/collection/protocol/v1/validating-hits).
