# -*- coding: utf-8 -*-
"""Send hits to Google Analytics through its Measurement Protocol API.


Example:
    ```
    ga = GoogleAnalytics('UA-12345-6')
    ga.set(user_id='abc123')
    ga.send_pageview('/page', 'domain.com')
    ```


Todo:
    * Add unit tests.
    * Add docstrings.

.. _Google Analytics Measurement Protocol guide:
   https://developers.google.com/analytics/devguides/collection/protocol/v1/


"""

__author__ = 'Yu Hui'
__version__ = '1.0a1'
__license__ = 'License :: OSI Approved :: MIT License'

from random import random # to generate the cache buster
import requests # to send hits to GA's collection endpoint

GA_ENDPOINT = "https://www.google-analytics.com/collect"
GA_DEBUG_ENDPOINT = "https://www.google-analytics.com/debug/collect"

HIT_TYPES = [
    'pageview',     # Pageview
    'screenview',   # Screenview / Appview
    'event',        # Event
    'transaction',  # Transaction (non-Enhanced Ecommerce)
    'item',         # Item (non-Enhanced Ecommerce)
    'social',       # Social
    'exception',    # App exception and crash
    'timing',       # User timing
]

class GoogleAnalytics(object):
    """GA tracker object for preparing and sending data to GA's endpoint."""

    tracker_type = 'web' # app or web
    debug = False

    app_name = None
    app_id = None
    app_version = None
    app_installer_id = None
    client_id = None
    custom_dimensions = {}
    custom_metrics = {}
    data_source = 'python'
    document_encoding = None
    hostname = None
    ip_address = None
    page = None
    property_id = None
    screen_name = None
    user_agent = 'python'
    user_id = None
    user_language = None
    version = 1

    # Configuration

    def __init__(
            self,
            property_id,
            client_id=None,
            user_id=None,
            document_encoding=None,
            ip_address=None,
            user_language=None,
            debug=False
        ):
        """Create a new tracker object with base properties.

        Params:
            property_id (str): Tracking ID / web property ID.
            client_id (str): (optional) Anonymous ID of a user,
                    device, or browser instance.
            user_id (str): Known ID of the user.
            document_encoding (str): (optional) Encoding character set of the
                    page/document.
            ip_address (str): (optional) IPv4 address of the user.
            user_language (str): (optional) ISO 639-1 language of the user.
            debug (bool): (optional) Whether to send debugging hits.
                    Default: False.

        Raises:
            ValueError if debug is not a boolean.

        """
        self.property_id = property_id
        self.user_id = user_id
        self.client_id = self.__client_id(client_id)
        self.document_encoding = document_encoding
        self.ip_address = ip_address
        self.user_language = user_language

        if debug is not None and not isinstance(debug, bool):
            raise ValueError('debug should be a boolean.')
        else:
            self.debug = debug

    def __client_id(self, client_id):
        """Set the Client ID from a preset client_id or a new one."""
        if not client_id:
            # no preset client_id, create one.
            if self.user_id:
                # use the User ID as the basis for the Client ID.
                from hashlib import sha1
                sha1_hash = sha1()
                sha1_hash.update(self.user_id)
                client_id = sha1_hash.hexdigest()
            else:
                # create a new Client ID.
                # the format is similar to the one created by analytics.js.
                unique_id = self.__random()

                from time import time
                timestamp = int(time())

                client_id = '{}.{}'.format(unique_id, timestamp)

        return client_id

    # Utilities

    def __cache_buster(self):
        return self.__random()

    def __is_number(self, value):
        return isinstance(value, (float, int))

    def __random(self):
        return int(random() * 10**8)

    # One-time setup

    def __set_app_parameters(
            self,
            app_name,
            app_id=None,
            app_version=None,
            app_installer_id=None,
        ):
        """Set the base app properties.

        Params:
            app_name (str): Name of the application.
            app_id (str): (optional) ID of the application.
            app_version (str): (optional) Version of the application.
            app_installer_id (str): (optional) Installer ID of the application.

        """
        if app_name is not None:
            self.tracker_type = 'app'
            self.app_name = app_name
            self.app_id = app_id
            self.app_version = app_version
            self.app_installer_id = app_installer_id

    def __set_custom_definitions(self, def_type, dictionary):
        """Set the base Custom Definitions (Dimensions or Metrics).

        Params:
            def_type (str): 'dimensions' or 'metrics'.
            dictionary (dict): Indices and values.
                    Refer to the specification for custom_dimensions and
                    custom_metrics.

        Raises:
            ValueError if def_type is not 'dimensions' or 'metrics'.
            ValueError if dictionary is not a dict.
            ValueError if a metric value is not an integer or float.

        """
        if def_type not in ['dimensions', 'metrics']:
            raise ValueError(
                'Unrecognised custom definition: {}.'.format(def_type)
            )

        if dictionary is None:
            return

        if not isinstance(dictionary, dict):
            raise ValueError(
                'Expected custom_{} as a dict.'.format(def_type)
            )

        if def_type == 'dimensions':
            custom_definitions = self.custom_dimensions
        elif def_type == 'metrics':
            custom_definitions = self.custom_metrics

        for index, value in dictionary.iteritems():
            if def_type == 'metrics' and not self.__is_number(value):
                raise ValueError(
                    '"{}" custom_metric should be a number.'.format(value)
                )

            if def_type == 'dimensions':
                key_prefix = 'cd'
            elif def_type == 'metrics':
                key_prefix = 'cm'
            key = '{}{}'.format(key_prefix, index)

            if value is None:
                if key in custom_definitions:
                    custom_definitions.pop(key, None)
            else:
                custom_definitions[key] = value

        return

    def __set_custom_dimensions(
            self,
            custom_dimensions,
        ):
        """Set base Custom Dimension-related properties.

        Params:
            custom_dimensions (dict): Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }

        """
        self.__set_custom_definitions(
            'dimensions',
            custom_dimensions
        )

    def __set_custom_metrics(
            self,
            custom_metrics,
        ):
        """Set base Custom Metric-related properties.

        Params:
            custom_metrics (dict): Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }

        """
        self.__set_custom_definitions(
            'metrics',
            custom_metrics
        )

    def __set_user_id(
            self,
            user_id=None,
        ):
        """Set base User ID."""
        self.user_id = user_id

    def set(
            self,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
            app_name=None,
            app_id=None,
            app_version=None,
            app_installer_id=None,
        ):
        """Set the base properties for all hits.
                All parameters are optional.

        Params:
            user_id (str): Known ID of the user.
            custom_dimensions (dict): Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }
            app_name (str): Name of the application.
            app_id (str): ID of the application.
            app_version (str): Version of the application.
            app_installer_id (str): Installer ID of the application.

        """
        self.__set_custom_dimensions(custom_dimensions)
        self.__set_custom_metrics(custom_metrics)
        self.__set_user_id(user_id)
        self.__set_app_parameters(
            app_name,
            app_id,
            app_version,
            app_installer_id
        )

    # Sending hits

    def __get_base_payload(self):
        """Get the base payload for all hits."""
        cache_buster = self.__cache_buster()

        payload = {
            'cid': self.client_id,
            'de': self.document_encoding,
            'ds': self.data_source,
            'tid': self.property_id,
            'ua': self.user_agent,
            'uid': self.user_id,
            'uip': self.ip_address,
            'ul': self.user_language,
            'v': self.version,
            'z': cache_buster,
        }

        if self.tracker_type == 'web':
            payload['dh'] = self.hostname
            payload['dp'] = self.page
        elif self.tracker_type == 'app':
            payload['an'] = self.app_name
            payload['aid'] = self.app_id
            payload['av'] = self.app_version
            payload['aiid'] = self.app_installer_id
            payload['cd'] = self.screen_name

        return payload

    def __get_content_groups(
            self,
            content_groups,
        ):
        """Get the payload for Content Groups.

        Params:
            content_groups (list): Content groups.
                    Syntax: [ group, group, ... ]
                    Example: [ 'foo', 'bar' ]

        Returns:
            (dict): Payload with Content Group properties.

        Raises:
            ValueError if content_groups is not a list.

        """
        payload = {}

        if content_groups is not None:
            if not isinstance(content_groups, list):
                raise ValueError('Expected content_groups as a list.')

            for i, content_group in enumerate(content_groups):
                key = 'cg{}'.format(i + 1)
                payload[key] = content_group

        return payload

    def __get_custom_definitions(self, def_type, dictionary):
        """Get the payload for Custom Definitions (Dimensions or Metrics).
        Merges the values of dictionary with the base custom_dimensions or
        custom_metrics dictionaries.

        Params:
            def_type (str): 'dimensions' or 'metrics'.
            dictionary (dict): Indices and values.
                    Refer to the specification for custom_dimensions and
                    custom_metrics.

        Returns:
            (dict): Payload with Custom Definition properties.

        Raises:
            ValueError if def_type is not 'dimensions' or 'metrics'.
            ValueError if dictionary is not a dict.
            ValueError if a metric value is not an integer or float.

        """
        if def_type not in ['dimensions', 'metrics']:
            raise ValueError(
                'Unrecognised custom definition: {}.'.format(def_type)
            )

        payload = {}
        if def_type == 'dimensions':
            payload.update(self.custom_dimensions)
        elif def_type == 'metrics':
            payload.update(self.custom_metrics)

        if dictionary is not None:
            if not isinstance(dictionary, dict):
                raise ValueError(
                    'Expected custom_{} as a dict.'.format(def_type)
                )

            for index, value in dictionary.iteritems():
                if def_type == 'metrics' and not self.__is_number(value):
                    raise ValueError(
                        '"{}" custom_metric should be a number.'.format(value)
                    )

                if def_type == 'dimensions':
                    key_prefix = 'cd'
                elif def_type == 'metrics':
                    key_prefix = 'cm'
                key = '{}{}'.format(key_prefix, index)

                if value is None:
                    if key in payload:
                        payload.pop(key, None)
                else:
                    payload[key] = value

        return payload

    def __get_custom_dimensions(self, custom_dimensions):
        """Get the payload for Custom Dimensions.

        Params:
            custom_dimensions (dict): Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }

        Returns:
            (dict): Payload with Custom Dimension properties.

        """
        payload = self.__get_custom_definitions(
            'dimensions',
            custom_dimensions,
        )
        return payload

    def __get_custom_metrics(self, custom_metrics):
        """Get the payload for Custom Metrics.

        Params:
            custom_metrics (dict): Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }

        Returns:
            (dict): Payload with Custom Metric properties.

        """
        payload = self.__get_custom_definitions(
            'metrics',
            custom_metrics,
        )
        return payload

    def __get_user_id(self):
        """Get the payload for User ID."""
        payload = {
            'uid': self.user_id
        }
        return payload

    def __send_hit(
            self,
            hit_type,
            hit_payload,
            custom_dimensions=None,
            custom_metrics=None,
            content_groups=None,
        ):
        """Send a hit to the GA collection or validation server.

        Params:
            hit_type (str): Type of hit. Refer to HIT_TYPES.
            hit_payload (dict): Payload of properties to send with the hit.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }
            content_groups (list): Content groups.
                    Syntax: [ group, group, ... ]
                    Example: [ 'foo', 'bar' ]

        Raises:
            ValueError if hit_type is not found in HIT_TYPES.

        """
        if hit_type not in HIT_TYPES:
            raise ValueError('Invalid hit_type: {}.'.format(hit_type))

        payload = self.__get_base_payload()
        payload['t'] = hit_type
        payload.update(hit_payload)

        custom_dimensions_payload = self.__get_custom_dimensions(
            custom_dimensions
        )
        payload.update(custom_dimensions_payload)

        custom_metrics_payload = self.__get_custom_metrics(
            custom_metrics
        )
        payload.update(custom_metrics_payload)

        if hit_type in ['pageview', 'screenview']:
            content_groups_payload = self.__get_content_groups(
                content_groups
            )
            payload.update(content_groups_payload)

        # remove any items that have None values
        for key, value in payload.iteritems():
            if value is None:
                payload.pop(key, None)

        endpoint = GA_DEBUG_ENDPOINT if self.debug else GA_ENDPOINT
        req = requests.post(endpoint, data=payload)
        if self.debug:
            response = req.json()
            self.__handle_debug_response(response['hitParsingResult'][0])

    # Public methods for sending hits.
    # Each method corresponds to a hit type.

    def send_event(
            self,
            event_category,
            event_action,
            event_label=None,
            event_value=None,
            non_interaction=False,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        """Send an Event hit.

        Params:
            event_category (str): Category of the event.
            event_action (str): Action of the event.
            event_label (str): (optional) Label of the event.
            event_value (int): (optional) Value of the event.
            non_interaction (bool): (optional) Whether this is non-interactive.
                    Default: False.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }

        Raises:
            ValueError if event_category is None.
            ValueError if event_action is None.
            ValueError if event_value is not an integer.
            ValueError if non_interaction is not a boolean.

        """
        if not event_category:
            raise ValueError('Missing event_category when sending event hit.')
        if not event_action:
            raise ValueError('Missing event_action when sending event hit.')
        if event_value and not isinstance(event_value, int):
            raise ValueError('event_value should be an integer when sending event hit.')
        if non_interaction and not isinstance(non_interaction, bool):
            raise ValueError('non_interaction should be a boolean when sending event hit.')

        hit_payload = {
            'ec': event_category,
            'ea': event_action,
            'el': event_label,
            'ev': event_value,
            'ni': int(non_interaction),
        }

        self.__send_hit(
            'event',
            hit_payload,
            custom_dimensions,
            custom_metrics,
        )

    def send_exception(
            self,
            ex_description,
            ex_fatal=False,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        """Send an Exception hit.

        Params:
            ex_description (str): Description of the exception.
            ex_fatal (bool): (optional) Whether the exception is fatal.
                    Default: False.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }

        Raises:
            ValueError if ex_description is None.
            ValueError if ex_fatal is not a boolean.

        """
        if not ex_description:
            raise ValueError('Missing ex_description when sending exception hit.')
        if ex_fatal and not isinstance(ex_fatal, bool):
            raise ValueError('ex_fatal should be a boolean when sending exception hit.')

        hit_payload = {
            'exd': ex_description,
            'exf': int(ex_fatal),
        }

        self.__send_hit(
            'exception',
            hit_payload,
            custom_dimensions,
            custom_metrics,
        )

    def send_pageview(
            self,
            page,
            hostname,
            title=None,
            custom_dimensions=None,
            custom_metrics=None,
            content_groups=None,
        ):
        """Send a Pageviw hit.

        Params:
            page (str): Path portion of the page URL.
            hostname (str): Hostname from which content was hosted.
            title (str): (optional) Title of the page / document.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }
            content_groups (list): Content groups.
                    Syntax: [ group, group, ... ]
                    Example: [ 'foo', 'bar' ]

        Raises:
            ValueError if page is None.
            ValueError if hostname is None.

        """
        if not page:
            raise ValueError('Missing page when sending pageview hit.')
        if not hostname:
            raise ValueError('Missing hostname when sending pageview hit.')

        self.hostname = hostname
        self.page = page

        hit_payload = {
            'dh': hostname,
            'dp': page,
            'dt': title,
        }

        self.__send_hit(
            'pageview',
            hit_payload,
            custom_dimensions,
            custom_metrics,
            content_groups,
        )

    def send_screenview(
            self,
            screen_name,
            custom_dimensions=None,
            custom_metrics=None,
            content_groups=None,
        ):
        """Send a Screenview hit.

        Params:
            screen_name (str): Name of the screen.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }
            content_groups (list): Content groups.
                    Syntax: [ group, group, ... ]
                    Example: [ 'foo', 'bar' ]

        Raises:
            ValueError if screen_name is None.

        """
        if not screen_name:
            raise ValueError('Missing screen_name when sending screenview hit.')

        self.screen_name = screen_name

        hit_payload = {
            'cd': screen_name,
        }

        self.__send_hit(
            'screenview',
            hit_payload,
            custom_dimensions,
            custom_metrics,
            content_groups,
        )

    def send_social(
            self,
            social_network,
            social_action,
            social_target,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        """Send a Social hit.

        Params:
            social_network (str): Social network of the social interaction.
            social_action (str): Action of the social interaction.
            social_target (str): Target of the social interaction.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }

        Raises:
            ValueError if social_network is None.
            ValueError if social_action is None.
            ValueError if social_target is None.

        """
        if not social_network:
            raise ValueError('Missing social_network when sending social hit.')
        if not social_action:
            raise ValueError('Missing social_action when sending social hit.')
        if not social_target:
            raise ValueError('Missing social_target when sending social hit.')

        hit_payload = {
            'sn': social_network,
            'sa': social_action,
            'st': social_target,
        }

        self.__send_hit(
            'social',
            hit_payload,
            custom_dimensions,
            custom_metrics,
        )

    def send_timing(
            self,
            timing_category,
            timing_var,
            timing_value,
            timing_label=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        """Send a Timing hit.

        Params:
            timing_category (str): Category of the user timing.
            timing_var (str): Variable of the user timing.
            timing_value (str): Value of the user timing in milliseconds.
            timing_label (str): (optional) Label of the user timing.
            custom_dimensions (dict): (optional) Custom Dimension indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 'foo', '3': 'bar' }
            custom_metrics (dict): (optional) Custom Metric indices and values.
                    Syntax: { index: value, index: value, ... }
                    Example: { '1': 10, '4': 5.6 }

        Raises:
            ValueError if timing_category is None.
            ValueError if timing_var is None.
            ValueError if timing_value is None.
            ValueError if timing_value is not an integer.

        """
        if not timing_category:
            raise ValueError('Missing timing_category when sending timing hit.')
        if not timing_var:
            raise ValueError('Missing timing_var when sending timing hit.')
        if not timing_value:
            raise ValueError('Missing timing_value when sending timing hit.')
        if timing_value and not isinstance(timing_value, int):
            raise ValueError('timing_value should be an integer when sending timing hit.')

        hit_payload = {
            'utc': timing_category,
            'utv': timing_var,
            'utt': timing_value,
            'utl': timing_label,
        }

        self.__send_hit(
            'timing',
            hit_payload,
            custom_dimensions,
            custom_metrics,
        )

    # Debug

    def __handle_debug_response(self, hit_parsing_result):
        """Show the message from the validation server."""
        valid = hit_parsing_result['valid']
        hit = hit_parsing_result['hit']
        print hit
        if valid:
            print "Valid hit."
        else:
            print "Invalid hit."
            parser_messages = hit_parsing_result['parserMessage']
            for parser_message in parser_messages:
                message_type = parser_message['messageType']
                description = parser_message['description']
                print "{}: {}".format(message_type, description)
