import tempfile
import functools
import tarfile

from git_annex_adapter import GitRepo


def func_chain(*funcs):
    def chain(f):
        for func in reversed(funcs):
            f = func(f)
        return f
    return chain


def with_temp_folder(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with tempfile.TemporaryDirectory() as tmp_cwd:
            return func(*args, **kwargs, cwd=tmp_cwd)
    return wrapper


def with_repo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        repo = GitRepo(kwargs['cwd'])
        del kwargs['cwd']
        return func(*args, **kwargs, repo=repo)
    return wrapper


with_temp_repo = func_chain(with_temp_folder, with_repo)


def from_tar(tar_path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tarfile.open(tar_path) as tar:
                tar.extractall(path=kwargs['cwd'])
                return func(*args, **kwargs)
        return wrapper
    return decorator


def with_tar_repo(tar_path):
    return func_chain(with_temp_folder, from_tar(tar_path), with_repo)