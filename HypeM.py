import requests
import json


class RateLimitError(Exception):

    def __init__(self):
        self.value = '403 Error/Rate Limit Encountered'


class APIError(Exception):

    def __init__(self, value):
        self.value = value


class HypeM(object):
    _auth = 'swagger'
    _api = 'https://api.hypem.com/v2/'
    headers = {'User-Agent': 'HypeM.py'}
    hm_token = ''

    def __init__(self, username=None, password=None, auth=None):
        if username:
            assert password, 'Must pass both username and password'
        if password:
            assert username, 'Must pass both username and password'
        if username and password:
            self.hm_token = self.get_token(username=username, password=password)
        if auth:
            self._auth = auth

    '''Helper properties and methods'''

    @property
    def _key(self):
        return 'key=' + self._auth

    def _query(self, qstring, hm_token):
        '''Handles auth, API query, status checking, and json conversion.
        May raise an exception depending on response status code.

        Args:
            - string qstring: string for API query without auth key
            - string hm_token: user token (or True if using self.hm_token)

        Returns json response as python dict.
        '''
        if hm_token:
            # if passed hm-token is valid, use it
            if type(hm_token) is str:
                qstring += self._hm_token(hm_token)
            # otherwise use the token assigned on init
            elif self.hm_token:
                qstring += self._hm_token(self.hm_token)
        qstring += self._key
        response = requests.get(self._api + qstring, headers=self.headers)
        self._check_status(response)
        return json.loads(response.text)

    def _param(self, param, value):
        '''Formats a parameter/value pair for html
        Args:
            - param: parameter name
            - value: value for parameter

        Returns correctly formatted parameter/value'''
        if value:
            return param + '=' + value + '&'
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
        return self._param('hm_token', hm_token)

    def _page_count(self, page, count):
        '''Formats page and count parameters'''
        return self._page(page) + self._count(count)

    def _check_status(self, response):
        '''Saves a bit of typing'''
        sc = response.status_code
        if sc == 200:
            return
        elif sc == 403:
            raise RateLimitError()
        elif sc == 401:
            response = json.loads(response.text)
            raise APIError(response['error_msg'])
        else:
            raise ValueError('Status code unhandled: ' + str(sc))

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
        return self._query(query_string, hm_token)

    def get_blogs_count(self, hm_token=None):
        '''Get total count of blogs in directory (useful for pagination)

        Args:
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'blogs/count?'
        return self._query(query_string, hm_token)

    def get_blog(self, siteid, hm_token=None):
        '''Get blog information like url, number of subscribers, etc

        Args:
            REQUIRED:
            - string siteid: the id of the site

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'blogs/' + siteid + '?'
        return self._query(query_string, hm_token)

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
        query_string = 'blogs/' + siteid + '/tracks?'
        query_string += self._page(page)
        query_string += self._count(count)
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

    def get_track(self, itemid, hm_token=None):
        '''Get metadata of a single track, by ID

        Args:
            REQUIRED:
            - string itemid: ID of track

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'tracks/' + itemid + '?'
        return self._query(query_string, hm_token)

    def get_track_blogs(self, itemid, hm_token=None):
        '''Blogs that posted a track, by ID

        Args:
            REQUIRED:
            - string itemid: ID of track

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'tracks/' + itemid + '/blogs?'
        return self._query(query_string, hm_token)

    def get_track_favorites(self, itemid, hm_token=None):
        '''Get users that favorited a track, by ID

        Args:
            REQUIRED:
            - string itemid: ID of track

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'tracks/' + itemid + '/users?'
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

    def get_set_tracks(self, setname, hm_token):
        '''Get tracks in a previously defined set specified by setname

        Args:
            REQUIRED:
            - string setname: A short name of the set, for example 'test'

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''

        query_string = 'set/' + setname + '/tracks?'
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

    def get_artist(self, artist, hm_token=None):
        '''Get artist metadata like artist thumbnail. Artist must be URI encoded

        Args:
            REQUIRED:
            - string artist: the artist

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'artists/' + artist + '?'
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

    def get_featured(self, type_param=None, page=None, count=None, hm_token=None):
        assert type_param in ('all', 'premiere') or type_param is None, '"type_param" must be "all" or "premiere"'
        query_string = 'featured?'
        query_string += self._param('type', type_param)
        query_string += self._page(page)
        query_string += self._count(count)
        return self._query(query_string, hm_token)

    def get_tags(self, hm_token=None):
        '''List all tags

        Args:
            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'tags?'
        return self._query(query_string, hm_token)

    def get_tag(self, tag, hm_token=None):
        '''Get blog information like url, number of subscribers, etc

        Args:
            REQUIRED:
            - string tag: the genre tag

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'tags/' + tag + '?'
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

    def get_user(self, username, hm_token=None):
        '''Get user metadata

        Args:
            REQUIRED:
            - string username: the username

            Optional:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response'''
        query_string = 'users/' + username + '?'
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

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
        return self._query(query_string, None)

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
        return self._query(query_string, hm_token)

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
        return self._query()

    def get_my_playlist(self, hm_token, playlist_id=0, page=None, count=None):
        '''Get items in my playlist

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
        query_string = 'me/playlists/' + playlist_id + '?'
        query_string += self._page_count(page, count)
        return self._query(query_string, hm_token)

    def get_my_history(self, hm_token, sort=None, page=None, count=None):
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
        query_string += self._param(sort)
        query_string += self._page_count(page, count)
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

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
        return self._query(query_string, hm_token)

    def get_my_feed_count(self, hm_token):
        '''Get my feed count

        Args:
            REQUIRED:
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response
        '''
        query_string = 'me/feed/count?'
        return self._query(query_string, hm_token)

    '''POST methods'''

    def get_token(self, username=None, password=None, fb_oauth_token=None,
                  tw_oauth_token=None, tw_oauth_token_secret=None):
        assert (username and password) or fb_oauth_token or (tw_oauth_token and tw_oauth_token_secret)
        return

    '''DELETE methods'''
