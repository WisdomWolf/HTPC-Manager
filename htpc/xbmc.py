from jsonrpclib import Server
from settings import *
from json import dumps

import urllib2
import urllib
import base64
import cherrypy
import os
import htpc
import platform
import subprocess
import sys

try:
    from PIL import Image
    from PIL import ImageEnhance
except:
    pass

def xbmcFetchDataFromUrl(url):
    try:
        data = urllib2.urlopen(url)
        return data
    except:
        return ''

def xbmcGetThumb(thumb, thumbWidth, thumbHeight, thumbOpacity):

    thumbParts = thumb.split('/')
    thumbFile = thumbParts.pop()
    thumbType = thumbParts.pop()

    xbmc_thumbs = os.path.join(htpc.userdata, 'xbmc_thumbs/')
    if not os.path.exists(xbmc_thumbs):
        os.makedirs(xbmc_thumbs)

    thumbOnDisk = os.path.join(xbmc_thumbs, thumbType + '_' + thumbFile)
    fileOut = os.path.join(xbmc_thumbs, thumbOnDisk + '_' + thumbWidth + '_' + thumbHeight + '.png')

    # If there is no local copy
    if not os.path.isfile(thumbOnDisk):
        config = readSettings()
        thumb = urllib.quote(thumb)
        url = 'http://' + config.get('xbmc_ip') + ':' + str(config.get('xbmc_port')) + '/image/' + thumb
        
        request = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (config.get('xbmc_username'), config.get('xbmc_password'))).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        fileObject = urllib2.urlopen(request)

        fileData = fileObject.read()
        f = open(thumbOnDisk, 'wb')
        f.write(fileData)
        f.close()

    # if there is no resized version
    if not os.path.isfile(fileOut):

        widthInt = int(thumbWidth)
        heightInt = int(thumbHeight)
        imageResized = False
        is_64bits = sys.maxsize > 2**32

        # Resize windows and linux with freeimage (dunno if it can exist on mac?) 32bit only
        if not is_64bits:
            try:
                import freeimage
                img = freeimage.Image(thumbOnDisk)
                cpy = img.resize(widthInt, heightInt, 5)
                cpy.save(fileOut)
                imageResized = True
                print 'Used FreeImage'
            except:
                pass

        # resize osx
        if platform.system() == 'Darwin' and not imageResized:
            try:
                subprocess.call(['sips', '-z', thumbHeight, thumbWidth, thumbOnDisk, '--out', fileOut])
                imageResized = True
                print 'Used sips'
            except:
                pass

        if platform.system() == 'Linux' and not imageResized:
            # resize with imagemagick
            try:
                subprocess.call(['convert', thumbOnDisk, '-resize', thumbWidth + 'x' + thumbHeight, fileOut])
                imageResized = True
                print 'Used ImageMagick'
            except:
                pass

        # resize PIL (for like openelec etc.)
        if not imageResized:
            try:
                image = Image.open(thumbOnDisk)
                newimage = image.resize((widthInt, heightInt), Image.ANTIALIAS).convert('RGBA')
                newimage.save(fileOut)
                print 'Used PIL'
            except:
                pass

    # If the image got resized fetch the resized one otherwise use the copy
    # This is just a fallback (it makes the browser slow)
    noresizeridentifier = os.path.join(htpc.userdata, 'no_resizer_found');
    if os.path.isfile(fileOut):
        f = open(fileOut, 'rb')
        try:
            os.unlink(noresizeridentifier)
        except:
            pass
    else:
        f = open(thumbOnDisk, 'rb')
        nf = open(noresizeridentifier, 'w')
        nf.write('1')
        nf.close()
    data = f.read()
    f.close()
    # Header setten en data returnen
    cherrypy.response.headers['Content-Type'] = "image/png"
    return data

def xbmcMakeUrl():
    config = readSettings()
    if config.has_key('xbmc_port') and config.has_key('xbmc_ip') and config.has_key('xbmc_username') and config.has_key('xbmc_password'):
        url = 'http://' + config.get('xbmc_username') + ':' + config.get('xbmc_password') + '@' + config.get('xbmc_ip') + ':' + str(config.get('xbmc_port'))
        return url

def xbmcGetMovies(limitstart=0,limitend=0,sortmethod='videotitle',sortorder='ascending'):
    ignorearticle = False
    config = readSettings()
    if config.has_key('sort_ignore_articles') and config.get('sort_ignore_articles') == 'yes':
        ignorearticle = True
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.VideoLibrary.GetMovies(sort={'order': sortorder, 'method' : sortmethod, 'ignorearticle' : ignorearticle}, properties=['title', 'year', 'plot', 'thumbnail', 'file', 'fanart', 'studio', 'trailer', 'genre', 'rating'], limits={'start' : int(limitstart), 'end' : int(limitend)})
    return dumps(data)

def xbmcGetShows(limitstart=0,limitend=0,sortmethod='videotitle',sortorder='ascending'):
    ignorearticle = bool(0)
    config = readSettings()
    if config.has_key('sort_ignore_articles') and config.get('sort_ignore_articles') == 'yes':
        ignorearticle = bool(1)
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.VideoLibrary.GetTVShows(sort={'order': sortorder, 'method' : sortmethod, 'ignorearticle' : ignorearticle}, properties=['title', 'year', 'plot', 'thumbnail'], limits={'start' : int(limitstart), 'end' : int(limitend)})
    return dumps(data)

def xbmcGetShow(id):
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    showinfo = server.VideoLibrary.GetTVShowDetails(tvshowid=int(id),properties=['title', 'thumbnail'])
    episodes = server.VideoLibrary.GetEpisodes(tvshowid=int(id),properties=['episode', 'season', 'thumbnail', 'plot', 'file'])
    episodes = episodes[u'episodes']
    seasons = {}
    for episode in episodes:
        if not seasons.has_key(episode[u'season']):
            seasons[episode[u'season']] = {}
        seasons[episode[u'season']][episode[u'episode']] = episode
    return dumps({'show' : showinfo, 'seasons' : seasons})

def xbmcPlayItem(file):
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.Player.Open(item={'file' : file})
    return dumps(data)

def xbmcNowPlaying():
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    player = server.Player.GetActivePlayers()
    application = server.Application.GetProperties(properties=['muted', 'volume', 'version'])
    if player:
        player = player[0]
        if player[u'type'] == 'video':
            try:
                playerInfo = server.Player.GetProperties(playerid=player[u'playerid'], properties=['speed', 'position', 'totaltime', 'time', 'percentage'])
            except:
                return
            if playerInfo:
                try:
                    itemInfo = server.Player.GetItem(playerid=player[u'playerid'], properties=['thumbnail', 'showtitle', 'year', 'episode', 'season', 'fanart'])
                    return dumps({'playerInfo' : playerInfo, 'itemInfo' : itemInfo, 'app' : application})
                except:
                    return

def xbmcControlPlayer(action):
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    if action == 'SetMute':
        method = 'Application.SetMute'
        data = server._request(methodname=method, params=['toggle'])
    elif action == 'MoveLeft':
        method = 'Player.MoveLeft'
        data = server._request(methodname=method, params={'playerid' : 1, 'value' : 'smallbackward'})
    elif action == 'MoveRight':
        method = 'Player.MoveRight'
        data = server._request(methodname=method, params={'playerid' : 1, 'value' : 'smallforward'})
    else:
        method = 'Player.' + action
        data = server._request(methodname=method, params={'playerid' : 1})
    return dumps(data)

def xbmcNotify(text):
    text = urllib2.unquote(text)
    config = readSettings()
    command = {'command': 'ExecBuiltIn', 'parameter': 'Notification(\'HTPC Manager\', \'' + text + '\')' }
    for key in command:
        if type(command[key]) == unicode:
            command[key] = command[key].encode('utf-8')

    enc_command = urllib.urlencode(command)
    url = 'http://' + config.get('xbmc_ip') + ':' + str(config.get('xbmc_port')) + '/xbmcCmds/xbmcHttp/?' + enc_command

    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (config.get('xbmc_username'), config.get('xbmc_password'))).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)

    return result.read()

def xbmcGetRecentMovies():
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.VideoLibrary.GetRecentlyAddedMovies(properties=['title', 'year', 'plot', 'thumbnail', 'file', 'fanart', 'studio', 'trailer', 'genre', 'rating'])
    return dumps(data)

def xbmcGetRecentShows():
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.VideoLibrary.GetRecentlyAddedEpisodes(properties=['episode', 'season', 'thumbnail', 'plot', 'fanart', 'title', 'file'])
    return dumps(data)

def xbmcGetRecentAlbums():
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.AudioLibrary.GetRecentlyAddedAlbums(properties=['artist', 'albumlabel', 'year', 'description', 'thumbnail'])
    return dumps(data)

def xbmcClean():
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.VideoLibrary.Clean()
    return dumps(data)

def xbmcScan():
    server = Server(xbmcMakeUrl() + '/jsonrpc')
    data = server.VideoLibrary.Scan()
    return dumps(data)