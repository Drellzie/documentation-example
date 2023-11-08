import tkinter as tk
from tkinter import ttk
import numpy as np
import datetime


def read_sample_locs(filename):
    """
    Read sample locations from a file or load preset locations.

    This function attempts to read sample locations from a file. If the file is not found, it loads preset
    locations. It returns the sample locations as a 2D NumPy array.

    Args:
        filename (str): The name of the file to read sample locations from.

    Returns:
        np.ndarray: A 2D NumPy array representing sample locations. The array has a shape of (12, 2).
    """
    try:
        with open(filename, 'rb') as file:
            byte_values = file.read().splitlines()
            byte_values = [byte_value for byte_value in byte_values if byte_value]
            string_values = [byte_value.decode(' utf-8').rstrip('\n') for byte_value in byte_values]
            sample_locations = np.array(string_values).reshape(12, 2)
    except FileNotFoundError:
        print('File not found, loading preset locations')
        sample_locations = [['g229000\r\n', 'g10500\r\n'], ['g229000\r\n', 'g110400\r\n'],
                            ['g229000\r\n', 'g120200\r\n'], ['g229000\r\n', 'g130400\r\n'],
                            ['g229000\r\n', 'g140400\r\n'], ['g229000\r\n', 'g150500\r\n'],
                            ['g222100\r\n', 'g150500\r\n'], ['g222100\r\n', 'g140400\r\n'],
                            ['g222100\r\n', 'g130400\r\n'], ['g222100\r\n', 'g120200\r\n'],
                            ['g222100\r\n', 'g110400\r\n'], ['g222100\r\n', 'g10500\r\n']]

    return sample_locations


def validate(new_text, valid_range):
    """
    Validate user input text based on a valid range.

    This function validates user input text by checking if it's an integer and within the specified valid range.

    Args:
        new_text (str): The text to validate.
        valid_range (tuple): A tuple containing the lower and upper limits of the valid range.

    Returns:
        bool: True if the text is valid within the specified range, False otherwise.
    """
    if not new_text:  # The field is being cleared
        return True

    try:
        guess = int(new_text)
        lower_limit, upper_limit = valid_range
        if lower_limit <= guess <= upper_limit:
            return True
        else:
            return False
    except ValueError:
        return False


def disable_frame(frame):
    """
    Disable all widgets in a frame.

    This function disables all the widgets (children) within a given frame.

    Args:
        frame: The frame containing the widgets to be disabled.
    """
    for child in frame.winfo_children():
        child.configure(state='disable')


def enable_frame(frame):
    """
    Enable all widgets in a frame

    This function enables all the widgets (children) within a given frame.

    Args:
        frame: The frame containing the widgets to be enabled.
    """
    for child in frame.winfo_children():
        child.configure(state='normal')


def convert_camera(camera_get):
    """
    Convert camera selection from a string to an integer.

    This function takes a string representing the camera selection and returns an integer.
    The conversion is done as follows:
    - If the input is 'Left', it returns 0.
    - For any other input, it returns 1.

    Args:
        camera_get (str): A string representing the camera selection ('Left' or 'Right').

    Returns:
        int: 0 if 'Left', 1 for any other input.
    """
    if camera_get == 'Left':
        camera_get = 0
    else:
        camera_get = 1
    return camera_get


class App(tk.Tk):
    """
    Represents the main application.

    This application controls the XY stage and manages sample runs. It provides different pages for interacting with
    the XY stage, setting parameters, and initiating sample runs.

    Methods:
        __init__(self, locations, camera_port, serial, *args, **kwargs): Initialize the application.
        initialise_ui(self): Create and initialize the user interface for the application.
        show_frame(self, cont): Switch the active frame in the application.
        share_values(self): Retrieve selected sample size and skip row values from the Main Page.
        create_runpage(self): Destroys and recreates the Run Page.

    """

    def __init__(self, locations, camera_port, serial, *args, **kwargs):
        """
        Initialize the application.

        This method sets up the main application by initializing variables and creating the user interface elements.

        Args:
            locations (list): A list of sample locations for each camera.
            camera_port (int): The port for the camera connection.
            serial (Serial): The serial communication object for the XY stage.
            *args: Variable length arguments.
            **kwargs: Keyword arguments.
        """
        tk.Tk.__init__(self, *args, **kwargs)

        # Initialise variables
        self.frames = {}
        self.locations = locations
        self.camera_port = camera_port
        self.serial = serial
        self.container = None

        # Set the window title and size
        self.wm_title("XY stage GUI")
        self.geometry("300x250")
        self.resizable(True, True)

        # GUI
        self.initialise_ui()

    def initialise_ui(self):
        """
        Create and initialize the user interface for the application.

        This method sets up the main application window and initializes pages (frames) for different functionalities.
        It allows switching between pages and manages the overall user interface.

        Note:
            The frames for the pages are added to the frame dictionary for easy switching.

        """
        # Create container
        self.container = tk.Frame(self, bg="#8AA7A9")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Add frames to the dictionary
        for F in (MainPage, SidePage, RunPage):
            frame = F(self.container, self)

            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.show_frame(MainPage)

    def show_frame(self, cont):
        """
        Switch the active frame in the application.

        This method switches the currently active frame to the specified frame.

        Args:
            cont: The frame to be displayed.

        """
        frame = self.frames[cont]
        frame.tkraise()  # raises the current frame to the top

    def share_values(self):
        """
        Retrieve selected sample size and skip row values from the Main Page.

        This method retrieves and returns the selected sample size and skip row values from the Main Page.

        Returns:
            tuple: A tuple containing the selected sample size and skip row values.
        """
        sample_size, skip_row = self.frames[MainPage].share_variables()
        return sample_size, skip_row

    def create_runpage(self):
        """
        Create or recreate the RunPage frame.

        This function creates a new instance of the RunPage frame or recreates it if it already exists. If a previous
        instance of RunPage exists, it is removed from the frames dictionary and destroyed to ensure a fresh start.

        The RunPage frame is responsible for configuring and running the sample capturing program. This function
        allows the user to start the program with new settings or restart it.
        """
        # Check if the RunPage frame exists in frames dictionary
        if RunPage in self.frames:
            # If it exists, get the existing instance of RunPage
            frame = self.frames[RunPage]
            # Remove the existing frame from the frames dictionary
            del self.frames[RunPage]
            # Destroy the existing frame
            frame.destroy()

        # Create a new instance of the RunPage frame
        frame = RunPage(self.container, self)
        self.frames[RunPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")


class MainPage(tk.Frame):
    """
    Represents the main page of the application.

    This page allows the user to control the XY stage and initiate sample runs. It provides options for setting the
    sample size and choosing whether to skip the first row during the run.

    Methods:
        __init__(self, parent, controller): Initialize the Main Page.
        create_main_page_ui(self): Create the user interface elements for the Main Page.
        share_variables(self): Retrieve the selected sample size and skip row values.
        run(self): Initiate the sample run by sending the XY stage to the first location.
    """

    def __init__(self, parent, controller):
        """
        Initialize the Main Page.

        This method sets up the Main Page by initializing variables and creating the user interface elements.

        Args:
            parent (tk.Widget): The parent widget to which this page should be attached.
            controller (App): The main application controller.
        """
        tk.Frame.__init__(self, parent, bg='grey')

        # Initialise variables
        self.controller = controller
        self.selected_sample_size = tk.StringVar()
        self.skip_row = tk.IntVar()

        # GUI
        self.create_main_page_ui()

    def create_main_page_ui(self):
        """
        Create the user interface elements for the Main Page.

        This method initializes and organizes various widgets for the Main Page, including labels, buttons, dropdown menus,
        and checkboxes. It provides options for setting the sample size, skipping the first row, and running the sample.

        Note:
            The page also includes a button to switch to the coordinate menu.

        """
        # Page header
        label = tk.Label(self, text="Main Page", bg="grey")
        label.pack(padx=0, pady=0)

        # Frame for the buttons
        button_frame = tk.Frame(self, bg="grey")
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)

        zero_button = tk.Button(
            button_frame,
            text="Zero",
            command=lambda: print(b'z\r\n'),
            height=4,
            bg='dark grey',
        )
        zero_button.pack(side="top", fill=tk.X)

        run_button = tk.Button(
            button_frame,
            text="Run",
            command=lambda: [self.run(), self.controller.show_frame(RunPage)],
            height=4,
            width=20,
            bg='#FBFF00',
            activebackground='#C8CB00'
        )
        run_button.pack(side="left", fill=tk.X)

        # Frame for the topdown menu and label
        options_frame = tk.Frame(button_frame, bg="grey")
        options_frame.pack(fill="both", expand=False, padx=10, pady=10)
        label = tk.Label(options_frame, text="Number of samples:", bg='grey')
        label.pack(side="top")

        # Dropdown menu
        self.selected_sample_size.set("4")
        options = ["4", "6", "8", "10", "12"]
        dropdown_menu = tk.OptionMenu(options_frame, self.selected_sample_size, *options)
        dropdown_menu.pack(side="top", fill=tk.X)

        checkbox = tk.Checkbutton(
            options_frame,
            text='Skip row 1',
            variable=self.skip_row,
            onvalue=1,
            offvalue=0,
            background='grey',
            activebackground='grey'
        )
        checkbox.pack(side='left', padx=15)

        # Switch menu button
        switch_window_button = tk.Button(
            self,
            text="Go to the cooridinate menu",
            command=lambda: self.controller.show_frame(SidePage)
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

    def share_variables(self):
        """
        Retrieve the selected sample size and skip row values.

        Returns:
            tuple: A tuple containing the selected sample size and skip row values.
        """
        return int(self.selected_sample_size.get()), int(self.skip_row.get())

    def run(self):
        """
        Initiate the sample run by sending the XY stage to the first location.

        This method retrieves the first location coordinates and prepares the XY stage to run the samples.
        """
        x, y = self.controller.locations[1][0]
        print(x)
        print(y)


class SidePage(tk.Frame):
    """
    Represents the Coordinate menu page of the application.

    This page allows the user to select a sample, camera, enter and save coordinates,
    and move the XY stage to the specified coordinates.

    Methods:
        __init__(self, parent, controller): Initialize the Coordinate menu page.
        create_side_page_ui(self): Create the user interface elements for the Coordinate menu page.
        go_to(self): Send XY stage commands to move to the specified coordinates.
        set_x_and_y(self, col, row): Set the x and y coordinates based on the provided column and row values.
        on_combobox_change(self, *args): Updates the x and y coordinates when the combobox selection changes.
        update_locs(self): Updates the sample locations and saves them.
        save_locs(self): Saves the sample locations to an external file.
    """

    def __init__(self, parent, controller):
        """
        Initialize the Coordinate menu page.

        This method sets up the Coordinate menu page by initializing variables and creating the user interface elements.

        Args:
            parent (tk.Widget): The parent widget to which this page should be attached.
            controller (App): The main application controller.
        """
        tk.Frame.__init__(self, parent, bg='grey')

        # Variables
        self.controller = controller
        self.location_files = ['samples_loc.txt', 'samples_loc.txt']
        self.selected_sample = tk.StringVar()
        self.selected_camera = tk.StringVar()
        self.y_entry_var = tk.StringVar()
        self.x_entry_var = tk.StringVar()

        # GUI
        self.create_side_page_ui()

    def create_side_page_ui(self):
        """
        Create the user interface elements for the Coordinate menu page.

        This method initializes and organizes various widgets for the Coordinate menu, including labels, Comboboxes,
        Entry fields, and buttons. It sets up sample and camera selection, coordinates input, and action buttons.
        """
        # Page header
        label = tk.Label(self, text="Coordinate menu", bg='grey')
        label.pack(padx=0, pady=0)

        # Select menu frame
        menu_frame = tk.Frame(self, bg='dark gray')
        menu_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Sample number frame
        sample_number_frame = tk.Frame(menu_frame, bg='dark gray')
        sample_number_frame.pack(fill="both", expand=False, padx=5, pady=5, side='left')
        label = tk.Label(sample_number_frame, text="Select sample number:", bg='dark grey')
        label.pack(side="top")

        # Setup variable and validation
        vcmd = (self.register(lambda P, valid_range=(1, 12): validate(P, valid_range)), '%P')
        self.selected_sample.set("1")
        self.selected_sample.trace_add("write", self.on_combobox_change)

        # Generate the options
        options = [str(i) for i in range(1, 13)]

        # Create a combobox with validation
        sample_combobox = ttk.Combobox(
            sample_number_frame,
            textvariable=self.selected_sample,
            values=options,
            validate="key",
            validatecommand=vcmd,
        )
        sample_combobox.pack(side="top", fill=tk.X)

        # Camera number frame
        camera_number_frame = tk.Frame(menu_frame, bg='dark gray')
        camera_number_frame.pack(fill="both", expand=False, padx=5, pady=5, side='left')
        label = tk.Label(camera_number_frame, text="Select camera position:", bg='dark grey')
        label.pack(side="top")

        # Setup variable and validation
        self.selected_camera.set("Right")
        # Create combobox with validation
        options = ["Left", "Right"]
        sample_combobox = tk.OptionMenu(camera_number_frame, self.selected_camera, *options)
        sample_combobox.pack(side="top", fill=tk.X)

        # Coordinate menu frame
        coordinate_frame = tk.Frame(self, bg='dark gray')
        coordinate_frame.pack(fill="both", expand=True, padx=5, pady=5)

        left_frame = tk.Frame(coordinate_frame, bg='dark gray')
        left_frame.pack(fill="both", expand=False, padx=10, pady=5, side='left')

        right_frame = tk.Frame(coordinate_frame, bg='dark gray')
        right_frame.pack(fill="both", expand=False, padx=5, pady=5, side='left')

        # Setup variables and validation
        self.x_entry_var.set('0500')
        self.y_entry_var.set('29000')
        vcmd_x = (self.register(lambda P, valid_range=(0, 59000): validate(P, valid_range)), '%P')
        vcmd_y = (self.register(lambda P, valid_range=(0, 29000): validate(P, valid_range)), '%P')

        # Create x and y entries with lables
        tk.Label(left_frame, text='x-coordinate').pack(side='top')
        x_coordinate_entry = tk.Entry(
            left_frame,
            textvariable=self.x_entry_var,
            validate='key',
            validatecommand=vcmd_x
        )
        x_coordinate_entry.pack(side='top')
        tk.Label(right_frame, text='y-coordinate').pack(side='top')
        y_coordinate_entry = tk.Entry(
            right_frame,
            textvariable=self.y_entry_var,
            validate='key',
            validatecommand=vcmd_y
        )
        y_coordinate_entry.pack(side='top')

        # Create buttons
        go_to_button = tk.Button(
            left_frame,
            text="Go to",
            command=lambda: self.go_to(),
            height=2,
            width=10,
            bg='#00FBFF',
            activebackground='#00C5C8'
        )
        go_to_button.pack(side="bottom", fill=tk.X)

        save_button = tk.Button(
            right_frame,
            text="Save coordinates",
            command=lambda: self.update_locs(),
            height=2,
            width=10,
            bg='#FBFF00',
            activebackground='#C8CB00'
        )
        save_button.pack(side="bottom", fill=tk.X)

        # Switch menu button
        switch_window_button = tk.Button(
            self,
            text="Go to the main Screen",
            command=lambda: self.controller.show_frame(MainPage),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

    def go_to(self):
        """
        Send XY stage commands to move to the specified coordinates.

        This method retrieves the x and y coordinates from the corresponding Entry widgets,
        constructs commands for the XY stage in the 'gXYYY' format, and sends these commands to the XY stage.
        The stage is expected to understand these commands in the 'utf-8' encoding.
        """
        x = self.x_entry_var.get()
        y = self.y_entry_var.get()
        row = f'g2{y}\r\n'
        col = f'g1{x}\r\n'
        self.controller.serial.write(bytes(row, 'utf-8'))
        self.controller.serial.write(bytes(col, 'utf-8'))

    def set_x_and_y(self, col, row):
        """
        Set the x and y coordinates based on the provided column and row values.

        This method extracts numerical x and y coordinates from the given row and column values, removes any
        leading characters, and updates the corresponding Entry widgets with the new values.

        Args:
            col (str): Column values in the format 'g1XXX'.
            row (str): Row values in the format 'g2XXX'.
        """
        co_x = col.strip('g\r\n')[1:]
        co_y = row.strip('g\r\n')[1:]
        self.x_entry_var.set(co_x)
        self.y_entry_var.set(co_y)

    def on_combobox_change(self, *args):
        """
        Updates the x and y coordinates when the combobox selection changes.

        This method is triggered when the user selects a different sample number in the combobox. It updates
        the x and y coordinates based on the selected sample number and camera number.

        Args:
            *args: Variable-length argument list.
        """
        selected_option = self.selected_sample.get()
        if selected_option:
            current_camera = convert_camera(self.selected_camera.get())
            y, x = self.controller.locations[current_camera][int(selected_option) - 1]
            self.set_x_and_y(x, y)

    def update_locs(self):
        """
        Updates the sample locations and saves them.

        This method updates the sample locations for the currently selected camera with the values
        entered by the user in the x and y coordinate input fields. It then saves the updated
        sample locations to an external text file.

        Note:
            The update applies to the sample specified by the user through the sample number and camera
            number selection.
        """
        x = self.x_entry_var.get()
        y = self.y_entry_var.get()
        current_sample = int(self.selected_sample.get()) - 1
        current_camera = convert_camera(self.selected_camera.get())
        row = f'g2{y}'
        col = f'g1{x}'
        self.controller.locations[current_camera][current_sample] = [row, col]
        self.save_locs()

    def save_locs(self):
        """
        Saves the sample locations to an external file.

        This method saves the sample locations for the currently selected camera to an external text file.
        The sample locations include both row and column coordinates.

        Note:
            This method uses the camera number selected by the user to determine the file to write to.
            It encodes and saves each row and column coordinate as separate lines in the file.
        """
        current_camera = convert_camera(self.selected_camera.get())
        with open(self.location_files[current_camera], 'wb') as file:
            for row in self.controller.locations[current_camera]:
                file.write(bytes(f'{row[0]}\r\n', 'utf-8'))
                file.write(bytes(f'{row[1]}\r\n', 'utf-8'))


class RunPage(tk.Frame):
    """
    Represents the 'Run Page' of the application.

    This class defines the user interface and functionality for the 'Run Page' where the user
    can start and control the automated execution of sample collection cycles.

    Args:
        parent (tk.Frame): The parent frame that contains this 'Run Page'.
        controller: The application's main controller, which manages frame transitions.

    Note:
        The method `create_run_page_ui` is called to initialize the graphical user interface elements
        for the 'Run Page.'

    Methods:
        create_run_page_ui(): Initialize the graphical user interface elements for the 'Run Page.'
        run_program(): Start the program execution.
        stop_program(): Stop the program execution.
        run_cycle(): Execute a single cycle of the program.
        goto_and_photo_row(start, end): Move to the specified location and capture photos.
        sleep(time): Pause the program for a specified time.
    """

    def __init__(self, parent, controller):
        """
        Initialize the 'Run Page' of the application.

        Args:
            parent (tk.Frame): The parent frame that contains this 'Run Page'.
            controller: The application's main controller, which manages frame transitions.

        Note:
            The method `create_run_page_ui` is called to initialize the graphical user interface elements for the 'Run Page.'
        """
        tk.Frame.__init__(self, parent, bg='grey')

        # Variables
        self.controller = controller
        self.count = 0
        self.sample_name = 0
        self.phase_duration = tk.StringVar()
        self.phase1_interval = tk.StringVar()
        self.phase2_interval = tk.StringVar()
        self.running = False
        self.start_time = None
        self.info_label = None
        self.run_button = None
        self.frame3 = None
        self.frame2 = None
        self.frame1 = None

        # GUI
        self.create_run_page_ui()

    def create_run_page_ui(self):
        """
        Create the user interface elements for the 'Run Page'.

        This method initializes and organizes the user interface elements for the 'Run Page' of the application.
        It includes the page header, an information label, a button for starting and stopping the program,
        input fields for setting phase duration and intervals, and a button for switching back to the main screen.

        The user can configure phase settings, start and stop the program, and navigate between screens.

        Note:
            The phase duration and interval values are set to default values.
        """
        # Page header
        label = tk.Label(self, text="Run Page", bg='grey')
        label.pack(side='top')

        # INFO label
        self.info_label = tk.Label(
            self,
            text="Wait for the XY stage to stop moving \nThen press start",
            bg='white',
            borderwidth=1,
            relief="solid",
            padx=5,
            pady=5
        )
        self.info_label.pack(side='top')

        # Frame for the button
        button_frame = tk.Frame(self, bg="grey")
        button_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.run_button = tk.Button(
            button_frame,
            text="Start",
            height=4,
            background='#2ECC71',
            activebackground='#186A3B',
            command=lambda: self.run_program()
        )
        self.run_button.pack(side="top", fill=tk.X)

        # Set variables
        self.phase_duration.set('30')
        self.phase1_interval.set('5')
        self.phase2_interval.set('30')

        # Run options
        self.frame1 = self.create_label_entry_label('Fast phase duration', ' Hours', self.phase_duration)
        self.frame2 = self.create_label_entry_label('Fast phase interval', '    Min', self.phase1_interval)
        self.frame3 = self.create_label_entry_label('Slow phase interval', '    Min', self.phase2_interval)

        # Switch menu button
        switch_window_button = tk.Button(
            self,
            text="Go to the main Screen",
            command=lambda: self.controller.show_frame(MainPage),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)

    def create_label_entry_label(self, label1, label2, entry):
        """
        Create a label-entry-label widget for user input.

        This method creates a compound widget with a label, an entry field, and another label, organized
        horizontally for user input. The labels provide context, and the entry field allows users to enter
        values.

        Args:
            label1 (str): The text to display on the first label.
            label2 (str): The text to display on the second label.
            entry (tk.StringVar): A Tkinter StringVar variable linked to the entry field for user input.

        Returns:
            tk.Frame: A Tkinter frame containing the label-entry-label widget.

        Note:
            The entry field's content is validated to ensure that entered values are within the specified
            valid range.
        """
        singular_frame = tk.Frame(self, bg='white')
        singular_frame.pack(fill='both', expand=True)

        label1 = tk.Label(singular_frame, text=label1, bg='white')
        label1.pack(side='left', padx=10)

        label2 = tk.Label(singular_frame, text=label2, bg='white')
        label2.pack(side='right')

        vcmd = (self.register(lambda P, valid_range=(0, 1000000): validate(P, valid_range)), '%P')
        entry = tk.Entry(
            singular_frame,
            textvariable=entry,
            validate='key',
            validatecommand=vcmd
        )
        entry.pack(side='right', padx=5)
        return singular_frame

    def run_program(self):
        """
        Start the sample capturing program.

        This method initiates the sample capturing program, begins capturing samples according to the
        user's configuration, and updates the user interface elements to reflect the program's status.

        Note:
            Start once the XY stage has stopped moving. Do not start the program until the previous loop has finished.
        """
        # Reconfigure run button
        self.run_button.config(
            text='Stop',
            background='#E74C3C',
            activebackground='#943126',
            command=lambda: [self.stop_program(), self.controller.show_frame(MainPage)]
        )
        # Update INFO and disable options
        self.info_label['text'] = f'Program running. \n{self.count} cycles made'
        disable_frame(self.frame1)
        disable_frame(self.frame2)
        disable_frame(self.frame3)

        # Start loop
        self.running = True
        self.start_time = datetime.datetime.now()
        self.run_cycle()

    def stop_program(self):
        """
        Stop the sample capturing program.

        This method stops the sample capturing program, resets the user interface elements, and allows
        the user to configure new capture settings or restart the program. It also recreates the RunPage frame
        to reinitialize all variables and settings for a fresh start.
        """
        # Reconfigure run button
        self.run_button.config(
            text='Start',
            background='#2ECC71',
            activebackground='#186A3B',
            command=lambda: self.run_program()
        )
        # Update INFO and enable options
        self.info_label['text'] = 'Wait for the XY stage to stop moving \nThen press start'
        enable_frame(self.frame1)
        enable_frame(self.frame2)
        enable_frame(self.frame3)

        # Destroy the run page frame and makes a new one. This reinitilises all variables.
        self.controller.create_runpage()

    def run_cycle(self):
        """
        Execute a cycle of the sample capturing process.

        This method performs a cycle of sample capturing. It moves the XY stage to capture photos
        of samples, updates the cycle count, and handles sleep intervals based on user-defined
        phase durations. The cycle continues until the program is stopped.

        Note:
            Before using this method, ensure that the XY stage and camera are properly configured.
        """
        if self.running:
            # Load variables
            sample_size, skip_row1 = self.controller.share_values()
            self.sample_name = 1
            cols = sample_size // 2

            # Update INFO
            self.count += 1
            self.info_label['text'] = f'Program running \nCycle number: {self.count}'

            self.sleep(0)
            # Run route
            self.goto_and_photo_row(skip_row1, cols + skip_row1)
            self.goto_and_photo_row(12 - skip_row1 - cols, 12 - skip_row1)

            time_now = datetime.datetime.now()
            # Sleep
            if (time_now - self.start_time) < datetime.timedelta(hours=int(self.phase_duration.get())):
                self.sleep(max(int(self.phase1_interval.get()) * 60 - (sample_size * 25), 0))
            else:
                self.sleep(max(int(self.phase2_interval.get()) * 60 - (sample_size * 25), 0))

            # Restart loop
            self.after(1000, self.run_cycle)

    def goto_and_photo_row(self, start, end):
        """
        Move to specific locations and capture photos of samples.

        This method iterates through a range of sample locations, moves the XY stage to the specified
        row and column, captures photos of the samples, and increments the sample name.

        Parameters:
            start (int): The starting index of the sample locations to visit.
            end (int): The ending index of the sample locations to visit.

        Note:
            Before using this method, ensure that the XY stage and camera are properly configured.
        """
        for i in range(start, end):
            if self.running:
                row, col = self.controller.locations[1][i]
                # self.controller.serial.write(bytes(f'{row}\r\n', 'utf-8'))
                self.sleep(0.5)
                # self.controller.serial.write(bytes(f'{col}\r\n', 'utf-8'))
                self.sleep(1)
                # PhotoApp.imgcap(f"samp{sample_name}", self.controller.camera_port)
                print('Going')
                self.sample_name += 1
                self.sleep(0)

    def sleep(self, time):
        """
        Sleeps for a specified amount of time in seconds.
        This method is used to pause program execution for a given duration.

        Parameters:
            time (float): The duration to sleep in seconds.

        """
        ms = int(time * 1000)
        var = tk.IntVar()
        self.after(ms, var.set, 1)
        self.wait_variable(var)
