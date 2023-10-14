from ThreadedCommandRunner import ThreadedCommandRunner
import psutil

DST_PATH = '/chia/dst/'
MIN_HDD_SPACE = 109

def log(str):
    print(str)
    
def output_callback(line):
    print(line)  # Example: Print live output

def get_hard_drive_size(drive_path='/'):
    try:
        partition = psutil.disk_usage(drive_path)
        total_size = partition.total / (1024 ** 3)  # Convert bytes to gigabytes
        return total_size
    except Exception as e:
        print(f"Error: {str(e)}")

def run_command(cmd):
    command_runner = ThreadedCommandRunner(cmd)
    command_runner.start(output_callback)
    command_runner.wait()  # Wait for the command to finish
    exit_code = command_runner.exit_code
    print(f"Command exit code: {exit_code}")
    command_runner.stop() # Cleanup resources
    return exit_code

def plot():
    cmd = f"chia_plot -n -1 -r 32 -t /chia/tmp/1/ -2 /chia/tmp/2/ -d {DST_PATH} -p 8c70cc58a37cc8f68b916fac8101e637ba999be58383e836335ab07f0524c2c09f2db9cee83c88f731ee7b40381a0eac -f b1833b2ff7c1b2a87654c93b3af6d07a1788b5edee7036e878b64a1b22ecfa7ba608152f1b368404037cef29fad1438a"
    return run_command(cmd)   

def clear_tmp():
    cmd = "find /chia/tmp/1/ -mindepth 1 -delete && find /chia/tmp/2/ -mindepth 1 -delete"
    return run_command(cmd)

def format_disk():
    cmd = "/home/klack/auto-plot/format_disk.sh"
    return run_command(cmd)

def is_drive_mounted(drive_path):
    partitions = psutil.disk_partitions(all=True)
    drive_path = drive_path.rstrip('\\/')

    for partition in partitions:
        if partition.mountpoint.rstrip('\\/') == drive_path:
            print(f"{drive_path} is mounted")
            return True
    print(f"Drive is not mounted")
    return False

def is_space_for_plot():
    print(f"Checking drive space")
    mounted = is_drive_mounted(DST_PATH)
    size = get_hard_drive_size(DST_PATH)
    if mounted and size > MIN_HDD_SPACE:
        print(f"Free space: {size}")
        return True   
    if not mounted:
        return False
    else:
        print(f"Not enough space on {DST_PATH}: {size}")
        return False

def loop():
    clear_tmp()
    # should disk be formatted?
        # is the drive attached?
        # partition named PLOTS exists
            # no
        # else yes      
    # while is_space_for_plot():
    plot()
    
    # unmount disk and alert user

loop()
# forma_disk()
# clear_tmp()
# plot()
