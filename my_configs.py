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


def to_user_home_dir(fname):
    """convert ~+a-b-c name to ~/.a/b/c"""
    sub_name = fname[1:]
    if sub_name.startswith("+"):
        sub_name = sub_name.replace("+", ".", 1)
    return Path("~") / "/".join(sub_name.split("-"))


def is_user_home_dir(path):
    return path.is_dir() and path.name.startswith("~")


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
                if is_dot_dir(fpath) or is_dot_file(fpath):
                    copy(fpath, self.to_backup_path(dot_file_to_backup_file(fpath)))
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
            if relative_path.parts:
                return "~" + "-".join([rename_dot_dir(d) for d in relative_path.parts])
            else:
                return ""
        except ValueError:
            return "_" + "-".join(rename_dot_dir(d) for d in p_path.parts[1:])

    def link(self):
        def inner_link(path):
            for p in path.iterdir():
                # if is symlink file then link to user home dir
                if is_link_file(p):
                    link_to(symlink_to_user_home_dot(p.name), p)
                # if is prefixed with ~ and not suffixed with .symlink dir then link to user home dir
                if is_link_dir(p):
                    link_to(symlink_to_user_home_dot(p.name), p)
                # if is prefixed with ~ and not suffixed with .symlink dir then link inner files and dirs into user home
                if is_user_home_dir(p):
                    for subp in p.iterdir():
                        link_to(to_user_home_dir(p.name) / subp.name, subp)
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
            print("MOVE {} to {}".format(dest_path, bak_path))
            dest_path.symlink_to(path.expanduser())
    else:
        dest_path.symlink_to(path.expanduser())


def add_suffix(path: Path, suffix):
    return path.parent / (path.name + suffix)


def is_link_file(path):
    return path.is_file() and path.name.endswith(".symlink")


def is_link_dir(path):
    return path.is_dir() and path.name.endswith(".symlink")


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


def symlink_to_user_home_dot(name):
    sub_name = "." + name.removesuffix(".symlink")
    return Path("~") / sub_name


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


def dot_file_to_backup_file(fpath):
    return fpath.parent / (fpath.name[1:] + ".symlink")


if __name__ == "__main__":
    config = Config(open("config.json"))
    config.backup()
    config.link()

    # just for move .bak file together
    # directory = Path("~/Downloads/tmp").expanduser()
    # directory.mkdir(exist_ok=True)
    # config.move_bak_files(directory)
