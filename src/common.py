from flask_jsonrpc.exceptions import InvalidParamsError

import fowardZ
import re


def hostExists(host):

    if not isinstance(host, basestring):
        raise InvalidParamsError('Host parameter must be a string.')

    result_host_get = fowardZ.sendToZabbix(method="host.get", params={'filter': {'name': host},
                                                                      #'selectMacros': 'extend',
                                                                      #'selectParentTemplates': 'templateid',
                                                                      #'selectGroups': 'groupid',
                                                                      'output': ['host', 'name', 'hostid'],
                                                                      'selectInterfaces': 'extend'},
                                           auth=None)

    if 'result' in result_host_get and result_host_get['result']:
        return result_host_get['result'][0]
    elif 'error' in result_host_get:
        raise InvalidParamsError('Error on check {0} existence.'.format(host))
    else:
        return False


def convertToSeconds(time):
    if re.match("^\d*[smhdwMy]?$", time) is None:
        raise InvalidParamsError('Wrong period format: \'{0}\'.'.format(time))

    mult = re.search('^\d+', time)

    if mult is None:
        mult = 1
    else:
        mult = int(mult.group())

    unit = re.search('[smhdwMy]$', time)

    if unit is not None:
        unit = unit.group()
    else:
        unit = 's'

    if unit == 's':
        seconds = mult
    elif unit == 'm':
        seconds = mult * 60
    elif unit == 'h':
        seconds = mult * 3600
    elif unit == 'd':
        seconds = mult * 86400
    elif unit == 'w':
        seconds = mult * 604800
    elif unit == 'M':
        seconds = mult * 2592000
    elif unit == 'y':
        seconds = mult * 31536000
    else:
        raise InvalidParamsError('Wrong period format: \'{0}\'.'.format(time))

    if (seconds < 3600) or (seconds > 63072000):
        raise InvalidParamsError('Time period should be between 1 hour (3600 seconds) and 2 years (63072000 seconds)')

    return str(seconds)


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


class N2I:

    @staticmethod
    def isName(group):
        if re.match('(^[0-9]+$)', group):
            return False
        else:
            return True

    def hostgroup(self, name):
        if self.isName(name):
            result = fowardZ.sendToZabbix(method="hostgroup.get", params={'filter': {'name': name}})
            if 'result' in result and result['result']:
                return result['result'][0]['groupid']
            else:
                raise InvalidParamsError('Hostgroup not found: \'{0}\' . '.format(name))
        else:
            return name

    def template(self, name):
        if self.isName(name):
            result = fowardZ.sendToZabbix(method="template.get", params={'filter': {'host': name}})

            if 'result' in result and result['result']:  # and 'templateid' in result['result'][0]['templateid']:
                return result['result'][0]['templateid']
            else:
                raise InvalidParamsError('Template not found: \'{0}\' . '.format(name))
        else:
            return name

    def proxy(self, name):
        if self.isName(name):
            result = fowardZ.sendToZabbix(method="proxy.get", params={'filter': {'host': name}})

            if 'result' in result and result['result']:  # and 'proxyid' in result['result'][0]['proxyid']:
                return result['result'][0]['proxyid']
            else:
                raise InvalidParamsError('Proxy not found: \'{0}\' . '.format(name))
        else:
            return name


def addGroup(addgroups, groups=None):
    if (groups is None) and addgroups is None:
        return []

    if addgroups is None:
        return groups

    if groups is None:
        groups = list()

    if not isinstance(addgroups, list):
        groupsList = [addgroups]
    else:
        groupsList = addgroups

    for group in groupsList:
        groups.append(group)

    return groups

n2i = N2I()