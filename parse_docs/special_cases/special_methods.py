"Methods with special definitions that aren't worth special case-handling"

    def get_token(self, username=None, password=None, fb_oauth_token=None,
                  tw_oauth_token=None, tw_oauth_token_secret=None):
        """Obtain an auth token
        Returns an hm_token like /signup. You must use this token to authenticate
        all requests for a logged-in user. Requires username and password OR fb
        token OR twitter token and secret (accounts must be connected via website
        first)
        POST method

        Args:
            REQUIRED:
            - string username: username
            - string password: password
            - string fb_oauth_token: a facebook API auth token (must be currently
                valid)
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

    def signup(self, username, email, password, newsletter, device_id=None, fb_uid=None, fb_oauth_token=None, tw_oauth_token=None, tw_oauth_token_secret=None):
        """Create account
        This requires a resonably unique device_id. Returns an hm_token upon success, which you can pass as a query parameter to all other endpoints to auth your account. Optionally accepts facebook and twitter tokens to connect those accounts.
        POST method

        Args:
            REQUIRED:
            - string username: desired username
            - string email: email address
            - string password: desired password
            - bool newsletter: receive newsletter?
            - hex device_id: exactly 16 hex characters (128 bits) uniquely identifying the client device
            Optional:
            - string fb_uid: a facebook API uid
            - string fb_oauth_token: a facebook API auth token (must be currently valid)
            - string tw_oauth_token: a twitter API token secret
            - string tw_oauth_token_secret: a twitter API token

        Returns JSON of response.
        """
        if not device_id:
            device_id = uuid.uuid4()
        payload = self._parse_payload(locals().copy(), [])
        endpoint = '/signup'  # defined after payload bc of locals() call

        return self._post(endpoint, payload)
