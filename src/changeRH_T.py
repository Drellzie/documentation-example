import datetime
import serial
import os

# Constants
serial_settings = {
    'pid': {'port': '/dev/ttyACM2', 'baudrate': 115200},
    'tcs': {'port': '/dev/ttyACM2', 'baudrate': 9600},
    'tsl': {'port': '/dev/ttyACM2', 'baudrate': 19200},
}

log_directory = '/home/afmlab/Documents/User/'


def generate_filenames(settings):
    """
    Generate log file names for each device based on the current time.

    Parameters:
        settings (dict): A dictionary of serial port settings for each device.

    Returns:
        dict: A dictionary where keys are device names and values are corresponding log file paths.
    """
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%T')
    return {device: os.path.join(log_directory, f"{device}-{current_time}.log") for device in settings}


def create_file(file_path):
    """
    Create an empty log file at the specified path.

    Parameters:
        file_path (str): The path to the log file.
    """
    with open(file_path, 'w') as logfile:
        logfile.write(" ")


def write_log(ser, file_path):
    """
    Read data from a serial port and write it to the log file.

    Parameters:
        ser (serial.Serial): The serial port to read data from.
        file_path (str): The path to the log file.
    """
    data = ser.readline().decode('utf-8')
    time_now = datetime.datetime.now()
    cur_data = f"{time_now}, {data}"
    if len(data) > 0:
        with open(file_path, 'a') as logfile:
            logfile.write(cur_data)
        print(f"Reading: {cur_data}")


def wait_and_write(wait_time_hours, serials):
    """
    Wait for a specified time and write data to the log files for each device.

    Parameters:
        wait_time_hours (int): The duration to wait in hours.
        serials (dict): A dictionary where keys are device names and values are serial ports.
    """
    wait_time = datetime.timedelta(hours=wait_time_hours)
    start = datetime.datetime.now()
    now = start
    while (now - start) < wait_time:
        for device, serial_port in serials.items():
            write_log(serial_port, file_paths[device])
        now = datetime.datetime.now()


def set_set_point(set_point, this_serial, command):
    """
    Set a set point (humidity or temperature) on the device.

    Parameters:
        set_point (float): The set point value to be set.
        this_serial (serial.Serial): The serial port of the device.
        command (str): The command to set the set point (e.g., 'sh' for humidity, 'st' for temperature).
    """
    encoded_command = f'{command}{set_point}\r\n'
    this_serial.write(encoded_command.encode('utf-8'))


if __name__ == "__main":
    file_paths = generate_filenames(serial_settings)
    serial_ports = {dir_name: serial.Serial(port=info['port'], baudrate=info['baudrate'], timeout=2) for dir_name, info
                    in serial_settings.items()}
    wait_and_write(10, serial_ports)
