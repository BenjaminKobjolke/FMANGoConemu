# GoConemu

_This is a Windows plugin for [fman](https://fman.io/), a dual pane file manager. It provides commands for working with
[Conemu](https://conemu.github.io/), a better Windows terminal, and network paths._

## Commands

### GoConemu

Press ALT+SHIFT+C to open the current directory in a new Conemu window.

### MapNetworkDrive

Use the Command Palette to run the "map_network_drive" command. This command:

1. Maps the current network path to a drive letter (using an existing mapping or creating a new one)
2. Navigates to the mapped path in fman

### Network Path Handling

When using the plugin with network paths (e.g., `\\SERVER\Share\Folder`), the plugin will:

1. Check if the network path is already mapped to a drive letter using `net use`
2. If a mapping exists:
   - Extract the drive letter (e.g., V:)
   - Construct a new path using the drive letter and the remaining path
   - Update the active pane in fman to the new path
   - Launch ConEmu with this new path
3. If no mapping exists:
   - Find a free drive letter starting from Z and counting backwards
   - Use `net use` to create a new network mapping
   - Update the active pane in fman to the new path
   - Launch ConEmu with the new mapped path

This improves compatibility with applications that don't handle UNC paths well and ensures proper handling of paths with spaces or special characters. Additionally, it keeps both fman and ConEmu in sync by updating the active pane in fman to the new drive letter path.

## Notes

This plugin assumes that ConEmu executable is located at `C:\Program Files\ConEmu\ConEmu64.exe`. Please
report if something goes wrong.

## Contributors

- [thesonofugly](https://github.com/thesonofugly)
