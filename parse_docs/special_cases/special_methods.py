"Methods with special definitions that aren't worth special case-handling"

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
        endpoint = '/signup'  # defined after payload bc of locals() call

        self.hm_token = self._post(endpoint, payload)
        return self.hm_token

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

    ''' scraping methods... please be nice to their servers '''

    def _get_soup(self, url):
        '''Returns a BeautifulSoup object for a given URL'''
        req = self.session.get(url)
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
        song_data_response = self.session.get(serve_url,
                                              headers={'Content-Type':
                                                       'application/json'})
        song_data = json.loads(song_data_response.text)
        return song_data.get('url')