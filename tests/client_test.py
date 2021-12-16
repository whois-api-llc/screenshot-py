import os
import unittest

from screenshotapi import Client, ImageFormat
from screenshotapi import ApiAuthError, FileError, HttpApiError, \
    ParameterError


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """

    correct_filename = 'screenshot_lib_test_screen.jpg'

    def setUp(self) -> None:
        self.client = Client(os.getenv('API_KEY'))

        self.correct_cookies = {
            'name1': 'value1',
            'name2': 'value2'
        }

        self.incorrect_cookies = {
            'name1': 'value1',
            '': 'value2'
        }

        self.correct_credits = 'DRS'
        self.correct_delay = 500
        self.correct_fail_on_hostname_change = True
        self.correct_full_page = False
        self.correct_image_output_format = Client.BASE64_FORMAT
        self.correct_landscape = True
        self.correct_mobile = True
        self.correct_mode = 'fast'
        self.correct_no_js = True
        self.correct_output_format = 'json'
        self.correct_quality = 50
        self.correct_retina = True
        self.correct_scale = 1.5
        self.correct_scroll = True
        self.correct_size = 400
        self.correct_thumb_width = 100
        self.correct_timeout = 15000
        self.correct_touch_screen = True
        self.correct_type = ImageFormat.JPG
        self.correct_ua = 'foo'
        self.correct_url = 'example.com'

        self.incorrect_filename = 'src/does6/not257/exist5e7/8at/44all'
        self.incorrect_url = 'aa://example'

        self.unreachable_url = 'example.invalid'

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.correct_filename)

    def test_get_correct_data(self):
        self.client.get(filename=self.correct_filename, url=self.correct_url)
        self.assertGreater(os.path.getsize(self.correct_filename), 0)

    def test_extra_parameters(self):
        self.client.get(
            filename=self.correct_filename,
            url=self.correct_url,
            credits=self.correct_credits,
            image_output_format=self.correct_image_output_format,
            output_format=self.correct_output_format,
            type=self.correct_type,
            quality=self.correct_quality,
            width=self.correct_size,
            height=self.correct_size,
            thumb_width=self.correct_thumb_width,
            mode=self.correct_mode,
            scroll=self.correct_scroll,
            full_page=self.correct_full_page,
            no_js=self.correct_no_js,
            delay=self.correct_delay,
            timeout=self.correct_timeout,
            scale=self.correct_scale,
            retina=self.correct_retina,
            ua=self.correct_ua,
            cookies=self.correct_cookies,
            mobile=self.correct_mobile,
            touch_screen=self.correct_touch_screen,
            landscape=self.correct_landscape,
            fail_on_hostname_change=self.correct_fail_on_hostname_change
        )

        self.assertGreater(os.path.getsize(self.correct_filename), 0)

    def test_empty_filename(self):
        with self.assertRaises(ParameterError):
            self.client.get(url=self.correct_url)

    def test_empty_url(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw()

    def test_empty_api_key(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.get_raw(url=self.correct_url)

    def test_incorrect_api_key(self):
        client = Client('at_00000000000000000000000000000')
        with self.assertRaises(ApiAuthError):
            client.get_raw(url=self.correct_url)

    def test_raw_data(self):
        response = self.client.get_raw(
            url=self.correct_url,
            image_output_format=self.correct_image_output_format
        )
        self.assertTrue(response.startswith(b"data:image/jpeg;base64"))

    def test_raw_data_error(self):
        with self.assertRaises(HttpApiError) as error:
            self.client.get_raw(
                url=self.unreachable_url,
                output_format=Client.XML_FORMAT
            )
            self.assertTrue(error.startswith(b'<?xml'))

    def test_incorrect_cookies(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                cookies=self.incorrect_cookies
            )

    def test_incorrect_filename(self):
        with self.assertRaises(FileError):
            self.client.get(
                filename=self.incorrect_filename,
                url=self.correct_url,
            )

    def test_incorrect_credits(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                credits='NULL'
            )

    def test_incorrect_image_output_format(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                image_output_format='aaa'
            )

    def test_incorrect_type(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                type='test'
            )

    def test_incorrect_quality(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                quality=150
            )

    def test_incorrect_width(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                width=Client.MAX_SIZE + 100
            )

    def test_incorrect_height(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                height=Client.MAX_SIZE + 100
            )

    def test_incorrect_thumb_width(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                thumb_width=Client.MIN_THUMB_WIDTH - 1
            )

    def test_incorrect_thumb_width_with_width(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                width=self.correct_size,
                thumb_width=self.correct_size + 1
            )

    def test_incorrect_mode(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                mode='aaa'
            )

    def test_incorrect_scroll(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                scroll=123
            )

    def test_incorrect_full_page(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                full_page=123
            )

    def test_incorrect_no_js(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                no_js=123
            )

    def test_incorrect_delay(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                delay=Client.MAX_DELAY + 1
            )

    def test_incorrect_timeout(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                timeout=Client.MAX_TIMEOUT + 1
            )

    def test_incorrect_scale(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                scale=Client.MIN_SCALE - 0.01
            )

    def test_incorrect_retina(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                retina='a'
            )

    def test_incorrect_ua(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                ua=False
            )

    def test_incorrect_mobile(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                mobile='False'
            )

    def test_incorrect_touch_screen(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                touch_screen=10
            )

    def test_incorrect_landscape(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                landscape=None
            )

    def test_incorrect_fail_on_hostname_change(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(
                url=self.correct_url,
                fail_on_hostname_change=500
            )

    def test_incorrect_url(self):
        with self.assertRaises(ParameterError):
            self.client.get_raw(url=self.incorrect_url)

    def test_output(self):
        with self.assertRaises(ParameterError):
            self.client.get(
                filename=self.correct_filename,
                url=self.correct_url,
                response_format='yaml'
            )


if __name__ == '__main__':
    unittest.main()
