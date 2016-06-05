import requests
import json
import uuid


class RateLimitError(Exception):

    def __init__(self):
        self.value = '403 Error/Rate Limit Encountered'


class APIError(Exception):

    def __init__(self, value):
        self.value = value


class HypeM(object):
    '''TODO: Change hm_token check to len > 0 instead of type == bool?'''

    _auth = 'swagger'  # auth doesn't even appear to be necessary
    _api = 'https://api.hypem.com/v2/'
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
                self.hm_token = self.get_token(username=username, password=password)
        if auth:
            self._auth = auth

    '''Helper properties and methods'''

    @property
    def _key(self):
        '''API auth key property'''
        return 'key=' + self._auth

    def _get(self, qstring, hm_token):
        '''Handles auth, API query, status checking, and json conversion.
        May raise an exception depending on response status code.
        Returns JSON response.

        Args:
            - string qstring: string for API query without auth key
            - string hm_token: user token (or True if using self.hm_token)
            - function requests_fn: appropriate function from the requests
                library (GET, POST, DELETE)'''
        if hm_token:
            qstring += self._hm_token(self.hm_token)
        qstring += self._key
        response = requests.get(self._api + qstring, headers=self.headers)
        self._check_status(response)
        return json.loads(response.text)

    def _post(self, endpoint, payload):
        response = requests.post(self._api + endpoint, data=payload)
        self._check_status(response)
        return json.loads(response.text)

    def _delete(self, endpoint, payload):
        response = requests.delete(self._api + endpoint, data=payload)
        self._check_status(response)
        return json.loads(response.text)

    def _param(self, param, value):
        '''Formats a parameter/value pair for html
        Args:
            - param: parameter name
            - value: value for parameter

        Returns correctly formatted parameter/value'''
        if value:
            return param + '=' + str(value) + '&'
        else:
            return ''

    def _count(self, count):
        '''Formats count parameter'''
        return self._param('count', count)

    def _page(self, page):
        '''Formats page parameter'''
        return self._param('page', page)

    def _hm_token(self, hm_token):
        '''Formats hm_token parameter'''
        if hm_token:
            # if passed a bool, use self.hm_token
            if type(hm_token) is bool:
                return self._param('hm_token', self.hm_token)
        # otherwise, use string
        return self._param('hm_token', hm_token)

    def _page_count(self, page, count):
        '''Formats page and count parameters'''
        return self._page(page) + self._count(count)

    def _check_status(self, response):
        '''Saves a bit of typing'''
        sc = response.status_code
        # 2xx statuses are all success
        if sc // 100 == 2:
            return
        elif sc == 403:
            raise RateLimitError()
        elif sc == 401:
            response = json.loads(response.text)
            raise APIError(response['error_msg'])
        else:
            raise ValueError('Status code unhandled: ' + str(sc))

    def get_own_auth(self):
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

    '''GET methods'''

    def get_blogs(self, hydrate=False, page=None, count=None, hm_token=None):
        '''Lists all blogs currently tracked by Hype Machine.
        Not paginated by default, but accepts page and count parameters as normal
        (recommended if hydrated). Pass hydrate=1 to get a sub-list of recently
        posted artists, and possibly other metadata

        Args:
            Optional:
            - bool hydrate: include recently posted tracks in response
            - int page: page of collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'blogs?'
        if hydrate:
            query_string += self._param('hydrate', 1)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_blogs_count(self, hm_token=None):
        '''Get total count of blogs in directory (useful for pagination)

        Args:
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'blogs/count?'
        return self._get(query_string, hm_token)

    def get_blog(self, siteid, hm_token=None):
        '''Get blog information like url, number of subscribers, etc

        Args:
            REQUIRED:
            - string siteid: the id of the site

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'blogs/' + str(siteid) + '?'
        return self._get(query_string, hm_token)

    def get_blog_tracks(self, siteid, page=None, count=None, hm_token=None):
        '''Get tracks covered by a blog

        Args:
            REQUIRED:
            - string siteid: the id of the site

            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'blogs/' + str(siteid) + '/tracks?'
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_tracks(self, q=None, sort=None, page=None, count=None, hm_token=None):
        '''List of tracks, unfiltered and chronological (equivalent to 'Latest -> All'
        on the site) by default. Sort options will yield fully sorted result sets when
        combined with a search parameter (?q=...) or summary charts (loved => popular,
        posted => popular/artists) on their own

        Args:
            Optional:
            - string q: a string to search for
            - string sort: sort chronologically, by number of favorites or number of
                blog posts (default is 'latest', must be combined with 'q' otherwise)
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        assert sort in ('latest', 'loved', 'posted') or sort is None, '"Sort" param must be "latest", "loved", or "posted"'
        query_string = 'tracks?'
        query_string += self._param('q', q)
        query_string += self._param('sort', sort)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_track(self, itemid, hm_token=None):
        '''Get metadata of a single track, by ID

        Args:
            REQUIRED:
            - string itemid: ID of track

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'tracks/' + str(itemid) + '?'
        return self._get(query_string, hm_token)

    def get_track_blogs(self, itemid, hm_token=None):
        '''Blogs that posted a track, by ID

        Args:
            REQUIRED:
            - string itemid: ID of track

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'tracks/' + str(itemid) + '/blogs?'
        return self._get(query_string, hm_token)

    def get_track_favorites(self, itemid, hm_token=None):
        '''Get users that favorited a track, by ID

        Args:
            REQUIRED:
            - string itemid: ID of track

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'tracks/' + str(itemid) + '/users?'
        return self._get(query_string, hm_token)

    def get_popular(self, mode=None, page=None, count=None, hm_token=None):
        '''Various popular charts: 3 day top 50 ('now'), calendar last week
        ('lastweek'), remixes excluded or remixes only. Aliased as
        /tracks?sort=popular for ontological consistency

        Args:
            Optional:
            - string mode: a string to search for (now, lastweek, noremix, remix)
            - string sort: sort chronologically, by number of favorites or number of
                blog posts (default is 'latest', must be combined with 'q' otherwise)
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        assert mode in ('now', 'lastweek', 'noremix', 'remix') or mode is None, \
            '"Mode" must be "now", "lastweek", "noremix," or "remix"'
        query_string = 'popular?'
        query_string += self._param('mode', mode)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_set_tracks(self, setname, hm_token):
        '''Get tracks in a previously defined set specified by setname

        Args:
            REQUIRED:
            - string setname: A short name of the set, for example 'test'

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'set/' + setname + '/tracks?'
        return self._get(query_string, hm_token)

    def get_artists(self, sort='popular', page=None, count=None, hm_token=None):
        '''Equivalent to popular artists chart on the site

        Args:
            REQUIRED:
            - string sort: sort mode (currently must be 'popular')

            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        assert sort == 'popular', '"Sort" currently must be "popular"'
        query_string = 'artists?'
        query_string += self._param('sort', sort)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_artist(self, artist, hm_token=None):
        '''Get artist metadata like artist thumbnail. Artist must be URI encoded

        Args:
            REQUIRED:
            - string artist: the artist

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'artists/' + artist + '?'
        return self._get(query_string, hm_token)

    def get_artist_tracks(self, artist, page=None, count=None, hm_token=None):
        '''Get tracks by an artist. Artist must be URI encoded

        Args:
            REQUIRED:
            - string artist: the artist

            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        query_string = 'artists/' + artist + '/tracks?'
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_featured(self, type_param=None, page=None, count=None, hm_token=None):
        assert type_param in ('all', 'premiere') or type_param is None, '"type_param" must be "all" or "premiere"'
        query_string = 'featured?'
        query_string += self._param('type', type_param)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def get_tags(self, hm_token=None):
        '''List all tags

        Args:
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'tags?'
        return self._get(query_string, hm_token)

    def get_tag(self, tag, hm_token=None):
        '''Get blog information like url, number of subscribers, etc

        Args:
            REQUIRED:
            - string tag: the genre tag

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'tags/' + tag + '?'
        return self._get(query_string, hm_token)

    def get_tag_tracks(self, tag, fav_from=None, fav_to=None, page=None,
                       count=None, hm_token=None):
        '''Get latest tracks for a tag

        Args:
            REQUIRED:
            - string tag: the genre tag

            Optional:
            - int fav_from: minimum favorite count
            - int fav_to: maximum favorite count
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        query_string = 'tags/' + tag + '/tracks?'
        query_string += self._param('fav_from', fav_from)
        query_string += self._param('fav_to', fav_to)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._get(query_string, hm_token)

    def search_users(self, q, hm_token=None):
        '''Search for a user by username/name

        Args:
            REQUIRED:
            - string q: username or name to search

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'users?'
        query_string += self._param('q', q)
        return self._get(query_string, hm_token)

    def get_user(self, username, hm_token=None):
        '''Get user metadata

        Args:
            REQUIRED:
            - string username: the username

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'users/' + username + '?'
        return self._get(query_string, hm_token)

    def get_user_favorites(self, username, page=None, count=None, hm_token=None):
        '''Get latest tracks for a tag

        Args:
            REQUIRED:
            - string username: the username

            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        query_string = 'users/' + username + '/favorites?'
        query_string += self._page_count(page, count)
        return self._get(query_string, hm_token)

    def get_user_playlist(self, username, playlist_id=0, page=None, count=None):
        '''Get items in the user's playlist

        Args:
            REQUIRED:
            - string username: the username
            - int playlist_id: the playlist id (0, 1, or 2)

            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        assert playlist_id in (0, 1, 2), '"Playlist_id" must be 0, 1, or 2'
        query_string = 'user/' + username + '/playlists/' + playlist_id + '?'
        query_string += self._page_count(page, count)
        # this endpoint doesn't take the hm_token param
        return self._get(query_string, None)

    def get_user_friends(self, username, page=None, count=None, hm_token=None):
        '''Not paginated by default, but accepts page and count parameters as normal

        Args:
            REQUIRED:
            - string username: the username

            Optional:
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        query_string = 'users/' + username + '/friends?'
        query_string += self._page_count(page, count)
        return self._get(query_string, hm_token)

    def get_my_favorites(self, hm_token, page=None, count=None):
        '''Get my favorites

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token

            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response
        '''
        query_string = 'me/favorites?'
        query_string += self._hm_token(hm_token)
        query_string += self._page_count(page, count)
        return self._get(query_string, hm_token)

    def get_my_playlist(self, hm_token, playlist_id=0, page=None, count=None):
        '''Get items in my playlist (assuming I have one)

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token
            - int playlist_id: id of playlist

            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response
        '''
        assert playlist_id in (0, 1, 2), '"Playlist_id" must be 0, 1, or 2'
        query_string = 'me/playlists/' + str(playlist_id) + '?'
        query_string += self._page_count(page, count)
        return self._get(query_string, hm_token)

    def get_my_history(self, hm_token, sort='latest', page=None, count=None):
        '''Get my history

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token

            Optional:
            - string sort: sort chronologically or by frequency of recent
                listening (default is 'latest') ('latest' or 'obsessed')
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response
        '''
        assert sort in ('latest', 'obsessed') or sort is None, \
            '"Sort" must be "latest" or "obsessed"'
        query_string = 'me/history?'
        query_string += self._param('sort', sort)
        query_string += self._page_count(page, count)
        return self._get(query_string, hm_token)

    def get_my_friends(self, hm_token, page=None, count=None):
        '''Get my friends
        Not paginated by default, but accepts page and count parameters as normal

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token

            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response
        '''
        query_string = 'me/friends?'
        query_string += self._page_count(page, count)
        return self._get(query_string, hm_token)

    def get_my_feed(self, hm_token, mode=None):
        '''Get my subscriptions feed

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token

            Optional:
            - string mode: feed items only from this source (default is 'all')
                ('all,' 'blogs,' 'artists,' 'friends')

        Returns JSON of response
        '''
        query_string = 'me/feed?'
        query_string += self._param('mode', mode)
        return self._get(query_string, hm_token)

    def get_my_feed_count(self, hm_token):
        '''Get my feed count

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        query_string = 'me/feed/count?'
        return self._get(query_string, hm_token)

    '''POST methods'''

    def get_token(self, username=None, password=None, fb_oauth_token=None,
                  tw_oauth_token=None, tw_oauth_token_secret=None):
        '''Obtain an auth token
        Returns an hm_token like /signup. You must use this token to authenticate
        all requests for a logged-in user. Requires username and password OR fb
        token OR twitter token and secret (accounts must be connected via website
        first)

        Args:
            - string username: username
            - string password: password
            - string fb_oauth_token: a facebook API auth token (must be currently
                valid)
            - string tw_oauth_token: a twitter API token secret
            - string tw_oauth_token_secret: a twitter API token

        Returns an hm_token '''
        assert (username and password) or fb_oauth_token or (tw_oauth_token and tw_oauth_token_secret)
        endpoint = 'get_token'
        payload = {}
        payload['username'] = username
        payload['password'] = password
        # device_id should be 128-bit HEX string
        # generate a random UUID
        device_id = str(uuid.uuid4())
        payload['device_id'] = device_id
        response = requests.post(self._api + endpoint, data=payload)
        self._check_status(response)
        return json.loads(response.text)['hm_token']

    def add_to_favorites(self, val, hm_token=None, type='item'):
        '''Add to favorites
        Returns 1 or 0, reflecting the final state of the item (1 is favorite,
        0 is not)

        Args:
            REQUIRED:
            - string val: id of resource to favorite, generally numerical
                paramType: Body
            - string hm_token: user token from /signup or /get_token
                paramType: Query

            Optional:
            - string type: type of resource to favorite (default is 'item')
                ('item', 'site', 'user')
                paramType: Body
        '''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        endpoint = 'me/favorites?' + 'hm_token=' + hm_token
        payload = {}
        payload['type'] = type
        payload['val'] = val
        return self._post(endpoint, payload)

    def add_to_playlist(self, itemid, hm_token=None, playlist_id=0):
        '''Add item to playlist.
        Returns 1 or 0, reflecting success and failure, respectively.
        Will also add item to favorites, if not already present there

        Args:
            REQUIRED:
            - string itemid: itemid of item to add
                paramType: Body
            - string hm_token: user token from /signup or /get_token
                paramType: Query

            Optional:
            - int playlist_id: id of playlist
            '''

        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        assert playlist_id in (0, 1, 2), '"Playlist_id" must be 0, 1, or 2'
        endpoint = 'me/playlists/' + str(playlist_id) + '?hm_token=' + hm_token
        payload = {}
        payload['itemid'] = itemid
        payload['playlist_id'] = playlist_id
        return self._post(endpoint, payload)

    def add_to_history(self, itemid, pos=0, hm_token=None, ts=None, type='listen'):
        '''Add user action to history.
        Log an action to site history, currently only listen events but
        eventually other types
        Returns status

        Args: TODO'''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        assert type == 'listen', '"Type" must currently be "listen"'
        endpoint = 'me/history?hm_token=' + hm_token
        payload = {}
        payload['itemid'] = itemid
        payload['pos'] = pos
        payload['type'] = type
        if ts:
            payload['ts'] = ts
        return self._post(endpoint, payload)

    def reset_feed_count(self, hm_token=None):
        '''Reset number of "unread" items in my feed to zero
        Returns status'''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        endpoint = 'me/feed/count?hm_token=' + hm_token
        return self._post(endpoint, {})

    def forgot_password(self, username):
        '''Request password reset email'''
        endpoint = 'forgot_password'
        payload = {}
        payload['username'] = username
        return self._post(endpoint, payload)

    def connect(self, hm_token=None, fb_uid=None, fb_oauth_token=None, tw_oauth_token=None, tw_oauth_token_secret=None):
        '''Connect existing Hype Machine account with an external service
        (Twitter, Facebook, etc)'''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        assert any(fb_uid, fb_oauth_token, tw_oauth_token, tw_oauth_token_secret), 'Must provide at least one valid token'
        if tw_oauth_token or tw_oauth_token_secret:
            assert tw_oauth_token and tw_oauth_token_secret, 'Must provide both twitter token and secret'
        '''Should this assert both fb_uid and fb_oauth_token as well?? Not sure'''
        endpoint = 'connect?hm_token=' + hm_token
        payload = {}
        if fb_uid:
            payload['fb_uid'] = fb_uid
        if fb_oauth_token:
            payload['fb_oauth_token'] = fb_oauth_token
        if tw_oauth_token:
            payload['tw_oauth_token'] = tw_oauth_token
            payload['tw_oauth_token_secret'] = tw_oauth_token_secret
        return self._post(endpoint, payload)

    def disconnect(self, type, hm_token=None):
        '''Disconnects a previously connected account.
        Does not verify connection prior to removal.'''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        assert type in ('fb', 'tw'), '"Type" must be "fb" or "tw"'
        endpoint = 'disconnect?hm_token=' + hm_token
        payload = {}
        payload['type'] = type
        return self._post(endpoint, payload)

    def signup(self, username, email, password, newsletter,
               fb_uid=None, fb_oauth_token=None, tw_oauth_token=None,
               tw_oauth_token_secret=None):
        '''Create account
        This requires a resonably unique device_id. Returns an hm_token upon
        success, which you can pass as a query parameter to all other endpoints
        to auth your account. Optionally accepts facebook and twitter tokens to
        connect those accounts.'''
        endpoint = 'signup'
        device_id = uuid.uuid4()
        payload = {}
        payload['username'] = username
        payload['email'] = email
        payload['password'] = password
        payload['newsletter'] = newsletter
        payload['device_id'] = device_id
        if fb_uid:
            payload['fb_uid'] = fb_uid
        if fb_oauth_token:
            payload['fb_oauth_token'] = fb_oauth_token
        if tw_oauth_token:
            payload['tw_oauth_token'] = tw_oauth_token
            payload['tw_oauth_token_secret'] = tw_oauth_token_secret
        return self._post(endpoint, payload)

    '''DELETE methods'''

    def remove_item_from_playlist(self, itemid, hm_token=None, playlist_id=0):
        '''Removes an item from a playlist.
        Returns 1 or 0, reflecting success and failure, respectively. Will NOT
        remove item from favorites'''
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Post methods require a valid hm_token'
        assert playlist_id in (0, 1, 2), '"Playlist_id" must be 0, 1, or 2'
        endpoint = 'me/playlists/' + str(playlist_id) + '/items/' + itemid + \
            '?hm_token=' + hm_token
        payload = {}
        payload['itemid'] = itemid
        return self._delete(endpoint, payload)
