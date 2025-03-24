from fman import DirectoryPaneCommand, show_alert
from fman.url import as_human_readable
import subprocess
import re
import os
import datetime
import traceback
import string
import ctypes

class GoConemu(DirectoryPaneCommand):
	def get_free_drive_letters(self):
		"""Get a list of free drive letters in reverse alphabetical order (Z to A)"""
		drives_bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
		all_letters = string.ascii_uppercase
		used = {all_letters[i] for i in range(26) if drives_bitmask & (1 << i)}
		free = [letter + ':' for letter in all_letters if letter not in used]
		# Return in reverse order (Z to A)
		return sorted(free, reverse=True)
	def __call__(self):
		# Set up logging
		log_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'fman_conemu_debug.log')
		self.log(log_file, "=== New GoConemu execution ===")
		
		conemu_path = "C:\\Program Files\\ConEmu\\ConEmu64.exe"
		current_path = self.pane.get_path()
		human_readable_path = as_human_readable(current_path)
		
		self.log(log_file, f"Original path: {human_readable_path}")
		
		# Check if the path is a network path (starts with \\)
		if human_readable_path.startswith('\\\\'):
			self.log(log_file, "Detected network path")
			
			try:
				# First, check if the network path is already mapped to a drive letter
				self.log(log_file, "Checking for existing drive mappings with 'net use'")
				net_use_output = subprocess.check_output('net use', shell=True).decode('utf-8')
				self.log(log_file, f"net use output:\n{net_use_output}")
				
				# Parse the network path to get server and share
				match = re.match(r'\\\\([^\\]+)\\([^\\]+)(.*)', human_readable_path)
				if match:
					server = match.group(1)
					share = match.group(2)
					remaining_path = match.group(3)
					server_share = f'\\\\{server}\\{share}'
					
					self.log(log_file, f"Server: {server}")
					self.log(log_file, f"Share: {share}")
					self.log(log_file, f"Server+Share: {server_share}")
					self.log(log_file, f"Remaining path: {remaining_path}")
					
					# Look for existing drive mappings
					drive_letter = None
					for line in net_use_output.splitlines():
						if server_share in line:
							# Extract the drive letter (e.g., "V:")
							parts = line.split()
							for part in parts:
								if len(part) == 2 and part[1] == ':':
									drive_letter = part
									break
							if drive_letter:
								break
					
					if drive_letter:
						# Use the existing drive mapping
						self.log(log_file, f"Found existing drive mapping: {drive_letter} for {server_share}")
						new_path = f"{drive_letter}{remaining_path}"
						self.log(log_file, f"Constructed new path: {new_path}")
						
						# Launch ConEmu with the new path
						cmd = f'"{conemu_path}" -Single -Dir "{new_path}"'
						self.log(log_file, f"Launching ConEmu with command: {cmd}")
						subprocess.call(cmd)
					else:
						# No existing mapping found, find a free drive letter and create a new mapping
						self.log(log_file, "No existing drive mapping found, creating a new one")
						
						# Get free drive letters using Windows API
						free_drives = self.get_free_drive_letters()
						self.log(log_file, f"Free drive letters: {free_drives}")
						
						if free_drives:
							# Use the first free drive letter (highest available letter)
							free_drive = free_drives[0]
							self.log(log_file, f"Using free drive letter: {free_drive}")
							# Create a new network mapping
							map_cmd = f'net use {free_drive} "{server_share}"'
							self.log(log_file, f"Creating new network mapping with command: {map_cmd}")
							result = subprocess.call(map_cmd, shell=True)
							self.log(log_file, f"Result of net use command: {result}")
							
							if result == 0:
								# Mapping was successful
								# Construct the new path with the mapped drive
								new_path = f"{free_drive}{remaining_path}"
								self.log(log_file, f"Constructed new path: {new_path}")
								
								# Launch ConEmu with the new path
								cmd = f'"{conemu_path}" -Single -Dir "{new_path}"'
								self.log(log_file, f"Launching ConEmu with command: {cmd}")
								subprocess.call(cmd)
							else:
								# Mapping failed, fall back to the original behavior
								self.log(log_file, f"Failed to create network mapping, falling back to original behavior")
								fallback_cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
								self.log(log_file, f"Falling back to original command: {fallback_cmd}")
								subprocess.call(fallback_cmd)
						else:
							# No free drive letters found, fall back to the original behavior
							self.log(log_file, f"No free drive letters found, falling back to original behavior")
							fallback_cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
							self.log(log_file, f"Falling back to original command: {fallback_cmd}")
							subprocess.call(fallback_cmd)
				else:
					# Couldn't parse the network path, fall back to the batch file approach
					self.log(log_file, "Couldn't parse network path, using pushd approach")
					
					# Create a simple batch file to handle the network path
					temp_batch_file = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'fman_conemu_launcher.bat')
					self.log(log_file, f"Creating batch file: {temp_batch_file}")
					
					with open(temp_batch_file, 'w') as f:
						f.write('@echo off\n')
						f.write(f'echo Current directory before pushd: %CD% > "{log_file}.batch.log"\n')
						f.write(f'pushd "{human_readable_path}"\n')
						f.write(f'echo Result of pushd (errorlevel): %errorlevel% >> "{log_file}.batch.log"\n')
						f.write(f'echo Current directory after pushd: %CD% >> "{log_file}.batch.log"\n')
						f.write(f'echo Starting ConEmu with: "{conemu_path}" -Single -Dir "%CD%" >> "{log_file}.batch.log"\n')
						f.write(f'"{conemu_path}" -Single -Dir "%CD%"\n')
						f.write(f'echo Result of start (errorlevel): %errorlevel% >> "{log_file}.batch.log"\n')
					
					# Just start the batch file directly
					self.log(log_file, "Starting batch file directly")
					self.log(log_file, temp_batch_file)
					os.startfile(temp_batch_file)
				
			except Exception as e:
				# If anything goes wrong, log the error and fall back to the original behavior
				self.log(log_file, f"Error handling network path: {str(e)}")
				self.log(log_file, traceback.format_exc())
				show_alert(f"Error handling network path: {str(e)}\nSee logs at: {log_file}")
				
				# Log the fallback command
				fallback_cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
				self.log(log_file, f"Falling back to original command: {fallback_cmd}")
				subprocess.call(fallback_cmd)
		else:
			# Not a network path, use the original behavior
			cmd = f'"{conemu_path}" -Single -Dir "{human_readable_path}"'
			self.log(log_file, f"Not a network path, using original command: {cmd}")
			subprocess.call(cmd)
			
	def log(self, log_file, message):
		"""Write a timestamped message to the log file"""
		timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
		with open(log_file, 'a', encoding='utf-8') as f:
			f.write(f"[{timestamp}] {message}\n")
