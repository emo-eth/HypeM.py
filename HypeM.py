import requests
import json
import uuid
import warnings
from bs4 import BeautifulSoup


class RateLimitError(Exception):

    def __init__(self):
        self.value = '403 Error/Rate Limit Encountered'


class APIError(Exception):

    def __init__(self, value):
        self.value = value


class HypeM(object):

    _auth = 'swagger'  # auth doesn't even appear to be necessary
    _api = 'https://api.hypem.com/v2'
    headers = {'User-Agent': 'HypeM.py'}
    hm_token = ''

    test_song = '2fv7a'
    test_blog = 22830
    test_artist = 'ratherbright'
    test_tag = 'indie'

    def __init__(self, username=None, password=None, auth=None, hm_token=None):
        if username:
            assert password, 'Must pass both username and password'
        if password:
            assert username, 'Must pass both username and password'
        if hm_token:
            self.hm_token = hm_token
        else:
            if username and password:
                self.hm_token = self.get_token(
                    username=username, password=password)
        if auth:
            self._auth = auth
        self.session = requests.Session()
        self.session.headers = self.headers

    '''Helper properties and methods'''

    @property
    def _key(self):
        '''API auth key property'''
        return 'key=' + self._auth

    def _get(self, qstring):
        '''Handles auth, API query, status checking, and json conversion.
        May raise an exception depending on response status code.
        Returns JSON response.

        Args:
            - string qstring: string for API query without auth key'''
        qstring += self._key
        response = requests.get(self._api + qstring, headers=self.headers)
        self._check_status(response)
        return json.loads(response.text)

    def _post(self, endpoint, payload):
        payload['key'] = self._auth
        response = requests.post(self._api + endpoint, data=payload)
        self._check_status(response)
        return json.loads(response.text)

    def _delete(self, endpoint, payload):
        payload['key'] = self._auth
        response = requests.delete(self._api + endpoint, data=payload)
        self._check_status(response)
        return json.loads(response.text)

    def _parse_params(self, locals_copy, endpoint_args):
        '''Format all params for GET request'''
        query_string = ''
        # remove self since it is superfluous
        for val in ['self', 'query_string'] + endpoint_args:
            locals_copy.pop(val)
        for param, val in locals_copy.items():
            query_string += self._param(param, val)
        return query_string

    def _parse_payload(self, locals_copy, endpoint_args):
        '''Remove self and endpoint args from POST/DELETE payload'''
        for val in ['self'] + endpoint_args:
            locals_copy.pop(val)
        return locals_copy

    def _param(self, param, value):
        '''Formats a parameter/value pair for html
        Args:
            - param: parameter name
            - value: value for parameter

        Returns correctly formatted parameter/value'''
        if value:
            if param == 'hm_token' and type(value) is bool:
                value = self.hm_token
            return param + '=' + str(value) + '&'
        else:
            return ''

    def _assert_hm_token(self, hm_token):
        '''Falls back to the object's hm_token if necessary, and and raises an
        assertion error if there is no token. Used for endpoints that require
        a valid hm_token.'''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        return hm_token

    def _check_status(self, response):
        '''Checks response status and raises errors accordingly'''
        sc = response.status_code
        # 2xx statuses are all success
        if sc // 100 == 2:
            assert response.text, 'Invalid response from server'
            return
        elif sc == 403:
            raise RateLimitError()
        elif sc == 401:
            response = json.loads(response.text)
            raise APIError(response['error_msg'])
        else:
            raise ValueError('Status code unhandled: ' +
                             str(sc) + ' for URL ' + response.url)

    def get_session_auth(self):
        '''Gets a session auth key from the HypeM website cookies'''
        req = requests.get('http://hypem.com', headers=self.headers)
        if req.status_code == 200:
            # it's, uh, either index 1 or 3..?
            auth = req.cookies['AUTH'].split('%3A')[1]
            self._auth = auth
            return auth
        else:
            print('Unable to access HypeM')
            return None

    def set_auth(self, auth):
        '''Change to user-supplied auth token.
        Uses auth from API documentation by default'''
        self._auth = auth

    ''' Methods '''

    ''' /artists '''

    def popular_artists(self, sort, page=None, count=None, hm_token=None):
        """Popular Artists
        Equivalent to popular artists chart on the site
        GET method

        Args:
            REQUIRED:
            - string sort: sort mode (currently must be 'popular')
                allowable values: popular
            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        assert str(sort) in ['popular'], '"sort" must be popular'

        query_string = '/artists?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def get_artist_info(self, artist, hm_token=None):
        """Get artist metadata
        Get artist metadata like artist thumbnail. Artist must be URI encoded
        GET method

        Args:
            REQUIRED:
            - string artist: the artist
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/artists/' + str(artist) + '?'
        query_string += self._parse_params(locals().copy(), ['artist'])
        return self._get(query_string)

    def get_artist_tracks(self, artist, page=None, count=None, hm_token=None):
        """Get artist tracks
        Artist must be URI encoded
        GET method

        Args:
            REQUIRED:
            - string artist: the artist
            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/artists/' + str(artist) + '/tracks?'
        query_string += self._parse_params(locals().copy(), ['artist'])
        return self._get(query_string)
    ''' /blogs '''

    def list_blogs(self, hydrate=None, page=None, count=None, hm_token=None):
        """List all blogs
        Lists all blogs currently tracked by Hype Machine. Not paginated by
        default, but accepts page and count parameters as normal (recommended
        if hydrated). Pass hydrate=1 to get a sub-list of recently posted
        artists, and possibly other metadata
        GET method

        Args:
            REQUIRED:

            Optional:
            - bool hydrate: include recently_posted?
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/blogs?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def list_blogs_count(self, hm_token=None):
        """Get count of blogs
        Get total count of blogs in directory (useful for pagination)
        GET method

        Args:
            REQUIRED:

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/blogs/count?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def get_site_info(self, siteid, hm_token=None):
        """Get blog metadata
        Get blog information like url, number of subscribers, etc
        GET method

        Args:
            REQUIRED:
            - int siteid: the id of the site
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/blogs/' + str(siteid) + '?'
        query_string += self._parse_params(locals().copy(), ['siteid'])
        return self._get(query_string)

    def get_blog_tracks(self, siteid, page=None, count=None, hm_token=None):
        """Get blog tracks

        GET method

        Args:
            REQUIRED:
            - int siteid: the id of the site
            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/blogs/' + str(siteid) + '/tracks?'
        query_string += self._parse_params(locals().copy(), ['siteid'])
        return self._get(query_string)

    ''' /featured '''

    def featured(self, type='all', page=None, count=None, hm_token=None):
        """Get featured things, interleaved or separated
        count and page are only meaningful in 'premieres' mode, otherwise we
        serve 6 pemieres and 1 site, in chronological order
        GET method

        Args:
            REQUIRED:

            Optional:
            - string type: type of featured thing to return (default is 'all')
                allowable values: premieres, all
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        assert str(type) in ['premieres', 'all'], ('"type" must be premieres'
                                                   'or all')

        query_string = '/featured?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    ''' /me '''

    def favorites_me(self, hm_token=None, page=None, count=None):
        """Get my favorites

        GET method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)

        query_string = '/me/favorites?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def toggle_favorite(self, type, val, hm_token=None):
        """Add to favorites
        Returns 1 or 0, reflecting the final state of the item (1 is favorite,
        0 is not)
        POST method

        Args:
            REQUIRED:
            - string type: type of resource to favorite
                allowable values: item, site, user
            - string val: id of resource to favorite, generally numerical
            - string hm_token: user token from /signup or /get_token
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(type) in ['item', 'site', 'user'], ('"type" must be item or'
                                                       'site or user')

        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/me/favorites'  # defined after payload bc of locals() call

        return self._post(endpoint, payload)

    def playlist_me(self, playlist_id, hm_token=None, page=None, count=None):
        """Get items in my playlist
        Playlist names are available at /me/playlist_names
        GET method

        Args:
            REQUIRED:
            - int playlist_id: id of playlist
                allowable values: 0, 1, 2
            - string hm_token: user token from /signup or /get_token
            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(playlist_id) in ['0', '1', '2'], ('"playlist_id" must be 0 '
                                                     'or 1 or 2')

        query_string = '/me/playlists/' + str(playlist_id) + '?'
        query_string += self._parse_params(locals().copy(), ['playlist_id'])
        return self._get(query_string)

    def add_playlist(self, playlist_id, itemid, hm_token=None):
        """Add item to playlist
        Returns 1 or 0, reflecting success and failure, respectively. Will
        also add item to favorites, if not already present there
        POST method

        Args:
            REQUIRED:
            - int playlist_id: id of playlist
                allowable values: 0, 1, 2
            - string itemid: itemid of item to add
            - string hm_token: user token from /signup or /get_token
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(playlist_id) in ['0', '1', '2'], ('"playlist_id" must be 0 '
                                                     'or 1 or 2')

        payload = self._parse_payload(locals().copy(), ['playlist_id'])
        endpoint = '/me/playlists/' + str(playlist_id) + ''
        # defined afterpayload bc of locals() call

        return self._post(endpoint, payload)

    def remove_playlist(self, playlist_id, itemid, hm_token=None):
        """Remove item from playlist
        Returns 1 or 0, reflecting success and failure, respectively. Will NOT
        remove item from favorites
        DELETE method

        Args:
            REQUIRED:
            - int playlist_id: id of playlist
                allowable values: 0, 1, 2
            - string itemid: itemid of item to remove
            - string hm_token: user token from /signup or /get_token
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(playlist_id) in ['0', '1', '2'], ('"playlist_id" must be 0 '
                                                     'or 1 or 2')

        payload = self._parse_payload(locals().copy(), ['playlist_id',
                                                        'itemid'])
        endpoint = ('/me/playlists/' + str(playlist_id) + '/items/' +
                    str(itemid) + '')
        # defined after payload bc of locals() call

        return self._delete(endpoint, payload)

    def history_me(self, hm_token=None, sort='latest', page=None, count=None):
        """Get my history

        GET method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:
            - string sort: sort chronologically or by frequency of recent
            listening (default is 'latest')
                allowable values: latest, obsessed
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(sort) in ['latest', 'obsessed'], ('"sort" must be latest or'
                                                     ' obsessed')

        query_string = '/me/history?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def log_user_action(self, type, itemid, pos, hm_token=None, ts=None):
        """Add user action to history
        Log an action to site history, currently only listen events but
        eventually other types
        POST method

        Args:
            REQUIRED:
            - string type: type of action to add
                allowable values: listen
            - string itemid: id of resource for action (for items only
                currently)
            - int pos: playback head position (must be < 45 to show in site
                history)
            - string hm_token: user token from /signup or /get_token
            Optional:
            - int ts: timestamp of action, defaults to now (you can provide
                past timestamps for offline plays)

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(type) in ['listen'], '"type" must be listen'

        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/me/history'  # defined after payload bc of locals() call

        return self._post(endpoint, payload)

    def friends_me(self, hm_token=None, count=None, page=None):
        """Get my friends
        Not paginated by default, but accepts page and count parameters as
        normal
        GET method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:
            - int count: items per page
            - int page: the page of the collection

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)

        query_string = '/me/friends?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def feed(self, hm_token=None, mode='all'):
        """Get my subscriptions feed

        GET method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:
            - string mode: feed items only from this source (default is 'all')
                allowable values: blogs, artists, friends, all

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(mode) in ['blogs', 'artists', 'friends', 'all'], (
            '"mode" ''must be blogs or artists or friends or all')

        query_string = '/me/feed?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def feed_count(self, hm_token=None):
        """Get number of "unread" items in my feed

        GET method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)

        query_string = '/me/feed/count?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def reset_feed_count(self, hm_token=None):
        """Reset number of "unread" items in my feed to zero

        POST method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)

        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/me/feed/count'
        # defined after payload bc of locals() call

        return self._post(endpoint, payload)

    ''' / '''

    def forgot_password(self, username):
        """Request password reset email

        POST method

        Args:
            REQUIRED:
            - string username: user to reset password for
            Optional:


        Returns JSON of response.
        """

        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/forgot_password'
        # defined after payload bc of locals() call

        return self._post(endpoint, payload)

    def connect(self, hm_token=None, fb_uid=None, fb_oauth_token=None,
                tw_oauth_token=None, tw_oauth_token_secret=None):
        """Connect existing Hype Machine account with an external service
        (Twitter, Facebook, etc)
        At least one external service token is required. To use this for 3rd
        party signup, try to log in with those credential first, then get
        hm_token and post it here with the 3rd party info
        POST method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            Optional:
            - string fb_uid: a facebook API uid
            - string fb_oauth_token: a facebook API auth token (must be
                currently valid)
            - string tw_oauth_token: a twitter API token secret
            - string tw_oauth_token_secret: a twitter API token

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert any(fb_uid, fb_oauth_token, tw_oauth_token,
                   tw_oauth_token_secret), (
            'Must provide at least one valid token')
        if tw_oauth_token or tw_oauth_token_secret:
            assert tw_oauth_token and tw_oauth_token_secret, (
                'Must provide both twitter token and secret')

        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/connect'  # defined after payload bc of locals() call

        return self._post(endpoint, payload)

    def disconnect(self, type, hm_token=None):
        """Disconnect an external service account
        Disconnects a previously connected account. Does not verify connection
        prior to removal.
        POST method

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            - string type: service to disconnect
                allowable values: fb, tw
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(type) in ['fb', 'tw'], '"type" must be fb or tw'

        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/disconnect'  # defined after payload bc of locals() call

        return self._post(endpoint, payload)

    def signup(self, username, email, password, newsletter, device_id=None,
               fb_uid=None, fb_oauth_token=None, tw_oauth_token=None,
               tw_oauth_token_secret=None):
        """Create account
        This requires a resonably unique device_id. Returns an hm_token upon
        success, which you can pass as a query parameter to all other
        endpoints to auth your account. Optionally accepts facebook and twitter
        tokens to connect those accounts.
        POST method

        Args:
            REQUIRED:
            - string username: desired username
            - string email: email address
            - string password: desired password
            - bool newsletter: receive newsletter?
            - hex device_id: exactly 16 hex characters (128 bits) uniquely
            identifying the client device
            Optional:
            - string fb_uid: a facebook API uid
            - string fb_oauth_token: a facebook API auth token (must be
                currently valid)
            - string tw_oauth_token: a twitter API token secret
            - string tw_oauth_token_secret: a twitter API token

        Returns JSON of response.
        """

        if not device_id:
            device_id = uuid.uuid4()
        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/signup'  # defined after payload bc of locals() call

        self.hm_token = self._post(endpoint, payload)
        return self.hm_token

    def get_token(self, username=None, password=None, fb_oauth_token=None,
                  tw_oauth_token=None, tw_oauth_token_secret=None):
        """Obtain an auth token
        Returns an hm_token like /signup. You must use this token to
        authenticate all requests for a logged-in user. Requires username and
        password OR fb token OR twitter token and secret (accounts must be
        connected via website first)
        POST method

        Args:
            REQUIRED:
            - string username: username
            - string password: password
            - string fb_oauth_token: a facebook API auth token (must be
            currently valid)
            - string tw_oauth_token: a twitter API token secret
            - string tw_oauth_token_secret: a twitter API token
            Optional:

        Returns JSON of response.
        """
        assert (username and password) or fb_oauth_token or (
            tw_oauth_token and tw_oauth_token_secret)
        device_id = str(uuid.uuid4())
        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/get_token'
        self.hm_token = self._post(endpoint, payload)['hm_token']

        return self.hm_token

    ''' /set '''

    def get_tracks_in_set(self, setname, hm_token=None):
        """Get tracks in a previously defined set specified by setname

        GET method

        Args:
            REQUIRED:
            - string setname: A short name of the set, for example 'test'
            Optional:
            - string hm_token: user token from /signup or /get_token, pass to
                include user's favorite information in result set

        Returns JSON of response.
        """

        query_string = '/set/' + str(setname) + '/tracks?'
        query_string += self._parse_params(locals().copy(), ['setname'])
        return self._get(query_string)

    ''' /tags '''

    def list_tags(self, hm_token=None):
        """List all tags

        GET method

        Args:
            REQUIRED:

            Optional:
            - string hm_token: user token from /signup or /get_token, pass to
                include user's favorite information in result set

        Returns JSON of response.
        """

        query_string = '/tags?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def get_tag_info(self, tag, hm_token=None):
        """Get blog metadata
        Get blog information like url, number of subscribers, etc
        GET method

        Args:
            REQUIRED:
            - string tag: the genere tag
            Optional:
            - string hm_token: user token from /signup or /get_token, pass to
                include user's favorite information in result set

        Returns JSON of response.
        """
        warnings.warn("This method doesn't seem to work and is "
                      "incorrectly documented at the source.", RuntimeWarning)
        query_string = '/tags/' + str(tag) + '?'
        query_string += self._parse_params(locals().copy(), ['tag'])
        return self._get(query_string)

    def get_tag_tracks(self, tag, fav_from=None, fav_to=None, page=None,
                       count=None, hm_token=None):
        """Get latest tracks for the tag

        GET method

        Args:
            REQUIRED:
            - int tag: the genre tag
            Optional:
            - int fav_from: minimum favorite count
            - int fav_to: maximum favorite count
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token, pass to
                include user's favorite information in result set

        Returns JSON of response.
        """

        query_string = '/tags/' + str(tag) + '/tracks?'
        query_string += self._parse_params(locals().copy(), ['tag'])
        return self._get(query_string)

    ''' /tracks '''

    def latest(self, q=None, sort='latest', page=None, count=None,
               hm_token=None):
        """Tracks
        List of tracks, unfiltered and chronological (equivalent to
        'Latest -> All' on the site) by default. Sort options will yield fully
        sorted result sets when combined with a search parameter (?q=...) or
        summary charts (loved => popular, posted => popular/artists) on their
        own
        GET method

        Args:
            REQUIRED:

            Optional:
            - string q: a string to search for
            - string sort: sort chronologically, by number of favorites or
            number of blog posts (default is 'latest', must be combined with
            'q' otherwise)
                allowable values: latest, loved, posted
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        assert str(sort) in ['latest', 'loved', 'posted'], (
            '"sort" must be latest or loved or posted')

        query_string = '/tracks?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def item(self, itemid, hm_token=None):
        """Single track
        Single track
        GET method

        Args:
            REQUIRED:
            - string itemid: id of item
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/tracks/' + str(itemid) + '?'
        query_string += self._parse_params(locals().copy(), ['itemid'])
        return self._get(query_string)

    def item_blogs(self, itemid, hm_token=None):
        """Posting blogs
        Blogs that posted this track
        GET method

        Args:
            REQUIRED:
            - string itemid: id of item
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/tracks/' + str(itemid) + '/blogs?'
        query_string += self._parse_params(locals().copy(), ['itemid'])
        return self._get(query_string)

    def item_users(self, itemid, hm_token=None):
        """Favoriting Users
        Users that favorited this track
        GET method

        Args:
            REQUIRED:
            - string itemid: id of item
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/tracks/' + str(itemid) + '/users?'
        query_string += self._parse_params(locals().copy(), ['itemid'])
        return self._get(query_string)

    def popular(self, mode='now', page=None, count=None, hm_token=None):
        """Popular tracks
        Various popular charts: 3 day top 50 ('now'), calendar last week
        ('lastweek'), remixes excluded or remixes only. Aliased as
        /tracks?sort=popular for ontological consistency
        GET method

        Args:
            REQUIRED:

            Optional:
            - string mode: Type of popular chart to display (default is 'now')
                allowable values: now, lastweek, noremix, remix
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        assert str(mode) in ['now', 'lastweek', 'noremix', 'remix'], (
            '"mode" must be now or lastweek or noremix or remix')

        query_string = '/popular?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    ''' /users '''

    def search_users(self, q=None, hm_token=None):
        """Search users
        Does not return anything without a query param
        GET method

        Args:
            REQUIRED:

            Optional:
            - string q: the username
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/users?'
        query_string += self._parse_params(locals().copy(), [])
        return self._get(query_string)

    def get_user(self, username, hm_token=None):
        """Get user metadata
        Get user information like url, number of subscribers, etc
        GET method

        Args:
            REQUIRED:
            - string username: the username
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/users/' + str(username) + '?'
        query_string += self._parse_params(locals().copy(), ['username'])
        return self._get(query_string)

    def get_user_tracks(self, username, page=None, count=None, hm_token=None):
        """Get the user's favorites

        GET method

        Args:
            REQUIRED:
            - string username: the username
            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/users/' + str(username) + '/favorites?'
        query_string += self._parse_params(locals().copy(), ['username'])
        return self._get(query_string)

    def playlis(self, username, playlist_id, page=None, count=None):
        """Get items in the user's playlist

        GET method

        Args:
            REQUIRED:
            - string username: the username
            - int playlist_id: id of playlist
                allowable values: 0, 1, 2
            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response.
        """

        assert str(playlist_id) in ['0', '1', '2'], (
            '"playlist_id" must be 0 or 1 or 2')

        query_string = ('/user/' + str(username) + '/playlists/' +
                        str(playlist_id) + '?')
        query_string += self._parse_params(locals().copy(),
                                           ['username', 'playlist_id'])
        return self._get(query_string)

    def get_user_history(self, username, page=None, count=None, hm_token=None):
        """Get the user's play history

        GET method

        Args:
            REQUIRED:
            - string username: the username
            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        query_string = '/users/' + str(username) + '/history?'
        query_string += self._parse_params(locals().copy(), ['username'])
        return self._get(query_string)

    def get_user_friends(self, username, hm_token=None, count=None, page=None):
        """Get the user's friends
        Not paginated by default, but accepts page and count parameters as
        normal
        GET method

        Args:
            REQUIRED:
            - string username: the username
            Optional:
            - string hm_token: user token from /signup or /get_token
            - int count: items per page
            - int page: the page of the collection

        Returns JSON of response.
        """

        query_string = '/users/' + str(username) + '/friends?'
        query_string += self._parse_params(locals().copy(), ['username'])
        return self._get(query_string)

    ''' scraping methods... please be nice to their servers '''

    def _get_soup(self, url):
        '''Returns a BeautifulSoup object for a given URL'''
        req = self.session.get(url)
        self._check_status(req)
        return BeautifulSoup(req.text, 'lxml')

    def get_track_tags(self, track_id):
        '''Scrapes the tags for a given, if any

        Args:
            - string track_id: track id of the song on HypeM

        Returns list of genre tags.'''

        genre_tags = []
        soup = self._get_soup('http://hypem.com/track/' + track_id)
        tag_box = soup.find('ul', 'tags')
        if not tag_box:
            return genre_tags
        tags = tag_box.find_all('li')
        if tags:
            for tag in tags:
                genre_tags.append(tag.text)
        return genre_tags

    def get_track_stream(self, track_id):
        '''Scrapes the link to the raw mp3 of a track.

        Args:
            - string track_id: the track_id of the song

        credit to @fzakaria: https://github.com/fzakaria/HypeScript

        Returns url to mp3 stream'''

        soup = self._get_soup('http://hypem.com/track/' + track_id)
        display_list = soup.find(id='displayList-data')
        if display_list is None:
            # if there is no display list, return empty string
            return ''
        # load the display_list variable as json, and get 1st element
        # (there may be more elements in display_list, but 1st should
        # be the specified track)
        track_list = json.loads(display_list.text)
        track_json = track_list['tracks'][0]
        key = track_json['key']
        id_ = track_json['id']
        type_ = track_json['type']
        if not type_:
            # type_ is false if stream no longer available
            return ''
        # get hypem to serve stream url
        serve_url = 'http://hypem.com/serve/source/{}/{}'.format(id_, key)
        song_data_response = self.session.get(serve_url,
                                              headers={'Content-Type':
                                                       'application/json'})
        song_data = json.loads(song_data_response.text)
        return song_data.get('url')

    ''' Aliases: methods renamed from HypeM nicknames '''

    get_popular_artists = popular_artists
    get_artist = get_artist_info
    get_blogs = list_blogs
    get_blogs_count = list_blogs_count
    get_blog = get_site_info
    get_featured = featured
    get_my_favorites = favorites_me
    favorite_track = toggle_favorite
    get_my_playlist = playlist_me
    add_to_playlist = add_playlist
    remove_from_playlist = remove_playlist
    get_my_history = history_me
    get_my_friends = friends_me
    get_my_feed = feed
    get_my_unread = feed_count
    reset_my_unread = reset_feed_count
    get_tags = list_tags
    get_tracks = latest
    get_track = item
    get_track_blogs = item_blogs
    get_track_favorites = item_users
    get_popular = popular
    get_user_playlist = playlis
