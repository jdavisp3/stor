from storage_utils import utils
from storage_utils.third_party.path import ClassProperty
from storage_utils.third_party.path import Path
from storage_utils.third_party.path import string_types


class StorageUtilsPathMixin(object):
    """Provides basic cross compatibility between paths on different file
    systems.

    Objects that utilize this mixin are able to be cross compatible when
    copying between storage systems, for example, copying from a posix file
    system to swift or vice versa.
    """
    copy = utils.copy
    copytree = utils.copytree

    @ClassProperty
    @classmethod
    def path_module(cls):
        """The path module used for path manipulation functions"""
        raise NotImplementedError('must implement path_module')  # pragma: no cover

    @ClassProperty
    @classmethod
    def path_class(cls):
        """What class should be used to construct new instances from this class"""
        return cls
    _next_class = path_class

    def _has_incompatible_path_module(self, other):
        """Returns true if the other path is a storage utils path and has a
        compatible path module for path operations"""
        return isinstance(other, StorageUtilsPathMixin) and other.path_module != self.path_module

    def __div__(self, rel):
        """Join two path components (self / rel), adding a separator character if needed."""
        if self._has_incompatible_path_module(rel):
            return NotImplemented
        return self.path_class(self.path_module.join(self, rel))

    def __rdiv__(self, rel):
        """Join two path components (rel / self), adding a separator character if needed."""
        if self._has_incompatible_path_module(rel):
            return NotImplemented
        return self.path_class(self.path_module.join(rel, self))

    # Make the / operator work even when true division is enabled.
    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    def __add__(self, more):
        if self._has_incompatible_path_module(more):
            return NotImplemented
        return self.path_class(super(StorageUtilsPathMixin, self).__add__(more))

    def __radd__(self, other):
        if self._has_incompatible_path_module(other):
            return NotImplemented
        if not isinstance(other, string_types):
            return NotImplemented
        return self.path_class(other.__add__(self))


class StorageUtilsPath(StorageUtilsPathMixin, Path):
    """
    A base Path object that utilizes a vendored path.py module
    and provides basic cross-compatibility on operations between
    paths on different file systems.

    For documentation on path.py, view
    https://pythonhosted.org/path.py/api.html

    For documentation on individual methods in the ``Path`` object,
    consult their counterparts in :mod:`os.path`.

    Some methods are additionally included from :mod:`shutil`.
    The functions are linked directly into the class namespace
    such that they will be bound to the Path instance. For example,
    ``Path(src).samepath(target)`` is equivalent to
    ``os.path.samepath(src, target)``. Therefore, when referencing
    the docs for these methods, assume ``src`` references ``self``,
    the Path instance.
    """
    @ClassProperty
    @classmethod
    def path_module(cls):
        return cls.module

    @ClassProperty
    @classmethod
    def path_class(cls):
        return cls._next_class

    def open(self, *args, **kwargs):
        """
        Opens a path and retains interface compatibility with
        `SwiftPath` by popping the unused ``swift_upload_args`` keyword
        argument.
        """
        kwargs.pop('swift_upload_kwargs', None)
        return super(StorageUtilsPath, self).open(*args, **kwargs)