c = get_config()
c.IPClusterEngines.engine_launcher_class = 'SSHEngineSetLauncher'
f = open('/home/kirienko/mpd.test','r').readlines()
c.SSHEngineSetLauncher.engines = dict(map(lambda x:(x.strip(),1),f))
c.SSHEngineSetLauncher.engine_args = ['--profile=ssh', '--ip="*"']
