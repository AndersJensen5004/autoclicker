import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import numpy as np
from scipy import stats
import traceback
import sys


class ClickStats:
    def __init__(self, master):
        self.master = master
        self.master.title("Click Stats")
        self.master.geometry("500x400")

        self.clicks = []
        self.click_times = []
        self.start_time = None
        self.is_recording = False
        self.cooldown = False

        self.create_widgets()

    def create_widgets(self):
        self.info_label = tk.Label(self.master, text="Click to start!", font=("Helvetica", 14))
        self.info_label.pack(pady=20)

        self.click_area = tk.Button(self.master, text="Click Me!", command=self.on_click)
        self.click_area.pack(fill=tk.BOTH, expand=True)

        self.stats_text = scrolledtext.ScrolledText(self.master, height=40, width=100)
        self.stats_text.pack(padx=10, pady=10)
        self.stats_text.pack_forget()  # Hide initially

    def on_click(self):
        if self.cooldown:
            return
        if not self.is_recording:
            self.start_recording()
        self.record_click()

    def start_recording(self):
        self.clicks = []
        self.click_times = []
        self.start_time = time.time()
        self.is_recording = True
        self.info_label.config(text="Clicking in progress...")
        self.master.after(10000, self.stop_recording)

    def record_click(self):
        if self.is_recording:
            current_time = time.time() - self.start_time
            self.clicks.append(current_time)
            if len(self.clicks) > 1:
                self.click_times.append(current_time - self.clicks[-2])

    def stop_recording(self):
        self.is_recording = False
        self.info_label.config(text="Time's up! Analyzing...")
        self.click_area.config(state=tk.DISABLED)
        self.master.after(100, self.analyze_clicks)

    def analyze_clicks(self):
        try:
            if len(self.click_times) < 2:
                messagebox.showinfo("Error", "Not enough clicks recorded")
                self.reset_ui()
                return

            click_times_array = np.array(self.click_times)

            self.stats_text.delete(1.0, tk.END)  # Clear previous content
            self.stats_text.pack(padx=10, pady=10)  # Show the text widget

            self.stats_text.insert(tk.END, f"Total Clicks: {len(self.clicks)}\n")
            self.stats_text.insert(tk.END, f"CPS: {len(self.clicks) / 10:.2f}\n\n")

            self.stats_text.insert(tk.END, "Time Between Clicks (seconds):\n")
            self.stats_text.insert(tk.END, f"Mean: {np.mean(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Median: {np.median(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Mode: {stats.mode(click_times_array).mode[0]:.6f}\n")
            self.stats_text.insert(tk.END, f"Standard Deviation: {np.std(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Variance: {np.var(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Minimum: {np.min(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Maximum: {np.max(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Range: {np.ptp(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"25th Percentile: {np.percentile(click_times_array, 25):.6f}\n")
            self.stats_text.insert(tk.END, f"75th Percentile: {np.percentile(click_times_array, 75):.6f}\n")
            self.stats_text.insert(tk.END,
                                   f"Interquartile Range: {np.percentile(click_times_array, 75) - np.percentile(click_times_array, 25):.6f}\n")
            self.stats_text.insert(tk.END, f"Kurtosis: {stats.kurtosis(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END, f"Skewness: {stats.skew(click_times_array):.6f}\n")
            self.stats_text.insert(tk.END,
                                   f"Coefficient of Variation: {np.std(click_times_array) / np.mean(click_times_array):.6f}\n")

            # New statistics
            self.stats_text.insert(tk.END, f"\nShapiro-Wilk Test (normality): {stats.shapiro(click_times_array)}\n")
            self.stats_text.insert(tk.END, f"Anderson-Darling Test (normality): {stats.anderson(click_times_array)}\n")
            self.stats_text.insert(tk.END,
                                   f"D'Agostino's K^2 Test (normality): {stats.normaltest(click_times_array)}\n")

            # Attempt to fit distributions
            distributions = [stats.norm, stats.expon, stats.lognorm, stats.gamma, stats.beta]
            best_distribution = None
            best_params = None
            best_sse = np.inf

            for distribution in distributions:
                try:
                    params = distribution.fit(click_times_array)
                    sse = np.sum(np.power(click_times_array - distribution.pdf(click_times_array, *params), 2))
                    if sse < best_sse:
                        best_distribution = distribution
                        best_params = params
                        best_sse = sse
                except:
                    continue

            if best_distribution:
                self.stats_text.insert(tk.END, f"\nBest fitting distribution: {best_distribution.name}\n")
                self.stats_text.insert(tk.END, f"Distribution parameters: {best_params}\n")

            percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
            self.stats_text.insert(tk.END, "\nPercentiles:\n")
            for p in percentiles:
                self.stats_text.insert(tk.END, f"{p}th: {np.percentile(click_times_array, p):.6f}\n")

            self.info_label.config(text="Analysis complete. Wait for cooldown...")
            self.cooldown = True
            self.master.after(2000, self.end_cooldown)

        except Exception as e:
            error_msg = f"An error occurred:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)  # Also print to console for debugging
            self.reset_ui()

    def end_cooldown(self):
        self.cooldown = False
        self.click_area.config(state=tk.NORMAL)
        self.info_label.config(text="Click to start a new session.")

    def reset_ui(self):
        self.click_area.config(state=tk.NORMAL)
        self.info_label.config(text="Click to start!")
        self.stats_text.pack_forget()  # Hide the stats text
        self.cooldown = False

def exception_handler(exception, value, tb):
    error_msg = f"An uncaught exception occurred:\n{str(value)}\n\nTraceback:\n{''.join(traceback.format_tb(tb))}"
    messagebox.showerror("Uncaught Exception", error_msg)
    print(error_msg)  # Also print to console for debugging

if __name__ == "__main__":
    sys.excepthook = exception_handler
    root = tk.Tk()
    app = ClickStats(root)
    root.mainloop()