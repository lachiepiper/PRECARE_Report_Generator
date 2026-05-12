import pandas as pd
from datetime import datetime



def dispatchActivity(date_from, date_to, df):
    """
    Within the date range set by args date_from and date_to, returns a 4 element
    list consiting of:
    [ Number of patients with interventions,
    Median time from dispatch to departure,
    Median time from dispatch to arrival,
    Median time from 000 call to patient
    ]
    by iterating through given dataframe
    """
    #Number of patients with interventions
    total_interventions = 0
    time_list_dispatchToArrival = []
    time_list_dispatchToDeparture = []
    time_list_000CallToArrival = []
    for index, row in df.iterrows():
        #handle empty date times
        if pd.isna(row['date_time_incident']):
            #take the earliest time, either time of incidence or, if empty, time of dispatch
            first_contact_time = row['dispatch_date_time']
            date = parse_date_and_time(row['dispatch_date_time'])[0]

        else:
            first_contact_time = row['date_time_incident']
            date = parse_date_and_time(str(row['date_time_incident']))[0]
            dateObject = datetime.strptime(date, "%Y-%m-%d")

        #collect data from within relevent dates
        if (dateObject.date() > date_from) and (dateObject.date() < date_to):
            #Number of patients with interventions
            total_interventions += checkInterventions(row)[0]
            # unsure how to calculate dispatch to arrival at this time
            time_list_dispatchToDeparture.append(row['dispatch_to_departure'])
            # Median time from dispatch to arrival (just the data to be calculated later)
            time_list_dispatchToArrival.append(row['dispatch_to_arrival_at_patient'])
            #Median time from 000 call to patient (just the data to be calculated later)
            time_list_000CallToArrival.append(time_difference(parse_date_and_time(first_contact_time)[1], parse_date_and_time(row['at_patient_time'])[1]))

    if len(time_list_dispatchToDeparture) > 0:
        dispatch_to_departure = analyse_times(time_list_dispatchToDeparture)
        dispatch_dep_Med = dispatch_to_departure['median']
        dispatch_dep_Min = dispatch_to_departure['min']
        dispatch_dep_Max = dispatch_to_departure['max']
    else:
        dispatch_dep_Med = "0"
        dispatch_dep_Min = "0"
        dispatch_dep_Max = "0"

    if len(time_list_dispatchToArrival) > 0:
        dispatch_to_arrival = analyse_times(time_list_dispatchToArrival)
        dispatch_arr_Med = dispatch_to_arrival['median']
        dispatch_arr_Min = dispatch_to_arrival['min']
        dispatch_arr_Max = dispatch_to_arrival['max']
    else:
        dispatch_arr_Med = "0"
        dispatch_arr_Min = "0"
        dispatch_arr_Max = "0"

    if len(time_list_000CallToArrival) > 0:
        _000CallToArrival = analyse_times(time_list_000CallToArrival)
        _000CallMed = _000CallToArrival['median']
        _000CallMin = _000CallToArrival['min']
        _000CallMmax = _000CallToArrival['max']

    else:
        _000CallMed = "0"
        _000CallMin = "0"
        _000CallMmax = "0"

    return [total_interventions,
            f"{dispatch_dep_Med} " +
                '(' + f"{dispatch_dep_Min}" + ' - ' + f"{dispatch_dep_Max}" + ')',
            f"{dispatch_arr_Med} " +
                '(' + f"{dispatch_arr_Min}" + ' - ' + f"{dispatch_arr_Max}" + ')',
            f"{_000CallMed} " +
                "(" + f"{_000CallMin}" + " - " + f"{_000CallMmax}" + ")"]

def caseClassification(date_from, date_to, df):
    total_arrests = 0
    interventions = 0
    for index, row in df.iterrows():
        #handle empty date times
        if pd.isna(row['date_time_incident']):
            #take the earliest time, either time of incidence or, if empty, time of dispatch
            date = parse_date_and_time(row['dispatch_date_time'])[0]

        else:
            date = parse_date_and_time(str(row['date_time_incident']))[0]
            dateObject = datetime.strptime(date, "%Y-%m-%d")

        #collect data from within relevent dates
        if (dateObject.date() > date_from) and (dateObject.date() < date_to):
            if is_datetime(row["arrest_time"]):
                total_arrests += 1
                if checkInterventions(row):
                    interventions += 1

    if total_arrests > 0:
        percentage = (interventions/total_arrests) * 100
        return [f"{total_arrests} ({percentage:.2f}%)"]
    else: return [f"0 (0%)"]

def interventionsPerformed(date_from, date_to, df):
    #precalculated intervention count list precalculated during dispatchActivity
    #yes I am aware that this is not the best way to go about this
    #I just want something that works and then I'll refactor
    #Ideally it runs in O(n) time not O(n)* 6 time
    intervention_count = {
        "RSI": 0,
        "Thoracostomy": 0,
        "Fem Art Line": 0,
        "Radial Art Line": 0,
        "Assisted ETT": 0,
        "PRECARE Access ( IO / IV / Central)": [0,0,0],
        "Echo / Ultrasound": 0,
        "Intra-arrest TOE": 0,
        "TTE": 0,
        "POC testing ABG": 0
        }

    intervention_count_list = []
    for index, row in df.iterrows():
        #handle empty date times
        if pd.isna(row['date_time_incident']):
            #take the earliest time, either time of incidence or, if empty, time of dispatch
            date = parse_date_and_time(row['dispatch_date_time'])[0]

        else:
            date = parse_date_and_time(str(row['date_time_incident']))[0]
            dateObject = datetime.strptime(date, "%Y-%m-%d")

        #collect data from within relevent dates
        if (dateObject.date() > date_from) and (dateObject.date() < date_to):
            row_interventions = checkInterventions(row)[1]
            for key, value in row_interventions.items():
                intervention_count[key] += row_interventions[key]

    for key, value in intervention_count.items():
        #account for special case
        if key ==  "PRECARE Access ( IO / IV / Central)":
            list(value)
            intervention_count_list.append(f"({value[0]} / {value[1]} / {value[2]})")
        else: intervention_count_list.append(value)

    return intervention_count_list

def ArtLineAnalysis(date_from, date_to, df):
    intraArrest_ArtLine = 0
    post_ROSC_Artline = 0
    PRECARE_Arrival_Time_List = []
    for index, row in df.iterrows():
        #handle empty date times
        if pd.isna(row['date_time_incident']):
            #take the earliest time, either time of incidence or, if empty, time of dispatch
            date = parse_date_and_time(row['dispatch_date_time'])[0]

        else:
            date = parse_date_and_time(str(row['date_time_incident']))[0]
            dateObject = datetime.strptime(date, "%Y-%m-%d")

        #collect data from within relevent dates
        if (dateObject.date() > date_from) and (dateObject.date() < date_to):
            if is_one(row["intra_arrest_artline"]):
                intraArrest_ArtLine += 1
                if is_numeric(row["art_ibp_time_calc"]):
                    PRECARE_Arrival_Time_List.append(int(row["art_ibp_time_calc"]));
            if is_one(row["rosc_art_rad"]) or is_one(row["rosc_art_fem"]):
                post_ROSC_Artline += 1

    if len(PRECARE_Arrival_Time_List) > 0:
        PRECARE_Arrival_Times = analyse_times(PRECARE_Arrival_Time_List)
        PRECARE_Arrival_Time_Med = PRECARE_Arrival_Times['median']
        PRECARE_Arrival_Time_Min = PRECARE_Arrival_Times['min']
        PRECARE_Arrival_Time_Max = PRECARE_Arrival_Times['max']
    else:
        PRECARE_Arrival_Time_Med = "0"
        PRECARE_Arrival_Time_Min = "0"
        PRECARE_Arrival_Time_Max = "0"

    return [str(intraArrest_ArtLine),
            f"{PRECARE_Arrival_Time_Med} " +
                '(' + f"{PRECARE_Arrival_Time_Min}" + ' - ' + f"{PRECARE_Arrival_Time_Max}" + ')',
            str(post_ROSC_Artline)]

def ROSCRateAnalysis(date_from, date_to, df):
    total_patients = 0
    any_ROSC = 0
    sustained_ROSC = 0
    never_sustained_ROSC = 0
    ROSC_Before_arrival = 0
    ROSC_OnAfter_arrival = 0
    ECMO_commenced = 0
    successful_cannulation = 0

    arrest_to_ROSC_time_list = []
    ROSC_time_fromArrival_list = []
    for index, row in df.iterrows():
        #handle empty date times
        if pd.isna(row['date_time_incident']):
            #take the earliest time, either time of incidence or, if empty, time of dispatch
            date = parse_date_and_time(row['dispatch_date_time'])[0]

        else:
            date = parse_date_and_time(str(row['date_time_incident']))[0]
            dateObject = datetime.strptime(date, "%Y-%m-%d")

        #collect data from within relevent dates
        if (dateObject.date() > date_from) and (dateObject.date() < date_to):
            total_patients += 1
            if is_one(row["any_rosc"]):
                any_ROSC += 1
            if is_numeric(row["arrest_time_to_rosc"]):
                arrest_to_ROSC_time_list.append(int(row["arrest_time_to_rosc"]))
            if is_one(row["sustained_rosc"]):
                sustained_ROSC += 1
            if is_zero(row["sustained_rosc"]):
                never_sustained_ROSC += 1
            if row["rosc_prior_arrival"] == "Before":
                ROSC_prior_arrival += 1
            elif row["rosc_prior_arrival"] == "On/After":
                ROSC_onAfter_arrival += 1
                if is_numeric(row["rosc_time_fromarrival_calc_2"]):
                    ROSC_time_fromArrival_list.append(int(row["rosc_time_fromarrival_calc_2"]))
            if row["ecmo_cannulation_commenced"]:
                ECMO_commenced += 1
                if is_one(row["success_cann"]):
                    successful_cannulation += 1

    try:
        any_ROSC_str = f"{any_ROSC}/{total_patients} {(any_ROSC/total_patients)*100:.2f}%"
        sustained_ROSC_str = f"{sustained_ROSC}/{total_patients} {(any_ROSC/total_patients)*100:.2f}%"

    except ZeroDivisionError:
        any_ROSC_str =  "0/0 (0%)"
        sustained_ROSC_str = "0/0 (0%)"

    if len(arrest_to_ROSC_time_list) > 0:
        arrest_to_ROSC_times = analyse_times(arrest_to_ROSC_time_list)
        arrest_to_ROSC_times_Med = arrest_to_ROSC_times['median']
        arrest_to_ROSC_times_Min = arrest_to_ROSC_times['min']
        arrest_to_ROSC_times_Max = arrest_to_ROSC_times['max']
    else:
        arrest_to_ROSC_times_Med = "0"
        arrest_to_ROSC_times_Min = "0"
        arrest_to_ROSC_times_Max = "0"

    if len(ROSC_time_fromArrival_list) > 0:
        ROSC_time_fromArrival = analyse_times(ROSC_time_fromArrival_list)
        ROSC_time_fromArrival_Med = ROSC_time_fromArrival['median']
        ROSC_time_fromArrival_Min = ROSC_time_fromArrival['min']
        ROSC_time_fromArrival_Max = ROSC_time_fromArrival['max']
    else:
        ROSC_time_fromArrival_Med = "0"
        ROSC_time_fromArrival_Min = "0"
        ROSC_time_fromArrival_Max = "0"

    return [any_ROSC_str,
            f"{arrest_to_ROSC_times_Med} " +
                '(' + f"{arrest_to_ROSC_times_Min}" + ' - ' + f"{arrest_to_ROSC_times_Max}" + ')',
            sustained_ROSC_str,
            str(never_sustained_ROSC),
            str(ROSC_Before_arrival),
            str(ROSC_OnAfter_arrival),
            '???', #unsure how to calculate missing data
            f"{ROSC_time_fromArrival_Med} " +
                '(' + f"{ROSC_time_fromArrival_Min}" + ' - ' + f"{ROSC_time_fromArrival_Max}" + ')',
            f"{ECMO_commenced} ({successful_cannulation})"]

def is_numeric(entry):
    """
    Checks if an entry is a number or a numeric string.
    Returns True if valid, False otherwise.
    """
    if pd.isna(entry):
        return False

    str_entry = str(entry).strip()

    if str_entry == "" or str_entry.lower() == "nan":
        return False

    try:
        float(str_entry)
        return True
    except ValueError:
        return False

def is_datetime(entry):
    """
    Checks if an entry is a valid datetime string in "D/M/YYYY H:MM" format.
    Returns True if valid, False otherwise.
    """
    if pd.isna(entry):
        return False

    str_entry = str(entry).strip()

    if str_entry == "" or str_entry.lower() == "nan":
        return False

    try:
        datetime.strptime(str_entry, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def checkInterventions(row):
    """
    takes a row from the PRECARE database and returns a bool as the first
    element of a tuple, indicating if an intervention has been performed.
    The second element is a dictionary of which interventions were done on that
    row
    """

    intervention_count = {
        "RSI": 0,
        "Thoracostomy": 0,
        "Fem Art Line": 0,
        "Radial Art Line": 0,
        "Assisted ETT": 0,
        "PRECARE Access ( IO / IV / Central)": [0,0,0],
        "Echo / Ultrasound": 0,
        "Intra-arrest TOE": 0,
        "TTE": 0,
        "POC testing ABG": 0
        }

    intervention = False
    #hardcoded indexes of columns where data exists in PRECARE DB
    index_RSI = "aeromedical_interventions___1"
    index_thoracostomy = "aeromedical_interventions___3"
    index_fem_artline = "med_team_intervention___1"
    index_rad_artline = "med_team_intervention___2"
    index_assisted_ETT = "airway_ett_team_assistance"
    index_vasc_access = "access"
    index_echo = "echo_ultrasound"
    index_TOE = "toe"
    index_ABG = "poc"
    index_TTE = "tte"

    if is_one(row[index_RSI]):
        intervention_count["RSI"] += 1
        intervention = True

    if is_one(row[index_thoracostomy]):
        intervention_count["Thoracostomy"] += 1
        intervention = True

    if is_one(row[index_fem_artline]):
        intervention_count["Fem Art Line"] += 1
        intervention = True


    if is_one(row[index_rad_artline]):
        intervention_count["Radial Art Line"] += 1
        intervention = True


    if access_present(row[index_vasc_access]):
        access_type = int(row[index_vasc_access])
        intervention = True
        if access_type == 1:
            intervention_count["PRECARE Access ( IO / IV / Central)"][0] += 1
        elif access_type == 2:
            intervention_count["PRECARE Access ( IO / IV / Central)"][1] += 1
        elif access_type == 3:
            intervention_count["PRECARE Access ( IO / IV / Central)"][2] += 1

    if is_one(row[index_echo]):
        intervention_count["Echo / Ultrasound"] += 1
        intervention = True

    if is_one(row[index_TOE]):
        intervention_count["Intra-arrest TOE"] += 1
        intervention = True

    if is_one(row[index_TTE]):
        intervention_count["TTE"] += 1
        intervention = True

    if is_one(row[index_ABG]):
        intervention_count["POC testing ABG"] += 1
        intervention = True

    return [intervention, intervention_count]

def access_present(value):
    if str(value) == "" or str(value).lower() == "nan":
        return False
    else: return str(int(value)).strip() in {"1", "2", "3"}


def is_one(value):
    if str(value) == "" or str(value).lower() == "nan":
        return False
    else: return int(value) == 1

def is_zero(value):
    if str(value) == "" or str(value).lower() == "nan":
        return False
    else: return int(value) == 0

def average_time(time_list):
    """
    Calculates the average time from a list of time strings in "HH:MM" format.
    Skips any empty strings, NaN values, or malformed entries.

    Args:
        time_list (list): A list of time strings e.g. ["08:30", "09:45", "###"]

    Returns:
        str: The average time as a string in "HH:MM" format, or None if no
             valid times were found.
    """
    total_minutes = 0
    valid_count = 0

    for entry in time_list:
        # Skip NaN values
        if pd.isna(entry):
            continue

        # Convert to string and strip whitespace
        str_entry = str(entry).strip()

        # Skip empty strings
        if str_entry == "":
            continue

        # Validate format — must be "XX:YY" with exactly one colon
        parts = str_entry.split(":")
        if len(parts) != 2:
            print(f"Skipping malformed entry: '{str_entry}'")
            continue

        # Validate that both parts are numeric
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
        except ValueError:
            print(f"  Skipping non-numeric entry: '{str_entry}'")
            continue

        # Validate that hours and minutes are within sensible ranges
        if not (0 <= hours <= 23) or not (0 <= minutes <= 59):
            print(f"  Skipping out-of-range entry: '{str_entry}'")
            continue

        # Convert the time to total minutes and accumulate
        total_minutes += (hours * 60) + minutes
        valid_count += 1

    # If no valid times were found, return None
    if valid_count == 0:
        print("No valid time entries found.")
        return None

    # Calculate the average in minutes and convert back to HH:MM
    average_minutes = total_minutes // valid_count
    avg_hours = average_minutes // 60
    avg_mins = average_minutes % 60

    return "{}:{}".format(avg_hours, avg_mins)

def analyse_times(time_list):
    """
    Calculates the median, min and max of a list of time values in either
    "MM:SS" format or as plain numeric strings (e.g. "42", "0", "137").
    Skips empty strings, NaN values, and malformed entries.

    Args:
        time_list (list): A list of time strings e.g. ["01:14", "42", "###"]

    Returns:
        dict: A dictionary containing "median", "min", and "max" as "MM:SS"
              strings, or None if no valid times were found.
    """

    def to_seconds(str_entry):
        """
        Converts a time string to total seconds.
        Accepts either "MM:SS" format or a plain integer string.
        Returns None if the entry is invalid.
        """
        # Case 1 — "MM:SS" format
        if ":" in str_entry:
            parts = str_entry.split(":")
            if len(parts) != 2:
                return None
            try:
                minutes = int(parts[0])
                seconds = int(parts[1])
            except ValueError:
                return None
            if not (0 <= minutes) or not (0 <= seconds <= 59):
                return None
            return (minutes * 60) + seconds

        # Case 2 — plain numeric string (treat as minutes directly)
        else:
            try:
                return int(str_entry) * 60
            except ValueError:
                return None

    def to_mm_ss(total_secs):
        """Converts total seconds back to a MM:SS string."""
        mins = total_secs // 60
        secs = total_secs % 60
        return f"{mins:02d}:{secs:02d}"

    # --- Build a clean list of valid times in seconds ---
    valid_seconds = []

    for entry in time_list:
        # Skip NaN values
        if pd.isna(entry):
            continue

        # Convert to string and strip whitespace
        str_entry = str(entry).strip()

        # Skip empty strings
        if str_entry == "":
            continue

        # Attempt to convert to seconds
        seconds = to_seconds(str_entry)
        if seconds is None:
            print(f"  Skipping malformed entry: '{str_entry}'")
            continue

        valid_seconds.append(seconds)

    # If no valid times were found, return None
    if not valid_seconds:
        print("No valid time entries found.")
        return None

    # --- Calculate min and max ---
    minimum = to_mm_ss(min(valid_seconds))
    maximum = to_mm_ss(max(valid_seconds))

    # --- Calculate median ---
    sorted_seconds = sorted(valid_seconds)
    count          = len(sorted_seconds)
    midpoint       = count // 2

    if count % 2 == 1:
        median_seconds = sorted_seconds[midpoint]
    else:
        median_seconds = (sorted_seconds[midpoint - 1] + sorted_seconds[midpoint]) // 2

    median = to_mm_ss(median_seconds)

    return {
        "median": median,
        "min":    minimum,
        "max":    maximum
    }

def parse_date_and_time(entry):
    """
    Splits a combined date and time string in the format
    "DD/MM/YYYY  H:MM:SS AM/PM" into separate date and 24 hour time values.

    Args:
        entry (str): A string in the format "30/10/2023  2:10:00 PM"

    Returns:
        tuple: A tuple of (date_str, time_str) where date_str is "DD/MM/YYYY"
               and time_str is "HH:MM" in 24 hour format.
               Returns (None, None) if the entry is invalid.
    """
    # Skip NaN values
    if pd.isna(entry):
        print ("isna")
        return (None, None)

    # Convert to string and strip whitespace
    str_entry = str(entry).strip()

    # Skip empty strings
    if str_entry == "":
        print('empty string')
        return (None, None)

    try:
        # Parse the full datetime string
        # %Y/%m/%d = day/month/year
        # %I        = 12 hour clock hour
        # %M        = minutes
        # %S        = seconds
        # %p        = AM/PM
        dt = datetime.strptime(str_entry, "%Y-%m-%d %H:%M")

        # Extract the date as a string in DD/MM/YYYY format
        date_str = dt.strftime("%Y-%m-%d")

        # Extract the time as a string in 24 hour HH:MM format
        # %H = 24 hour clock hour
        time_str = dt.strftime("%H:%M")

        return (date_str, time_str)

    except ValueError:
        print(f"  Skipping malformed entry: '{str_entry}'")
        return (None, None)


def time_difference(time1_str, time2_str):
    """
    Calculates the difference between two time strings in HH:MM format.
    Returns the result as a string in MM:SS format.
    """
    fmt = "%M:%S"
    time1 = datetime.strptime(time1_str, fmt)
    time2 = datetime.strptime(time2_str, fmt)

    difference = time1 - time2

    total_seconds = int(difference.total_seconds())

    # Handle negative differences (e.g. 01:00 - 08:00)
    if total_seconds < 0:
        total_seconds = abs(total_seconds)
        sign = "-"
    else:
        sign = ""

    minutes   = total_seconds // 60
    seconds = (total_seconds % 60)

    return f"{minutes:02d}:{seconds:02d}"
