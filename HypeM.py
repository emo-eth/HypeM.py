import uuid
import warnings
import json
from bs4 import BeautifulSoup
from BaseAPI import BaseAPI


class HypeM(BaseAPI):
    '''Wrapper for the public HypeM RESTful HTTP API'''
    memo = {}  # used to cache method calls

    test_song = '2fv7a'
    test_blog = 22830
    test_artist = 'ratherbright'
    test_tag = 'indie'

    def __init__(self, username=None, password=None,
                 hm_token=None, payload_auth={'key': 'swagger'},
                 cache_life=3600):
        '''
        Args:
            Optional:
            string username: username of account with which to authenticate
            string password: password of account with which to authenticate
            string hm_token: hm_token of account with which to authenticate
            dict payload_auth: dictionary of auth information for calls
            number cache_life: length of time in seconds that a method call is
                retrieved from a cache before being retrieved from the server
                again
            '''
        super(HypeM, self).__init__('https://api.hypem.com/v2/',
                                    payload_auth=payload_auth,
                                    cache_life=cache_life)
        if username or password:
            assert username and password, ('Must pass both username and' +
                                           ' password')
        if hm_token:
            self.hm_token = hm_token
        else:
            self.hm_token = ''
        if username and password and not self.hm_token:
            self.hm_token = self.get_token(
                username=username, password=password)

    def _assert_hm_token(self, hm_token):
        if not hm_token:
            hm_token = self.hm_token
        assert hm_token, 'Authemticated methods require a valid hm_token'
        return hm_token

    ''' /artists '''

    @BaseAPI._memoize
    def popular_artists(self, sort='popular', page=None, count=None,
                        hm_token=None):
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'artists?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['artist'])
        query_string = 'artists/' + str(artist) + '?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['artist'])
        query_string = 'artists/' + str(artist) + '/tracks?' + params

        return self._get(query_string)

    ''' /blogs '''

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'blogs?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'blogs/count?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['siteid'])
        query_string = 'blogs/' + str(siteid) + '?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['siteid'])
        query_string = 'blogs/' + str(siteid) + '/tracks?' + params

        return self._get(query_string)

    ''' /featured '''

    @BaseAPI._memoize
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

        assert str(type) in ['premieres',
                             'all'], '"type" must be premieres or all'

        params = self._parse_params(locals().copy(), [])
        query_string = 'featured?' + params

        return self._get(query_string)

    ''' /me '''

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'me/favorites?' + params

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
        assert str(type) in ['item', 'site',
                             'user'], '"type" must be item or site or user'

        payload = self._parse_payload(locals().copy(), [])
        endpoint = 'me/favorites?' + self._param('hm_token', hm_token)

        return self._post(endpoint, payload)

    @BaseAPI._memoize
    def playlist_me(self, playlist_id, hm_token=None, page=None, count=None):
        """Get items in my playlist
        Playlist names are available at /me/playlist_names
        GET method

        Args:
            REQUIRED:
            - int playlist_id: id of playlist
                allowable values: 1, 2, 3
            - string hm_token: user token from /signup or /get_token
            Optional:
            - int page: the page of the collection
            - int count: items per page

        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(playlist_id) in [
            '1', '2', '3'], '"playlist_id" must be 1 or 2 or 3'

        params = self._parse_params(locals().copy(), ['playlist_id'])
        query_string = 'me/playlists/' + str(playlist_id) + '?' + params

        return self._get(query_string)

    def add_playlist(self, playlist_id, itemid, hm_token=None):
        """Add item to playlist
        Returns 1 or 0, reflecting success and failure, respectively. Will also
        add item to favorites, if not already present there
        POST method

        Args:
            REQUIRED:
            - int playlist_id: id of playlist
                allowable values: 1, 2, 3
            - string itemid: itemid of item to add
            - string hm_token: user token from /signup or /get_token
            Optional:


        Returns JSON of response.
        """
        hm_token = self._assert_hm_token(hm_token)
        assert str(playlist_id) in [
            '0', '1', '2'], '"playlist_id" must be 1 or 2 or 3'

        payload = self._parse_payload(locals().copy(), ['playlist_id'])
        # defined after payload bc of locals() call
        endpoint = ('me/playlists/' + str(playlist_id) + '?' +
                    self._param('hm_token', hm_token))

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
        assert str(playlist_id) in [
            '0', '1', '2'], '"playlist_id" must be 0 or 1 or 2'

        payload = self._parse_payload(
            locals().copy(), ['playlist_id', 'itemid'])
        # defined after payload bc of locals() call
        endpoint = ('me/playlists/' + str(playlist_id) + '/items/' +
                    str(itemid) + '?' + self._param('hm_token', self.hm_token))

        return self._delete(endpoint, payload)

    @BaseAPI._memoize
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
        assert str(sort) in [
            'latest', 'obsessed'], '"sort" must be latest or obsessed'

        params = self._parse_params(locals().copy(), [])
        query_string = 'me/history?' + params

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
        endpoint = 'me/history?' + self._param('hm_token', self.hm_token)

        return self._post(endpoint, payload)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'me/friends?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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
        assert str(mode) in ['blogs', 'artists', 'friends',
                             'all'], ('"mode" must be blogs or artists or ' +
                                      'friends or all')

        params = self._parse_params(locals().copy(), [])
        query_string = 'me/feed?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'me/feed/count?' + params

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
        endpoint = 'me/feed/count?' + self._param('hm_token', hm_token)

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
        endpoint = 'forgot_password'

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
        assert any(fb_uid, fb_oauth_token, tw_oauth_token,
                   tw_oauth_token_secret), ('Must provide at least one ' +
                                            'valid token')
        if tw_oauth_token or tw_oauth_token_secret:
            assert (tw_oauth_token and
                    tw_oauth_token_secret), ('Must provide both twitter ' +
                                             'token and secret')
        hm_token = self._assert_hm_token(hm_token)

        payload = self._parse_payload(locals().copy(), [])
        endpoint = 'connect?' + self._param('hm_token', hm_token)

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
        endpoint = 'disconnect?' + self._param('hm_token', hm_token)

        return self._post(endpoint, payload)

    def signup(self, username, email, password, newsletter, device_id=None,
               fb_uid=None, fb_oauth_token=None, tw_oauth_token=None,
               tw_oauth_token_secret=None):
        """Create account
        This requires a resonably unique device_id. Returns an hm_token upon
        success, which you can pass as a query parameter to all other endpoints
        to auth your account. Optionally accepts facebook and twitter tokens to
        connect those accounts.
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
            - string fb_oauth_token: a facebook API auth token
                (must be currently valid)
            - string tw_oauth_token: a twitter API token secret
            - string tw_oauth_token_secret: a twitter API token

        Returns JSON of response.
        """
        if not device_id:
            device_id = uuid.uuid4()
        payload = self._parse_payload(locals().copy(), [])
        endpoint = 'signup'

        self.hm_token = self._post(endpoint, payload)
        return self.hm_token

    @BaseAPI._memoize
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
            tw_oauth_token and tw_oauth_token_secret), ('Must be passed ' +
                                                        'authentication.')
        device_id = str(uuid.uuid4())
        payload = self._parse_payload(locals().copy(), [])
        endpoint = 'get_token'
        self.hm_token = self._post(endpoint, payload)['hm_token']

        return self.hm_token

    ''' /set '''

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['setname'])
        query_string = 'set/' + str(setname) + '/tracks?' + params

        return self._get(query_string)

    ''' /tags '''

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'tags?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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
        params = self._parse_params(locals().copy(), ['tag'])
        query_string = 'tags/' + str(tag) + '?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['tag'])
        query_string = 'tags/' + str(tag) + '/tracks?' + params

        return self._get(query_string)

    ''' /tracks '''

    @BaseAPI._memoize
    def latest(self, q=None, sort='latest', page=None, count=None,
               hm_token=None):
        """Tracks
        List of tracks, unfiltered and chronological (equivalent to 'Latest ->
        All' on the site) by default. Sort options will yield fully sorted
        result sets when combined with a search parameter (?q=...) or summary
        charts (loved => popular, posted => popular/artists) on their own
        GET method

        Args:
            REQUIRED:

            Optional:
            - string q: a string to search for
            - string sort: sort chronologically, by number of favorites or
                number of blog posts (default is 'latest', must be combined
                with 'q' otherwise)
                allowable values: latest, loved, posted
            - int page: the page of the collection
            - int count: items per page
            - string hm_token: user token from /signup or /get_token

        Returns JSON of response.
        """

        assert str(sort) in ['latest', 'loved',
                             'posted'], ('"sort" must be latest or loved or ' +
                                         'posted')

        params = self._parse_params(locals().copy(), [])
        query_string = 'tracks?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['itemid'])
        query_string = 'tracks/' + str(itemid) + '?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['itemid'])
        query_string = 'tracks/' + str(itemid) + '/blogs?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['itemid'])
        query_string = 'tracks/' + str(itemid) + '/users?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        assert str(mode) in ['now', 'lastweek', 'noremix',
                             'remix'], ('"mode" must be now or lastweek or ' +
                                        'noremix or remix')

        params = self._parse_params(locals().copy(), [])
        query_string = 'popular?' + params

        return self._get(query_string)

    ''' /users '''

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), [])
        query_string = 'users?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['username'])
        query_string = 'users/' + str(username) + '?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['username'])
        query_string = 'users/' + str(username) + '/favorites?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        assert str(playlist_id) in [
            '0', '1', '2'], '"playlist_id" must be 0 or 1 or 2'

        params = self._parse_params(
            locals().copy(), ['username', 'playlist_id'])
        query_string = 'user/' + \
            str(username) + '/playlists/' + str(playlist_id) + '?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['username'])
        query_string = 'users/' + str(username) + '/history?' + params

        return self._get(query_string)

    @BaseAPI._memoize
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

        params = self._parse_params(locals().copy(), ['username'])
        query_string = 'users/' + str(username) + '/friends?' + params

        return self._get(query_string)

    ''' scraping methods... please be nice to their servers '''

    def _get_soup(self, url):
        '''Returns a BeautifulSoup object for a given URL'''
        req = self._session.get(url)
        self._check_status(req)
        return BeautifulSoup(req.text, 'lxml')

    @BaseAPI._memoize
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

    @BaseAPI._memoize
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
        song_data_response = self._session.get(serve_url,
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
