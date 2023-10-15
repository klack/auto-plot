from ThreadedCommandRunner import ThreadedCommandRunner
import psutil

DST_PATH = '/chia/dst/'
MIN_HDD_SPACE = 109 #TB

# Log output
def log(str):
    print(str)
    
# Callback used by ThreadedCommandRunner
def output_callback(line):
    log(line)  # Example: Print live output

# Get hard drive size in gigabytes
def get_hard_drive_size(drive_path='/'):
    try:
        partition = psutil.disk_usage(drive_path)
        total_size = partition.total / (1024 ** 3)  # Convert bytes to gigabytes
        return total_size
    except Exception as e:
        log(f"Error: {str(e)}")

# Runs a single threaded command and returns the exit code
def run_command(cmd):
    command_runner = ThreadedCommandRunner(cmd)
    command_runner.start(output_callback)
    command_runner.wait()  # Wait for the command to finish
    exit_code = command_runner.exit_code
    log(f"Command exit code: {exit_code}")
    command_runner.stop() # Cleanup resources
    return exit_code

# Plot one plot
def plot():
    log("Plotting a plot")
    cmd = f"chia_plot -n -1 -r 32 -t /chia/tmp/1/ -2 /chia/tmp/2/ -d {DST_PATH} -p 8c70cc58a37cc8f68b916fac8101e637ba999be58383e836335ab07f0524c2c09f2db9cee83c88f731ee7b40381a0eac -f b1833b2ff7c1b2a87654c93b3af6d07a1788b5edee7036e878b64a1b22ecfa7ba608152f1b368404037cef29fad1438a"
    return run_command(cmd)   

# Clear temporary files used by madmax
def clear_tmp():
    log("Clearing tmp files")
    cmd = "find /chia/tmp/1/ -mindepth 1 -delete && find /chia/tmp/2/ -mindepth 1 -delete"
    return run_command(cmd)

# Format a drive and create a partition in exFat format labeled PLOTS
def format_disk():
    cmd = "/home/klack/auto-plot/format_disk.sh"
    return run_command(cmd)

# Check if a drive is mounted by path
def is_drive_mounted(drive_path):
    partitions = psutil.disk_partitions(all=True)
    drive_path = drive_path.rstrip('\\/')

    for partition in partitions:
        if partition.mountpoint.rstrip('\\/') == drive_path:
            log(f"{drive_path} is mounted")
            return True
    log(f"Drive is not mounted")
    return False

def folder_exists(folder_path):
    return os.path.exists(folder_path) and os.path.isdir(folder_path)

def drive_is_attached():
    return folder_exists("/dev/chiadst") # chiadst only exists when udev detects a drive attached to port 5

def plot_partition_exists():
    return folder_exists("/dev/disk/by-label/PLOTS")

def unmount():
    cmd = "umount /dev/chiadst"
    return run_command(cmd)

# Check if there is enough free space on the mounted drive
def is_space_for_plot():
    log(f"Checking drive space")
    mounted = is_drive_mounted(DST_PATH)
    size = get_hard_drive_size(DST_PATH)
    if mounted and size > MIN_HDD_SPACE:
        log(f"Free space: {size}")
        return True   
    if not mounted:
        log(f"{DST_PATH} is not mounted")
        return False
    else:
        log(f"Not enough space on {DST_PATH}: {size}")
        return False

def prepare_hdd():
    if drive_is_attached():
        if plot_partition_exists():
            return True
        else:
            exit_code = format_disk()
            if exit_code == 0:
                return True
            else:
                return False
    else:
        log(f"No drive attached")
        return False

def loop():
    if prepare_hdd():
        clear_tmp()
        while is_space_for_plot():
            exit_code = plot()
            if exit_code != 0:
                log("Recieved non zero exit code")
                break
            # unmount disk and alert user
        log("Stopping plotting")
    else:
        log("Failed Preparing HDD")

loop()