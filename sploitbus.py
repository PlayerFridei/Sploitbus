# Created by PlayerFridei
# Version 0.1 Early Testing

import sys
import logging
import random
import readline  # For command history and up arrow functionality
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from prettytable import PrettyTable
import socket
import time
import shtab
from argparse import ArgumentParser
from colorama import init, Fore, Style

# Initialize colorama
init()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def read_coils(client, address, count):
    try:
        result = client.read_coils(address, count)
        if result.isError():
            logging.error(f"Failed to read coils: {result}")
            return []
        return result.bits
    except ModbusException as e:
        logging.error(f"Exception while reading coils: {e}")
        return []

def read_discrete_inputs(client, address, count):
    try:
        result = client.read_discrete_inputs(address, count)
        if result.isError():
            logging.error(f"Failed to read discrete inputs: {result}")
            return []
        return result.bits
    except ModbusException as e:
        logging.error(f"Exception while reading discrete inputs: {e}")
        return []

def read_holding_registers(client, address, count):
    try:
        result = client.read_holding_registers(address, count)
        if result.isError():
            logging.error(f"Failed to read holding registers: {result}")
            return []
        return result.registers
    except ModbusException as e:
        logging.error(f"Exception while reading holding registers: {e}")
        return []

def read_input_registers(client, address, count):
    try:
        result = client.read_input_registers(address, count)
        if result.isError():
            logging.error(f"Failed to read input registers: {result}")
            return []
        return result.registers
    except ModbusException as e:
        logging.error(f"Exception while reading input registers: {e}")
        return []

def write_coil(client, address, value):
    try:
        result = client.write_coil(address, value)
        if result.isError():
            logging.error(f"Failed to write coil: {result}")
        else:
            print(Fore.GREEN + f"Written coil at address {address} to {value}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing coil: {e}")

def write_register(client, address, value):
    try:
        result = client.write_register(address, value)
        if result.isError():
            logging.error(f"Failed to write register: {result}")
        else:
            print(Fore.GREEN + f"Written register at address {address} to {value}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing register: {e}")

def write_multiple_coils(client, address, values):
    try:
        result = client.write_coils(address, values)
        if result.isError():
            logging.error(f"Failed to write multiple coils: {result}")
        else:
            print(Fore.GREEN + f"Written multiple coils starting at address {address}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing multiple coils: {e}")

def write_multiple_registers(client, address, values):
    try:
        result = client.write_registers(address, values)
        if result.isError():
            logging.error(f"Failed to write multiple registers: {result}")
        else:
            print(Fore.GREEN + f"Written multiple registers starting at address {address}" + Style.RESET_ALL)
    except ModbusException as e:
        logging.error(f"Exception while writing multiple registers: {e}")

def display_table(headers, data):
    table = PrettyTable(headers)
    for row in data:
        table.add_row(row)
    print(table)

def message_parser(client):
    try:
        holding_registers = read_holding_registers(client, 0, 10)
        messages = []
        for reg in holding_registers:
            try:
                char = chr(reg)
                if char.isprintable():
                    messages.append(char)
                else:
                    messages.append('?')
            except ValueError:
                messages.append('?')
        return ''.join(messages)
    except Exception as e:
        logging.error(f"Failed to parse messages: {e}")
        return "No messages found."

def grab_banner(client):
    try:
        coils = read_coils(client, 0, 10)
        holding_registers = read_holding_registers(client, 0, 10)
        input_registers = read_input_registers(client, 0, 10)
        discrete_inputs = read_discrete_inputs(client, 0, 10)
        messages = message_parser(client)

        banner_data = []
        if coils:
            banner_data.append(["Coils", coils])
        if holding_registers:
            banner_data.append(["Holding Registers", holding_registers])
        if input_registers:
            banner_data.append(["Input Registers", input_registers])
        if discrete_inputs:
            banner_data.append(["Discrete Inputs", discrete_inputs])
        if messages:
            banner_data.append(["Messages", messages])

        if banner_data:
            banner_table = PrettyTable()
            banner_table.field_names = ["Type", "Index", "Value"]
            for section, data in banner_data:
                if section == "Messages":
                    banner_table.add_row([section, "", data])
                else:
                    for i, v in enumerate(data):
                        banner_table.add_row([section, i, v])
            print(Fore.CYAN + "Banner Information:" + Style.RESET_ALL)
            print(banner_table)
        else:
            print(Fore.RED + "No banner information found." + Style.RESET_ALL)
    except Exception as e:
        logging.error(f"Failed to grab banner: {e}")

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
        ["hex_modify <address> <hex_value>", "Modify register value at the given address."],
        ["hex_randomize <count>", "Randomize values in the given number of registers."],
        ["text_edit <text>", "Edit text in the first registers."],
        ["crash_system [speed]", "Overload the system with random data at the given speed (default: 0.01s)."],
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
                print(Fore.GREEN + f"Written coil at address {address} to {value}" + Style.RESET_ALL)
            elif cmd == "write_register":
                if len(command) != 3:
                    print(Fore.RED + "Usage: write_register <address> <value>" + Style.RESET_ALL)
                    continue
                address, value = int(command[1]), int(command[2])
                write_register(client, address, value)
                print(Fore.GREEN + f"Written register at address {address} to {value}" + Style.RESET_ALL)
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
                try:
                    server_info = socket.gethostbyaddr(args.ip)
                    print(Fore.CYAN + f"Modbus Server Hostname: {server_info[0]}" + Style.RESET_ALL)
                    print(Fore.CYAN + f"Modbus Server IP Address: {args.ip}" + Style.RESET_ALL)
                    print(Fore.CYAN + f"Modbus Server Aliases: {', '.join(server_info[1])}" + Style.RESET_ALL)
                except socket.herror as e:
                    logging.error(f"Failed to get network details: {e}")
                    print(Fore.RED + f"Failed to get network details: {e}" + Style.RESET_ALL)
            elif cmd == "grab_banner":
                grab_banner(client)
            elif cmd == "help":
                display_help()
            elif cmd == "hex_modify":
                if len(command) != 3:
                    print(Fore.RED + "Usage: hex_modify <address> <hex_value>" + Style.RESET_ALL)
                    continue
                address, value = int(command[1]), command[2]
                hex_modify(client, address, value)
            elif cmd == "hex_randomize":
                if len(command) != 2:
                    print(Fore.RED + "Usage: hex_randomize <count>" + Style.RESET_ALL)
                    continue
                count = int(command[1])
                hex_randomize(client, count)
            elif cmd == "text_edit":
                if len(command) < 2:
                    print(Fore.RED + "Usage: text_edit <text>" + Style.RESET_ALL)
                    continue
                text = ' '.join(command[1:])
                text_edit(client, text)
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
