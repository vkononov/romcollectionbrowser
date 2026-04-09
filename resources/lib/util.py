from builtins import str
from builtins import object
import os
import re

try:
    import html as _html_stdlib
except ImportError:
    _html_stdlib = None

from html.parser import HTMLParser

import xbmc, xbmcaddon, xbmcvfs

#
# CONSTANTS AND GLOBALS #
#
SCRIPTNAME = 'Rom Collection Browser'
SCRIPTID = 'script.games.rom.collection.browser'
CURRENT_CONFIG_VERSION = "2.2.0"
CURRENT_DB_VERSION = '2.2.2'
ISTESTRUN = False

__addon__ = xbmcaddon.Addon(id='%s' % SCRIPTID)
__language__ = __addon__.getLocalizedString

#time to wait before automatic playback starts
WAITTIME_PLAYERSTART = 500
#time that xbmc needs to close the player (before we can load the list again)
WAITTIME_PLAYERSTOP = 500
#time that xbmc needs to update controls (before we can rely on position)
WAITTIME_UPDATECONTROLS = 100
#don't call onAction if last call was not more than x ms before
WAITTIME_ONACTION = 50
#don't call onAction if last call was not more than x ms before (we need higher values on xbox)
WAITTIME_ONACTION_XBOX = 600
#use a little delay before applying filter settings
WAITTIME_APPLY_FILTERS = 500

LOG_LEVEL_ERROR = 0
LOG_LEVEL_WARNING = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3

CURRENT_LOG_LEVEL = LOG_LEVEL_INFO

MAXNUMGAMES_ENUM = [0, 100, 250, 500, 1000, 2500, 5000, 10000]

SETTING_RCB_VIEW_MODE = 'rcb_view_mode'
SETTING_RCB_SKIN = 'rcb_skin'
SETTING_RCB_LOGLEVEL = 'rcb_logLevel'
SETTING_RCB_ESCAPECOMMAND = 'rcb_escapeEmulatorCommand'
SETTING_RCB_PREFERLOCALNFO = 'rcb_PreferNfoFileIfAvailable'
SETTING_RCB_ENABLEFULLREIMPORT = 'rcb_enableFullReimport'
SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES = 'rcb_overwriteWithNullvalues'
SETTING_RCB_IGNOREGAMEWITHOUTDESC = 'rcb_ignoreGamesWithoutDesc'
SETTING_RCB_SHOWENTRYALLCONSOLES = 'rcb_showEntryAllConsoles'
SETTING_RCB_PREVENTUNFILTEREDSEARCH = 'rcb_preventUnfilteredSearch'
SETTING_RCB_USECLEARLOGOASTITLE = 'rcb_useClearlogoAsTitle'
SETTING_RCB_SHOWSCROLLBARS = 'rcb_showScrollbars'
SETTING_RCB_SAVEVIEWSTATEONEXIT = 'rcb_saveViewStateOnExit'
SETTING_RCB_SAVEVIEWSTATEONLAUNCHEMU = 'rcb_saveViewStateOnLaunchEmu'
SETTING_RCB_SHOWIMPORTOPTIONSDIALOG = 'rcb_showImportOptions'
SETTING_RCB_SCRAPINGMODE = 'rcb_scrapingMode'
SETTING_RCB_SCRAPONSTART = 'rcb_scrapOnStartUP'
SETTING_RCB_LAUNCHONSTARTUP = 'rcb_launchOnStartup'
SETTING_RCB_SCRAPEONSTARTUPACTION = 'rcb_scrapeOnStartupAction'
SETTING_RCB_SHOWFAVORITESTARS = 'rcb_showFavoriteStars'
SETTING_RCB_FAVORITESSELECTED = 'rcb_favoritesSelected'
SETTING_RCB_SEARCHTEXT = 'rcb_searchText'
SETTING_RCB_CURRENTSCREENSAVER = 'rcb_currentScreensaver'
SETTING_RCB_IMPORTOPTIONS_DISABLEROMCOLLECTIONS = 'rcb_disableRomcollections'
SETTING_RCB_IMPORTOPTIONS_ISRESCRAPE = 'rcb_isRescrape'
SETTING_RCB_NFOFOLDER = 'rcb_nfoFolder'
SETTING_RCB_PRELAUNCHDELAY = 'rcb_prelaunchDelay'
SETTING_RCB_POSTLAUNCHDELAY = 'rcb_postlaunchDelay'
SETTING_RCB_USEVBINSOLOMODE = 'rcb_useVBInSoloMode'
SETTING_RCB_SUSPENDAUDIO = 'rcb_suspendAudio'
SETTING_RCB_TOGGLESCREENMODE = 'rcb_toggleScreenMode'
SETTING_RCB_DISABLESCREENSAVER = 'rcb_disableScreenSaver'
SETTING_RCB_EMUAUTOCONFIGPATH = 'rcb_pathToEmuAutoConfig'
SETTING_RCB_MAXNUMGAMESTODISPLAY = 'rcb_maxNumGames'
SETTING_RCB_COLORFILE = 'rcb_colorfile'
SETTING_RCB_SHOWNAVIGATIONHINT = 'rcb_showNavigationHint'
SETTING_RCB_PLOT_STRIP_HTML = 'rcb_plotStripHtml'
SETTING_RCB_IGNORE_ARTICLES_WHEN_SORTING = 'rcb_ignoreArticlesWhenSorting'

SCRAPING_OPTION_AUTO_ACCURATE = 0
SCRAPING_OPTION_INTERACTIVE = 1

SCRAPING_OPTION_AUTO_ACCURATE_TXT = 'Automatic: Accurate'
SCRAPING_OPTION_INTERACTIVE_TXT = 'Interactive: Select Matches'

#
# UI #
#

VIEW_MAINVIEW = 'mainView'
VIEW_GAMEINFOVIEW = 'gameInfoView'

IMAGE_CONTROL_BACKGROUND = 'background'
IMAGE_CONTROL_GAMELIST = 'gamelist'
IMAGE_CONTROL_GAMELISTSELECTED = 'gamelistselected'
IMAGE_CONTROL_GAMEINFO_BIG = 'gameinfobig'

IMAGE_CONTROL_GAMEINFO_UPPERLEFT = 'gameinfoupperleft'
IMAGE_CONTROL_GAMEINFO_UPPERRIGHT = 'gameinfoupperright'
IMAGE_CONTROL_GAMEINFO_LOWERLEFT = 'gameinfolowerleft'
IMAGE_CONTROL_GAMEINFO_LOWERRIGHT = 'gameinfolowerright'

IMAGE_CONTROL_GAMEINFO_UPPER = 'gameinfoupper'
IMAGE_CONTROL_GAMEINFO_LOWER = 'gameinfolower'
IMAGE_CONTROL_GAMEINFO_LEFT = 'gameinfoleft'
IMAGE_CONTROL_GAMEINFO_RIGHT = 'gameinforight'

IMAGE_CONTROL_1 = 'extraImage1'
IMAGE_CONTROL_2 = 'extraImage2'
IMAGE_CONTROL_3 = 'extraImage3'
VIDEO_CONTROL_VideoWindowBig = 'videowindowbig'
VIDEO_CONTROL_VideoWindowSmall = 'videowindowsmall'
VIDEO_CONTROL_VideoFullscreen = 'videofullscreen'

IMAGE_CONTROL_CLEARLOGO = 'clearlogo'

html_unescape_table = {
    "&amp;": "&",
    "&quot;": '"',
    "&apos;": "'",
    "&gt;": ">",
    "&lt;": "<",
    "&nbsp;": " ",
    "&#x26;": "&",
    "&#x27;": "\'",
    "&#xB2;": "2",
    "&#xB3;": "3",
}

def html_unescape(text):
    if text is None:
        return ''
    text = convertToUnicodeString(text)
    if _html_stdlib is not None:
        return _html_stdlib.unescape(text)
    for key in list(html_unescape_table.keys()):
        text = text.replace(key, html_unescape_table[key])
    return text


#replace html tags with kodi tags in plot
html_kodi_table = {
    "<i>": "[I]",
    "</i>": "[/I]",
    "<b>": "[B]",
    "</b>": "[/B]",
    "<br>": "[CR]",
}


def html_to_kodi(text):
    """Legacy: basic tag replace. Prefer html_plot_to_kodi_labels or format_game_plot_for_display."""
    for key in list(html_kodi_table.keys()):
        text = text.replace(key, html_kodi_table[key])

    return text


class _StripPlotHTMLParser(HTMLParser):
    """Collect visible text; approximate paragraph breaks after block-level tags."""

    _BLOCK_BREAK = frozenset({
        'p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'section', 'article', 'blockquote', 'pre',
    })

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self._chunks = []

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t == 'br':
            self._chunks.append('\n')
        elif t in self._BLOCK_BREAK:
            self._chunks.append('\n')

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self._BLOCK_BREAK:
            self._chunks.append('\n')

    def handle_data(self, data):
        self._chunks.append(data)

    def get_text(self):
        s = ''.join(self._chunks)
        s = re.sub(r'[ \t\f\v]+', ' ', s)
        s = re.sub(r'\n{3,}', '\n\n', s)
        return s.strip()


def strip_html_plot(text):
    """Turn HTML (e.g. from NFO plot) into plain text for Kodi labels."""
    if not text:
        return ''
    raw = html_unescape(text)
    parser = _StripPlotHTMLParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception:
        return re.sub(r'<[^>]+>', ' ', raw)
    return parser.get_text()


def _strip_plot_crlf_edges(t):
    """Remove leading/trailing [CR] so plots do not start or end with a blank line."""
    t = re.sub(r'^(\s*\[CR\]\s*)+', '', t)
    t = re.sub(r'(\s*\[CR\]\s*)+$', '', t)
    return t.strip()


def html_plot_to_kodi_labels(text):
    """Map common HTML to Kodi formatting ([B],[I],[CR]). Unknown tags removed.

    Kodi skins use label/textbox formatting tags, not a full HTML engine.
    """
    if not text:
        return ''
    t = html_unescape(text)
    # Anchor: keep link text only (URLs in plot are long and not clickable in labels)
    t = re.sub(r'(?is)<a\s[^>]*>(.*?)</a>', r'\1', t)
    # Line breaks (single) inside a paragraph
    t = re.sub(r'(?i)<br\s*/?>', '[CR]', t)
    # Paragraphs: use double [CR] between blocks (visible gap). Opening <p> must not add a leading break.
    t = re.sub(r'(?is)</p\s*>\s*<p(?:\s[^>]*)?>', '[CR][CR]', t)
    t = re.sub(r'(?is)^\s*<p(?:\s[^>]*)?>', '', t)
    t = re.sub(r'(?is)</p\s*>', '[CR][CR]', t)
    t = re.sub(r'(?is)<p(?:\s[^>]*)?>', '', t)
    # Emphasis (including semantic HTML from scrapers)
    pairs = (
        ('em', '[I]', '[/I]'),
        ('i', '[I]', '[/I]'),
        ('strong', '[B]', '[/B]'),
        ('b', '[B]', '[/B]'),
    )
    for tag, o, c in pairs:
        t = re.sub(r'</%s\s*>' % tag, c, t, flags=re.IGNORECASE)
        t = re.sub(r'<%s\s*>' % tag, o, t, flags=re.IGNORECASE)
    # Legacy simple tags
    t = html_to_kodi(t)
    # Drop any remaining markup
    t = re.sub(r'<[^>]+>', '', t)
    # Collapse 3+ consecutive line breaks to at most a paragraph gap (double [CR])
    t = re.sub(r'(?:\s*\[CR\]\s*){3,}', '[CR][CR]', t)
    return _strip_plot_crlf_edges(t)


def ignore_articles_when_sorting_games():
    """Match Kodi-style title sort: skip leading The / A / An when sorting by game name."""
    if ISTESTRUN:
        return True
    try:
        s = getSettings().getSetting(SETTING_RCB_IGNORE_ARTICLES_WHEN_SORTING)
        if s == '':
            return True
        return s.upper() == 'TRUE'
    except Exception:
        return True


def sql_game_list_order_by(sort_column, sort_direction, ignore_articles=None):
    """Build ORDER BY clause for GameView queries. When sorting by name and ignore_articles is
    true, strip English articles for ordering (secondary sort by full name for stability).
    """
    if sort_direction is None or str(sort_direction).strip() == '':
        sort_direction = 'ASC'
    sort_direction = str(sort_direction).upper()
    if sort_direction not in ('ASC', 'DESC'):
        sort_direction = 'ASC'
    if ignore_articles is None:
        ignore_articles = ignore_articles_when_sorting_games()
    if ignore_articles and sort_column == 'name':
        sort_key = (
            "(CASE "
            "WHEN LOWER(TRIM(name)) GLOB 'the *' THEN TRIM(SUBSTR(TRIM(name), 5)) "
            "WHEN LOWER(TRIM(name)) GLOB 'a *' THEN TRIM(SUBSTR(TRIM(name), 3)) "
            "WHEN LOWER(TRIM(name)) GLOB 'an *' THEN TRIM(SUBSTR(TRIM(name), 4)) "
            "ELSE TRIM(name) END)"
        )
        return "ORDER BY %s COLLATE NOCASE %s, name COLLATE NOCASE %s" % (
            sort_key, sort_direction, sort_direction)
    return "ORDER BY %s COLLATE NOCASE %s" % (sort_column, sort_direction)


def format_game_plot_for_display(text, strip_html_override=None):
    """Prepare stored description for Kodi listitem/skin properties.

    strip_html_override: if True/False, force plain or Kodi formatting; if None, use addon setting.
    """
    if not text:
        return ''
    if strip_html_override is True:
        return strip_html_plot(text)
    if strip_html_override is False:
        return html_plot_to_kodi_labels(text)
    if ISTESTRUN:
        return html_plot_to_kodi_labels(text)
    try:
        if getSettings().getSetting(SETTING_RCB_PLOT_STRIP_HTML).upper() == 'TRUE':
            return strip_html_plot(text)
    except Exception:
        pass
    return html_plot_to_kodi_labels(text)


def joinPath(part1, *parts):
    if (part1.startswith('smb://')):
        #remove trailing "/"
        path = part1.strip("/")
        for part in parts:
            path = "%s/%s" % (path, part)
    else:
        path = os.path.join(part1, *parts)

    return path


#
# METHODS #
#

def current_os():
    cos = ''
    # FIXME TODO Add other platforms
    # Map between Kodi's platform name (defined in http://kodi.wiki/view/List_of_boolean_conditions)
    # and the os name in emu_autoconfig.xml
    platforms = ('System.Platform.Android',
                 'System.Platform.OSX',
                 'System.Platform.Windows',
                 'System.Platform.Linux')

    for platform in platforms:
        if xbmc.getCondVisibility(platform):
            cos = platform.split('.')[-1]
            break

    return cos


class KodiVersions(object):
    HELIX = 14
    ISENGARD = 15
    JARVIS = 16
    KRYPTON = 17
    LEIA = 18

    @classmethod
    def getKodiVersion(self):
        version = xbmc.getInfoLabel("System.BuildVersion")[:2]
        # Alternately:
        # version = xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')
        return int(version)


def localize(string_id):
    try:
        return __language__(string_id)
    except:
        return "Sorry. No translation available for string with id: " + str(string_id)


def getAddonDataPath():
    path = u''
    path = convertToUnicodeString(xbmcvfs.translatePath('special://profile/addon_data/%s' % (SCRIPTID)))

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            path = ''
    return path


def getAddonInstallPath():
    path = u''
    path = convertToUnicodeString(__addon__.getAddonInfo('path'))

    return path


def convertToUnicodeString(s, encoding='utf-8'):
    """Safe decode byte strings to Unicode"""
    if isinstance(s, bytes):  # This works in Python 2.7 and 3+
        s = s.decode(encoding)
    return s


def path_exists(path):
    """True if path exists for local files or Kodi VFS (nfs://, smb://, special://, ...).

    os.path.exists only sees the real filesystem; Clean Database and similar checks
    must use xbmcvfs so remote sources are not treated as missing.
    """
    if not path:
        return False
    path = convertToUnicodeString(path)
    return bool(xbmcvfs.exists(path))


def getEmuAutoConfigPath():
    settings = getSettings()
    path = settings.getSetting(SETTING_RCB_EMUAUTOCONFIGPATH)
    if path == '':
        path = os.path.join(getAddonDataPath(), u'emu_autoconfig.xml')

    if not xbmcvfs.exists(path):
        oldPath = os.path.join(getAddonInstallPath(), 'resources', 'emu_autoconfig.xml')
        xbmcvfs.copy(oldPath, path)

    return path


def getTempDir():
    tempDir = os.path.join(getAddonDataPath(), 'tmp')

    try:
        #check if folder exists
        if not os.path.isdir(tempDir):
            os.mkdir(tempDir)
        return tempDir
    except Exception as exc:
        Logutil.error('Error creating temp dir: ' + str(exc))
        return None


def getConfigXmlPath():
    if not ISTESTRUN:
        addonDataPath = getAddonDataPath()
        configFile = os.path.join(addonDataPath, "config.xml")
    else:
        configFile = os.path.join(getAddonInstallPath(), "resources", "lib", "TestDataBase", "config.xml")

    Logutil.info('Path to configuration file: ' + str(configFile))
    return configFile


def getSettings():
    settings = xbmcaddon.Addon(id='%s' % SCRIPTID)
    return settings


#HACK: XBMC does not update labels with empty strings
def setLabel(label, control):
    if label == '':
        label = ' '

    control.setLabel(str(label))


#HACK: XBMC does not update labels with empty strings
def getLabel(control):
    label = control.getLabel()
    if label == ' ':
        label = ''

    return label


def getConfiguredSkin():
    skin = "Default"
    settings = getSettings()
    skin = settings.getSetting(SETTING_RCB_SKIN)
    if skin == "Estuary":
        skin = "Default"

    return skin


RCBHOME = getAddonInstallPath()


class Logutil(object):
    # Class variable
    currentLogLevel = None

    levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
    prefix = ['RCB_ERROR', 'RCB_WARNING', 'RCB_INFO', 'RCB_DEBUG']

    # Note that we don't call __init__ since we use class methods, not instance methods

    @classmethod
    def __log(cls, level, message):
        # Init if not already set
        if cls.currentLogLevel is None:
            xbmc.log("RCB: initialising log level")
            cls.currentLogLevel = cls.getCurrentLogLevel()
            xbmc.log("RCB: current log level initialised to " + str(cls.currentLogLevel))

        if cls.currentLogLevel < level:
            return

        try:
            #xbmc.log(u"{0} {1}".format(str(cls.prefix[level]), message).encode('utf-8'))
            xbmc.log(u"{0} {1}".format(str(cls.prefix[level]), message))
        except Exception as e:
            xbmc.log(("Warning when trying to log in RCB: {0}".format(e)))

    @classmethod
    def debug(cls, message):
        cls.__log(LOG_LEVEL_DEBUG, message)

    @classmethod
    def info(cls, message):
        cls.__log(LOG_LEVEL_INFO, message)

    @classmethod
    def warn(cls, message):
        cls.__log(LOG_LEVEL_WARNING, message)

    @classmethod
    def error(cls, message):
        cls.__log(LOG_LEVEL_ERROR, message)

    @staticmethod
    def getCurrentLogLevel():
        logLevel = 1
        try:
            settings = getSettings()
            logLevelStr = settings.getSetting(SETTING_RCB_LOGLEVEL)
            if logLevelStr == 'ERROR':
                logLevel = LOG_LEVEL_ERROR
            elif logLevelStr == 'WARNING':
                logLevel = LOG_LEVEL_WARNING
            elif logLevelStr == 'INFO':
                logLevel = LOG_LEVEL_INFO
            elif logLevelStr == 'DEBUG':
                logLevel = LOG_LEVEL_DEBUG
        except:
            pass
        return logLevel
