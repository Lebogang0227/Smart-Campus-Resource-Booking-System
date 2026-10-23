import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import booking_rules
import database as db
import booking_rules as rules
from models import build_user_from_record



class BookingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Campus Resource Booking System")
        self.geometry("900x600")
        self.current_user = None
        self.active_campus = None
        self.container = tk.Frame(self)
        self.container.pack(fill = "both", expand = True)
        self.frames = {}

        for ScreenClass in (LoginScreen, RegisterScreen, DashboardScreen):
            frame = ScreenClass(self.container, self)
            self.frames[ScreenClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)
        self.show_screen("LoginScreen")

    def show_screen(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if name == "DashboardScreen":
            frame.refresh()

class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = tk.Label(self, text="Smart Campus Resource Booking",
                         font=("Arial", 20, "bold"))
        title.pack(pady=30)

        # --- Username ---
        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        #Password
        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        #Login button
        tk.Button(self, text="Login", width=20, command=self.login).pack(pady=10)

        #Register link
        tk.Button(self, text="Register as Lecturer",
                  command=lambda: app.show_screen("RegisterScreen")).pack()

        #Accounts
        info = tk.Label(
            self,
            text=(
                "Accounts :\n"
                "  Admin (CENT): admin_cent / admin321\n"
                "  Admin (BRYN): admin_bryn / admin321\n"
                "  Admin (PTR): admin_ptr / admin321\n"
                "  Operator   : operator  / op123"
            ),
            fg="grey",
            font=("Arial", 8),
            justify="left",
        )
        info.pack(side="bottom", pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return

        record = db.get_user(username)
        if record is None:
            messagebox.showerror("Error", "User not found.")
            return

        user = build_user_from_record(record)
        if not user.check_password(password):
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.app.current_user = user
        self.password_entry.delete(0, tk.END)
        self.app.show_screen("DashboardScreen")

class RegisterScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Register a New Lecturer Account",
                 font=("Arial", 18, "bold")).pack(pady=20)

        # Username
        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Campus
        tk.Label(self, text="Select Campus:").pack()
        self.campus_combo = ttk.Combobox(self, values=db.get_campuses(), state="readonly")
        self.campus_combo.pack(pady=5)

        tk.Button(self, text="Register", width=20, command=self.register).pack(pady=10)
        tk.Button(self, text="Back to Login",
                  command=lambda: app.show_screen("LoginScreen")).pack()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        campus = self.campus_combo.get()

        if not username or not password or not campus:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters.")
            return

        success = db.add_user(username, password, "lecturer", campus)
        if success:
            messagebox.showinfo("Success", "Account created. You can now log in.")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.app.show_screen("LoginScreen")
        else:
            messagebox.showerror("Error", "Username already exists.")

class DashboardScreen(tk.Frame):
    """Main screen shown after login. Contents depend on the user's role."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Top bar
        self.top_bar = tk.Frame(self, bg="#eeeeee", height=40)
        self.top_bar.pack(fill="x")
        self.user_label = tk.Label(self.top_bar, text="", bg="#eeeeee",
                                   font=("Arial", 10, "bold"))
        self.user_label.pack(side="left", padx=10)
        tk.Button(self.top_bar, text="Logout",
                  command=self.logout).pack(side="right", padx=10)

        # Campus selector
        self.campus_frame = tk.Frame(self)
        self.campus_frame.pack(fill="x", pady=5)
        tk.Label(self.campus_frame, text="Active Campus:").pack(side="left", padx=10)
        self.campus_combo = ttk.Combobox(self.campus_frame, values=db.get_campuses(),
                                         state="readonly", width=25)
        self.campus_combo.pack(side="left")
        self.campus_combo.bind("<<ComboboxSelected>>", self.on_campus_change)
        self.rules_label = tk.Label(self.campus_frame, text="", fg="blue",
                                    font=("Arial", 9))
        self.rules_label.pack(side="left", padx=15)

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def logout(self):
        self.app.current_user = None
        self.app.active_campus = None
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        self.app.show_screen("LoginScreen")

    def on_campus_change(self, event=None):
        self.app.active_campus = self.campus_combo.get()
        self.rules_label.config(
            text=rules.describe_rules(self.app.active_campus)
        )
        self.build_tabs()

    def refresh(self):
        user = self.app.current_user
        if user is None:
            return

        # Show who is logged in
        self.user_label.config(text=user.get_description())

        # Decide which campus is active and lock the dropdown if admin
        if user.role == "admin":
            self.campus_combo.set(user.campus)
            self.campus_combo.config(state="disabled")
            self.app.active_campus = user.campus
        elif user.role == "operator":
            self.campus_combo.config(state="readonly")
            if not self.campus_combo.get():
                self.campus_combo.set(db.get_campuses()[0])
            self.app.active_campus = self.campus_combo.get()
        else:  # lecturer
            self.campus_combo.config(state="readonly")
            if not self.campus_combo.get():
                self.campus_combo.set(user.campus or db.get_campuses()[0])
            self.app.active_campus = self.campus_combo.get()

        self.rules_label.config(
            text=rules.describe_rules(self.app.active_campus)
        )

        self.build_tabs()

    def build_tabs(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        user = self.app.current_user
        campus = self.app.active_campus

        print(f"[DEBUG] Building tabs for role={user.role!r}, campus={campus!r}")

        if user.role == "lecturer":
            self.notebook.add(BookResourceTab(self.notebook, self.app, campus),
                              text="Book a Resource")
            self.notebook.add(MyBookingsTab(self.notebook, self.app),
                              text="My Bookings")
            self.notebook.add(AvailabilityTab(self.notebook, self.app, campus),
                              text="Availability")

        elif user.role == "admin":
            self.notebook.add(ManageResourcesTab(self.notebook, self.app, campus),
                              text="Manage Resources")
            self.notebook.add(CampusBookingsTab(self.notebook, self.app, campus),
                              text="Campus Bookings")
            self.notebook.add(CampusReportTab(self.notebook, self.app, campus),
                              text="Campus Report")

        elif user.role == "operator":
            self.notebook.add(AllResourcesTab(self.notebook, self.app),
                              text="All Resources")
            self.notebook.add(AllBookingsTab(self.notebook, self.app),
                              text="All Bookings")
            self.notebook.add(ComparisonTab(self.notebook, self.app),
                              text="Cross-Campus Comparison")

        else:
            tk.Label(self.notebook, text=f"Unknown role: {user.role}").pack()

#TABS

class BookResourceTab(tk.Frame):
    def __init__(self, parent, app, campus):
        super().__init__(parent)
        self.app = app
        self.campus = campus

        # Resource selector
        tk.Label(self, text="Select Resource:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.resource_combo = ttk.Combobox(self, state="readonly", width=40)
        self.resource_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.load_resources()

        # Date
        tk.Label(self, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = tk.Entry(self, width=20)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Start time
        tk.Label(self, text="Start Time (HH:MM):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.time_entry = tk.Entry(self, width=20)
        self.time_entry.insert(0, "09:00")
        self.time_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Duration
        tk.Label(self, text="Duration (minutes):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.duration_entry = tk.Entry(self, width=20)
        self.duration_entry.insert(0, "60")
        self.duration_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Book button
        tk.Button(self, text="Create Booking", command=self.create_booking).grid(
            row=4, column=0, columnspan=2, pady=15)

        # Feedback label
        self.message = tk.Label(self, text="", fg="green")
        self.message.grid(row=5, column=0, columnspan=2)

    def load_resources(self):
        resources = db.get_resources(self.campus)
        self.resource_map = {}
        display = []
        for r in resources:
            label = f"{r['resource_code']} - {r['name']}"
            display.append(label)
            self.resource_map[label] = r["resource_code"]
        self.resource_combo["values"] = display
        if display:
            self.resource_combo.current(0)

    def create_booking(self):
        """Validate and save a new booking."""
        resource_label = self.resource_combo.get()
        if not resource_label:
            messagebox.showerror("Error", "Please select a resource.")
            return

        resource_code = self.resource_map[resource_label]
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()

        try:
            duration = int(self.duration_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Duration must be a whole number of minutes.")
            return

        # Step 1: check campus rules
        ok, msg = rules.validate_booking(self.campus, date_str, time_str, duration)
        if not ok:
            messagebox.showerror("Booking Rejected", msg)
            return

        # Step 2: check for overlapping bookings
        existing = db.get_bookings_for_resource(resource_code)
        for b in existing:
            if rules.times_overlap(date_str, time_str, duration,
                                   b["booking_date"], b["start_time"], b["duration"]):
                messagebox.showerror(
                    "Booking Rejected",
                    f"This resource is already booked on {b['booking_date']} "
                    f"from {b['start_time']} for {b['duration']} minutes."
                )
                return

        # Step 3: save
        db.create_booking(resource_code, self.app.current_user.username,
                          self.campus, date_str, time_str, duration)
        self.message.config(text=f"Booking confirmed for {resource_code} on {date_str} at {time_str}.")
        messagebox.showinfo("Success", "Booking confirmed!")


class MyBookingsTab(tk.Frame):
    """Lecturer tab: list bookings made by the current user."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.tree = ttk.Treeview(self,
                                 columns=("id", "resource", "date", "time", "duration", "status"),
                                 show="headings")
        for col, heading in zip(("id", "resource", "date", "time", "duration", "status"),
                                ("ID", "Resource", "Date", "Start", "Duration (min)", "Status")):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Button(self, text="Cancel Selected Future Booking",
                  command=self.cancel_selected).pack(pady=5)
        tk.Button(self, text="Refresh", command=self.load).pack(pady=5)
        self.load()

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        bookings = db.get_bookings_for_user(self.app.current_user.username)
        for b in bookings:
            self.tree.insert("", "end", values=(
                b["id"], b["resource_code"], b["booking_date"],
                b["start_time"], b["duration"], b["status"]
            ))

    def cancel_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a booking first.")
            return
        item = self.tree.item(selected[0])
        booking_id = item["values"][0]
        date_str = item["values"][2]
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Could not read booking date.")
            return
        if date_obj < datetime.now().date():
            messagebox.showerror("Error", "Cannot cancel a past booking.")
            return
        if messagebox.askyesno("Confirm", "Cancel this booking?"):
            db.cancel_booking(booking_id)
            self.load()
            messagebox.showinfo("Done", "Booking cancelled.")


class AvailabilityTab(tk.Frame):
    """Shows which resources are booked for a given date."""

    def __init__(self, parent, app, campus):
        super().__init__(parent)
        self.app = app
        self.campus = campus

        top = tk.Frame(self)
        top.pack(fill="x", pady=5)
        tk.Label(top, text="Check availability for date (YYYY-MM-DD):").pack(side="left", padx=5)
        self.date_entry = tk.Entry(top, width=15)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(side="left")
        tk.Button(top, text="Check", command=self.check).pack(side="left", padx=5)

        self.result = tk.Text(self, height=20)
        self.result.pack(fill="both", expand=True, padx=5, pady=5)

    def check(self):
        date_str = self.date_entry.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be YYYY-MM-DD.")
            return

        self.result.delete("1.0", tk.END)
        resources = db.get_resources(self.campus)
        if not resources:
            self.result.insert(tk.END, "No resources for this campus.\n")
            return

        for r in resources:
            self.result.insert(tk.END, f"\n{r['resource_code']} - {r['name']}\n")
            bookings = [b for b in db.get_bookings_for_resource(r["resource_code"])
                        if b["booking_date"] == date_str and b["status"] == "active"]
            if not bookings:
                self.result.insert(tk.END, "   AVAILABLE all day\n")
            else:
                for b in bookings:
                    self.result.insert(
                        tk.END,
                        f"   BOOKED {b['start_time']} for {b['duration']} min by {b['username']}\n"
                    )


class ManageResourcesTab(tk.Frame):
    def __init__(self, parent, app, campus):
        super().init__(parent)
        self.app = app
        self.campus = campus

 # Form
        form = tk.Frame(self)
        form.pack(fill="x", pady=10)

        tk.Label(form, text="Code:").grid(row=0, column=0, padx=5, pady=3, sticky="e")
        self.code_entry = tk.Entry(form, width=20)
        self.code_entry.grid(row=0, column=1)

        tk.Label(form, text="Name:").grid(row=0, column=2, padx=5, pady=3, sticky="e")
        self.name_entry = tk.Entry(form, width=25)
        self.name_entry.grid(row=0, column=3)

        tk.Label(form, text="Type:").grid(row=0, column=4, padx=5, pady=3, sticky="e")
        self.type_entry = tk.Entry(form, width=20)
        self.type_entry.grid(row=0, column=5)

        # Buttons
        btn_row = tk.Frame(self)
        btn_row.pack(pady=5)
        tk.Button(btn_row, text="Add Resource", command=self.add).pack(side="left", padx=5)
        tk.Button(btn_row, text="Update Selected", command=self.update).pack(side="left", padx=5)
        tk.Button(btn_row, text="Delete Selected", command=self.delete).pack(side="left", padx=5)
        tk.Button(btn_row, text="Refresh", command=self.load).pack(side="left", padx=5)

        # List
        self.tree = ttk.Treeview(self,
                                 columns=("code", "name", "type"),
                                 show="headings")
        for col, heading in zip(("code", "name", "type"),
                                ("Code", "Name", "Type")):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=200, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load()

    def on_select(self, event=None):
        """Fill the form fields when the user clicks a row."""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, values[0])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.type_entry.delete(0, tk.END)
        self.type_entry.insert(0, values[2])

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in db.get_resources(self.campus):
            self.tree.insert("", "end", values=(r["resource_code"], r["name"], r["resource_type"]))

    def add(self):
        code = self.code_entry.get().strip().upper()
        name = self.name_entry.get().strip()
        rtype = self.type_entry.get().strip()

        if not code or not name:
            messagebox.showerror("Error", "Code and Name are required.")
            return

        if db.add_resource(code, name, self.campus, rtype):
            messagebox.showinfo("Success", "Resource added.")
            self.load()
        else:
            messagebox.showerror("Error", "A resource with that code already exists.")

    def update(self):
        code = self.code_entry.get().strip().upper()
        name = self.name_entry.get().strip()
        rtype = self.type_entry.get().strip()

        if not code or not name:
            messagebox.showerror("Error", "Select a resource first.")
            return
        db.update_resource(code, name, rtype)
        messagebox.showinfo("Success", "Resource updated.")
        self.load()

    def delete(self):
        code = self.code_entry.get().strip().upper()
        if not code:
            messagebox.showerror("Error", "Select a resource first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete resource {code}?"):
            return
        db.delete_resource(code)
        messagebox.showinfo("Success", "Resource deleted.")
        self.load()


class CampusBookingsTab(tk.Frame):
    """Admin tab: show all bookings for the campus."""

    def __init__(self, parent, app, campus):
        super().__init__(parent)
        self.app = app
        self.campus = campus

        self.tree = ttk.Treeview(self,
                                 columns=("id", "resource", "user", "date", "time", "duration", "status"),
                                 show="headings")
        for col, heading in zip(("id", "resource", "user", "date", "time", "duration", "status"),
                                ("ID", "Resource", "User", "Date", "Start", "Duration", "Status")):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Button(self, text="Refresh", command=self.load).pack(pady=5)
        self.load()

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for b in db.get_bookings_for_campus(self.campus):
            self.tree.insert("", "end", values=(
                b["id"], b["resource_code"], b["username"],
                b["booking_date"], b["start_time"], b["duration"], b["status"]
            ))


class CampusReportTab(tk.Frame):
    """Admin tab: campus-level reports (requirement 7.1)."""

    def __init__(self, parent, app, campus):
        super().__init__(parent)
        self.app = app
        self.campus = campus

        self.text = tk.Text(self, font=("Courier", 10))
        self.text.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Button(self, text="Generate Report", command=self.generate).pack(pady=5)

    def generate(self):
        self.text.delete("1.0", tk.END)
        bookings = db.get_bookings_for_campus(self.campus)
        active = [b for b in bookings if b["status"] == "active"]

        self.text.insert(tk.END, f"CAMPUS REPORT — {self.campus}\n")
        self.text.insert(tk.END, "=" * 40 + "\n\n")
        self.text.insert(tk.END, f"Total bookings (all time): {len(bookings)}\n")
        self.text.insert(tk.END, f"Active bookings         : {len(active)}\n")

        if active:
            # Most frequently used resource
            usage = {}
            for b in active:
                usage[b["resource_code"]] = usage.get(b["resource_code"], 0) + 1
            most = max(usage, key=usage.get)
            self.text.insert(tk.END, f"Most used resource      : {most} ({usage[most]} bookings)\n")

            # Average duration
            total = sum(b["duration"] for b in active)
            avg = total / len(active)
            self.text.insert(tk.END, f"Average duration        : {avg:.1f} minutes\n")

            # Breakdown
            self.text.insert(tk.END, "\nUsage breakdown:\n")
            for code, count in sorted(usage.items(), key=lambda x: -x[1]):
                self.text.insert(tk.END, f"  {code:<15} {count} booking(s)\n")
        else:
            self.text.insert(tk.END, "\nNo active bookings yet.\n")


class AllResourcesTab(tk.Frame):
    """Operator tab: every resource across all campuses."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.tree = ttk.Treeview(self,
                                 columns=("code", "name", "campus", "type"),
                                 show="headings")
        for col, heading in zip(("code", "name", "campus", "type"),
                                ("Code", "Name", "Campus", "Type")):
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Button(self, text="Refresh", command=self.load).pack(pady=5)
        self.load()

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in db.get_all_resources():
            self.tree.insert("", "end", values=(r["resource_code"], r["name"],
                                                r["campus"], r["resource_type"]))


class AllBookingsTab(tk.Frame):
    """Operator tab: every booking system-wide."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.tree = ttk.Treeview(self,
                                 columns=("id", "campus", "resource", "user", "date",
                                          "time", "duration", "status"),
                                 show="headings")
        for col in ("id", "campus", "resource", "user", "date", "time", "duration", "status"):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=90, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Button(self, text="Refresh", command=self.load).pack(pady=5)
        self.load()

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for b in db.get_all_bookings():
            self.tree.insert("", "end", values=(
                b["id"], b["campus"], b["resource_code"], b["username"],
                b["booking_date"], b["start_time"], b["duration"], b["status"]
            ))


class ComparisonTab(tk.Frame):
    """Operator tab: cross-campus comparison (requirement 7.2)."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.text = tk.Text(self, font=("Courier", 10))
        self.text.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Button(self, text="Generate Comparison", command=self.generate).pack(pady=5)

    def generate(self):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "CROSS-CAMPUS COMPARISON\n")
        self.text.insert(tk.END, "=" * 50 + "\n\n")

        campuses = db.get_campuses()
        header = f"{'Campus':<15}{'Bookings':<10}{'Avg Dur':<10}{'Top Resource':<20}\n"
        self.text.insert(tk.END, header)
        self.text.insert(tk.END, "-" * 55 + "\n")

        for campus in campuses:
            bookings = [b for b in db.get_bookings_for_campus(campus)
                        if b["status"] == "active"]
            if not bookings:
                self.text.insert(tk.END, f"{campus:<15}{0:<10}{'-':<10}{'-':<20}\n")
                continue

            usage = {}
            for b in bookings:
                usage[b["resource_code"]] = usage.get(b["resource_code"], 0) + 1
            top = max(usage, key=usage.get)
            avg = sum(b["duration"] for b in bookings) / len(bookings)
            self.text.insert(tk.END,
                             f"{campus:<15}{len(bookings):<10}{avg:<10.1f}{top:<20}\n")

        self.text.insert(tk.END, "\nCampus Rules:\n")
        for campus in campuses:
            self.text.insert(tk.END, f"  {campus}: {rules.describe_rules(campus)}\n")