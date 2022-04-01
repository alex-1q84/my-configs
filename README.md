# Backup And Manage All of My Configuration Files

## Features I want to have

- [X] can specification where to backup the config files
- [X] backup current file and directory as list in configurations
- [X] convention over setting
- [X] link file to destination position
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

## How to use this tool

1. clone this repository
```bash
git clone https://github.com/alex-1q84/my-configs.git
```
2. set where you want to back up your config files in the `config.json`, eg.
```json
"backup_dir": "~/Dropbox/configs/"
```
3. list all the files and directories in the `config.json`, eg.
```json
  "paths": [
    "/usr/local/etc/shadowsocks-libev.json",
    "~/.gitconfig",
    "~/.config/fish",
    "~/.vimrc"
  ]
```
the final `config.json` file should look like as follows
```json
{
  "backup_dir": "~/Dropbox/configs/",
  "paths": [
    "/usr/local/etc/shadowsocks-libev.json",
    "~/.gitconfig",
    "~/.config/fish",
    "~/.vimrc"
  ]
}
```
5. run the `my_configs.py` script and you config files and directories will be backed up and linked back to original path
```bash
python3 my_configs.py
```
