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

    def test_elapsed_callback_request_raises(self, _handler_fixture):
        """Test that a static date that has expired raises ValueError."""
        handler = _handler_fixture
        with pytest.raises(
            ValueError, match="2023-12-31 09:00:00 is in the past"
        ):
            handler.request_callback("2023-12-31T09:00"),
            "An elapsed callback request did not raise as expected"


# handler.request_callback("2024-04-02T12:00") # passes
# handler.request_callback("2024-03-31T19:59") # not on sunday
# handler.request_callback("2024-03-27T13:11") # in the past

# handler.request_callback("2024-03-29T13:11") # passes
# handler.request_callback("2024-04-30T12:55") # more than 6 days into future


# test opening hours on a day
# handler.request_callback(_get_next_weekday_as_datestring("Sunday"))
# handler.request_callback(_get_next_weekday_as_datestring(
# "Thursday", time="23:59"))
# handler.request_callback(_get_next_weekday_as_datestring(
# "Monday", time="08:59"))
