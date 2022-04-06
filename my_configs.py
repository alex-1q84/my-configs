# coding: utf-8

import json
import shutil
from pathlib import Path


class display:
    def __init__(self, template: str):
        self.template = template

    def __call__(self, func):
        from functools import wraps

        @wraps(func)
        def wrapper(*argvs, **kwargs):
            result = func(*argvs, **kwargs)
            print(self.template.format(*argvs))
            return result

        return wrapper


class Config:

    def __init__(self, config_path):
        self.__dict__ = json.load(config_path)
        if self.backup_dir:
            self.backup_dir = Path(self.backup_dir).expanduser()

    def init_dir(self, directory):
        path = Path(directory).expanduser()
        if not path.exists():
            path.mkdir()

    def backup(self):
        self.init_dir(self.backup_dir)
        for p in config.paths:
            fpath = Path(p).expanduser()
            if fpath.exists():
                if is_dot_dir(fpath):
                    copy(fpath, self.to_backup_path(to_backup_dir(fpath)))
                elif is_dot_file(fpath):
                    copy(fpath, self.to_backup_path(to_backup_file(fpath)))
                else:
                    # backup file to the given backup path or fail
                    copy(fpath, self.to_backup_path(fpath))

    def to_backup_path(self, fpath):
        backup_dir = self.mapping_dir(fpath)
        return (self.backup_dir / backup_dir / fpath.name).expanduser()

    def mapping_dir(self, fpath) -> str:
        def rename_dot_dir(fname: str) -> str:
            if fname.startswith("."):
                return "+" + fname[1:]
            else:
                return fname

        p_path = fpath.parent.expanduser()
        try:
            relative_path = p_path.relative_to(Path("~").expanduser())
            return "-".join([rename_dot_dir(d) for d in relative_path.parts])
        except ValueError:
            return "_" + "-".join(rename_dot_dir(d) for d in p_path.parts[1:])

    def link(self):
        def inner_link(path):
            for p in path.iterdir():
                # if is symlink file then link to user home dir
                if is_link_file(p):
                    link_to(Path("~") / to_dot_file_name(p.name), p)
                # if is + ending dir then link to user home dir
                if is_link_dir(p):
                    link_to(Path("~") / link_dir_to_dot_dir_name(p.name), p)
                # if is + prefixing dir then link inner files and dirs to user home dir
                if is_hidden_dir(p):
                    for subp in p.iterdir():
                        link_to(Path("~") / hidden_dir_to_dot_dir_name(p.name) / subp.name, subp)
                # if is _ prefixing dir then link to absolute path
                if is_abs_path_dir(p):
                    for subp in p.iterdir():
                        link_to(to_abs_path(p.name) / subp.name, subp)
                # else if normal dir then go into the dir and perform the link method
                # will ignore not symlink files
                elif is_dir(p):
                    inner_link(p)

        inner_link(self.backup_dir)

    def move_bak_files(self, dest_dir):
        for p in config.paths:
            bak_path = add_suffix(Path(p), ".bak").expanduser()
            if bak_path.exists():
                bak_path.rename(Path(dest_dir).expanduser() / bak_path.name)
            else:
                print("File or directory not exist:", bak_path)


def is_link_file(path):
    return path.is_file() and path.name.endswith(".symlink")


@display("LINK {} to {}")
def link_to(dest_path: Path, path: Path):
    dest_path = dest_path.expanduser()
    path = path.expanduser()
    if dest_path.exists():
        if dest_path.samefile(path):
            return
        else:
            bak_path = add_suffix(dest_path, ".bak")
            dest_path.rename(bak_path)
            print("move {} to {}".format(dest_path, bak_path))
            dest_path.symlink_to(path.expanduser())
    else:
        dest_path.symlink_to(path.expanduser())


def add_suffix(path: Path, suffix):
    return path.parent / (path.name + suffix)


def is_link_dir(path):
    return path.is_dir() and path.name.endswith("+")


def is_hidden_dir(path):
    return path.is_dir() and is_hidden_dir_name(path.name)


def is_hidden_dir_name(fname):
    return fname.startswith("+")


def hidden_dir_to_dot_dir_name(fname):
    return "." + fname[1:]


def is_abs_path_dir(path):
    return path.is_dir() and is_abs_path_dir_name(path.name)


def is_abs_path_dir_name(fname):
    return fname.startswith("_")


def to_abs_path(fname):
    if is_abs_path_dir_name(fname):
        return Path("/" + "/".join(fname[1:].split("-")))
    else:
        raise Exception("invalide dir name " + fname + ", abs path dir name should starts with _")


def is_dir(path):
    return path.is_dir()


def to_dot_file_name(name):
    return "." + name.replace(".symlink", "")


def link_dir_to_dot_dir_name(name):
    return "." + name[:-1]


@display("BACKUP {} TO {}")
def copy(from_path, to_path):
    src_path = Path(from_path).expanduser()
    dest_path = Path(to_path).expanduser()
    if not src_path.exists():
        print("WARN: file or directory {} not exist".format(from_path))
        return

    if dest_path.exists() and src_path.samefile(dest_path):
        return

    dest_dir = dest_path.parent
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
config.backup()
config.link()
directory = Path("~/Downloads/tmp")
directory.mkdir(exist_ok=True)
config.move_bak_files(directory)
