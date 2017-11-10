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

import requests # to send his to GA's collection endpoint
from random import random # to generate the cache buster

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

    data_source = 'python'
    debug = False
    document_encoding = None
    ip_address = None
    property_id = None
    user_agent = 'python'
    user_id = None
    user_language = None
    version = 1

    # Configuration

    def __init__(
            self,
            property_id,
            user_id=None,
            document_encoding=None,
            ip_address=None,
            user_language=None,
            debug=False
        ):
        self.property_id = property_id
        self.user_id = user_id

        config_payload = {
            'v': self.version,
            'cid': self.__client_id(),
            'tid': self.property_id,
            'ds': self.data_source,
            'ua': self.user_agent,
        }

        if document_encoding:
            self.document_encoding = document_encoding
            config_payload['de'] = document_encoding
        if ip_address:
            self.ip_address = ip_address
            config_payload['uip'] = ip_address
        if user_language:
            self.user_language = user_language
            config_payload['ul'] = user_language

        self.config_payload = config_payload

        if debug and not isinstance(debug, bool):
            raise ValueError('debug should be a boolean when configuring tracker.')
        self.debug = debug

    def __client_id(self):
        if self.user_id:
            from hashlib import sha1
            sha1_hash = sha1()
            sha1_hash.update(self.user_id)
            client_id = sha1_hash.hexdigest()
        else:
            unique_id = self.__random()

            from time import time
            timestamp = int(time())

            client_id = '{}.{}'.format(unique_id, timestamp)

        return client_id

    # Utility

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
        app_payload = {}

        if app_name is not None:
            app_payload['an'] = app_name

            if app_id:
                app_payload['aid'] = app_id
            if app_version:
                app_payload['av'] = app_version
            if app_installer_id:
                app_payload['aiid'] = app_installer_id

        return app_payload

    def __set_content_group_parameters(
            self,
            content_groups,
        ):
        content_groups_payload = {}
        if content_groups is not None and isinstance(content_groups, list):
            for i, content_group in enumerate(content_groups):
                content_group_key = 'cg{}'.format(i + 1)
                content_groups_payload[content_group_key] = content_group
        return content_groups_payload

    def __set_custom_dimension_parameters(
            self,
            custom_dimensions,
        ):
        custom_dimension_payload = {}
        if custom_dimensions:
            for index, value in custom_dimensions.iteritems():
                key = 'cd{}'.format(index)
                custom_dimension_payload[key] = str(value)
        return custom_dimension_payload

    def __set_custom_metric_parameters(
            self,
            custom_metrics,
        ):
        custom_metric_payload = {}
        if custom_metrics:
            for index, value in custom_metrics.iteritems():
                if not isinstance(value, int) and not isinstance(value, float):
                    raise ValueError('{} should be a number to use as a metric.')
                key = 'cd{}'.format(index)
                custom_metric_payload[key] = value
        return custom_metric_payload

    def __set_user_id_parameter(
            self,
            user_id=None,
        ):
        user_id_payload = {}
        if user_id:
            user_id_payload['uid'] = user_id
        elif self.user_id:
            user_id_payload['uid'] = self.user_id
        return user_id_payload

    def __set_other_parameters(
            self,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        other_payload = {}

        user_id_payload = self.__set_user_id_parameter(user_id)
        other_payload.update(user_id_payload)

        custom_dimension_payload = self.__set_custom_dimension_parameters(custom_dimensions)
        other_payload.update(custom_dimension_payload)

        custom_metric_payload = self.__set_custom_metric_parameters(custom_metrics)
        other_payload.update(custom_metric_payload)

        return other_payload

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
        set_payload = {}

        other_payload = self.__set_other_parameters(
            user_id,
            custom_dimensions,
            custom_metrics,
        )
        set_payload.update(other_payload)

        app_payload = self.__set_app_parameters(
            app_name,
            app_id,
            app_version,
            app_installer_id
        )
        set_payload.update(app_payload)

        self.config_payload.update(set_payload)

    # Sending hits

    def __cache_buster(self):
        cache_buster = self.__random()
        return cache_buster

    def __send_hit(
            self,
            hit_type,
            hit_payload,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        if hit_type not in HIT_TYPES:
            raise ValueError('Invalid hit_type {}.'.format(hit_type))

        cache_buster = self.__cache_buster()
        payload = {
            't': hit_type,
            'z': cache_buster,
        }
        payload.update(self.config_payload)

        other_payload = self.__set_other_parameters(
            user_id,
            custom_dimensions,
            custom_metrics,
        )
        payload.update(other_payload)

        payload.update(hit_payload)

        endpoint = GA_DEBUG_ENDPOINT if self.debug else GA_ENDPOINT
        req = requests.post(endpoint, data=payload)
        if self.debug:
            response = req.json()
            self.__handle_debug_response(response['hitParsingResult'][0])

    def send_event(
            self,
            event_category,
            event_action,
            event_label=None,
            event_value=None,
            non_interaction=False,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
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
        }
        if event_label:
            hit_payload['el'] = event_label
        if event_value:
            hit_payload['ev'] = event_value
        if non_interaction:
            hit_payload['ni'] = int(non_interaction)

        self.__send_hit(
            'event',
            hit_payload,
            user_id,
            custom_dimensions,
            custom_metrics,
        )

    def send_exception(
            self,
            ex_description,
            ex_fatal=False,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        if not ex_description:
            raise ValueError('Missing ex_description when sending exception hit.')
        if ex_fatal and not isinstance(ex_fatal, bool):
            raise ValueError('ex_fatal should be a boolean when sending exception hit.')

        hit_payload = {
            'exd': ex_description,
        }
        if ex_fatal:
            hit_payload['exf'] = int(ex_fatal)

        self.__send_hit(
            'exception',
            hit_payload,
            user_id,
            custom_dimensions,
            custom_metrics,
        )

    def send_pageview(
            self,
            page,
            hostname,
            title=None,
            content_groups=None,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        if not page:
            raise ValueError('Missing page when sending pageview hit.')
        if not hostname:
            raise ValueError('Missing hostname when sending pageview hit.')

        hit_payload = {
            'dh': hostname,
            'dp': page,
        }
        if title:
            hit_payload['dt'] = title

        content_groups_payload = self.__set_content_group_parameters(content_groups)
        if content_groups_payload:
            hit_payload.update(content_groups_payload)

        self.__send_hit(
            'pageview',
            hit_payload,
            user_id,
            custom_dimensions,
            custom_metrics,
        )

    def send_screenview(
            self,
            screen_name,
            content_groups=None,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        if not screen_name:
            raise ValueError('Missing screen_name when sending screenview hit.')

        hit_payload = {
            'cd': screen_name,
        }

        content_groups_payload = self.__set_content_group_parameters(content_groups)
        if content_groups_payload:
            hit_payload.update(content_groups_payload)

        self.__send_hit(
            'screenview',
            hit_payload,
            user_id,
            custom_dimensions,
            custom_metrics,
        )

    def send_social(
            self,
            social_network,
            social_action,
            social_target,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
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
            user_id,
            custom_dimensions,
            custom_metrics,
        )

    def send_timing(
            self,
            timing_category,
            timing_var,
            timing_value,
            timing_label=None,
            user_id=None,
            custom_dimensions=None,
            custom_metrics=None,
        ):
        if not timing_category:
            raise ValueError('Missing timing_category when sending timing hit.')
        if not timing_var:
            raise ValueError('Missing timing_var when sending timing hit.')
        if not timing_value:
            raise ValueError('Missing timing_value when sending timing hit.')

        hit_payload = {
            'utc': timing_category,
            'utv': timing_var,
            'utt': timing_value,
        }
        if timing_label:
            hit_payload['utl'] = timing_label

        self.__send_hit(
            'timing',
            hit_payload,
            user_id,
            custom_dimensions,
            custom_metrics,
        )

    # Debug

    def __handle_debug_response(self, hit_parsing_result):
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
