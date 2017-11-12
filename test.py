# -*- coding: utf-8 -*-
"""Unit tests for google.analytics.measurement_protocol's GoogleAnalytics."""

import unittest

def main():
    suite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    main()
