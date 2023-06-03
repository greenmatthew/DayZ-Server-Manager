# DayZ Server Manager by Matthew Green is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.
# Based on a work at https://git.matthewgreen.gg/matthewgreen/DayZ-Server-Manager.

import os
import subprocess
import re
import shutil
import traceback

# Configuration
steamcmd_dir:str = None
install_dir:str = None
server_app_id:int = None
game_app_id:int = None
username:str = None

manager_config:str = "manager.cfg"
server_config:str = "serverDZ.cfg"
modslist_file:str = "modslist.csv"

def remove_comments(line:str):
    comment_index = line.find('#')
    if (comment_index >= 0):
        if (comment_index == 0):
            return ""
        return line[:comment_index]

def try_cast_str_to_int(value:str):
    try:
        return int(value)
    except:
        return None

def check_global_vars():
    if steamcmd_dir is None:
        raise ValueError("The 'steamcmd_dir' configuration variable is not set.")
    if install_dir is None:
        raise ValueError("The 'install_dir' configuration variable is not set.")
    if server_app_id is None:
        raise ValueError("The 'server_app_id' configuration variable is not set or is not a valid integer.")
    if game_app_id is None:
        raise ValueError("The 'game_app_id' configuration variable is not set or is not a valid integer.")
    if username is None:
        raise ValueError("The 'username' configuration variable is not set.")

def load_manager_config():
    with open(manager_config, 'r') as file:
        for line in file:
            line = line.strip()
            line = remove_comments(line)
            if not line:
                continue

            key, value = line.split('=')
            key = key.strip()
            value = value.strip().strip('"')

            if key == 'steamcmd_dir':
                steamcmd_dir = value
            elif key == 'install_dir':
                install_dir = value
            elif key == 'server_app_id':
                server_app_id = try_cast_str_to_int(value)
            elif key == 'game_app_id':
                game_app_id = try_cast_str_to_int(value)
            elif key == 'username':
                username = value
        
        check_global_vars()
            
def get_steamcmd_exe() -> str:
    return f"{steamcmd_dir}/steamcmd.exe"

def get_server_exe() -> str:
    return f"{install_dir}/DayZServer_x64.exe"

def check_if_steamcmd_is_installed():
    postfix = "If you do not have SteamCMD already. Download it for Windows from here: https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip. DayZ Server is only available for Windows at the time of this program being made. Once it is installed put the file path for the directory at the top of the "
    if (not os.path.exists(steamcmd_dir)):
        raise Exception(f"SteamCMD directory is missing: {steamcmd_dir}. {postfix}")
    if (not os.path.exists(get_steamcmd_exe())):
        raise Exception(f"SteamCMD executable file is missing: {get_steamcmd_exe()}. {postfix}")

def create_if_missing_default_server_cfg():

    if (os.path.exists(server_config)):
        print(f"Found server config file: {server_config}. It can be modified to alter the server's execution.")
    else:
        print(f"Failed to find server config file: {server_config}")
        print(f"Creating a server config from default template.")
        with open(server_config, 'w') as file:
            file.write('''\
hostname = "SERVER";  // Server name
password = "";              // Password to connect to the server
passwordAdmin = "";         // Password to become a server admin

enableWhitelist = 0;        // Enable/disable whitelist (value 0-1)

maxPlayers = 60;            // Maximum amount of players

verifySignatures = 2;       // Verifies .pbos against .bisign files. (only 2 is supported)
forceSameBuild = 1;         // When enabled, the server will allow the connection only to clients with the same .exe revision as the server (value 0-1)

disableVoN = 0;             // Enable/disable voice over network (value 0-1)
vonCodecQuality = 20;        // Voice over network codec quality, the higher the better (values 0-30)

disable3rdPerson=0;         // Toggles the 3rd person view for players (value 0-1)
disableCrosshair=0;         // Toggles the cross-hair (value 0-1)

disablePersonalLight = 1;   // Disables personal light for all clients connected to the server
lightingConfig = 0;         // 0 for a brighter night setup, 1 for a darker night setup

serverTime="SystemTime";    // Initial in-game time of the server. "SystemTime" means the local time of the machine. Another possibility is to set the time to some value in "YYYY/MM/DD/HH/MM" format, e.g., "2015/4/8/17/23".
serverTimeAcceleration=12;  // Accelerated Time (value 0-24)// This is a time multiplier for in-game time. In this case, the time would move 24 times faster than normal, so an entire day would pass in one hour.
serverNightTimeAcceleration=1;  // Accelerated Night Time - The numerical value being a multiplier (0.1-64) and also multiplied by serverTimeAcceleration value. Thus, in case it is set to 4 and serverTimeAcceleration is set to 2, night time would move 8 times faster than normal. An entire night would pass in 3 hours.
serverTimePersistent=0;     // Persistent Time (value 0-1)// The actual server time is saved to storage, so when active, the next server start will use the saved time value.

guaranteedUpdates=1;        // Communication protocol used with the game server (use only number 1)

loginQueueConcurrentPlayers=5;  // The number of players concurrently processed during the login process. Should prevent a massive performance drop during connection when a lot of people are connecting at the same time.
loginQueueMaxPlayers=500;       // The maximum number of players that can wait in the login queue

instanceId = 1;             // DayZ server instance id, to identify the number of instances per box and their storage folders with persistence files

storageAutoFix = 1;         // Checks if the persistence files are corrupted and replaces corrupted ones with empty ones (value 0-1)

logFile = "serverconsole.log"


class Missions
{
	class DayZ
	{
		template = "dayzOffline.chernarusplus"; // Mission to load on server startup. <MissionName>.<TerrainName>
	};
};
''')
    print("\n")

def create_if_missing_empty_modslist():
    if (os.path.exists(modslist_file)):
        print(f"Found modslist file: {modslist_file}. It can be modified to add Steam workshop mods to the server.")
    else:
        print(f"Failed to find modslist file: {modslist_file}.")
        print(f"Creating a modslist from default template.")
        with open(modslist_file, 'w') as file:
            file.write("# To add a new Steam Workshop mod:\n# Put a Steam Workshop ID and exact name on Steam Workshop seperated by a comma (whitespace ignored) all on a single line.\n# If you want to add another mod do it on another line.\n# Steam Workshop IDs can be found at the end of the Steam URL of the workshop item: https://steamcommunity.com/sharedfiles/filedetails/?id=2950280649.\n# Note: the '#' character makes it so that the character and any character after it, on the same line, is ignored when the file is parsed.\n# Example:\n# 2950280649, DayZ-Rat # Remove the first '#' character on this line and you have a valid line for adding a workshop item.\n")
    print("\n")

def is_valid_file_name(name):
    # Regular expression to match valid file names
    pattern = r'^[a-zA-Z0-9_\-. ]+$'
    return re.match(pattern, name) is not None

def parse_modslist(file_path: str) -> dict[int, str]:
    data = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            line = remove_comments(line)
            if not line:
                continue
            elements = line.split(',')
            if len(elements) != 2:
                raise ValueError(f"Invalid line format: {line}")
            try:
                key = int(elements[0].strip())
            except ValueError:
                raise ValueError(f"Invalid workshop ID: {elements[0].strip()}")
            value = elements[1].strip()
            if not is_valid_file_name(value):
                raise ValueError(f"Invalid mod name: {value}, must be a valid file name.")
            data[key] = value
    return data

def run_steamcmd(args: str):
    run_command = f"{get_server_exe()} {args}"
    try:
        subprocess.run(run_command, check=True)
    except subprocess.CalledProcessError as e:
        raise ChildProcessError(f"SteamCMD error {e}")

def update(validate:bool):
    run_command = f"+force_install_dir {install_dir} +login {username} +app_update {server_app_id} {'validate' if (validate) else ''}"

    mods_list_file = "./modslist.txt"
    if (os.path.exists(mods_list_file)):
        mods_list = parse_modslist(mods_list_file)
        mods_args = ""
        for workshop_id in mods_list:
            mods_args += f" +workshop_download_item {game_app_id} {workshop_id} "
        run_command += mods_args

    run_command += " +quit"

    run_steamcmd(run_command)

def update_server(validate:bool):
    print(f"Attempting to download/update server with app_id: {server_app_id} @ '{install_dir}'\n\n")
    run_steamcmd(f"+force_install_dir {install_dir} +login {username} +app_update {server_app_id} {'validate' if (validate) else ''} +quit")
    print("\n\n")

def update_mods(modslist:dict[int, str], validate:bool):
    if (len(modslist) <= 0):
        return

    run_command = f"+login {username}"
    mods_args = ""
    for workshop_id, mod_name in modslist.items():
        print(f"Attempting to download/update item: {workshop_id} ({mod_name})")
        mods_args += f" +workshop_download_item {game_app_id} {workshop_id}{' validate' if (validate) else ''}"
    print("\n")
    run_command += mods_args

    run_command += " +quit"
    run_steamcmd(run_command)
    print("\n\n")

def quick_copy_recursive(source_dir, destination_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_dir, os.path.relpath(source_file, source_dir))
            if not os.path.exists(destination_file):
                os.makedirs(os.path.dirname(destination_file), exist_ok=True)
                shutil.copy2(source_file, destination_file)

def full_copy_recursive(source_dir, destination_dir):
    shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

def install_mods(modslist:dict[int, str]):
    workshop_dir = f"{steamcmd_dir}/steamapps/workshop/content/{game_app_id}/"
    server_keys_dir = f"{install_dir}/keys"

    for workshop_id, mod_name in modslist.items():
        print(f"Attempting to install item: {workshop_id} ({mod_name})")
        item_dir = f"{workshop_dir}/{workshop_id}"
        if (not os.path.exists(item_dir)):
            continue

        server_item_dir = f"{install_dir}/@{mod_name}"
        # if (not os.path.exists(server_item_dir)):
        #     os.mkdir(server_item_dir)
        os.symlink(item_dir, server_item_dir)
        
        item_keys_dir = f"{item_dir}/keys"
        if (os.path.exists(item_keys_dir)):
            quick_copy_recursive(item_keys_dir, server_keys_dir)
    print("\n\n")


def run_server(modslist:dict[int, str]):
    run_command = f"{get_server_exe()} -config=serverDZ.cfg"
    if (len(modslist) > 0):
        run_command += f" \"-mod="
        mods = ""
        first:bool = True
        for workshop_id, mod_name in modslist.items():
            if (first):
                mods += f"@{mod_name}"
            else:
                mods += f";@{mod_name}"
        run_command += f"{mods}\""
        print(f"Attempting to run server using the config: '{server_config}' and mods: '{mods}'\n\n")
    else:
        print(f"Attempting to run server using the config: '{server_config}'\n\n")
    try:
        subprocess.run(run_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Game error {e}")

def main():
    try:
        load_manager_config()

        check_if_steamcmd_is_installed()
        create_if_missing_default_server_cfg()
        create_if_missing_empty_modslist()

        # update_server(validate=False)

        modslist = parse_modslist("./modslist.txt")
        if (len(modslist) > 0):
            # update_mods(modslist=modslist, validate=False)
            install_mods(modslist=modslist)

        run_server(modslist)
    except Exception as e:
        print("\n\nAn exception occurred:")
        traceback.print_exc()
    
    input("\n\nPress Enter to exit...")

if __name__ == "__main__":
    main()