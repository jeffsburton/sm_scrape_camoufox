import asyncio
import subprocess
import sys
import time

# Assuming Profile dataclass is available from a file named 'profile.py'
from profile import Profile

# Define the path to the Private Internet Access command-line tool.
# Please ensure this path is correct for your installation.
VPN_PATH = 'C:\\Program Files\\Private Internet Access\\piactl.exe'

async def _run_piactl_command(args: list[str]) -> tuple[str, str]:
    """
    Helper to run piactl commands asynchronously.
    It hides the console window on Windows and raises an exception if the command fails
    or if piactl.exe is not found.

    Args:
        args: A list of string arguments to pass to piactl.exe.

    Returns:
        A tuple containing the standard output (stdout) and standard error (stderr)
        of the command as strings.

    Raises:
        FileNotFoundError: If piactl.exe cannot be found at the specified VPN_PATH.
        Exception: If the piactl command exits with a non-zero status code or
                   an unexpected error occurs during execution.
    """
    creation_flags = 0
    if sys.platform == "win32":
        # Use subprocess.CREATE_NO_WINDOW to prevent a console window from appearing
        # when piactl.exe is executed on Windows.
        creation_flags = subprocess.CREATE_NO_WINDOW

    try:
        # Create a subprocess to run the piactl command.
        # stdout and stderr are piped to capture their output.
        process = await asyncio.create_subprocess_exec(
            VPN_PATH,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=creation_flags
        )

        # Wait for the command to complete and capture its output.
        stdout_data, stderr_data = await process.communicate()

        # Decode stdout and stderr from bytes to string.
        # 'errors="ignore"' is used for robustness to handle potential
        # non-UTF-8 characters in the output.
        stdout = stdout_data.decode(errors='ignore').strip()
        stderr = stderr_data.decode(errors='ignore').strip()

        # If the command exited with a non-zero return code, it indicates an error.
        if process.returncode != 0:
            raise Exception(
                f"Command '{VPN_PATH} {' '.join(args)}' failed with exit code {process.returncode}. Stderr: {stderr}"
            )

        return stdout, stderr
    except FileNotFoundError:
        # Specifically catch if the piactl.exe executable itself is not found.
        raise FileNotFoundError(
            f"'{VPN_PATH}' not found. Please ensure Private Internet Access is installed "
            "and the VPN_PATH constant is set correctly."
        )
    except Exception as e:
        # Catch any other general exceptions that might occur during subprocess creation or communication.
        raise Exception(f"An unexpected error occurred while running piactl command: {e}")

async def _get_connection_state() -> str:
    """
    Retrieves the current VPN connection state using 'piactl.exe get connectionstate'.

    Returns:
        A string representing the current connection state (e.g., "Connected", "Disconnected").
        Returns "Unknown" if there's an error in retrieving the state.
    """
    try:
        # Run the command to get the connection state.
        stdout, _ = await _run_piactl_command(["get", "connectionstate"])
        return stdout
    except Exception as e:
        print(f"Warning: Could not retrieve VPN connection state: {e}")
        return "Unknown"

async def _wait_for_connection_state(target_state: str, timeout_seconds: int = 60) -> bool:
    """
    Waits for the VPN connection state to reach the specified `target_state`
    within a given timeout period.

    Args:
        target_state: The desired VPN connection state (e.g., "Connected", "Disconnected").
        timeout_seconds: The maximum number of seconds to wait for the state change.

    Returns:
        True if the `target_state` is reached within the timeout, False otherwise.
    """
    start_time = time.monotonic() # Use monotonic time for reliable duration calculation.
    # print(f"Waiting for VPN connection state to become '{target_state}'...")
    while time.monotonic() - start_time < timeout_seconds:
        current_state = await _get_connection_state()
        if current_state == target_state:
            # print(f"VPN state is now '{target_state}'.")
            return True
        # Wait for a short period before checking the state again to avoid busy-waiting.
        await asyncio.sleep(2)
    print(f"Timeout: VPN state did not become '{target_state}' within {timeout_seconds} seconds.")
    return False

async def disconnect_vpn() -> None:
    """
    Disconnects the VPN connection using 'piactl.exe disconnect' and waits
    until the connection state is confirmed as "Disconnected".

    Raises:
        Exception: If the disconnection command fails, or if the VPN
                   does not transition to "Disconnected" state within the timeout.
    """
    # print("Attempting to disconnect VPN...")
    try:
        # Issue the disconnect command with a 20-second timeout.
        stdout, stderr = await _run_piactl_command(["-t", "20", "disconnect"])
        if stderr:
            print(f"PIACTL disconnect command output (stderr): {stderr}")

        # Wait for the VPN to actually disconnect.
        if not await _wait_for_connection_state("Disconnected"):
            raise Exception("Failed to verify VPN disconnected within the timeout.")
        # print("VPN disconnected successfully.")
    except Exception as e:
        print(f"Error during VPN disconnection: {e}")
        raise # Re-raise the exception to propagate the failure.

async def connect_and_verify(profile: Profile) -> None:
    """
    Connects to the VPN using 'piactl.exe' for the given profile and verifies the connection.
    This function first ensures the VPN is disconnected, then sets the region based on
    the profile's `code`, initiates the connection, and waits for the "Connected" state.
    It includes an additional safety sleep as in your original Node.js code.

    Args:
        profile: An instance of the Profile dataclass containing VPN details.

    Raises:
        Exception: If any step of the connection process (disconnect, set region, connect,
                   or verification) fails or times out.
    """
    # print(f"Initiating VPN connection for profile: {profile.profile} (City: {profile.city}, Code: {profile.code})...")
    try:
        # 1. Ensure the VPN is disconnected to have a clean state before connecting.
        await disconnect_vpn()

        # 2. Set the VPN region according to the profile's city code.
        # print(f"Setting VPN region to '{profile.code}'...")
        stdout, stderr = await _run_piactl_command(["set", "region", profile.code])
        if stderr:
            print(f"PIACTL set region command output (stderr): {stderr}")

        # 3. Connect to the VPN.
        # print("Issuing VPN connect command...")
        # '-t 20' sets a 20-second timeout for the connect command.
        stdout, stderr = await _run_piactl_command(["-t", "20", "connect"])
        if stderr:
            # Note: stderr isn't always an error; some CLIs output info/warnings here.
            print(f"PIACTL connect command output (stderr): {stderr}")

        # 4. Wait for the VPN to report a "Connected" state.
        if not await _wait_for_connection_state("Connected"):
            raise Exception("VPN did not connect successfully within the timeout.")

        # print("VPN connection established. Waiting for 6 seconds for safety...")
        # 5. A small additional delay for safety, mirroring your Node.js implementation.
        await asyncio.sleep(6)
        # print("VPN connected and verified successfully.")

    except Exception as e:
        print(f"Failed to connect and verify VPN: {e}")
        raise # Re-raise the exception to propagate the failure.

# Example Usage (uncomment the following section to test this code):
# You would typically call these functions from an asyncio event loop.
#
# async def main():
#     # Create a dummy profile instance for testing purposes
#     test_profile = Profile(
#         profile="TestProfile",
#         city="Dallas",
#         code="us_dallas", # Use a valid PIA region code for testing
#         timezone="America/Chicago",
#         vpn_extra="", vpn="", password="", recovery="", browser="",
#         proxy_address="", proxy_port=0, proxy_username="", proxy_password=""
#     )
#
#     try:
#         # Attempt to connect to the VPN
#         await connect_and_verify(test_profile)
#         print("\nSuccessfully connected and verified VPN. Waiting for 10 seconds before disconnecting...")
#
#         # Keep the VPN connected for a short duration
#         await asyncio.sleep(10)
#
#         # Attempt to disconnect the VPN
#         await disconnect_vpn()
#         print("\nSuccessfully disconnected VPN.")
#     except Exception as e:
#         print(f"\nAn error occurred during the VPN operation: {e}")
#
# if __name__ == "__main__":
#     # Run the asynchronous main function.
#     asyncio.run(main())