from fman import DirectoryPaneCommand, show_alert
from fman.url import as_human_readable
import subprocess
import os

from .utils import (
    get_free_drive_letters,
    find_existing_drive_mapping,
    parse_network_path,
    create_network_mapping,
    create_batch_file
)
from .logger import Logger

class GoConemu(DirectoryPaneCommand):
    def __call__(self):
        # Initialize logger
        logger = Logger()
        log_file = logger.get_log_file_path()
        logger.log("=== New GoConemu execution ===")
        
        conemu_path = "C:\\Program Files\\ConEmu\\ConEmu64.exe"
        current_path = self.pane.get_path()
        human_readable_path = as_human_readable(current_path)
        
        logger.log(f"Original path: {human_readable_path}")
        
        # Check if the path is a network path (starts with \\)
        if human_readable_path.startswith('\\\\'):
            logger.log("Detected network path")
            
            try:
                # First, check if the network path is already mapped to a drive letter
                logger.log("Checking for existing drive mappings with 'net use'")
                net_use_output = subprocess.check_output('net use', shell=True).decode('utf-8')
                logger.log(f"net use output:\n{net_use_output}")
                
                # Parse the network path to get server and share
                server, share, remaining_path, server_share = parse_network_path(human_readable_path)
                
                if server_share:
                    logger.log(f"Server: {server}")
                    logger.log(f"Share: {share}")
                    logger.log(f"Server+Share: {server_share}")
                    logger.log(f"Remaining path: {remaining_path}")
                    
                    # Look for existing drive mappings
                    drive_letter = find_existing_drive_mapping(server_share, net_use_output)
                    
                    if drive_letter:
                        # Use the existing drive mapping
                        logger.log(f"Found existing drive mapping: {drive_letter} for {server_share}")
                        new_path = f"{drive_letter}{remaining_path}"
                        logger.log(f"Constructed new path: {new_path}")
                        
                        # Launch ConEmu with the new path
                        cmd = f'"{conemu_path}" -Single -Dir "{new_path}"'
                        logger.log(f"Launching ConEmu with command: {cmd}")
                        subprocess.call(cmd)
                    else:
                        # No existing mapping found, find a free drive letter and create a new mapping
                        logger.log("No existing drive mapping found, creating a new one")
                        
                        # Get free drive letters using Windows API
                        free_drives = get_free_drive_letters()
                        logger.log(f"Free drive letters: {free_drives}")
                        
                        if free_drives:
                            # Use the first free drive letter (highest available letter)
                            free_drive = free_drives[0]
                            logger.log(f"Using free drive letter: {free_drive}")
                            
                            # Create a new network mapping
                            logger.log(f"Creating new network mapping for {server_share}")
                            result = create_network_mapping(free_drive, server_share)
                            logger.log(f"Result of net use command: {result}")
                            
                            if result == 0:
                                # Mapping was successful
                                # Construct the new path with the mapped drive
                                new_path = f"{free_drive}{remaining_path}"
                                logger.log(f"Constructed new path: {new_path}")
                                
                                # Launch ConEmu with the new path
                                cmd = f'"{conemu_path}" -Single -Dir "{new_path}"'
                                logger.log(f"Launching ConEmu with command: {cmd}")
                                subprocess.call(cmd)
                            else:
                                # Mapping failed, fall back to the original behavior
                                logger.log(f"Failed to create network mapping, falling back to original behavior")
                                fallback_cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
                                logger.log(f"Falling back to original command: {fallback_cmd}")
                                subprocess.call(fallback_cmd)
                        else:
                            # No free drive letters found, fall back to the original behavior
                            logger.log(f"No free drive letters found, falling back to original behavior")
                            fallback_cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
                            logger.log(f"Falling back to original command: {fallback_cmd}")
                            subprocess.call(fallback_cmd)
                else:
                    # Couldn't parse the network path, fall back to the batch file approach
                    logger.log("Couldn't parse network path, using pushd approach")
                    
                    # Create a simple batch file to handle the network path
                    temp_batch_file = create_batch_file(human_readable_path, conemu_path, log_file)
                    logger.log(f"Created batch file: {temp_batch_file}")
                    
                    # Just start the batch file directly
                    logger.log("Starting batch file directly")
                    logger.log(temp_batch_file)
                    os.startfile(temp_batch_file)
                
            except Exception as e:
                # If anything goes wrong, log the error and fall back to the original behavior
                logger.log(f"Error handling network path: {str(e)}")
                import traceback
                logger.log(traceback.format_exc())
                show_alert(f"Error handling network path: {str(e)}")
                
                # Log the fallback command
                fallback_cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
                logger.log(f"Falling back to original command: {fallback_cmd}")
                subprocess.call(fallback_cmd)
        else:
            # Not a network path, use the original behavior
            cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
            logger.log(f"Not a network path, using original command: {cmd}")
            subprocess.call(cmd)
