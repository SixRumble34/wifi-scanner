import platform
import re
import subprocess


def is_windows():
    """Check if the script is running on Windows."""
    return platform.system() == "Windows"


def create_network_entry(ssid, signal, security):
    """Create a formatted Wi-Fi network entry."""
    if security and "Open" in security:
        password_protected = "No"
    elif security:
        password_protected = "Yes"
    else:
        password_protected = "Unknown"

    return (
        ssid,
        signal or "Unknown",
        security or "Unknown",
        password_protected,
    )


def scan_wifi_windows():
    """Scan for available Wi-Fi networks on Windows."""
    if not is_windows():
        print("This scanner can only run on Windows.")
        return []

    try:
        result = subprocess.run(
            [
                "netsh",
                "wlan",
                "show",
                "networks",
                "mode=bssid",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except FileNotFoundError:
        print("\nError: 'netsh' could not be found.")
        return []

    if result.returncode != 0:
        print("\nError scanning Wi-Fi networks:")
        print(result.stderr.strip())
        return []

    networks = []

    ssid_pattern = re.compile(
        r"SSID\s+\d+\s+:\s(.*)"
    )
    signal_pattern = re.compile(
        r"Signal\s+:\s(\d+)%"
    )
    security_pattern = re.compile(
        r"Authentication\s+:\s(.+)"
    )

    ssid = None
    signal = None
    security = None

    for line in result.stdout.splitlines():
        ssid_match = ssid_pattern.search(line)

        if ssid_match:
            if ssid is not None:
                networks.append(
                    create_network_entry(
                        ssid,
                        signal,
                        security,
                    )
                )

            ssid = ssid_match.group(1).strip()

            if not ssid:
                ssid = "<Hidden Network>"

            signal = None
            security = None

            continue

        signal_match = signal_pattern.search(line)

        if signal_match:
            signal = signal_match.group(1) + "%"
            continue

        security_match = security_pattern.search(line)

        if security_match:
            security = security_match.group(1).strip()

    if ssid is not None:
        networks.append(
            create_network_entry(
                ssid,
                signal,
                security,
            )
        )

    return networks


def display_results(networks):
    """Display available Wi-Fi networks."""
    print("\n===================================")
    print("Detected Wi-Fi Networks")
    print("===================================")

    if not networks:
        print("No Wi-Fi networks found.")
        return

    for index, network in enumerate(networks, start=1):
        ssid, signal, security, password_protected = network

        print(
            f"{index}. "
            f"SSID: {ssid} | "
            f"Signal: {signal} | "
            f"Security: {security} | "
            f"Password Protected: {password_protected}"
        )


def get_current_wifi_connection():
    """Get information about the current Wi-Fi connection."""
    if not is_windows():
        return None

    try:
        result = subprocess.run(
            [
                "netsh",
                "wlan",
                "show",
                "interfaces",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except FileNotFoundError:
        print("\nError: 'netsh' could not be found.")
        return None

    if result.returncode != 0:
        print("\nError retrieving Wi-Fi connection.")
        return None

    state_pattern = re.compile(
        r"^\s*State\s*:\s*(.+)$",
        re.IGNORECASE,
    )
    ssid_pattern = re.compile(
        r"^\s*SSID\s*:\s*(.+)$",
        re.IGNORECASE,
    )
    signal_pattern = re.compile(
        r"^\s*Signal\s*:\s*(\d+)%$",
        re.IGNORECASE,
    )
    security_pattern = re.compile(
        r"^\s*Authentication\s*:\s*(.+)$",
        re.IGNORECASE,
    )

    connection = {
        "ssid": "Unknown",
        "state": "Unknown",
        "signal": "Unknown",
        "security": "Unknown",
        "password_protected": "Unknown",
    }

    for line in result.stdout.splitlines():
        state_match = state_pattern.search(line)

        if state_match:
            connection["state"] = state_match.group(1).strip()
            continue

        ssid_match = ssid_pattern.search(line)

        if ssid_match:
            connection["ssid"] = ssid_match.group(1).strip()
            continue

        signal_match = signal_pattern.search(line)

        if signal_match:
            connection["signal"] = signal_match.group(1) + "%"
            continue

        security_match = security_pattern.search(line)

        if security_match:
            connection["security"] = security_match.group(1).strip()

    security = connection["security"]

    if security == "Unknown":
        connection["password_protected"] = "Unknown"
    elif "Open" in security:
        connection["password_protected"] = "No"
    else:
        connection["password_protected"] = "Yes"

    return connection


def display_current_connection():
    """Display information about the current Wi-Fi connection."""
    connection = get_current_wifi_connection()

    print("\n===================================")
    print("Current Wi-Fi Connection")
    print("===================================")

    if not connection:
        print("Unable to retrieve connection.")
        return

    print(f"SSID:               {connection['ssid']}")
    print(f"State:              {connection['state']}")
    print(f"Signal:             {connection['signal']}")
    print(f"Security:           {connection['security']}")
    print(
        f"Password Protected: "
        f"{connection['password_protected']}"
    )


def return_to_menu():
    """Pause before returning to the main menu."""
    input("\nPress Enter to return to menu...")


def main():
    """Run the Windows Wi-Fi Scanner."""
    if not is_windows():
        print("This program is designed for Windows.")
        return

    while True:
        print("\n===================================")
        print("       Windows Wi-Fi Scanner")
        print("===================================")
        print("1. Scan Available Wi-Fi")
        print("2. Current Wi-Fi Connection")
        print("3. Exit")

        choice = input("\nSelect: ").strip()

        if choice == "1":
            print("\nScanning...")
            print("Please wait...")

            networks = scan_wifi_windows()
            display_results(networks)
            return_to_menu()

        elif choice == "2":
            display_current_connection()
            return_to_menu()

        elif choice == "3":
            print("\nExiting...")
            break

        else:
            print("\nInvalid selection.")
            return_to_menu()


if __name__ == "__main__":
    main()