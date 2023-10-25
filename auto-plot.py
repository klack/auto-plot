from ThreadedCommandRunner import ThreadedCommandRunner
import psutil, os, time

DST_PATH = '/chia/dst/'
MIN_HDD_SPACE = 109 #GB

# Log output
def log(str, end="\n", flush=False):
    print(str, end="\n", flush=flush)
    
# Callback used by ThreadedCommandRunner
def output_callback(line):
    log(line)  # Example: Print live output

def get_free_space_gb(path='/'):
    disk_info = psutil.disk_usage(path)
    free_space_gb = disk_info.free / (2**30)  # Convert bytes to gigabytes
    return free_space_gb

# Runs a single threaded command and returns the exit code
def run_command(cmd):
    log(f"Running command: {cmd}")
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
    cmd = (f"/opt/chia-plotter/build/chia_plot -n 1 -r 32 -t /chia/tmp/1/ -2 /chia/tmp/2/ -d {DST_PATH} -p 8c70cc58a37cc8f68b916fac8101e637ba999be58383e836335ab07f0524c2c09f2db9cee83c88f731ee7b40381a0eac -f b1833b2ff7c1b2a87654c93b3af6d07a1788b5edee7036e878b64a1b22ecfa7ba608152f1b368404037cef29fad1438a")
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
            # log(f"{drive_path} is mounted")
            return True
    # log(f"Drive is not mounted")
    return False

# Check if a path exists
def path_exists(folder_path):
    return os.path.exists(folder_path)

# Check if destination drive is attached
def drive_is_attached():
    return path_exists("/dev/chiadst") # chiadst only exists when udev detects a drive attached to port 5

# Check of the plot partition exists on the destination drive
def plot_partition_exists():
    return path_exists("/dev/disk/by-label/PLOTS")

# Remount drives
def remount():
    cmd = "mount -a"
    return run_command(cmd)

# Unmount a drive
def unmount():
    cmd = "umount /dev/chiadst1 && rm /dev/chiadst"
    return run_command(cmd)

# Check if there is enough free space on the mounted drive
def is_space_for_plot():
    log(f"Checking drive space")
    mounted = is_drive_mounted(DST_PATH)
    free = get_free_space_gb(DST_PATH)
    if mounted and free > MIN_HDD_SPACE:
        log(f"Free space: {free}")
        return True   
    if not mounted:
        log(f"{DST_PATH} is not mounted")
        return False
    else:
        log(f"Not enough space on {DST_PATH}: {free}")
        return False

# Checks if hard drive is formated, format if not
def prepare_hdd():
    if drive_is_attached():
        if plot_partition_exists():
            log(f"Drive is already prepared")
            return True
        else:
            log(f"Formatting disk")
            exit_code = format_disk()
            if exit_code == 0:
                return True
            else:
                return False
    else:
        log(f"No drive attached")
        return False

def plot_until_full():
    if prepare_hdd():
        time.sleep(10)
        remount()
        clear_tmp()
        while is_space_for_plot():
            exit_code = plot()
            if exit_code != 0:
                log("Recieved non zero exit code")
                return
        log("No more space, stopping plotting")
    else:
        log("Hard drive is not prepared")

def wait_for_hdd():
    log("Waiting for drive to be attached")
    while not drive_is_attached():
        time.sleep(10)
        print(".", end="", flush=True)
    log("No longer waiting")

# Main program loop
while True:    
    plot_until_full()
    unmount()
    wait_for_hdd()
    #TODO prune plots under correct size
    