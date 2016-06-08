from flask_jsonrpc import Error

try:
    from flaskext.babel import gettext as _
    _("You're lazy...") # this function lazy-loads settings
except (ImportError, NameError):
    _ = lambda t, *a, **k: t


class VisibleNameLengthError(Error):
    """The parameter visible_name reached the maximum length and was not possible to decrease its length.
    """
    code = -32001
    message = _('Visible name has too many characters and it was not possible to truncate.')
