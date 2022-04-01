# Backup And Manage All of My Configuration Files

## Features I want to have

- [X] can specification where to backup the config files
- [X] backup current file and directory as list in configurations
- [X] convention over setting
- [] link file to destination position
  link files in special directory to destination

## File backup rename rules

- `/a/b/c` absolute path file will be backup to `_a-b/c`
- `~/.xx/yy` directory in user home will backup to `+xx/yy`
- `~/.xx` file will backup to `xx.symlink`
- `~/.xx` directory will backup to `xx+`

## File link rules

- every `xx.symlink` file will soft link into `~` directory
- every `xx+` directory will soft link into `~` directory
- every file and directory in directory with `_` prefix will link to absolute path
