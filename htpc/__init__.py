import os
import sys
import cherrypy
import htpc.settings

from Cheetah.Template import Template

from htpc.updater import *
from htpc.tasks import *
from htpc.sabnzbd import *
from htpc.sickbeard import *
from htpc.couchpotato import *
from htpc.xbmc import *
from htpc.nzbsearch import *
from filemanager.reader import *

# Standaard variabelen
host = "0.0.0.0"
port = 8084
root = os.path.dirname(os.path.abspath(sys.argv[0]))
password = ''

# Userdata folder maken
userdata = os.path.join(root, 'userdata/')
if not os.path.isdir(userdata):
    os.makedirs(userdata)

# Interfaces folder
defaultinterface = 'default'
interfaces = os.path.join(root, 'interfaces/')

# Settings file
settingsfile = os.path.join(userdata, 'config.cfg')
config = htpc.settings.readSettings()

interfacefolder = 'default'
if config.has_key('theme') and config.get('theme') != '':
    interfacefolder = config.get('theme')

if config.has_key('my_port') and config.get('my_port') != '':
    configPort = config.get('my_port')
    port = int(configPort)

def CheckUpdateSchedule():
    config = readSettings();
    data = config.get('updateavailable')
    return data  
    
class pageHandler:
    def __init__(self, root):

        self.root = root
        self.webdir = os.path.join(self.root, 'interfaces/' + interfacefolder + '/')
        self.defaultwebdir = os.path.join(self.root, 'interfaces/' + defaultinterface + '/')
        self.appname = 'HTPC Manager'
        my_scheduler.start()

    def loadTemplateFile(self, template):
        if os.path.isfile(os.path.join(self.webdir, template)):
            tpl = os.path.join(self.webdir, template)
        else:
            tpl = os.path.join(self.defaultwebdir, template)
        return tpl

    @cherrypy.expose()
    def index(self):
        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()
        template = Template(file=self.loadTemplateFile('main.tpl'), searchList=[searchList]);
        template.appname = self.appname
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = ''
        template.jsfile = 'main.js'
        template.updateavailable = CheckUpdateSchedule()
        
        return template.respond()

    @cherrypy.expose()
    def settings(self, **kwargs):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # get available paths
        r = reader()
        availpaths = r.getDriveInfo()

        # Als er een POST is
        if kwargs:
            if kwargs.has_key('save_settings'):
                for path in availpaths:
                    if not kwargs.has_key('paths__' + path):
                        kwargs['paths__' + path] = 'no'
                if not kwargs.has_key('use_nzb'):
                    kwargs['use_nzb'] = 'no'
                if not kwargs.has_key('use_sb'):
                    kwargs['use_sb'] = 'no'
                if not kwargs.has_key('use_cp'):
                    kwargs['use_cp'] = 'no'
                if not kwargs.has_key('use_xbmc'):
                    kwargs['use_xbmc'] = 'no'
                if not kwargs.has_key('use_nzbmatrix'):
                    kwargs['use_nzbmatrix'] = 'no'
                if not kwargs.has_key('use_filemanger'):
                    kwargs['use_filemanger'] = 'no'    
                if not kwargs.has_key('xbmc_show_banners'):
                    kwargs['xbmc_show_banners'] = 'no'
                if not kwargs.has_key('sort_ignore_articles'):
                    kwargs['sort_ignore_articles'] = 'no'
                if not kwargs.has_key('use_dash_nzb'):
                    kwargs['use_dash_nzb'] = 'no'
                if not kwargs.has_key('use_dash_cp'):
                    kwargs['use_dash_cp'] = 'no'
                if not kwargs.has_key('use_dash_sb'):
                    kwargs['use_dash_sb'] = 'no'
                if not kwargs.has_key('use_dash_rec_music'):
                    kwargs['use_dash_rec_music'] = 'no'                    
                if not kwargs.has_key('use_dash_rec_tv'):
                    kwargs['use_dash_rec_tv'] = 'no'                      
                if not kwargs.has_key('use_dash_rec_movies'):
                    kwargs['use_dash_rec_movies'] = 'no'                      
                htpc.settings.saveSettings(kwargs)

            if kwargs.has_key('regenerate_thumbs'):
                htpc.settings.removeThumbs()

            raise cherrypy.HTTPRedirect('')

        # Paths for filemanager
        searchList['availpaths'] = availpaths
        searchList['availinterfaces'] = os.listdir(htpc.interfaces)

        # Fill template
        template = Template(file=self.loadTemplateFile('settings.tpl'), searchList=[searchList])
        template.appname = self.appname
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.jsfile = 'settings.js'
        template.submenu = 'settings'

        template.noresizer_found = 0
        noresizeridentifier = os.path.join(htpc.userdata, 'no_resizer_found');
        if os.path.isfile(noresizeridentifier):
            template.noresizer_found = 1

        return template.respond()

    @cherrypy.expose()
    def sabnzbd(self, **kwargs):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # Template vullen
        template = Template(file=self.loadTemplateFile('sabnzbd.tpl'), searchList=[searchList])
        template.appname = self.appname
        template.jsfile = 'sabnzbd.js'
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = 'sabnzbd'

        return template.respond()

    @cherrypy.expose()
    def sickbeard(self, **args):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # Template vullen
        template = Template(file=self.loadTemplateFile('sickbeard.tpl'), searchList=[searchList])
        template.jsfile = 'sickbeard.js'

        template.appname = self.appname
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = 'sickbeard'

        return template.respond()

    @cherrypy.expose()
    def couchpotato(self, **args):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # Template vullen
        template = Template(file=self.loadTemplateFile('couchpotato.tpl'), searchList=[searchList])
        template.jsfile = 'couchpotato.js'

        template.appname = self.appname
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = 'couchpotato'

        return template.respond()

    @cherrypy.expose()
    def xbmc(self, **args):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # Template vullen
        template = Template(file=self.loadTemplateFile('xbmc.tpl'), searchList=[searchList])
        template.jsfile = 'xbmc.js'

        template.appname = self.appname
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = 'xbmc'
        template.page_can_search = 'yes'

        return template.respond()

    @cherrypy.expose()
    def nzbsearch(self, **kwargs):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # Template vullen
        template = Template(file=self.loadTemplateFile('nzbsearch.tpl'), searchList=[searchList])
        template.appname = self.appname
        template.jsfile = 'nzbsearch.js'
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = 'nzbsearch'

        return template.respond()

    @cherrypy.expose()
    def filemanager(self, **kwargs):

        # Searchlist voor template ophalen
        searchList = htpc.settings.readSettings()

        # Template vullen
        template = Template(file=self.loadTemplateFile('filemanager.tpl'), searchList=[searchList])
        template.appname = self.appname
        template.jsfile = 'filemanager.js'
        template.defaultwebdir = self.defaultwebdir
        template.webdir = self.webdir
        template.submenu = 'filemanager'

        return template.respond()

    @cherrypy.expose()
    def json(self, **args):

        # Kijken welke actie we moeten ondernemen
        if args.get('which') == 'sabnzbd':
            if args.get('action') == 'history':
                return sabnzbdGetHistory(args.get('limit'))
            if args.get('action') == 'status':
                return sabnzbdGetStatus()
            if args.get('action') == 'warnings':
                return sabnzbdGetWarnings()
            if args.get('action') == 'pause' or args.get('action') == 'resume':
                return sabnzbdTogglePause(args.get('action'))
            if args.get('action') == 'addnzb':
                return sabnzbdAddNzbFromUrl(args.get('nzb_url'), args.get('nzb_category'))
            if args.get('action') == 'delete':
                return sabnzbdDeleteNzb(args.get('id'))
            if args.get('action') == 'deletehistory':
                return sabnzbdDeleteHistory(args.get('id'))
            if args.get('action') == 'retry':
                return sabnzbdRetry(args.get('id'))
            if args.get('action') == 'categories':
                return sabnzbdGetCategories()
            if args.get('action') == 'change_cat':
                return sabnzbdChangeCategory(args.get('id'), args.get('value'))
            if args.get('action') == 'speed':
                return sabnzbdSetSpeed(args.get('value'))

        if args.get('which') == 'sickbeard':
            if args.get('action') == 'showlist':
                return sbGetShowList()
            if args.get('action') == 'nextaired':
                return sbGetNextAired()
            if args.get('action') == 'getposter':
                return sbGetPoster(args.get('tvdbid'))
            if args.get('action') == 'history':
                return sbGetHistory(args.get('limit'))
            if args.get('action') == 'searchtvdb':
                return sbSearchShow(args.get('query'))
            if args.get('action') == 'logs':
                return sbGetLogs()
            if args.get('action') == 'addshow':
                return sbAddShow(args.get('tvdbid'))
            if args.get('action') == 'getshow':
                return sbGetShow(args.get('tvdbid'))

        if args.get('which') == 'couchpotato':
            if args.get('action') == 'movie.list':
                return cpGetMovieList()
            if args.get('action') == 'notification.list':
                return cpGetNotificationList()
            if args.get('action') == 'movie.delete':
                return cpDeleteMovie(args.get('id'))
            if args.get('action') == 'movie.refresh':
                return cpRefreshMovie(args.get('id'))
            if args.get('action') == 'movie.search':
                return cpSearchMovie(args.get('q'))
            if args.get('action') == 'movie.add':
                return cpAddMovie(args.get('profile_id'), args.get('identifier'), args.get('title'))

        if args.get('which') == 'xbmc':
            if args.get('action') == 'movies':
                limitstart = 0;
                if (args.has_key('start')):
                    limitstart = args.get('start')
                limitend = 0;
                if (args.has_key('end')):
                    limitend = args.get('end')
                return xbmcGetMovies(limitstart, limitend, args.get('sortmethod'), args.get('sortorder'))
            if args.get('action') == 'thumb':
                opacity = 100
                if args.has_key('o'):
                    opacity = args.get('o')
                return xbmcGetThumb(args.get('thumb'), args.get('w'), args.get('h'), opacity)
            if args.get('action') == 'shows':
                limitstart = 0;
                if (args.has_key('start')):
                    limitstart = args.get('start')
                limitend = 0;
                if (args.has_key('end')):
                    limitend = args.get('end')
                return xbmcGetShows(limitstart, limitend)
            if args.get('action') == 'play':
                return xbmcPlayItem(args.get('item'))
            if args.get('action') == 'getshow':
                return xbmcGetShow(args.get('item'))
            if args.get('action') == 'nowplaying':
                return xbmcNowPlaying()
            if  args.get('action') == 'controlplayer':
                return xbmcControlPlayer(args.get('do'));
            if  args.get('action') == 'notify':
                return xbmcNotify(args.get('text'));
            if  args.get('action') == 'recentmovies':
                return xbmcGetRecentMovies()
            if  args.get('action') == 'recentshows':
                return xbmcGetRecentShows()
            if  args.get('action') == 'recentalbums':
                return xbmcGetRecentAlbums()
            if  args.get('action') == 'clean':
                return xbmcClean()
            if  args.get('action') == 'scan':
                return xbmcScan()

        if args.get('which') == 'nzbsearch':
            if args.has_key('query'):
                return searchNZBs(args.get('query'))

        if args.get('which') == 'system':
            if  args.get('action') == 'shutdown':
                cherrypy.engine.exit()
                sys.exit(0)
            if  args.get('action') == 'restart':
                cherrypy.engine.exit()
                arguments = sys.argv[:]
                arguments.insert(0, sys.executable)
                if sys.platform == 'win32':
                    arguments = ['"%s"' % arg for arg in arguments]
                os.chdir(os.getcwd())
                os.execv(sys.executable, arguments)
            if args.get('action') == 'diskspace':
                if args.has_key('path') and args.get('path') != '':
                    r = reader()
                    fileList = r.readDir(path=args.get('path'))
                    return dumps(fileList)
                else:
                    settings = htpc.settings.readSettings()
                    r = reader()
                    availpaths = r.getDriveInfo()
                    toReturn = {}
                    for path in availpaths:
                        if settings.has_key('paths__' + path.lower()) and settings.get('paths__' + path.lower()) == 'yes':
                            toReturn[path] = availpaths[path]
                    return dumps(toReturn)
            if args.get('action') == 'update':
                cherrypy.engine.exit()
                DownloadNewVersion()
                CheckForUpdates()
                cherrypy.server.start()
                return dumps({'update' : 'success'})
            if args.get('action') == 'checkupdate':
                updateAvail = CheckForUpdates()
                return dumps(updateAvail)
