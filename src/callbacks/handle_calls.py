"""Handle calls requesting callbacks."""

import calendar
import datetime as dt

import pandas as pd


class CallHandler:
    """Class handles request callbacks according to call centre rules.

    Parameters
    ----------
    now : dt.datetime
        Current datetime. Exposed to allow override for testing.

    Methods
    -------
    _standardise_datestring()
        Internal method for standardising user datestring.
    _is_during_accepted_window()
        Internal method for validating user-requested callback is within
        acceptable time window.
    _is_during_work_hours()
        Internal method for validating user-requested callback is within
        working hours.
    request_callback()
        Public method for requesting a callback appointment.

    Attributes
    ----------
    current_time : dt.datetime
        Datetime of query.
    callback_time : dt.datetime
        Datetime of requested callback.
    office_hours : dict
        Office hours with abbreviated day name as keys and list of float
        representation of start and finish hours. Use None for days that are
        not worked, by default {
            "Mon":[9.0, 18.0],
            "Tue":[9.0, 18.0],
            "Wed":[9.0, 18.0],
            "Thu":[9.0, 20.0],
            "Fri":[9.0, 20.0],
            "Sat":[9.0, 12.5],
            "Sun":[None, None],
            }

    """

    def __init__(self, now=dt.datetime.now()):
        self.current_time = now
        self.callback_time = now
        self.office_hours = {
            "Mon": [9.0, 18.0],
            "Tue": [9.0, 18.0],
            "Wed": [9.0, 18.0],
            "Thu": [9.0, 20.0],
            "Fri": [9.0, 20.0],
            "Sat": [9.0, 12.5],
            "Sun": [None, None],
        }

    def _standardise_datestring(
        self, user_datestring: str, form: str = "%Y-%m-%dT%H:%M"
    ) -> dt.datetime:
        """Ensure user has passed a valid datestring & converts to datetime.

        Parameters
        ----------
        user_datestring : str
            The datestring passed by the user.
        form : str, optional
            The expected date format. Must be a valid C-standard date code
            format compatible with datetime. See
            https://docs.python.org/3/library/datetime.html
            #strftime-and-strptime-format-codes for examples, by default
            "%Y-%m-%dT%H:%M"

        Returns
        -------
        dt.datetime
            Standardised datetime.

        Raises
        ------
        ValueError
            user_datestring is an invalid format or invalid date.

        """
        try:
            standard_date = dt.datetime.strptime(user_datestring, form)
        except ValueError:
            raise ValueError(
                f"Bad date: {user_datestring}\n Did you use format: {form}"
            )
        return standard_date

    def _is_during_accepted_window(
        self,
        standard_dt: dt.datetime,
        min_hours: float = 2.0,
        max_hours: float = 144.0,
    ) -> None:
        """Check if the requested callback is within the acceptable window.

        Ignores dates that are not working days as defined in the office_hours
        attribute.

        Parameters
        ----------
        standard_dt : dt.datetime
            The datetime representation of the user datestring.
        min_hours : float, optional
            Minimum number of hours required to elapse prior to scheduled
            callback, by default 2.0
        max_hours : float, optional
            Maximum number of hours allowed to schedule callback, by default
            144.0 (6 days).

        Returns
        -------
        None

        Raises
        ------
        ValueError
            Requested callback has elapsed.
        ValueError
            Requested callback is smaller than min_hours.
        ValueError
            Requested callback is greater than max_hours.

        """
        delta = standard_dt - self.current_time
        delta_secs = delta.total_seconds()
        if delta_secs < 0:
            raise ValueError(f"{standard_dt} is in the past")
        elif (delta_secs / 3600) < min_hours:
            raise ValueError(
                f"{standard_dt} is too soon. Cannot callback within 2 hours."
            )
        else:
            # determine the number of non-working days and disregard them
            this_date = self.current_time.today()
            date_list = [
                this_date + dt.timedelta(days=x) for x in range(delta.days)
            ]
            date_list = pd.date_range(
                start=self.current_time.today(), end=standard_dt
            ).tolist()
            # generalised to work with days that are None for start/finish time
            n_hols = sum(
                [
                    None
                    in self.office_hours[calendar.day_abbr[date.weekday()]]
                    for date in date_list
                ]
            )
            # subtract the number of non-working days from the total time delta
            delta_sec = delta_secs - n_hols / 86400  # s/day
            if delta_sec > max_hours * 3600:
                raise ValueError(
                    f"{standard_dt} is too late. Cannot book callback more"
                    f" than {int(max_hours/24)} days into the future."
                )
            else:
                return None

    def _is_during_work_hours(
        self,
        standard_dt: dt.datetime,
    ) -> None:
        """Check if the requested callback datetime is in office hours.

        Parameters
        ----------
        standard_dt : dt.datetime
            The datetime representation of the user datestring.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            Callback is requested on a non-working day.
        ValueError
            Callback is requested outside of office hours.

        """
        requested_day = calendar.day_abbr[standard_dt.weekday()]
        requested_time = float(standard_dt.hour + (standard_dt.minute / 60))
        requested_day_hours = self.office_hours[requested_day]
        if None in requested_day_hours:
            raise ValueError(f"Callbacks are unavailable on {requested_day}")
        else:
            if (requested_time < requested_day_hours[0]) or (
                requested_time >= requested_day_hours[-1]
            ):
                raise ValueError(
                    f"Office hours on {requested_day} : {requested_day_hours}"
                )
            else:
                return None

    def request_callback(self, datestring: str) -> None:
        """Handle a request for a callback appointment.

        Public method used to validate the user's callback appointment request
        against the specified rules.

        Parameters
        ----------
        datestring : str
            The datestring passed by the user, in "%Y-%m-%dT%H:%M" format.

        Returns
        -------
        standard_date
            Standardised datetime representation of user's requested datestring
            if eligible for a callback.

        Raises
        ------
        ValueError
            user_datestring is an invalid format or invalid date.
        ValueError
            Requested callback has elapsed.
        ValueError
            Requested callback is smaller than min_hours.
        ValueError
            Requested callback is greater than max_hours.
        ValueError
            Callback is requested on a non-working day.
        ValueError
            Callback is requested outside of office hours.

        """
        standard_date = self._standardise_datestring(datestring)
        self.current_time = dt.datetime.now()
        self.callback_time = standard_date
        self._is_during_accepted_window(standard_date)
        self._is_during_work_hours(standard_date)
        print(f"Your appointment is booked for {datestring}")
        return standard_date
