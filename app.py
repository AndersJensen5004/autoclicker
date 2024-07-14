import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard
import threading
import time
import random
import math
import queue


class Win98Style(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_use('clam')

        self.configure('.',
                       background='#c0c0c0',
                       foreground='black',
                       font=('monospace', 10))

        self.configure('TButton',
                       padding=3,
                       relief='raised',
                       background='#c0c0c0')

        self.map('TButton',
                 background=[('active', '#d4d0c8'), ('pressed', '#bab5ab')],
                 relief=[('pressed', 'sunken')])


        self.configure('TButton.border',
                       relief='raised',
                       borderwidth=2)

        self.configure('TCheckbutton',
                       background='#c0c0c0')

        self.configure('TLabel',
                       background='#c0c0c0')

        self.configure('Custom.Horizontal.TScale',
                       troughcolor='#808080',
                       sliderrelief='raised',
                       sliderthickness=20,
                       sliderlength=15,
                       background='#c0c0c0')


class CustomScale(ttk.Scale):
    def __init__(self, master=None, **kwargs):
        ttk.Scale.__init__(self, master, **kwargs)
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)

    def on_click(self, event):
        self.set(self.get_value_from_pixel(event.x))
        self.event_generate('<<ScaleChanged>>')

    def on_drag(self, event):
        self.set(self.get_value_from_pixel(event.x))
        self.event_generate('<<ScaleChanged>>')

    def get_value_from_pixel(self, x):
        return (x / self.winfo_width()) * (self['to'] - self['from']) + self['from']


class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Autoclicker 98")
        self.master.geometry("300x220")
        self.master.configure(bg='#c0c0c0')
        self.master.resizable(False, False)

        self.click_queue = queue.Queue()
        self.master.after(100, self.check_queue)

        # Set the icon
        icon = tk.PhotoImage(file="autoclicker_icon.png")
        self.master.iconphoto(False, icon)

        self.is_clicking = False
        self.toggle_key = "Button.middle"
        self.click_interval = 1.0
        self.recording_key = False
        self.enable_jitters = tk.BooleanVar(value=False)

        self.create_widgets()

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10 10 10 10")
        main_frame.grid(sticky=(tk.W, tk.E, tk.N, tk.S))

        self.key_label = ttk.Label(main_frame, text="Toggle Key: Middle Mouse Button")
        self.key_label.grid(row=0, column=0, pady=(0, 5), sticky='w')

        self.key_button = ttk.Button(main_frame, text="Set Toggle Key", command=self.start_recording_key)
        self.key_button.grid(row=1, column=0, pady=(0, 10), sticky='ew')

        ttk.Label(main_frame, text="Clicks per Second:").grid(row=2, column=0, sticky='w')

        slider_frame = ttk.Frame(main_frame)
        slider_frame.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        slider_frame.columnconfigure(0, weight=1)

        self.cps_value = tk.StringVar()
        self.cps_value.set("10")
        self.cps_slider = CustomScale(slider_frame, from_=1, to=20, orient="horizontal",
                                      command=self.update_interval, style='Custom.Horizontal.TScale')
        self.cps_slider.set(10)
        self.cps_slider.grid(row=0, column=0, sticky='ew')
        self.cps_display = ttk.Label(slider_frame, textvariable=self.cps_value, width=3)
        self.cps_display.grid(row=0, column=1, padx=(5, 0))

        self.jitter_checkbox = ttk.Checkbutton(main_frame, text="Enable Mouse Jitters", variable=self.enable_jitters)
        self.jitter_checkbox.grid(row=4, column=0, sticky='w', pady=(0, 10))

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, sticky='ew')
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_clicking)
        self.start_button.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_clicking, state='disabled')
        self.stop_button.grid(row=0, column=1, sticky='ew', padx=(5, 0))
    def start_recording_key(self):
        self.recording_key = True
        self.key_label.config(text="Press any key or mouse button...")

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

    def on_mouse_click(self, x, y, button, pressed):
        if self.recording_key and pressed:
            self.toggle_key = str(button)
            self.key_label.config(text=f"Toggle Key: {self.toggle_key}")
            self.recording_key = False
        elif str(button) == self.toggle_key and pressed:
            self.toggle_clicking()

    def update_interval(self, val):
        self.cps_value.set(f"{int(float(val))}")
        self.click_interval = 1.0 / float(val)

    def toggle_clicking(self):
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def check_queue(self):
        try:
            while True:
                button, state = self.click_queue.get_nowait()
                if button == "start_button":
                    self.start_button.state(state)
                elif button == "stop_button":
                    self.stop_button.state(state)
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.check_queue)

    def start_clicking(self):
        self.is_clicking = True
        self.click_queue.put(("start_button", ["pressed", "disabled"]))
        self.click_queue.put(("stop_button", ["!disabled"]))
        self.click_thread = threading.Thread(target=self.click_loop)
        self.click_thread.daemon = True  # This allows the thread to be terminated when the main program exits
        self.click_thread.start()

    def stop_clicking(self):
        self.is_clicking = False
        self.click_queue.put(("start_button", ["!pressed", "!disabled"]))
        self.click_queue.put(("stop_button", ["disabled"]))

    def click_loop(self):
        mouse_controller = mouse.Controller()
        base_interval = self.click_interval

        # delay before clicking starts
        start_delay = random.uniform(self.click_interval / 8, self.click_interval / 6)
        time.sleep(start_delay)

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

            if not self.is_clicking:
                break

    def on_closing(self):
        self.stop_clicking()
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        # Wait for the click_thread to finish if it exists
        if hasattr(self, 'click_thread') and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    Win98Style()
    app = AutoClicker(master=root)
    root.mainloop()