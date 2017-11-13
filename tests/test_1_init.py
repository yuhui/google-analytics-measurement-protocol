# -*- coding: utf-8 -*-
"""Unit tests for google.analytics.measurement_protocol's GoogleAnalytics."""

import unittest

from google.analytics.measurement_protocol import GoogleAnalytics

PROPERTY_ID = 'UA-12345-6'
ORIGINAL_USER_ID = 'utama'
REVISED_USER_ID = 'raffles'

class CreateDefaultTracker(unittest.TestCase):
    """Tests for __init__()."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID)

    def test_01_matches_property_id(self):
        self.assertEqual(
            self.ga.property_id,
            PROPERTY_ID,
            '"{}" should be "{}"'.format(self.ga.property_id, PROPERTY_ID),
        )

    def test_02_empty_user_id(self):
        self.assertIsNone(self.ga.user_id)

    def test_03_random_client_id(self):
        self.assertIsNotNone(self.ga.client_id)
        client_id_parts = self.ga.client_id.split('.')
        self.assertEqual(
            len(client_id_parts),
            2,
            '"{}" does not have 2 parts'.format(self.ga.client_id),
        )

    def test_04_empty_custom_dimensions(self):
        self.assertEqual(self.ga.custom_dimensions, {}, 'custom_dimensions is not empty')

    def test_05_empty_custom_metrics(self):
        self.assertEqual(self.ga.custom_metrics, {}, 'custom_metrics is not empty')

    def test_06_empty_app_name(self):
        self.assertIsNone(self.ga.app_name)

    def test_07_empty_app_id(self):
        self.assertIsNone(self.ga.app_id)

    def test_08_empty_app_version(self):
        self.assertIsNone(self.ga.app_version)

    def test_09_empty_app_installer_id(self):
        self.assertIsNone(self.ga.app_installer_id)

    def test_10_web_tracker_type(self):
        self.assertEqual(
            self.ga.tracker_type,
            'web',
            '"{}" should be "web"'.format(self.ga.tracker_type),
        )

    def test_11_false_debug(self):
        self.assertFalse(self.ga.debug)

    def test_12_user_agent_is_sys_version(self):
        from sys import version as sys_version
        self.assertEqual(
            self.ga.user_agent,
            sys_version.replace('\n', ''),
            '"{}" should be "{}"'.format(self.ga.user_agent, sys_version),
        )

class CreateDefaultTrackerWithNonBooleanDebug(unittest.TestCase):
    """Tests for __init__() with non-boolean debug."""

    def __create_tracker_with_string_debug(self):
        self.ga = GoogleAnalytics(PROPERTY_ID, debug='False')

    def __create_tracker_with_int_debug(self):
        self.ga = GoogleAnalytics(PROPERTY_ID, debug=0)

    def test_01_raises_error_with_string_debug(self):
        self.assertRaises(ValueError, self.__create_tracker_with_string_debug)

    def test_02_raises_error_with_int_debug(self):
        self.assertRaises(ValueError, self.__create_tracker_with_int_debug)

class CreateDefaultTrackerWithUserId(unittest.TestCase):
    """Tests for __init__() with user_id."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID, user_id=ORIGINAL_USER_ID)

    def test_01_matches_user_id(self):
        self.assertEqual(
            self.ga.user_id,
            ORIGINAL_USER_ID,
            '"{}" should be "{}"'.format(self.ga.user_id, ORIGINAL_USER_ID),
        )

    def test_02_client_id(self):
        from hashlib import sha1
        sha1_hash = sha1()
        sha1_hash.update(ORIGINAL_USER_ID)
        hashed_user_id = sha1_hash.hexdigest()
        self.assertEqual(
            self.ga.client_id,
            hashed_user_id,
            '"{}" should be "{}"'.format(self.ga.client_id, hashed_user_id)
        )

class CreateDefaultTrackerWithNewUserId(unittest.TestCase):
    """Tests for __init__() with user_id and then a new one."""

    def setUp(self):
        self.ga = GoogleAnalytics(PROPERTY_ID, user_id=ORIGINAL_USER_ID)
        self.ga.set(
            user_id=REVISED_USER_ID,
        )

    def test_01_matches_user_id(self):
        self.assertEqual(
            self.ga.user_id,
            REVISED_USER_ID,
            '"{}" should be "{}"'.format(self.ga.user_id, REVISED_USER_ID),
        )

    def test_02_client_id(self):
        from hashlib import sha1
        sha1_hash = sha1()
        sha1_hash.update(ORIGINAL_USER_ID)
        hashed_user_id = sha1_hash.hexdigest()
        self.assertEqual(
            self.ga.client_id,
            hashed_user_id,
            '"{}" should be "{}"'.format(self.ga.client_id, hashed_user_id)
        )

def main():
    unittest.main()

if __name__ == '__main__':
    main()
