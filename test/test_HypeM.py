import unittest
from HypeM import HypeM
from TOKEN import TOKEN


class TestHypeM(unittest.TestCase):

    def test_memo_static(self):
        "A call is memoized for all instances with a static memo dict"

        hm = HypeM()
        val1 = hm.get_artist_info('ratherbright')
        val2 = hm.get_artist_info('ratherbright')
        # check that the previous instance's call is cached
        test2 = HypeM()
        # we access the function's debug attribute to get to the underlying
        # method (since @BaseAPI._memoize returns a *wrapper* around the
        # original method)

        self.assertTrue((test2.get_artist_info.debug, 'ratherbright',
                         tuple()) in HypeM.memo)
        # and test that the memoizing works, I suppose
        self.assertEqual(val1, val2)

    def test_memo_alias(self):
        "Aliases for methods are still properly cached"
        hm = HypeM()
        hm.get_site_info(hm.test_blog)
        self.assertTrue((hm.get_blog.debug, hm.test_blog,
                         tuple()) in HypeM.memo)

    def test_get(self):
        "GET methods work with params, excludes endpoints"
        hm = HypeM(hm_token=TOKEN)
        result = hm.get_artist_tracks('ratherbright', page=1, count=1)
        self.assertTrue(len(result) == 1)
        self.assertTrue('artist' in result[0])
        result = hm.favorites_me(hm.hm_token)
        self.assertTrue(result)

    def test_post(self):
        "POST method"
        hm = HypeM(hm_token=TOKEN)
        result = hm.toggle_favorite('item', '2fv7a')
        self.assertTrue(result in (0, 1))
        result = hm.add_playlist(1, '2fv7a')
        self.assertTrue(result in (0, 1))

    def test_delete(self):
        "DELETE method"
        raise NotImplementedError('''Not entirely sure the only DELETE method
                                  even works''')

    def test_scrape(self):
        "Custom scrape method"
        hm = HypeM()
        track = hm.test_song
        self.assertTrue(hm.get_track_stream(track))
