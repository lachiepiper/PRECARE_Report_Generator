import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import pandas as pd
from datetime import date, datetime, timedelta
import reportMetrics
import csv


# Global variables
df = None
output_path = None
filename = "PRECARE_activity_report.csv"
date_from = date(1900, 1, 1)
date_to = date(1900, 1, 1)


def resource_path(filename):
    """
    Returns the correct path to a resource file whether running
    as a script or as a PyInstaller bundle.
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as a PyInstaller bundle
        return os.path.join(sys._MEIPASS, filename)
    else:
        # Running as a normal script
        return os.path.join(os.path.dirname(__file__), filename)

def choose_file():
    global df

    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    #debug
    #file_path = "/Users/lachiepiper/Desktop/ECMO/ECMO Application/PRECARE_DATA_2026-05-11_1023.csv"
    if file_path:
        try:
            df = pd.read_csv(file_path)
            print(f"File loaded successfully: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{e}")


def choose_output_destination():
    global output_path

    output_path = filedialog.askdirectory(title="Select Output Destination")
    #debug
    #output_path = "/Users/lachiepiper/Desktop/ECMO/ECMO Application/OUTPUT TESTS"
    if output_path:
        print(f"Selected output destination: {output_path}")

def open_calendar(title, cal_button, is_from):
    """
    Opens a popup window with a Calendar widget. When the user selects
    a date and clicks confirm, the global date variable is updated and
    the label next to the button is updated to show the chosen date.

    Args:
        title (str):        Title of the popup window.
        cal_button (tk.Button): The Button whom is to have their label updated to the chosen date.
        is_from (bool):     True if this is the 'from' date, False for 'to' date.
    """
    global date_from, date_to

    # Create a popup window on top of the main window
    popup = tk.Toplevel()
    popup.title(title)
    popup.resizable(False, False)
    popup.grab_set()  # Prevent interaction with the main window while popup is open

    cal = Calendar(
        popup,
        selectmode="day",
        date_pattern="dd/mm/yyyy"
    )
    cal.pack(padx=10, pady=10)

    def on_confirm():
        global date_from, date_to
        selected = cal.get_date()

        if is_from:
            date_from = datetime.strptime(selected, "%d/%m/%Y").date()
            print(f"Date from: {date_from}")
        else:
            date_to = datetime.strptime(selected, "%d/%m/%Y").date()
            print(f"Date to: {date_to}")

        # Update the label next to the button to show the selected date
        cal_button.config(text=selected)
        popup.destroy()

    btn_confirm = tk.Button(popup, text="Confirm", command=on_confirm)
    btn_confirm.pack(pady=(0, 10))

def generate_report_csv():
    if df is None:
        messagebox.showwarning("No File", "Please load a CSV file first.")
        return
    if output_path is None:
        messagebox.showwarning("No Destination", "Please select an output destination first.")
        return

    full_path = os.path.join(output_path, filename)
    write_dispatchActivity(full_path)
    write_caseClassification(full_path)
    write_Interventions(full_path)
    write_ArtLine(full_path)
    write_ROSCRates(full_path)

    print("report generated")
    #return reportCSVBuilder()

def write_dispatchActivity(csv):
    global df
    global date_from, date_to

    month_list = reportMetrics.dispatchActivity(
        date.today() - timedelta(days=30), date.today(), df
        )
    three_month_list = reportMetrics.dispatchActivity(
        date.today() - timedelta(days=90), date.today(), df
        )
    dispatchActivity_df = pd.DataFrame({
        "Dispatch activity" : ["Number of patients with interventions",
        "Median time from dispatch to departure (range)",
        "Median time from dispatch to arrival (range)",
        "Median time from 000 call to patient (range)"],
        "Last 30 Days": month_list,
        "Last 90 Days": three_month_list
    })
    if customDates():
        custom_date_list = reportMetrics.dispatchActivity(date_from, date_to, df)
        dispatchActivity_df.insert(
            3,
            date_from.strftime("%d/%m/%Y") + " - " + date_to.strftime("%d/%m/%Y"),
            custom_date_list
            )

    dispatchActivity_df.to_csv(csv, index=False)
    print(f"Dispatch activity Saved to: {csv}")

def write_caseClassification(csv):
    global df
    global date_from, date_to

    month_data = reportMetrics.caseClassification(
        date.today() - timedelta(days=30), date.today(), df
        )
    three_month_data = reportMetrics.caseClassification(
        date.today() - timedelta(days=90), date.today(), df
        )
    caseClassification_df = pd.DataFrame({
        "Case Classification":["Number of times patient was confirmed in cardiac arrest (% cases where interventions performed)"],
        "Last 30 Days": month_data,
        "Last 90 Days": three_month_data
    })

    if customDates():
        custom_date_data = reportMetrics.caseClassification(date_from, date_to, df)
        caseClassification_df.insert(
            3,
            date_from.strftime("%d/%m/%Y") + " - " + date_to.strftime("%d/%m/%Y"),
            custom_date_data
            )

    caseClassification_df.to_csv(csv, mode="a", index=False)
    print(f"Case Classification Saved to: {csv}")

def write_Interventions(csv):
    global df
    global date_from, date_to

    month_list = reportMetrics.interventionsPerformed(
        date.today() - timedelta(days=30), date.today(), df
        )
    three_month_list = reportMetrics.interventionsPerformed(
        date.today() - timedelta(days=90), date.today(), df
        )
    Interventions_df = pd.DataFrame({
        "Aeromedical Interventions performed":["RSI", "Thoracostomy",
        "Fem Art Line", "Radial Art line",
        "Assisted ETT", "PRECARE Access ( IO / IV / Central)",
        "Echo / Ultrasound", "Intra-arrest TOE",
        "TTE", "POC testing ABG"],
        "Last 30 Days": month_list,
        "Last 90 Days": three_month_list
    })

    if customDates():
        custom_date_data = reportMetrics.interventionsPerformed(date_from, date_to, df)
        Interventions_df.insert(
            3,
            date_from.strftime("%d/%m/%Y") + " - " + date_to.strftime("%d/%m/%Y"),
            custom_date_data
            )

    Interventions_df.to_csv(csv, mode="a", index=False)
    print(f"Interventions Performed Saved to: {csv}")

def write_ArtLine(csv):
    global df
    global date_from, date_to

    month_list = reportMetrics.ArtLineAnalysis(
        date.today() - timedelta(days=30), date.today(), df
        )
    three_month_list = reportMetrics.ArtLineAnalysis(
        date.today() - timedelta(days=90), date.today(), df
        )
    ArtLine_df = pd.DataFrame({
        "Arterial Lines":["Number of intra-arrest Art line insertions",
        "Median time PRECARE arrival to art line transduced (range)",
        "Number of art lines inserted post ROSC"],
        "Last 30 Days": month_list,
        "Last 90 Days": three_month_list
    })

    if customDates():
        custom_date_list = reportMetrics.ArtLineAnalysis(date_from, date_to, df)
        ArtLine_df.insert(
            3,
            date_from.strftime("%d/%m/%Y") + " - " + date_to.strftime("%d/%m/%Y"),
            custom_date_list
            )

    ArtLine_df.to_csv(csv, mode="a", index=False)
    print(f"Artline Analysis Saved to: {csv}")

def write_ROSCRates(csv):
    global df
    global date_from, date_to

    month_list = reportMetrics.ROSCRateAnalysis(
        date.today() - timedelta(days=30), date.today(), df
        )
    three_month_list = reportMetrics.ROSCRateAnalysis(
        date.today() - timedelta(days=90), date.today(), df
        )
    ROSCRates_df = pd.DataFrame({
        "ROSC Rates":["Number of patients who achieved ROSC at any time",
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
    })

    if customDates():
        custom_date_list = reportMetrics.ROSCRateAnalysis(date_from, date_to, df)
        ROSCRates_df.insert(
            3,
            date_from.strftime("%d/%m/%Y") + " - " + date_to.strftime("%d/%m/%Y"),
            custom_date_list
            )

    ROSCRates_df.to_csv(csv, mode="a", index=False)
    print(f"ROSC Rates  Saved to: {csv}")

def customDates():
    return ((date_from != date(1900,1,1)) and (date_to != date(1900,1,1)))

def show_info():
    """Opens a popup window with information about the application."""
    popup = tk.Toplevel()
    popup.title("About")
    popup.resizable(False, False)
    popup.grab_set()

    # Title label
    lbl_title = tk.Label(
        popup,
        text="ECPR Report Generator",
        font=("Helvetica", 14, "bold")
    )
    lbl_title.pack(padx=20, pady=(20, 5))

    # Info text
    info_text = (
        "This application generates ECPR activity reports\n"
        "Instructions:\n"
        "PLEASE NOTE: This application will only take CSVs from the REDCap PRECARE database\n"
        "Data Exports -> All Data -> Export Data -> CSV/Microsoft Excel (raw data)\n"
        "PLEASE ONLY USE RAW DATA, NOT LABELS\n\n"
        "1. Click 'Choose File' to load your CSV data file.\n"
        "2. Click 'Choose Output Destination' to select\n"
        "   where the report will be saved.\n"
        "3. Optionally select a custom date range.\n"
        "4. Click 'Create Report' to generate the report.\n\n"
        "Reports include the last 30 and 90 days by default.\n"
        "A custom date range column is added if dates are selected."
    )
    lbl_info = tk.Label(
        popup,
        text=info_text,
        justify="left",
        wraplength=320
    )
    lbl_info.pack(padx=20, pady=(0, 10))

    # Separator
    tk.Frame(popup, height=1, bg="grey").pack(fill="x", padx=20, pady=5)

    # Version label
    lbl_version = tk.Label(
        popup,
        text="Version 1.0 \n © Lachlan Piper - Westmead Hospital",
        fg="grey",
        font=("Helvetica", 9)
    )
    lbl_version.pack(pady=(0, 5))

    # Close button
    btn_close = tk.Button(popup, text="Close", width=10, command=popup.destroy)
    btn_close.pack(pady=(0, 15))

def write_header_image(root):
    """Loads and displays an image at the top of the window."""
    try:
        from PIL import Image, ImageTk
        img = Image.open(resource_path("assets/wma_photo.png"))
        #img = img.resize((500, 100))            # resize to fit the window
        photo = ImageTk.PhotoImage(img)
        lbl_image = tk.Label(root, image=photo)
        lbl_image.image = photo                 # keep reference to prevent garbage collection
        lbl_image.pack(pady=(10, 0))
    except Exception as e:
        print(f"Could not load image: {e}")

def make_file_buttons(root):
    # get file address
    btn_choose_file = tk.Button(root, text="Choose File", command=choose_file)
    btn_choose_file.pack(pady=10)

    #get output destination
    btn_choose_output = tk.Button(root, text="Choose Output Destination", command=choose_output_destination)
    btn_choose_output.pack(pady=5)

def make_calender_elements(root):
        # --- Date range selector ---
        date_frame = tk.Frame(root)
        date_frame.pack(pady=15)

        # Button to open 'from' calendar
        btn_cal_from = tk.Button(
            date_frame,
            text='No date selected',
            command=lambda: open_calendar("Select From Date", btn_cal_from , is_from=True)
        )
        btn_cal_from.grid(row=0, column=1, padx=5)

        # "Analyse data from:" label
        lbl_from = tk.Label(date_frame, text="Analyse data from:")
        lbl_from.grid(row=0, column=0, padx=3)

        # "to" label
        lbl_to = tk.Label(date_frame, text="to")
        lbl_to.grid(row=0, column=2, padx=3)

        # Button to open 'to' calendar
        btn_cal_to = tk.Button(
            date_frame,
            text='No date selected',
            command=lambda: open_calendar("Select To Date", btn_cal_to, is_from=False)
        )
        btn_cal_to.grid(row=0, column=3, padx=5)

def make_info_button(root):
    """Places a small info button in the bottom right corner."""
    try:
        from PIL import Image, ImageTk
        img = Image.open(resource_path("assets/info.png"))
        img = img.resize((24, 24))
        photo = ImageTk.PhotoImage(img)
        btn_info = tk.Button(root, image=photo, command=show_info, bd=0, cursor="hand2")
        btn_info.image = photo                  # keep reference to prevent garbage collection
    except Exception as e:
        # Fallback to a plain text button if image can't be loaded
        print(f"Could not load info icon: {e}")
        btn_info = tk.Button(root, text="ℹ", font=("Helvetica", 14), command=show_info, bd=0, cursor="hand2")

    # Place in the bottom right corner using place() for precise positioning
    btn_info.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

def main():
    root = tk.Tk()
    root.title("PRECARE Report Generator")
    root.resizable(False, False)

    write_header_image(root)
    make_file_buttons(root)
    make_calender_elements(root)

    # Separator line
    tk.Frame(root, height=1, bg="grey").pack(fill="x", padx=20, pady=5)
    #generate report on click
    btn_create_output = tk.Button(root, text="Create Report", command=generate_report_csv)
    btn_create_output.pack(pady=15)

    # Centre the window on screen after all widgets are packed
    root.update_idletasks()
    width  = int(root.winfo_reqwidth()* 1.2)
    height = root.winfo_reqheight()
    x = (root.winfo_screenwidth()  // 2) - (width  // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Info button — placed after geometry is set so positioning is correct
    make_info_button(root)

    # --- macOS focus fix ---
    root.lift()                  # raise window to the top
    root.attributes("-topmost", True)   # force it above all other windows
    root.after(100, lambda: root.attributes("-topmost", False))  # release after 200ms
    root.focus_force()           # force keyboard and mouse focus

    root.mainloop()


if __name__ == "__main__":
    main()
