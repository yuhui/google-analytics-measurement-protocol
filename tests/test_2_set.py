# -*- coding: utf-8 -*-
"""Unit tests for google.analytics.measurement_protocol's GoogleAnalytics."""

import unittest

from google.analytics.measurement_protocol import GoogleAnalytics

PROPERTY_ID = 'UA-12345-6'
APP_NAME = 'test app'
APP_ID = 'test.app.py'
APP_VERSION = '1.0'
APP_INSTALLER_ID = 'test.py'
ORIGINAL_CUSTOM_DIMENSIONS = {
    '1': 'foo',
    '3': 'bar',
    '10': '79',
}
ORIGINAL_CUSTOM_METRICS = {
    '2': 10,
    '4': 101.6,
}
ORIGINAL_USER_ID = 'utama'
REVISED_CUSTOM_DIMENSIONS = {
    '2': 'lorem',
    '4': 'ipsum',
    '10': '143',
}
REVISED_CUSTOM_METRICS = {
    '1': 8,
    '4': 98.7,
}
REVISED_USER_ID = 'raffles'
STRING_CUSTOM_DIMENSIONS = "{ '5': 'dolor sit amet' }"
STRING_CUSTOM_METRICS = "{ '9': 24738 }"
BAD_CUSTOM_METRICS = {
    '3': 'word',
}

class SetAppName(unittest.TestCase):
    """Tests for set() with app name, app ID, app version, app installer ID."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            app_name=APP_NAME,
        )

    def test_01_app_tracker_type(self):
        self.assertEqual(
            self.ga.tracker_type,
            'app',
            '"{}" should be "app"'.format(self.ga.tracker_type),
        )

    def test_02_matches_app_name(self):
        self.assertEqual(
            self.ga.app_name,
            APP_NAME,
            '"{}" should be "{}"'.format(self.ga.app_name, APP_NAME),
        )

    def test_03_empty_app_id(self):
        self.assertIsNone(self.ga.app_id)

    def test_04_empty_app_version(self):
        self.assertIsNone(self.ga.app_version)

    def test_05_empty_app_installer_id(self):
        self.assertIsNone(self.ga.app_installer_id)

class SetAppFieldsWithoutAppName(unittest.TestCase):
    """Tests for set() with app fields without app name."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            app_id=APP_ID,
            app_version=APP_VERSION,
            app_installer_id=APP_INSTALLER_ID,
        )

    def test_01_web_tracker_type(self):
        self.assertEqual(
            self.ga.tracker_type,
            'web',
            '"{}" should be "web"'.format(self.ga.tracker_type),
        )

    def test_02_empty_app_name(self):
        self.assertIsNone(self.ga.app_name)

    def test_03_empty_app_id(self):
        self.assertIsNone(self.ga.app_id)

    def test_04_empty_app_version(self):
        self.assertIsNone(self.ga.app_version)

    def test_05_empty_app_installer_id(self):
        self.assertIsNone(self.ga.app_installer_id)

class SetUserId(unittest.TestCase):
    """Tests for set() with user_id."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            user_id=ORIGINAL_USER_ID,
        )

    def test_01_random_client_id(self):
        self.assertIsNotNone(self.ga.client_id)
        client_id_parts = self.ga.client_id.split('.')
        self.assertEqual(
            len(client_id_parts),
            2,
            '"{}" does not have 2 parts'.format(self.ga.client_id),
        )

    def test_02_matches_user_id(self):
        self.assertEqual(
            self.ga.user_id,
            ORIGINAL_USER_ID,
            '"{}" should be "{}"'.format(self.ga.user_id, ORIGINAL_USER_ID),
        )

class SetNewUserId(unittest.TestCase):
    """Tests for set() with user_id and then a new one."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            user_id=ORIGINAL_USER_ID,
        )
        self.ga.set(
            user_id=REVISED_USER_ID,
        )

    def test_01_matches_user_id(self):
        self.assertEqual(
            self.ga.user_id,
            REVISED_USER_ID,
            '{} should be {}'.format(self.ga.user_id, REVISED_USER_ID),
        )

class SetCustomDimensionsMetrics(unittest.TestCase):
    """Tests for set() with custom_dimensions."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            custom_dimensions=ORIGINAL_CUSTOM_DIMENSIONS,
            custom_metrics=ORIGINAL_CUSTOM_METRICS,
        )

    def test_01_matches_custom_dimensions(self):
        original_custom_dimensions = {
            'cd{}'.format(index): value for index, value in ORIGINAL_CUSTOM_DIMENSIONS.iteritems()
        }
        self.assertEqual(
            self.ga.custom_dimensions,
            original_custom_dimensions,
            '{} should be {}'.format(self.ga.custom_dimensions, original_custom_dimensions),
        )

    def test_02_matches_custom_metrics(self):
        original_custom_metrics = {
            'cm{}'.format(index): value for index, value in ORIGINAL_CUSTOM_METRICS.iteritems()
        }
        self.assertEqual(
            self.ga.custom_metrics,
            original_custom_metrics,
            '{} should be {}'.format(self.ga.custom_metrics, original_custom_metrics),
        )

class SetNewCustomDimensionsMetrics(unittest.TestCase):
    """Tests for set() with custom_dimensions and then a new one."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            custom_dimensions=ORIGINAL_CUSTOM_DIMENSIONS,
            custom_metrics=ORIGINAL_CUSTOM_METRICS,
        )
        self.ga.set(
            custom_dimensions=REVISED_CUSTOM_DIMENSIONS,
            custom_metrics=REVISED_CUSTOM_METRICS,
        )

    def test_01_matches_custom_dimensions(self):
        import copy
        merged_custom_dimensions = copy.deepcopy(ORIGINAL_CUSTOM_DIMENSIONS)
        merged_custom_dimensions.update(REVISED_CUSTOM_DIMENSIONS)
        merged_custom_dimensions = {
            'cd{}'.format(index): value for index, value in merged_custom_dimensions.iteritems()
        }
        self.assertEqual(
            self.ga.custom_dimensions,
            merged_custom_dimensions,
            '{} should be {}'.format(self.ga.custom_dimensions, merged_custom_dimensions),
        )

    def test_02_matches_custom_metrics(self):
        import copy
        merged_custom_metrics = copy.deepcopy(ORIGINAL_CUSTOM_METRICS)
        merged_custom_metrics.update(REVISED_CUSTOM_METRICS)
        merged_custom_metrics = {
            'cm{}'.format(index): value for index, value in merged_custom_metrics.iteritems()
        }
        self.assertEqual(
            self.ga.custom_metrics,
            merged_custom_metrics,
            '{} should be {}'.format(self.ga.custom_metrics, merged_custom_metrics),
        )

class SetBadCustomDimensionsMetrics(unittest.TestCase):
    """Tests for set() with custom_dimensions and metrics and then a new, bad one."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)
        self.ga.set(
            custom_dimensions=ORIGINAL_CUSTOM_DIMENSIONS,
            custom_metrics=ORIGINAL_CUSTOM_METRICS,
        )

    def __set_string_custom_dimensions(self):
        self.ga.set(
            custom_dimensions=STRING_CUSTOM_DIMENSIONS
        )

    def __set_string_custom_metrics(self):
        self.ga.set(
            custom_dimensions=STRING_CUSTOM_METRICS
        )

    def __set_bad_custom_metrics(self):
        self.ga.set(
            custom_metrics=BAD_CUSTOM_METRICS,
        )

    def test_01_raises_error_with_string_custom_dimensions(self):
        self.assertRaises(ValueError, self.__set_string_custom_dimensions)

    def test_02_raises_error_with_string_custom_metrics(self):
        self.assertRaises(ValueError, self.__set_string_custom_metrics)

    def test_03_raises_error_with_bad_custom_metrics(self):
        self.assertRaises(ValueError, self.__set_bad_custom_metrics)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
