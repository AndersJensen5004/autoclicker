import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk
from pynput import mouse, keyboard
import threading
import time
import random
import math


class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Autoclicker")
        self.master.geometry("400x250")

        self.is_clicking = False
        self.toggle_key = None
        self.click_interval = 1.0
        self.recording_key = False
        self.enable_jitters = tk.BooleanVar(value=True)

        self.create_widgets()

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)

        self.key_label = ttk.Label(self.master, text="Toggle Key: None")
        self.key_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.key_button = ttk.Button(self.master, text="Set Toggle Key", command=self.start_recording_key)
        self.key_button.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        ttk.Label(self.master, text="Clicks per Second:").grid(row=2, column=0, padx=10, pady=10)
        self.cps_value = tk.StringVar()
        self.cps_value.set("10")
        self.cps_slider = ttk.Scale(self.master, from_=1, to=20, orient="horizontal", command=self.update_interval)
        self.cps_slider.set(10)
        self.cps_slider.grid(row=2, column=1, padx=10, pady=10)
        self.cps_display = ttk.Label(self.master, textvariable=self.cps_value)
        self.cps_display.grid(row=2, column=2, padx=10, pady=10)

        self.jitter_checkbox = ttk.Checkbutton(self.master, text="Enable Mouse Jitters", variable=self.enable_jitters)
        self.jitter_checkbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.start_button = ttk.Button(self.master, text="Start", command=self.start_clicking)
        self.start_button.grid(row=4, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_clicking, state='disabled')
        self.stop_button.grid(row=4, column=1, padx=10, pady=10)

    def start_recording_key(self):
        self.recording_key = True
        self.key_label.config(text="Press any key...")

    def on_key_press(self, key):
        if self.recording_key:
            try:
                self.toggle_key = key.char
            except AttributeError:
                self.toggle_key = str(key)
            self.key_label.config(text=f"Toggle Key: {self.toggle_key}")
            self.recording_key = False
        elif hasattr(key, 'char') and key.char == self.toggle_key:
            self.toggle_clicking()

    def update_interval(self, val):
        self.cps_value.set(f"{int(float(val))}")
        self.click_interval = 1.0 / float(val)

    def toggle_clicking(self):
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if not self.toggle_key:
            print("Please set a toggle key.")
            return

        self.is_clicking = True
        self.start_button.state(["pressed", "disabled"])
        self.stop_button.state(["!disabled"])
        self.click_thread = threading.Thread(target=self.click_loop)
        self.click_thread.start()

    def stop_clicking(self):
        self.is_clicking = False
        self.start_button.state(["!pressed", "!disabled"])
        self.stop_button.state(["disabled"])
        if hasattr(self, 'click_thread'):
            self.click_thread.join()

    def click_loop(self):
        mouse_controller = mouse.Controller()
        base_interval = self.click_interval

        # Variables for varying the base interval
        variation_period_min = 2.76  # Minimum time in seconds for a variation cycle
        variation_period_max = 5.4  # Maximum time in seconds for a variation cycle
        variation_amplitude = 0.113  # Maximum change in base interval

        start_time = time.time()
        current_variation_period = random.uniform(variation_period_min, variation_period_max)

        while self.is_clicking:
            current_time = time.time()
            time_in_cycle = (current_time - start_time) % current_variation_period
            cycle_progress = time_in_cycle / current_variation_period

            # Slowly vary the base interval using a sine wave
            current_base_interval = base_interval * (1 + variation_amplitude * math.sin(cycle_progress * 2 * math.pi))

            # Randomize the click interval using a normal distribution centered around the current base interval
            skew = random.uniform(0.844, 1.26)
            mean_interval = current_base_interval * skew
            randomized_interval = random.gauss(mean_interval, mean_interval * 0.12)

            # Add random tiny delays using an exponential distribution to simulate human-like behavior
            if random.random() < 0.05:  # 5% chance to add a delay
                tiny_delay_factor = random.uniform(1.235, 2.367)
                max_tiny_delay = 3.06 * base_interval
                tiny_delay = min(random.expovariate(1 / (base_interval * tiny_delay_factor)), max_tiny_delay)
                time.sleep(tiny_delay)

            # Simulate mouse click
            mouse_controller.click(mouse.Button.left, 1)
            time.sleep(randomized_interval)

            # Slightly move the mouse to simulate natural movement if jitters are enabled
            if self.enable_jitters.get():
                current_position = mouse_controller.position
                jitter_magnitude = random.gauss(0, 1.6)
                offset_x = random.randint(-3, 3) + jitter_magnitude
                offset_y = random.randint(-3, 3) + jitter_magnitude
                mouse_controller.position = (current_position[0] + offset_x, current_position[1] + offset_y)

            # Check if we need to start a new variation cycle
            if time_in_cycle >= current_variation_period:
                start_time = current_time
                current_variation_period = random.uniform(variation_period_min, variation_period_max)

    def on_closing(self):
        self.stop_clicking()
        self.keyboard_listener.stop()
        self.master.destroy()


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = AutoClicker(master=root)
    root.mainloop()
