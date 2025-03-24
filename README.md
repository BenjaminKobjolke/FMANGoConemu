# GoConemu

_This is a Windows plugin for [fman](https://fman.io/), a dual pane file manager. It opens the current directory in
[Conemu](https://conemu.github.io/), a better Windows terminal._

## Usage

Simply press ALT+SHIFT+C to open the directory you're in in a new Conemu window.

### Network Path Handling

When using the plugin with network paths (e.g., `\\SERVER\Share\Folder`), the plugin will:

1. Check if the network path is already mapped to a drive letter using `net use`
2. If a mapping exists:
   - Extract the drive letter (e.g., V:)
   - Construct a new path using the drive letter and the remaining path
   - Launch ConEmu with this new path
3. If no mapping exists:
   - Find a free drive letter starting from Z and counting backwards
   - Use `net use` to create a new network mapping
   - Launch ConEmu with the new mapped path

This improves compatibility with applications that don't handle UNC paths well and ensures proper handling of paths with spaces or special characters.

## Notes

This plugin assumes that ConEmu executable is located at `C:\Program Files\ConEmu\ConEmu64.exe`. Please
report if something goes wrong.

## Contributors

- [thesonofugly](https://github.com/thesonofugly)
