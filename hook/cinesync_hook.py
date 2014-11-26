from ftrack_connect_cinesync import __main__ as cinesync_main


def register(registry, **kw):
    '''Register hooks.'''
    action = cinesync_main.CinesyncLauncher()
    action.register()
