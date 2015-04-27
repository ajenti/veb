import os
import pwd
import grp


def ensure_directory(path, uid=None, gid=None, mode=None):
    if not os.path.exists(path):
        os.makedirs(path)
    if uid is not None:
        if isinstance(uid, basestring):
            if gid is None:
                gid = uid
            uid = pwd.getpwnam(uid).pw_uid
        if gid is None:
            gid = uid
        if isinstance(gid, basestring):
            gid = grp.getgrnam(gid).gr_gid
        os.chown(path, uid, gid)
    if mode:
        os.chmod(path, mode)


def absolute_path(path, root):
    if not path.startswith('/'):
        return os.path.join(root, path)
    return path
