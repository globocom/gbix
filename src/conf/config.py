#################################################
#                GBIX Admin                     #
#################################################
# These are the credentials to GBIX do any      #
# operations that requires Admin permissions,   #
# like getting all triggers in getTriggers      #
# method.                                       #
#                                               #
#################################################
credentials = dict(
    user='admin.api',
    password='mypassword'
)


#################################################
#                RO Instance                    #
#################################################
# In case you have a Read-Only Zabbix instance, #
# when activating 'status=True', the method     #
# generateGraphs will return the urls pointing  #
# always to Zabbix Read-Only instance set in    #
# 'fe_readonly_instance_url'.                   #
#                                               #
#################################################
active_ro_instance = dict(
    status=False,
    fe_readonly_instance_url='http://myzabbix.read-only.instance/'
)

#################################################
#               Zabbix endpoint.                #
#################################################
# When Zabbix and GBIX are in the same host     #
# Eg: http://localhost:81/api_jsonrpc.php     #
#                                               #
# When Zabbix is remote for GBIX                #
# Eg: http://myzabbix.com/api_jsonrpc.php       #
#                                               #
#################################################
endpointZ = 'http://api.zabbix.dev.globoi.com/'


###########################################################
#                      Cache Options.                     #
###########################################################
# Parameters used in UWSGI's caches. Every cache          #
# here must be in accordance to uwsgi.ini file.           #
#                                                         #
# See more in:                                            #
# http://uwsgi-docs.readthedocs.io/en/latest/Caching.html #
#                                                         #
###########################################################
cache_options = dict(
    triggerGet=dict(
        name='cache_getTriggers',
        expiration_time=60
    ),
    default=dict(
        name='cache_all',
        expiration_time=60
    ),
    updates=dict(
        name='cache_updates',
        expiration_time=30
    ),
    itemGet=dict(
        name='itemGet',
        expiration_time=3600
    ),
    graphGet=dict(
        name='graphGet',
        expiration_time=3600
    )
)