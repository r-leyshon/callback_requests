"""Tests for handle_calls module."""
import calendar
import datetime as dt

import pandas as pd
import pytest

from callbacks.handle_calls import CallHandler


def _get_next_weekday_as_datestring(required_day: str, time: str = "09:00"):
    d = required_day.title()
    now = dt.datetime.now()
    date_list = pd.date_range(start=now.today(), periods=7).tolist()
    required_date = [
        i for i in date_list if calendar.day_name[i.weekday()] == d
    ][0]
    required_date = required_date.isoformat().split("T")[0]
    required_datetime = required_date + "T" + time
    return required_datetime


@pytest.fixture(scope="function")
def _handler_fixture():
    return CallHandler()


class TestCallHandler:
    """Tests for CallHandler class."""

    def test_bad_date_raises(self, _handler_fixture):
        """Test that an invalid date raises."""
        handler = _handler_fixture
        with pytest.raises(
            ValueError,
            match=".*Did you use format: %Y-%m-%dT%H:%M",
        ):
            handler.request_callback("2025-01-32T25:60")

    def test_elapsed_callback_request_raises(self, _handler_fixture):
        """Test that a static date that has expired raises ValueError."""
        handler = _handler_fixture
        with pytest.raises(
            ValueError, match="2023-12-31 09:00:00 is in the past"
        ):
            handler.request_callback("2023-12-31T09:00"),
            "An elapsed callback request did not raise as expected"

    def test_callback_request_on_a_sunday_fails(self, _handler_fixture):
        """Test that requesting a callback on a Sunday fails.

        Date of the Sunday is dynamically generated with
        _get_next_weekday_as_datestring.
        """
        handler = _handler_fixture
        with pytest.raises(
            ValueError, match="Callbacks are unavailable on Sun"
        ):
            handler.request_callback(_get_next_weekday_as_datestring("Sunday"))

    def test_callback_request_far_into_future_fails(self, _handler_fixture):
        """Test that asking for a date far into the future fails."""
        handler = _handler_fixture
        with pytest.raises(
            ValueError,
            match=".*Cannot book callback more than 6 days into the future.",
        ):
            handler.request_callback("2050-01-01T09:00")
