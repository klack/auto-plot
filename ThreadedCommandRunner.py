import subprocess
import threading

class ThreadedCommandRunner:
    def __init__(self, command):
        self.command = command
        self.process = None
        self.output = []
        self.exit_code = None
        self.is_running = False
        self.output_callback = None

    def _run_command(self):
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            self.is_running = True

            while self.is_running:
                line = self.process.stdout.readline()
                if line == "":
                    break
                self.output.append(line.strip())
                if self.output_callback:
                    self.output_callback(line.strip())

            self.process.wait()
            self.exit_code = self.process.returncode
            self.is_running = False
        except Exception as e:
            self.exit_code = -1
            self.output.append(f"Error: {str(e)}")

    def start(self, output_callback=None):
        """
        Start the execution of the command.
        :param output_callback: A callback function to handle live output (optional).
        """
        self.output_callback = output_callback
        self.thread = threading.Thread(target=self._run_command)
        self.thread.start()

    def wait(self):
        """
        Wait for the command to finish execution.
        """
        if self.thread:
            self.thread.join()

    def stop(self):
        """
        Stop the execution of the command (if running).
        """
        if self.process and self.is_running:
            try:
                self.process.terminate()
                self.process.wait()
            except Exception as e:
                pass  # Handle exceptions if needed

if __name__ == "__main__":
    def output_callback(line):
        print(line)  # Example: Print live output

    command_runner = ThreadedCommandRunner("your_shell_command_here")
    command_runner.start(output_callback)

    # You can perform other tasks while the command is running

    command_runner.wait()  # Wait for the command to finish
    exit_code = command_runner.exit_code
    print(f"Command exit code: {exit_code}")

    # Cleanup resources
    command_runner.stop()
    