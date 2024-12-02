#!/usr/bin/env python3

import argparse
import os
from getpass import getpass

try:
    import requests
except ImportError:
    print("requests library not found, installing...")
    os.system("pip install requests")
    import requests


# Define your API URL
API_URL = "http://localhost:8002/api"

# Function to make the register request
def register(username):
    password = getpass(prompt="Enter your password: ")
    url = f"{API_URL}/register"
    payload = {'username': username, 'password': password}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Registration successful")
    else:
        print(f"Registration failed: {response.status_code}: {response.json().get('detail')}")

# Function to make the login request and store the JWT token
def login(username):
    password = getpass(prompt="Enter your password: ")
    url = f"{API_URL}/login"
    payload = {'username': username, 'password': password}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        jwt = response.json().get('msg')
        with open('/tmp/cins_jwt', 'w') as f:
            f.write(jwt)
        print("Login successful, JWT token saved.")
    else:
        print(f"Login failed: {response.status_code}: {response.json().get('detail')}")

def command_search(keyword, limit,includeids,jwt):
    url = f"{API_URL}/commands"
    params = {'keyword': keyword,"limit":limit,"include_ids":includeids,"jwt":jwt}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        search_result = response.json().get('msg')
        if includeids:
            for command in search_result:
                print(command[0],command[1])
        else:
            for command in search_result:
                print(command[0])
    else:
        print(f"Search failed: {response.status_code}: {response.json().get('detail')}")

def command_save(command, jwt):
    url = f"{API_URL}/commands"
    params = {"jwt":jwt}
    payload = {'command': command}
    response = requests.post(url,data=payload, params=params)
    if response.status_code == 200:
        print(response.json().get('msg')) 
    else:
        print(f"Save failed: {response.status_code}: {response.json().get('detail')}")


def macro_search(name,jwt):
    url = f"{API_URL}/macro"
    params = {'name': name,"jwt":jwt}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        search_result = response.json().get('msg')
        for command in search_result:
            print(command)
    else:
        print(f"Search failed: {response.status_code}: {response.json().get('detail')}")

def macro_save(commands,name,jwt):
    url = f"{API_URL}/macro"
    params = {"jwt":jwt}
    payload = {'commands': commands,"name":name}
    response = requests.post(url,data=payload, params=params)
    if response.status_code == 200:
        print(response.json().get('msg')) 
    else:
        print(f"Save failed: {response.status_code}: {response.json().get('detail')}")

def macro_names(jwt):
    url = f"{API_URL}/macros"
    params = {"jwt":jwt}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json().get('msg')
        if not result:
            print("No macros found.")
        for macro_name in result:
            print(macro_name)
    else:
        print(f"Save failed: {response.status_code}: {response.json().get('detail')}")

def main():
    # Set up argparse
    parser = argparse.ArgumentParser(description="Casper in the Shell (cins) - CLI tool")
    # Define subcommands
    subparsers = parser.add_subparsers(dest="subargument")
    
    # Register subcommand
    register_parser = subparsers.add_parser('register', help="Register a new user")
    register_parser.add_argument('-u', '--username', required=True, help="Username for registration")
    
    # Login subcommand
    login_parser = subparsers.add_parser('login', help="Login and get JWT")
    login_parser.add_argument('-u', '--username', required=True, help="Username for login")
    
    # Search subcommand
    search_parser = subparsers.add_parser('search', help="Search for commands",aliases=['sc'])
    search_parser.add_argument('-kw', '--keyword',default="", required=False, help="Keyword to search for")
    search_parser.add_argument('-l', '--limit',default=0, required=False, help="Limit returned command count, not using this will return all commands that match.")
    search_parser.add_argument('-ii', '--includeids',default=False, required=False, help="Include ids to create macros from.")

    save_parser = subparsers.add_parser('save', help="Save a command",aliases=['sv'])
    save_parser.add_argument('-cmd', '--command', required=True, help="Command to save")

    macro_search_parser = subparsers.add_parser('macro-search', help="Fetch commands of given macro name",aliases=['msc'])
    macro_search_parser.add_argument('-n', '--name',default="", required=False, help="Name of macro to fetch commands")

    macro_fetch_parser = subparsers.add_parser('macro-names', help="Fetch all user saved macro names",aliases=['mn'])

    macro_save_parser = subparsers.add_parser('macro-save', help="Save a macro",aliases=['msv'])
    macro_save_parser.add_argument('-n', '--name', required=True, help="Name of macro to fetch commands")
    macro_save_parser.add_argument('-cmds', '--commands', required=True, help="Command ids to save(comma or whitespace seperated.)")
    # Parse arguments
    args = parser.parse_args()
    
    # Execute based on subcommand
    if args.subargument == "register":
        register(args.username)
    elif args.subargument == "login":
        login(args.username)
    elif args.subargument in ["search", "sc", "save", "sv","macro-search","msc","macro-save","msv","macro-names","mn"]:
        # Check if JWT file exists
        if os.path.exists('/tmp/cins_jwt'):
            with open('/tmp/cins_jwt', 'r') as f:
                jwt = f.read().strip()
            if args.subargument in ["search", "sc"]:
                command_search(args.keyword,args.limit,args.includeids,jwt)
            elif args.subargument in ["save", "sv"]:
                command_save(args.command, jwt)
            elif args.subargument in ["macro-search", "msc"]:
                macro_search(args.name, jwt)
            elif args.subargument in ["macro-save", "msv"]:
                macro_save(args.commands,args.name, jwt)
            elif args.subargument in ["macro-names", "mn"]:
                macro_names(jwt)
        else:
            print("JWT token not found. Please login first.")
    else:
        print("Casper in the Shell (cins) - CLI tool")
        print("Use -h or --help to see all arguments")
if __name__ == "__main__":
    main()