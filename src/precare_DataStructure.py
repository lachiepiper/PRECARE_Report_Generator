"""
precare_data.py
---------------
Dataclass representing one PRECARE activity report.

Designed to be filled piecemeal as values are calculated —
every field is Optional and defaults to None, so you can
assign fields one at a time as they become available:

    report = PrecareReport()
    report.patients_with_interventions_30d = 5
    report.patients_with_interventions_90d = 24
    ...

The three time periods are:
    _30d        Last 30 days
    _90d        Last 90 days
    _range      Custom date range (optional — may remain None)

Time fields that carry a range in the CSV are stored as three
separate fields:
    <name>              median value (decimal minutes)
    <name>_low          lower bound of range
    <name>_high         upper bound of range
"""

from __future__ import annotations
import csv
import io
import pandas as pd
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PrecareReport:

    # ── Optional date range label ────────────────────────────────────────────
    # e.g. "01/05/2022 - 29/05/2026"
    # Set this if the custom date range column is present.
    custom_dates_present: Optional[bool] = None
    date_range_label: Optional[str] = None

    # ════════════════════════════════════════════════════════════════════════
    # DISPATCH ACTIVITY
    # ════════════════════════════════════════════════════════════════════════

    # Number of patients with interventions
    patients_with_interventions_30d:    Optional[int]   = None
    patients_with_interventions_90d:    Optional[int]   = None
    patients_with_interventions_range:  Optional[int]   = None

    # Median time from dispatch to departure (decimal minutes)
    dispatch_to_departure_30d:          Optional[float] = None
    dispatch_to_departure_30d_low:      Optional[float] = None
    dispatch_to_departure_30d_high:     Optional[float] = None

    dispatch_to_departure_90d:          Optional[float] = None
    dispatch_to_departure_90d_low:      Optional[float] = None
    dispatch_to_departure_90d_high:     Optional[float] = None

    dispatch_to_departure_range:        Optional[float] = None
    dispatch_to_departure_range_low:    Optional[float] = None
    dispatch_to_departure_range_high:   Optional[float] = None

    # Median time from dispatch to arrival (decimal minutes)
    dispatch_to_arrival_30d:            Optional[float] = None
    dispatch_to_arrival_30d_low:        Optional[float] = None
    dispatch_to_arrival_30d_high:       Optional[float] = None

    dispatch_to_arrival_90d:            Optional[float] = None
    dispatch_to_arrival_90d_low:        Optional[float] = None
    dispatch_to_arrival_90d_high:       Optional[float] = None

    dispatch_to_arrival_range:          Optional[float] = None
    dispatch_to_arrival_range_low:      Optional[float] = None
    dispatch_to_arrival_range_high:     Optional[float] = None

    # Median time from 000 call to patient (decimal minutes)
    call_to_patient_30d:                Optional[float] = None
    call_to_patient_30d_low:            Optional[float] = None
    call_to_patient_30d_high:           Optional[float] = None

    call_to_patient_90d:                Optional[float] = None
    call_to_patient_90d_low:            Optional[float] = None
    call_to_patient_90d_high:           Optional[float] = None

    call_to_patient_range:              Optional[float] = None
    call_to_patient_range_low:          Optional[float] = None
    call_to_patient_range_high:         Optional[float] = None

    cases_attended_30d:                 Optional[int] = None
    cases_attended_90d:                 Optional[int] = None
    cases_attended_range:               Optional[int] = None

    total_non_arrest_30d:               Optional[int] = None
    total_non_arrest_90d:               Optional[int] = None
    total_non_arrest_range:             Optional[int] = None

    non_arrest_percent_30d:             Optional[float] = None
    non_arrest_percent_90d:             Optional[float] = None
    non_arrest_percent_range:           Optional[float] = None

    non_arrest_treatment_30d:           Optional[float] = None
    non_arrest_treatment_90d:           Optional[float] = None
    non_arrest_treatment_range:         Optional[float] = None

    successful_ECPR_count_30d:           Optional[float] = None
    successful_ECPR_count_90d:           Optional[float] = None
    successful_ECPR_count_range:         Optional[float] = None

    # ════════════════════════════════════════════════════════════════════════
    # CASE CLASSIFICATION
    # ════════════════════════════════════════════════════════════════════════

    # Number of times patient confirmed in cardiac arrest (count + %)
    cardiac_arrests_30d:                Optional[int]   = None
    cardiac_arrests_30d_pct:            Optional[float] = None

    cardiac_arrests_90d:                Optional[int]   = None
    cardiac_arrests_90d_pct:            Optional[float] = None

    cardiac_arrests_range:              Optional[int]   = None
    cardiac_arrests_range_pct:          Optional[float] = None

    # ════════════════════════════════════════════════════════════════════════
    # AEROMEDICAL INTERVENTIONS
    # ════════════════════════════════════════════════════════════════════════

    rsi_30d:                            Optional[int]   = None
    rsi_90d:                            Optional[int]   = None
    rsi_range:                          Optional[int]   = None

    thoracostomy_30d:                   Optional[int]   = None
    thoracostomy_90d:                   Optional[int]   = None
    thoracostomy_range:                 Optional[int]   = None

    fem_art_line_30d:                   Optional[int]   = None
    fem_art_line_90d:                   Optional[int]   = None
    fem_art_line_range:                 Optional[int]   = None

    radial_art_line_30d:                Optional[int]   = None
    radial_art_line_90d:                Optional[int]   = None
    radial_art_line_range:              Optional[int]   = None

    assisted_ett_30d:                   Optional[int]   = None
    assisted_ett_90d:                   Optional[int]   = None
    assisted_ett_range:                 Optional[int]   = None

    # PRECARE Access (IO / IV / Central)
    access_io_30d:                      Optional[int]   = None
    access_iv_30d:                      Optional[int]   = None
    access_central_30d:                 Optional[int]   = None

    access_io_90d:                      Optional[int]   = None
    access_iv_90d:                      Optional[int]   = None
    access_central_90d:                 Optional[int]   = None

    access_io_range:                    Optional[int]   = None
    access_iv_range:                    Optional[int]   = None
    access_central_range:               Optional[int]   = None

    echo_ultrasound_30d:                Optional[int]   = None
    echo_ultrasound_90d:                Optional[int]   = None
    echo_ultrasound_range:              Optional[int]   = None

    intra_arrest_toe_30d:               Optional[int]   = None
    intra_arrest_toe_90d:               Optional[int]   = None
    intra_arrest_toe_range:             Optional[int]   = None

    tte_30d:                            Optional[int]   = None
    tte_90d:                            Optional[int]   = None
    tte_range:                          Optional[int]   = None

    poc_abg_30d:                        Optional[int]   = None
    poc_abg_90d:                        Optional[int]   = None
    poc_abg_range:                      Optional[int]   = None

    # ════════════════════════════════════════════════════════════════════════
    # ARTERIAL LINES
    # ════════════════════════════════════════════════════════════════════════

    # Number of intra-arrest art line insertions
    art_line_intra_arrest_30d:          Optional[int]   = None
    art_line_intra_arrest_90d:          Optional[int]   = None
    art_line_intra_arrest_range:        Optional[int]   = None

    # Median time PRECARE arrival to art line transduced (decimal minutes)
    art_line_time_to_transduced_30d:        Optional[float] = None
    art_line_time_to_transduced_30d_low:    Optional[float] = None
    art_line_time_to_transduced_30d_high:   Optional[float] = None

    art_line_time_to_transduced_90d:        Optional[float] = None
    art_line_time_to_transduced_90d_low:    Optional[float] = None
    art_line_time_to_transduced_90d_high:   Optional[float] = None

    art_line_time_to_transduced_range:      Optional[float] = None
    art_line_time_to_transduced_range_low:  Optional[float] = None
    art_line_time_to_transduced_range_high: Optional[float] = None

    # Number of art lines inserted post ROSC
    art_line_post_rosc_30d:             Optional[int]   = None
    art_line_post_rosc_90d:             Optional[int]   = None
    art_line_post_rosc_range:           Optional[int]   = None

    # ════════════════════════════════════════════════════════════════════════
    # ROSC RATES
    # ════════════════════════════════════════════════════════════════════════

    # Number of patients who achieved ROSC at any time (numerator/denominator/%)
    rosc_any_num_30d:                   Optional[int]   = None
    rosc_any_den_30d:                   Optional[int]   = None
    rosc_any_pct_30d:                   Optional[float] = None

    rosc_any_num_90d:                   Optional[int]   = None
    rosc_any_den_90d:                   Optional[int]   = None
    rosc_any_pct_90d:                   Optional[float] = None

    rosc_any_num_range:                 Optional[int]   = None
    rosc_any_den_range:                 Optional[int]   = None
    rosc_any_pct_range:                 Optional[float] = None

    # Median time of arrest to ROSC (decimal minutes)
    arrest_to_rosc_30d:                 Optional[float] = None
    arrest_to_rosc_30d_low:             Optional[float] = None
    arrest_to_rosc_30d_high:            Optional[float] = None

    arrest_to_rosc_90d:                 Optional[float] = None
    arrest_to_rosc_90d_low:             Optional[float] = None
    arrest_to_rosc_90d_high:            Optional[float] = None

    arrest_to_rosc_range:               Optional[float] = None
    arrest_to_rosc_range_low:           Optional[float] = None
    arrest_to_rosc_range_high:          Optional[float] = None

    # Number of patients who achieved sustained ROSC >20 mins (numerator/denominator/%)
    rosc_sustained_num_30d:             Optional[int]   = None
    rosc_sustained_den_30d:             Optional[int]   = None
    rosc_sustained_pct_30d:             Optional[float] = None

    rosc_sustained_num_90d:             Optional[int]   = None
    rosc_sustained_den_90d:             Optional[int]   = None
    rosc_sustained_pct_90d:             Optional[float] = None

    rosc_sustained_num_range:           Optional[int]   = None
    rosc_sustained_den_range:           Optional[int]   = None
    rosc_sustained_pct_range:           Optional[float] = None

    # Sustained ROSC gained breakdown
    rosc_never_30d:                     Optional[int]   = None
    rosc_never_90d:                     Optional[int]   = None
    rosc_never_range:                   Optional[int]   = None

    rosc_before_precare_30d:            Optional[int]   = None
    rosc_before_precare_90d:            Optional[int]   = None
    rosc_before_precare_range:          Optional[int]   = None

    rosc_on_after_precare_30d:          Optional[int]   = None
    rosc_on_after_precare_90d:          Optional[int]   = None
    rosc_on_after_precare_range:        Optional[int]   = None

    # Median time from PRECARE arrival to ROSC (decimal minutes)
    precare_arrival_to_rosc_30d:        Optional[float] = None
    precare_arrival_to_rosc_30d_low:    Optional[float] = None
    precare_arrival_to_rosc_30d_high:   Optional[float] = None

    precare_arrival_to_rosc_90d:        Optional[float] = None
    precare_arrival_to_rosc_90d_low:    Optional[float] = None
    precare_arrival_to_rosc_90d_high:   Optional[float] = None

    precare_arrival_to_rosc_range:      Optional[float] = None
    precare_arrival_to_rosc_range_low:  Optional[float] = None
    precare_arrival_to_rosc_range_high: Optional[float] = None

    # ECMO cannulation (commenced / successful)
    ecmo_commenced_30d:                 Optional[int]   = None
    ecmo_successful_30d:                Optional[int]   = None

    ecmo_commenced_90d:                 Optional[int]   = None
    ecmo_successful_90d:                Optional[int]   = None

    ecmo_commenced_range:               Optional[int]   = None
    ecmo_successful_range:              Optional[int]   = None

    ROSC_on_Arrival_Hospital_30d:        Optional[int]   = None
    ROSC_on_Arrival_Hospital_90d:        Optional[int]   = None
    ROSC_on_Arrival_Hospital_range:      Optional[int]   = None
    # ════════════════════════════════════════════════════════════════════════
    # DISCHARGE DISPOSITION
    # ════════════════════════════════════════════════════════════════════════
    discharged_alive_30d:                 Optional[int]   = None
    discharged_alive_90d:                 Optional[int]   = None
    discharged_alive_range:               Optional[int]   = None
    # ════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ════════════════════════════════════════════════════════════════════════

    def has_date_range(self) -> bool:
        """Return True if the optional custom date range column was populated."""
        return self.date_range_label is not None

    def report_title(self) -> str:
        """Return a display title, including the date range label if available."""
        base = "PRECARE Activity Report"
        if self.has_date_range():
            return f"{base}  —  {self.date_range_label}"
        return base

    def rosc_any_pct_30d_calculated(self) -> Optional[float]:
        """Recalculate any-ROSC percentage from numerator/denominator."""
        if self.rosc_any_num_30d is None or self.rosc_any_den_30d in (None, 0):
            return None
        return self.rosc_any_num_30d / self.rosc_any_den_30d * 100

    def rosc_any_pct_90d_calculated(self) -> Optional[float]:
        """Recalculate any-ROSC percentage from numerator/denominator."""
        if self.rosc_any_num_90d is None or self.rosc_any_den_90d in (None, 0):
            return None
        return self.rosc_any_num_90d / self.rosc_any_den_90d * 100

    def rosc_any_pct_range_calculated(self) -> Optional[float]:
        """Recalculate any-ROSC percentage from numerator/denominator."""
        if self.rosc_any_num_range is None or self.rosc_any_den_range in (None, 0):
            return None
        return self.rosc_any_num_range / self.rosc_any_den_range * 100

    def rosc_sustained_pct_30d_calculated(self) -> Optional[float]:
        """Recalculate sustained-ROSC percentage from numerator/denominator."""
        if self.rosc_sustained_num_30d is None or self.rosc_sustained_den_30d in (None, 0):
            return None
        return self.rosc_sustained_num_30d / self.rosc_sustained_den_30d * 100

    def rosc_sustained_pct_90d_calculated(self) -> Optional[float]:
        """Recalculate sustained-ROSC percentage from numerator/denominator."""
        if self.rosc_sustained_num_90d is None or self.rosc_sustained_den_90d in (None, 0):
            return None
        return self.rosc_sustained_num_90d / self.rosc_sustained_den_90d * 100

    def rosc_sustained_pct_range_calculated(self) -> Optional[float]:
        """Recalculate sustained-ROSC percentage from numerator/denominator."""
        if self.rosc_sustained_num_range is None or self.rosc_sustained_den_range in (None, 0):
            return None
        return self.rosc_sustained_num_range / self.rosc_sustained_den_range * 100

    def to_min(self, mmss):
        m, s = map(int, mmss.split(":"))
        return m + s/60

    def to_mmss(self, time_str: str) -> str:
        if ":" in time_str:
            return time_str  # already in MM:SS format
        total_seconds = round(float(time_str) * 60)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def parse_time_to_decimal(self, time_str: str) -> float:
        """Convert a 'HH:MM:SS' or 'MM:SS' or 'M:SS' string to decimal minutes."""
        parts = time_str.strip().split(':')

        if len(parts) == 3:
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            total_minutes = hours * 60 + minutes + seconds / 60
        elif len(parts) == 2:
            minutes, seconds = int(parts[0]), int(parts[1])
            total_minutes = minutes + seconds / 60
        else:
            raise ValueError(f"Invalid time format: '{time_str}'. Expected 'HH:MM:SS', 'MM:SS', or 'M:SS'.")

        return total_minutes

    def parse_ecmo_ranges(self, ecmo_string: str) -> list[int]:
        """
        Parses a clinical data string formatted as 'A (B)'
        and returns a list of integers [A, B].
        """
        # Split the string at the opening parenthesis
        parts = ecmo_string.split('(')

        if len(parts) == 2:
            # Clean up whitespace and the closing parenthesis, then cast to integers
            primary_val = int(parts[0].strip())
            secondary_val = int(parts[1].replace(')', '').strip())

            return [primary_val, secondary_val]
        else:
            raise ValueError(f"Unrecognized data format: '{ecmo_string}'. Expected 'A (B)'.")

    def parse_time_ranges(self, input_str: str) -> list[float]:
        """
        Parse a string in the format "MM:SS (MM:SS - MM:SS)" or
        "HH:MM:SS (HH:MM:SS - HH:MM:SS)" into a list of decimal minute values
        [median, low, high]. Both formats can be mixed within the same string.
        Handles single-digit values (e.g. "9:30" or "09:30").
        Args:
            input_str: A string like "10:30 (9:00 - 12:15)"
                       or "1:10:30 (0:09:00 - 1:12:15)"
        Returns:
            A list [median, low, high] as decimal minutes.
        Raises:
            ValueError: If the string does not match the expected format.
        """
        if input_str == "0 (0 - 0)":
            return [0, 0, 0]

        # Each time token matches either HH:MM:SS or MM:SS
        time_token = r"\d{1,2}:\d{2}(?::\d{2})?"

        pattern = (
            r"^\s*"
            rf"({time_token})"           # median
            r"\s*\(\s*"
            rf"({time_token})"           # low
            r"\s*-\s*"
            rf"({time_token})"           # high
            r"\s*\)\s*$"
        )

        match = re.match(pattern, input_str)
        if not match:
            raise ValueError(
                f"Input '{input_str}' does not match expected format "
                f"'MM:SS (MM:SS - MM:SS)' or 'HH:MM:SS (HH:MM:SS - HH:MM:SS)'."
            )

        median_str, low_str, high_str = match.group(1), match.group(2), match.group(3)

        median = self.parse_time_to_decimal(median_str)
        low    = self.parse_time_to_decimal(low_str)
        high   = self.parse_time_to_decimal(high_str)

        return [median, low, high]


    def parse_percentages(self, string):
        """takes a string in the form X (Y.00%) and returns string X and float Y
        Note: depending on input, output X could be a single digit string, or a fraction string eg "6/8".
            This is not handled by the function
        """
        x,y = map(str, string.split(" "))
        y = y.strip("(,)")[0:-1]    #strip parentheses and % chars
        return [x, float(y)]

    def parse_access(self, string):
        string = string[1:-1] #remove paretheses
        IO,IV,Central = map(int, string.split("/"))
        return [IO, IV, Central]

    # ════════════════════════════════════════════════════════════════════════
    # SETTERS
    # ════════════════════════════════════════════════════════════════════════
    def set_dispatchActivity(self, df: pd.DataFrame):
        """
        sets data from a dataframe with format:
                "Dispatch activity" : ["Number of patients with interventions",
                "Median time from dispatch to departure (range)",
                "Median time from dispatch to arrival (range)",
                "Median time from 000 call to patient (range)"],
                "Last 30 Days": list,
                "Last 90 Days": list,
                optional: "From dateX to dateY": list
        presence of optional dates indicated by arg customdates
        """
        if self.custom_dates_present:
            self.patients_with_interventions_range = int(df.iloc[0, 3])

            time_list = self.parse_time_ranges(df.iloc[1, 3])
            self.dispatch_to_departure_range = time_list[0]
            self.dispatch_to_departure_range_low = time_list[1]
            self.dispatch_to_departure_range_high = time_list[2]

            time_list = self.parse_time_ranges(df.iloc[2, 3])
            self.dispatch_to_arrival_range = time_list[0]
            self.dispatch_to_arrival_range_low = time_list[1]
            self.dispatch_to_arrival_range_high = time_list[2]

            time_list = self.parse_time_ranges(df.iloc[3, 3])
            self.call_to_patient_range = time_list[0]
            self.call_to_patient_range_low = time_list[1]
            self.call_to_patient_range_high = time_list[2]

            self.cases_attended_range = df.iloc[4, 3]

            list = self.parse_percentages(df.iloc[5, 3])
            fraction_lst = list[0].split("/")
            self.non_arrest_treatment_range = fraction_lst[0]
            self.total_non_arrest_range = fraction_lst[1]
            self.non_arrest_percent_range = list[1]
            self.successful_ECPR_count_range = df.iloc[6, 3]

        month_list = df["Last 30 Days"]
        three_month_list = df["Last 90 Days"]
        # Number of patients with interventions
        self.patients_with_interventions_30d = int(month_list[0])
        self.patients_with_interventions_90d = int(three_month_list[0])

        # Median time from dispatch to departure (decimal minutes)
        time_list = self.parse_time_ranges(month_list[1])
        self.dispatch_to_departure_30d = time_list[0]
        self.dispatch_to_departure_30d_low = time_list[1]
        self.dispatch_to_departure_30d_high = time_list[2]

        time_list = self.parse_time_ranges(three_month_list[1])
        self.dispatch_to_departure_90d = time_list[0]
        self.dispatch_to_departure_90d_low = time_list[1]
        self.dispatch_to_departure_90d_high = time_list[2]

        # Median time from dispatch to arrival (decimal minutes)
        time_list = self.parse_time_ranges(month_list[2])
        self.dispatch_to_arrival_30d = time_list[0]
        self.dispatch_to_arrival_30d_low = time_list[1]
        self.dispatch_to_arrival_30d_high = time_list[2]

        time_list = self.parse_time_ranges(three_month_list[2])
        self.dispatch_to_arrival_90d = time_list[0]
        self.dispatch_to_arrival_90d_low = time_list[1]
        self.dispatch_to_arrival_90d_high = time_list[2]

        # Median time from 000 call to patient (decimal minutes)
        time_list = self.parse_time_ranges(month_list[3])
        self.call_to_patient_30d = time_list[0]
        self.call_to_patient_30d_low = time_list[1]
        self.call_to_patient_30d_high = time_list[2]

        time_list = self.parse_time_ranges(three_month_list[3])
        self.call_to_patient_90d = time_list[0]
        self.call_to_patient_90d_low = time_list[1]
        self.call_to_patient_90d_high = time_list[2]

        self.cases_attended_30d = month_list[4]
        self.cases_attended_90d = three_month_list[4]

        list = self.parse_percentages(month_list[5])
        fraction_lst = list[0].split("/")
        self.non_arrest_treatment_30d =fraction_lst[0]
        self.total_non_arrest_30d =  fraction_lst[1]
        self.non_arrest_percent_30d = list[1]

        list = self.parse_percentages(three_month_list[5])
        fraction_lst = list[0].split("/")
        self.non_arrest_treatment_90d = fraction_lst[0]
        self.total_non_arrest_90d =  fraction_lst[1]
        self.non_arrest_percent_90d = list[1]

        self.successful_ECPR_count_30d = month_list[6]
        self.successful_ECPR_count_90d = three_month_list[6]

    def set_CaseClassification(self, df: pd.dataframe):
        """sets data from a dataframe with Format:
            "Case Classification":["Number of times patient was confirmed in cardiac arrest (% cases where interventions performed)"],
            "Last 30 Days": month_data,
            "Last 90 Days": three_month_data
            Optional: Custom date data
        """
        if self.custom_dates_present:
            self.cardiac_arrests_range = int(self.parse_percentages(df.iloc[0, 3])[0])
            self.cardiac_arrests_range_pct = self.parse_percentages(df.iloc[0, 3])[1]

        month_list = df["Last 30 Days"]
        three_month_list = df["Last 90 Days"]

        self.cardiac_arrests_30d = int(self.parse_percentages(month_list[0])[0])
        self.cardiac_arrests_30d_pct = self.parse_percentages(month_list[0])[1]

        self.cardiac_arrests_90d = int(self.parse_percentages(three_month_list[0])[0])
        self.cardiac_arrests_90d_pct = self.parse_percentages(three_month_list[0])[1]

    def set_Interventions(self, df:pd.dataframe):
        """ Sets data based on a dataframe of format:
                "Aeromedical Interventions performed":["RSI", "Thoracostomy",
                "Fem Art Line", "Radial Art line",
                "Assisted ETT", "PRECARE Access ( IO / IV / Central)",
                "Echo / Ultrasound", "Intra-arrest TOE",
                "TTE", "POC testing ABG"],
                "Last 30 Days": month_list,
                "Last 90 Days": three_month_list
                Optional: custom date data
        """

        if self.custom_dates_present:
            self.rsi_range = int(df.iloc[0, 3])
            self.thoracostomy_range = int(df.iloc[1, 3])
            self.fem_art_line_range = int(df.iloc[2, 3])
            self.radial_art_line_range = int(df.iloc[3, 3])
            self.assisted_ett_range = int(df.iloc[4, 3])

            access = self.parse_access(df.iloc[5, 3])

            self.access_io_range = access[0]
            self.access_iv_range = access[1]
            self.access_central_range = access[2]

            self.echo_ultrasound_range = int(df.iloc[6, 3])
            self.intra_arrest_toe_range = int(df.iloc[7, 3])
            self.tte_range = int(df.iloc[8, 3])
            self.poc_abg_range = int(df.iloc[9, 3])

        month_list = df["Last 30 Days"]
        three_month_list = df["Last 90 Days"]

        self.rsi_30d = int(month_list[0])
        self.rsi_90d = int(three_month_list[0])

        self.thoracostomy_30d = int(month_list[1])
        self.thoracostomy_90d = int(three_month_list[1])

        self.fem_art_line_30d = int(month_list[2])
        self.fem_art_line_90d = int(three_month_list[2])

        self.radial_art_line_30d = int(month_list[3])
        self.radial_art_line_90d = int(three_month_list[3])

        self.assisted_ett_30d = int(month_list[4])
        self.assisted_ett_90d = int(three_month_list[4])

        # PRECARE Access (IO / IV / Central)
        access = self.parse_access(month_list[5])
        self.access_io_30d = access[0]
        self.access_iv_30d = access[1]
        self.access_central_30d = access[2]

        access = self.parse_access(three_month_list[5])
        self.access_io_90d = access[0]
        self.access_iv_90d = access[1]
        self.access_central_90d = access[2]

        self.echo_ultrasound_30d = int(month_list[6])
        self.echo_ultrasound_90d = int(three_month_list[6])

        self.intra_arrest_toe_30d = int(month_list[7])
        self.intra_arrest_toe_90d = int(three_month_list[7])

        self.tte_30d = int(month_list[8])
        self.tte_90d = int(three_month_list[8])

        self.poc_abg_30d = int(month_list[9])
        self.poc_abg_90d = int(three_month_list[9])

    def set_Artline_data(self, df:pd.dataframe):
        """
        Sets data based on a dataframe of format:
            "Arterial Lines":["Number of intra-arrest Art line insertions",
            "Median time PRECARE arrival to art line transduced (range)",
            "Number of art lines inserted post ROSC"],
            "Last 30 Days": month_list,
            "Last 90 Days": three_month_list
            Optional: custom date data
        """
        if self.custom_dates_present:
            self.art_line_intra_arrest_range = int(df.iloc[0,3])

            time_list = self.parse_time_ranges(df.iloc[1,3])
            self.art_line_time_to_transduced_range = time_list[0]
            self.art_line_time_to_transduced_range_low = time_list[1]
            self.art_line_time_to_transduced_range_high = time_list[2]
            self.art_line_post_rosc_range = int(df.iloc[2,3])

        month_list = df["Last 30 Days"]
        three_month_list = df["Last 90 Days"]

        # Number of intra-arrest art line insertions
        self.art_line_intra_arrest_30d = int(month_list[0])
        self.art_line_intra_arrest_90d = int(three_month_list[0])

        # Median time PRECARE arrival to art line transduced (decimal minutes)
        time_list = self.parse_time_ranges(month_list[1])
        self.art_line_time_to_transduced_30d = time_list[0]
        self.art_line_time_to_transduced_30d_low = time_list[1]
        self.art_line_time_to_transduced_30d_high = time_list[2]

        time_list = self.parse_time_ranges(three_month_list[1])
        self.art_line_time_to_transduced_90d = time_list[0]
        self.art_line_time_to_transduced_90d_low = time_list[1]
        self.art_line_time_to_transduced_90d_high = time_list[2]

        # Number of art lines inserted post ROSC
        self.art_line_post_rosc_30d = int(month_list[2])
        self.art_line_post_rosc_90d = int(three_month_list[2])

    def set_ROSC_rates(self, df: pd.dataframe):
        """Sets ROSC rate data based on a dataframe of format:
                "ROSC Rates":"Number of patients who achieved ROSC at any time",
                "Median time of arrest to time of ROSC (range)",
                "Number of patients who achieved sustained ROSC >20mins",
                "Sustained ROSC gained:	never",
                "			before PRECARE arrival",
                "			on/after PRECARE arrival",
                "			Missing data",
                "Median time from PRECARE arrival to ROSC (range)",
                "ECMO cannulation commenced (number successful cannulations)"],
                "Last 30 Days" : month_list,
                "Last 90 Days": three_month_list
                Optional: custom date data
        """

        def parse_integer_ranges(string: str) -> list[int]:
            """
            Parse a string in the format "X (Y - Z)" and return [X, Y, Z] as integers.

            Example: "24 (10 - 38)" → [24, 10, 38]
            """
            string = string.strip()
            x, rest = string.split(" (")
            y, z    = rest.rstrip(")").split(" - ")
            return [int(x), int(y), int(z)]

        def parse_ecmo_ranges(string):
            #get claude to make this
            string = string.strip()
            x, rest  = string.split(" (")
            y = rest.rstrip(")")
            return [int(x), int(y)]

        if self.custom_dates_present:
            num_list = self.parse_percentages(df.iloc[0,3])
            self.rosc_any_num_range = int(num_list[0].split("/")[0])
            self.rosc_any_den_range = int(num_list[0].split("/")[1])
            self.rosc_any_pct_range = num_list[1]

            time_list = self.parse_time_ranges(df.iloc[1,3])
            self.arrest_to_rosc_range = time_list[0]
            self.arrest_to_rosc_range_low = time_list[1]
            self.arrest_to_rosc_range_high = time_list[2]

            num_list = self.parse_percentages(df.iloc[2,3])
            self.rosc_sustained_num_range = int(num_list[0].split("/")[0])
            self.rosc_sustained_den_range = int(num_list[0].split("/")[1])
            self.rosc_sustained_pct_range = num_list[1]

            self.rosc_never_range = int(df.iloc[3,3])

            self.rosc_before_precare_range = int(df.iloc[4,3])
            self.rosc_on_after_precare_range = int(df.iloc[5,3])

            list = self.parse_time_ranges(df.iloc[7,3])
            self.precare_arrival_to_rosc_range = list[0]
            self.precare_arrival_to_rosc_range_low = list[1]
            self.precare_arrival_to_rosc_range_high = list[2]

            list = self.parse_ecmo_ranges(df.iloc[8,3])
            self.ecmo_commenced_range = list[0]
            self.ecmo_successful_range = list[1]

            self.ROSC_on_Arrival_Hospital = df.iloc[9,3]

        month_list = df["Last 30 Days"]
        three_month_list = df["Last 90 Days"]

        # Number of patients who achieved ROSC at any time (numerator/denominator/%)
        num_list = self.parse_percentages(month_list[0])
        self.rosc_any_num_30d = int(num_list[0].split("/")[0])
        self.rosc_any_den_30d = int(num_list[0].split("/")[1])
        self.rosc_any_pct_30d = num_list[1]

        num_list = self.parse_percentages(three_month_list[0])
        self.rosc_any_num_90d = int(num_list[0].split("/")[0])
        self.rosc_any_den_90d = int(num_list[0].split("/")[1])
        self.rosc_any_pct_90d = num_list[1]

        # Median time of arrest to ROSC (decimal minutes)
        time_list = self.parse_time_ranges(month_list[1])
        self.arrest_to_rosc_30d = time_list[0]
        self.arrest_to_rosc_30d_low = time_list[1]
        self.arrest_to_rosc_30d_high = time_list[2]

        time_list = self.parse_time_ranges(three_month_list[1])
        self.arrest_to_rosc_90d = time_list[0]
        self.arrest_to_rosc_90d_low = time_list[1]
        self.arrest_to_rosc_90d_high = time_list[2]

        # Number of patients who achieved sustained ROSC >20 mins (numerator/denominator/%)
        num_list = self.parse_percentages(month_list[2])
        self.rosc_sustained_num_30d = int(num_list[0].split("/")[0])
        self.rosc_sustained_den_30d = int(num_list[0].split("/")[1])
        self.rosc_sustained_pct_30d = num_list[1]

        num_list = self.parse_percentages(three_month_list[2])
        self.rosc_sustained_num_90d = int(num_list[0].split("/")[0])
        self.rosc_sustained_den_90d = int(num_list[0].split("/")[1])
        self.rosc_sustained_pct_90d = num_list[1]


        # Sustained ROSC gained breakdown
        self.rosc_never_30d = int(month_list[3])
        self.rosc_never_90d = int(three_month_list[3])

        self.rosc_before_precare_30d = int(month_list[4])
        self.rosc_before_precare_90d = int(three_month_list[4])

        self.rosc_on_after_precare_30d = int(month_list[5])
        self.rosc_on_after_precare_90d = int(three_month_list[5])

        # Median time from PRECARE arrival to ROSC (decimal minutes)
        list = self.parse_time_ranges(month_list[7])
        self.precare_arrival_to_rosc_30d = list[0]
        self.precare_arrival_to_rosc_30d_low = list[1]
        self.precare_arrival_to_rosc_30d_high = list[2]

        list = self.parse_time_ranges(three_month_list[7])
        self.precare_arrival_to_rosc_90d = list[0]
        self.precare_arrival_to_rosc_90d_low = list[1]
        self.precare_arrival_to_rosc_90d_high = list[2]

        # ECMO cannulation (commenced / successful)
        list = self.parse_ecmo_ranges(month_list[8])
        self.ecmo_commenced_30d = list[0]
        self.ecmo_successful_30d = list[1]

        list = self.parse_ecmo_ranges(three_month_list[8])
        self.ecmo_commenced_90d = list[0]
        self.ecmo_successful_90d = list[1]

        self.ROSC_on_Arrival_Hospital = month_list[9]
        self.ROSC_on_Arrival_Hospital = three_month_list[9]

    def set_DischargeStatus(self, df:pd.dataframe):
        if self.custom_dates_present:
            self.discharged_alive_range =int(df.iloc[0,3])

        month_list = df["Last 30 Days"]
        three_month_list = df["Last 90 Days"]
        self.discharged_alive_30d = month_list[0]
        self.discharged_alive_90d = three_month_list[0]


    # ════════════════════════════════════════════════════════════════════════
    # CSV EXPORT
    # ════════════════════════════════════════════════════════════════════════

    def to_csv(self, path: Optional[str] = None) -> str:
        """
        Serialise the report back to a CSV matching the original format.

        Each row is:
            Description | Last 30 Days | Last 90 Days | <date range label> (optional)

        Time values stored as decimal minutes are converted back to MM:SS strings.
        Compound values (fractions, counts with %, access tuples, ECMO) are
        reassembled into the same format as the original CSV.

        Parameters
        ----------
        path : str, optional
            If provided, the CSV is written to this file path in addition to
            being returned as a string.

        Returns
        -------
        str
            The full CSV content as a string.
        """

        # ── Formatting helpers ────────────────────────────────────────────────

        def fmt_time(minutes: Optional[float]) -> str:
            """Convert decimal minutes back to MM:SS string, e.g. 8.5 → '08:30'."""
            if minutes is None:
                return ""
            total_seconds = round(minutes * 60)
            m, s = divmod(total_seconds, 60)
            return f"{m:02d}:{s:02d}"

        def fmt_time_with_range(median: Optional[float],
                                low: Optional[float],
                                high: Optional[float]) -> str:
            """Reassemble 'MM:SS (MM:SS - MM:SS)' from three decimal-minute values."""
            if median is None:
                return ""
            med_str = fmt_time(median)
            if low is None or high is None:
                return med_str
            return f"{med_str} ({fmt_time(low)} - {fmt_time(high)})"

        def fmt_float_with_range(median: Optional[float],
                                low: Optional[float],
                                high: Optional[float]) -> str:
            """Reassemble 'X (Y- Z)' from three float values."""
            if median is None:
                return ""
            if low is None or high is None:
                return med_str
            return f"{median} ({low} - {high})"


        def fmt_count_pct(count: Optional[int], pct: Optional[float]) -> str:
            """Reassemble 'N (PP.PP%)' format."""
            if count is None:
                return ""
            if pct is None:
                return str(count)
            return f"{count} ({pct:.2f}%)"

        def fmt_rosc_fraction(num: Optional[int],
                              den: Optional[int],
                              pct: Optional[float]) -> str:
            """Reassemble 'N/D PP.PP%' format."""
            if num is None or den is None:
                return ""
            if pct is None:
                return f"{num}/{den}"
            return f"{num}/{den} ({pct:.2f}%)"

        def fmt_access(io: Optional[int],
                       iv: Optional[int],
                       central: Optional[int]) -> str:
            """Reassemble '(IO / IV / Central)' format."""
            if io is None and iv is None and central is None:
                return ""
            io_str      = str(io)      if io      is not None else "?"
            iv_str      = str(iv)      if iv      is not None else "?"
            central_str = str(central) if central is not None else "?"
            return f"({io_str} / {iv_str} / {central_str})"

        def fmt_ecmo(commenced: Optional[int], successful: Optional[int]) -> str:
            """Reassemble 'N (S)' format."""
            if commenced is None:
                return ""
            if successful is None:
                return str(commenced)
            return f"{commenced} ({successful})"

        def fmt_int(val: Optional[int]) -> str:
            return str(val) if val is not None else ""

        # ── Column headers ────────────────────────────────────────────────────
        # Use custom_dates_present as the single source of truth for whether
        # the range column should appear. Fall back to date_range_label as the
        # column header text, or a generic label if no label was set.
        include_range = bool(self.custom_dates_present)
        col_range = self.date_range_label if self.date_range_label else "Custom Date Range"

        def row(description, v30, v90, vrange=None):
            """Build one CSV row, including the range column only if custom_dates_present."""
            r = [description, v30, v90]
            if include_range:
                r.append(vrange if vrange is not None else "")
            return r

        # ── Build rows ────────────────────────────────────────────────────────

        rows = []

        # ── Dispatch activity heading ─────────────────────────────────────────
        rows.append(row("Dispatch activity", "Last 30 Days", "Last 90 Days", col_range))

        rows.append(row(
            "Number of patients with interventions",
            fmt_int(self.patients_with_interventions_30d),
            fmt_int(self.patients_with_interventions_90d),
            fmt_int(self.patients_with_interventions_range),
        ))

        rows.append(row(
            "Median time from dispatch to departure (range)",
            fmt_time_with_range(self.dispatch_to_departure_30d,
                                self.dispatch_to_departure_30d_low,
                                self.dispatch_to_departure_30d_high),
            fmt_time_with_range(self.dispatch_to_departure_90d,
                                self.dispatch_to_departure_90d_low,
                                self.dispatch_to_departure_90d_high),
            fmt_time_with_range(self.dispatch_to_departure_range,
                                self.dispatch_to_departure_range_low,
                                self.dispatch_to_departure_range_high),
        ))

        rows.append(row(
            "Median time from dispatch to arrival (range)",
            fmt_time_with_range(self.dispatch_to_arrival_30d,
                                self.dispatch_to_arrival_30d_low,
                                self.dispatch_to_arrival_30d_high),
            fmt_time_with_range(self.dispatch_to_arrival_90d,
                                self.dispatch_to_arrival_90d_low,
                                self.dispatch_to_arrival_90d_high),
            fmt_time_with_range(self.dispatch_to_arrival_range,
                                self.dispatch_to_arrival_range_low,
                                self.dispatch_to_arrival_range_high),
        ))

        rows.append(row(
            "Median time from 000 call to patient (range)",
            fmt_time_with_range(self.call_to_patient_30d,
                                self.call_to_patient_30d_low,
                                self.call_to_patient_30d_high),
            fmt_time_with_range(self.call_to_patient_90d,
                                self.call_to_patient_90d_low,
                                self.call_to_patient_90d_high),
            fmt_time_with_range(self.call_to_patient_range,
                                self.call_to_patient_range_low,
                                self.call_to_patient_range_high),
        ))

        # ── Case classification heading ───────────────────────────────────────
        rows.append(row("Case Classification", "Last 30 Days", "Last 90 Days", col_range))

        rows.append(row(
            "Number of times patient was confirmed in cardiac arrest "
            "(% cases where interventions performed)",
            fmt_count_pct(self.cardiac_arrests_30d, self.cardiac_arrests_30d_pct),
            fmt_count_pct(self.cardiac_arrests_90d, self.cardiac_arrests_90d_pct),
            fmt_count_pct(self.cardiac_arrests_range, self.cardiac_arrests_range_pct),
        ))

        # ── Aeromedical interventions heading ─────────────────────────────────
        rows.append(row("Aeromedical Interventions performed", "Last 30 Days", "Last 90 Days", col_range))

        rows.append(row("RSI",
            fmt_int(self.rsi_30d), fmt_int(self.rsi_90d), fmt_int(self.rsi_range)))

        rows.append(row("Thoracostomy",
            fmt_int(self.thoracostomy_30d), fmt_int(self.thoracostomy_90d),
            fmt_int(self.thoracostomy_range)))

        rows.append(row("Fem Art Line",
            fmt_int(self.fem_art_line_30d), fmt_int(self.fem_art_line_90d),
            fmt_int(self.fem_art_line_range)))

        rows.append(row("Radial Art line",
            fmt_int(self.radial_art_line_30d), fmt_int(self.radial_art_line_90d),
            fmt_int(self.radial_art_line_range)))

        rows.append(row("Assisted ETT",
            fmt_int(self.assisted_ett_30d), fmt_int(self.assisted_ett_90d),
            fmt_int(self.assisted_ett_range)))

        rows.append(row(
            "PRECARE Access ( IO / IV / Central)",
            fmt_access(self.access_io_30d, self.access_iv_30d, self.access_central_30d),
            fmt_access(self.access_io_90d, self.access_iv_90d, self.access_central_90d),
            fmt_access(self.access_io_range, self.access_iv_range, self.access_central_range),
        ))

        rows.append(row("Echo / Ultrasound",
            fmt_int(self.echo_ultrasound_30d), fmt_int(self.echo_ultrasound_90d),
            fmt_int(self.echo_ultrasound_range)))

        rows.append(row("Intra-arrest TOE",
            fmt_int(self.intra_arrest_toe_30d), fmt_int(self.intra_arrest_toe_90d),
            fmt_int(self.intra_arrest_toe_range)))

        rows.append(row("TTE",
            fmt_int(self.tte_30d), fmt_int(self.tte_90d), fmt_int(self.tte_range)))

        rows.append(row("POC testing ABG",
            fmt_int(self.poc_abg_30d), fmt_int(self.poc_abg_90d),
            fmt_int(self.poc_abg_range)))

        # ── Arterial lines heading ────────────────────────────────────────────
        rows.append(row("Arterial Lines", "Last 30 Days", "Last 90 Days", col_range))

        rows.append(row(
            "Number of intra-arrest Art line insertions",
            fmt_int(self.art_line_intra_arrest_30d),
            fmt_int(self.art_line_intra_arrest_90d),
            fmt_int(self.art_line_intra_arrest_range),
        ))

        rows.append(row(
            "Median time PRECARE arrival to art line transduced (range)",
            fmt_time_with_range(self.art_line_time_to_transduced_30d,
                                self.art_line_time_to_transduced_30d_low,
                                self.art_line_time_to_transduced_30d_high),
            fmt_time_with_range(self.art_line_time_to_transduced_90d,
                                self.art_line_time_to_transduced_90d_low,
                                self.art_line_time_to_transduced_90d_high),
            fmt_time_with_range(self.art_line_time_to_transduced_range,
                                self.art_line_time_to_transduced_range_low,
                                self.art_line_time_to_transduced_range_high),
        ))

        rows.append(row(
            "Number of art lines inserted post ROSC",
            fmt_int(self.art_line_post_rosc_30d),
            fmt_int(self.art_line_post_rosc_90d),
            fmt_int(self.art_line_post_rosc_range),
        ))

        # ── ROSC rates heading ────────────────────────────────────────────────
        rows.append(row("ROSC Rates", "Last 30 Days", "Last 90 Days", col_range))

        rows.append(row(
            "Number of patients who achieved ROSC at any time",
            fmt_rosc_fraction(self.rosc_any_num_30d, self.rosc_any_den_30d,
                              self.rosc_any_pct_30d),
            fmt_rosc_fraction(self.rosc_any_num_90d, self.rosc_any_den_90d,
                              self.rosc_any_pct_90d),
            fmt_rosc_fraction(self.rosc_any_num_range, self.rosc_any_den_range,
                              self.rosc_any_pct_range),
        ))

        rows.append(row(
            "Median time of arrest to time of ROSC (range)",
            fmt_time_with_range(self.arrest_to_rosc_30d,
                                self.arrest_to_rosc_30d_low,
                                self.arrest_to_rosc_30d_high),
            fmt_time_with_range(self.arrest_to_rosc_90d,
                                self.arrest_to_rosc_90d_low,
                                self.arrest_to_rosc_90d_high),
            fmt_time_with_range(self.arrest_to_rosc_range,
                                self.arrest_to_rosc_range_low,
                                self.arrest_to_rosc_range_high),
        ))

        rows.append(row(
            "Number of patients who achieved sustained ROSC >20mins",
            fmt_rosc_fraction(self.rosc_sustained_num_30d, self.rosc_sustained_den_30d,
                              self.rosc_sustained_pct_30d),
            fmt_rosc_fraction(self.rosc_sustained_num_90d, self.rosc_sustained_den_90d,
                              self.rosc_sustained_pct_90d),
            fmt_rosc_fraction(self.rosc_sustained_num_range, self.rosc_sustained_den_range,
                              self.rosc_sustained_pct_range),
        ))

        rows.append(row(
            "Sustained ROSC gained:\tnever",
            fmt_int(self.rosc_never_30d),
            fmt_int(self.rosc_never_90d),
            fmt_int(self.rosc_never_range),
        ))

        rows.append(row(
            "\t\t\tbefore PRECARE arrival",
            fmt_int(self.rosc_before_precare_30d),
            fmt_int(self.rosc_before_precare_90d),
            fmt_int(self.rosc_before_precare_range),
        ))

        rows.append(row(
            "\t\t\ton/after PRECARE arrival",
            fmt_int(self.rosc_on_after_precare_30d),
            fmt_int(self.rosc_on_after_precare_90d),
            fmt_int(self.rosc_on_after_precare_range),
        ))

        rows.append(row(
            "\t\t\tMissing data",
            "???", "???", "???",
        ))

        rows.append(row(
            "Median time from PRECARE arrival to ROSC (range)",
            fmt_float_with_range(self.precare_arrival_to_rosc_30d,
                                self.precare_arrival_to_rosc_30d_low,
                                self.precare_arrival_to_rosc_30d_high),
            fmt_float_with_range(self.precare_arrival_to_rosc_90d,
                                self.precare_arrival_to_rosc_90d_low,
                                self.precare_arrival_to_rosc_90d_high),
            fmt_float_with_range(self.precare_arrival_to_rosc_range,
                                self.precare_arrival_to_rosc_range_low,
                                self.precare_arrival_to_rosc_range_high),
        ))

        rows.append(row(
            "ECMO cannulation commenced (number successful cannulations)",
            fmt_ecmo(self.ecmo_commenced_30d, self.ecmo_successful_30d),
            fmt_ecmo(self.ecmo_commenced_90d, self.ecmo_successful_90d),
            fmt_ecmo(self.ecmo_commenced_range, self.ecmo_successful_range),
        ))

        # ── Write to string buffer ────────────────────────────────────────────
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerows(rows)
        csv_string = buffer.getvalue()

        # ── Optionally write to file ──────────────────────────────────────────
        if path is not None:
            with open(path, "w", newline="", encoding="utf-8") as f:
                f.write(csv_string)

        return csv_string

    @classmethod
    def factory(cls, custom_dates: bool = False, date_range_label: Optional[str] = None) -> "PrecareReport":
        """
        Create a new empty PrecareReport.

        Parameters
        ----------
        custom_dates : bool
            Set to True if a custom date range will be populated.
            Controls whether to_csv() emits the range column.
        date_range_label : str, optional
            Human-readable label for the date range column header,
            e.g. "01/05/2022 - 29/05/2026". Only used when custom_dates=True.
        """
        instance = cls(
            custom_dates_present=custom_dates,
            date_range_label=date_range_label if custom_dates else None,
                )
        return instance
