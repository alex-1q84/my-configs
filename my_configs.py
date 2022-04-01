# coding: utf-8

import json
import shutil
from pathlib import Path


class Config:

    def __init__(self, config_path):
        self.__dict__ = json.load(config_path)
        if self.backup_dir:
            self.backup_dir = Path(self.backup_dir).expanduser()

    def init_base(self):
        print("will backup your configuration files into " + str(config.backup_dir))
        path = Path(self.backup_dir).expanduser()
        if not path.exists():
            path.mkdir()

    def backup(self):
        print("backup files " + str(config.pathes))
        for p in config.pathes:
            fpath = Path(p).expanduser()
            if fpath.exists():
                if is_dot_dir(fpath):
                    backup_path = self.to_backup_path(to_backup_dir(fpath))
                    print("backup path: " + str(backup_path))
                    copy(fpath, backup_path)
                elif is_dot_file(fpath):
                    backup_path = self.to_backup_path(to_backup_file(fpath))
                    print("backup path: " + str(backup_path))
                    copy(fpath, backup_path)
                else:
                    # backup file to the given backup path or fail
                    backup_path = self.to_backup_path(fpath)
                    print("backup path: " + str(backup_path))
                    copy(fpath, backup_path)

    def to_backup_path(self, fpath):
        backup_dir = self.mapping_dir(fpath)
        return (self.backup_dir / backup_dir / fpath.name).expanduser()

    def mapping_dir(self, fpath) -> str:
        p_path = fpath.parent.expanduser()
        try:
            relative_path = p_path.relative_to(Path("~").expanduser())
            return "-".join([rename_dot_dir(d) for d in relative_path.parts])
        except ValueError:
            return "_" + "-".join(rename_dot_dir(d) for d in p_path.parts[1:])

    def link(self):
        for p in self.backup_dir.iterdir():
            # FIXME
            pass


def rename_dot_dir(fname: str) -> str:
    if fname.startswith("."):
        return "+" + fname[1:]
    else:
        return fname

def copy(from_path, to_path):
    dest_dir = Path(to_path).expanduser().parent
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
    if Path(from_path).is_file():
        shutil.copy2(from_path, to_path)
    elif Path(from_path).is_dir():
        shutil.copytree(from_path, to_path, dirs_exist_ok=True)


def is_dot_dir(fpath):
    return fpath.is_dir() and fpath.name.startswith(".")


def is_dot_file(fpath):
    return fpath.is_file() and fpath.name.startswith(".")


def to_backup_dir(fpath):
    return fpath.parent / (fpath.name[1:] + "+")


def to_backup_file(fpath):
    return fpath.parent / (fpath.name[1:] + ".symlink")


config = Config(open("config.json"))
config.init_base()
config.backup()
config.link()
