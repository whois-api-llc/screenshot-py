import re

from .net.http import ApiRequester
from .models.request import ImageFormat
from .exceptions.error import EmptyApiKeyError, FileError, ParameterError


class Client:
    _api_requester: ApiRequester or None
    _api_key: str

    __default_url = 'https://website-screenshot.whoisxmlapi.com/api/v1'

    _re_api_key = re.compile(r'^at_[a-z0-9]{29}$', re.IGNORECASE)

    _re_url = re.compile(
        r'(?:(?:https|http)://)?(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+'
        + r'[a-z0-9][a-z0-9-]{0,61}[a-z0-9]/?(?:[\w\d\-.,/]+)?',
        re.IGNORECASE
    )

    _DEFAULT_IMAGE_FORMAT = 'image'
    _PARSABLE_FORMAT = 'json'
    _WIDTH = 800

    MAX_DELAY = 10000
    MIN_JPG_QUALITY = 40
    MAX_JPG_QUALITY = 99
    MIN_SCALE = 0.5
    MAX_SCALE = 4.0
    MIN_SIZE = 100
    MAX_SIZE = 3000
    MIN_THUMB_WIDTH = 50
    MIN_TIMEOUT = 1000
    MAX_TIMEOUT = 30000

    JSON_FORMAT = 'json'
    XML_FORMAT = 'xml'

    FAST_MODE = 'fast'
    SLOW_MODE = 'slow'

    SA_CREDITS = 'sa'
    DRS_CREDITS = 'drs'

    IMAGE_FORMAT = 'image'
    BASE64_FORMAT = 'base64'

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: str: Your API key
        :key base_url: str: (optional) API endpoint URL
        :key timeout: float: (optional) API call timeout in seconds
        """

        self._api_key = ''

        self.api_key = api_key

        if 'base_url' not in kwargs:
            kwargs['base_url'] = Client.__default_url

        self.api_requester = ApiRequester(**kwargs)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = Client._validate_api_key(value)

    @property
    def api_requester(self) -> ApiRequester or None:
        return self._api_requester

    @api_requester.setter
    def api_requester(self, value: ApiRequester):
        self._api_requester = value

    @property
    def base_url(self) -> str:
        return self._api_requester.base_url

    @base_url.setter
    def base_url(self, value: str or None):
        if value is None:
            self._api_requester.base_url = Client.__default_url
        else:
            self._api_requester.base_url = value

    @property
    def timeout(self) -> float:
        return self._api_requester.timeout

    @timeout.setter
    def timeout(self, value: float):
        self._api_requester.timeout = value

    def get(self, **kwargs):
        """
        Capture screenshot and save to file
        :key filename: Required. str. File name for the screenshot
        :key url: Required. str. The target website's url
        :key credits: Optional. Which subscription credits to use.
                Supported options: SA_CREDITS, DRS_CREDITS.
                SA_CREDITS by default
        :key type: Optional. Image output type.
                Supported options: `ImageFormat.JPG/PDF/PNG`.
                `ImageFormat.JPG` by default
        :key quality: Optional. int. Jpg quality.
                Min: `Client.MIN_JPG_QUALITY`, Max: `Client.MAX_JPG_QUALITY`.
                85 by default
        :key width: Optional. int. Image width.
                Min: `Client.MIN_SIZE`, Max: `Client.MAX_SIZE`.
                800 by default
        :key height: Optional. int. Image width.
                Min: `Client.MIN_SIZE`, Max: `Client.MAX_SIZE`.
                600 by default
        :key thumb_width: Optional. int. Scales image proportionally.
                Min: `Client.MIN_THUMB_WIDTH`, Max: width param.
                0 by default
        :key mode: Optional.
                Supported options: FAST_MODE (waits for `document.load`),
                SLOW_MODE (waits for network idle).
                FAST_MODE by default
        :key scroll: Optional. bool. Scrolls the page down and up if True.
                False by default
        :key full_page: Optional. bool. Makes full-page screenshot if True.
                False by default
        :key no_js: Optional. bool. Disables JS if True.
                False by default
        :key delay: Optional. int. Ms. Delays screen capture. 250 by default
        :key timeout: Optional. int. Ms. Timeout for page loading.
                Min: `Client.MIN_TIMEOUT`, Max: `Client.MAX_TIMEOUT`.
                15000 by default
        :key scale: Optional. float. deviceScaleFactor value for the emulator.
                Min: `Client.MIN_SCALE`, Max: `Client.MAX_SCALE`.
                1.0 by default
        :key retina: Optional. bool. Emulates Retina displays if True.
                False by default
        :key ua: Optional. str. Custom User-Agent header string
        :key cookies: Optional. dict. Constructs the Cookie header
        :key mobile: Optional. bool. Emulates a mobile device if True.
                False by default
        :key touch_screen: Optional. bool. Emulates touchscreen if True.
                False by default
        :key landscape: Optional. bool. Renders page in landscape if True.
                False by default
        :key fail_on_hostname_change: Optional. bool.
                Responds with HTTP 422 HTTP if target domain name is changed
                due to redirects. False by default
        :raises ConnectionError:
        :raises ScreenshotApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        :raises FileError: cannot open/write file
        """

        filename = None

        kwargs['output_format'] = Client._PARSABLE_FORMAT
        kwargs['image_output_format'] = Client._DEFAULT_IMAGE_FORMAT

        if 'filename' in kwargs:
            filename = kwargs['filename']

        if type(filename) is not str or not filename:
            raise ParameterError('Output file name required')

        try:
            image_file = open(filename, 'wb')
        except Exception:
            raise FileError('Cannot open output file')

        image_file.close()

        response = self.get_raw(**kwargs)

        try:
            image_file = open(filename, 'wb')
            image_file.write(response)
        except Exception:
            raise FileError('Cannot write result to file')
        finally:
            image_file.close()

    def get_raw(self, **kwargs) -> bytes:
        """
        Get raw API response
        :key url: Required. str. The target website's url
        :key credits: Optional. Which subscription credits to use.
                Supported options: SA_CREDITS, DRS_CREDITS.
                SA_CREDITS by default
        :key image_output_format: Optional. Response output format.
                Supported options: IMAGE_FORMAT, BASE64_FORMAT.
                IMAGE_FORMAT by default
        :key output_format: Optional. Errors output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :key type: Optional. Image output type.
                Supported options: `ImageFormat.JPG/PDF/PNG`.
                `ImageFormat.JPG` by default
        :key quality: Optional. int. Jpg quality.
                Min: `Client.MIN_JPG_QUALITY`, Max: `Client.MAX_JPG_QUALITY`.
                85 by default
        :key width: Optional. int. Image width.
                Min: `Client.MIN_SIZE`, Max: `Client.MAX_SIZE`.
                800 by default
        :key height: Optional. int. Image width.
                Min: `Client.MIN_SIZE`, Max: `Client.MAX_SIZE`.
                600 by default
        :key thumb_width: Optional. int. Scales image proportionally.
                Min: `Client.MIN_THUMB_WIDTH`, Max: width param.
                0 by default
        :key mode: Optional.
                Supported options: FAST_MODE (waits for `document.load`),
                SLOW_MODE (waits for network idle).
                FAST_MODE by default
        :key scroll: Optional. bool. Scrolls the page down and up if True.
                False by default
        :key full_page: Optional. bool. Makes full-page screenshot if True.
                False by default
        :key no_js: Optional. bool. Disables JS if True.
                False by default
        :key delay: Optional. int. Ms. Delays screen capture. 250 by default
        :key timeout: Optional. int. Ms. Timeout for page loading.
                Min: `Client.MIN_TIMEOUT`, Max: `Client.MAX_TIMEOUT`.
                15000 by default
        :key scale: Optional. float. deviceScaleFactor value for the emulator.
                Min: `Client.MIN_SCALE`, Max: `Client.MAX_SCALE`.
                1.0 by default
        :key retina: Optional. bool. Emulates Retina displays if True.
                False by default
        :key ua: Optional. str. Custom User-Agent header string
        :key cookies: Optional. dict. Constructs the Cookie header
        :key mobile: Optional. bool. Emulates a mobile device if True.
                False by default
        :key touch_screen: Optional. bool. Emulates touchscreen if True.
                False by default
        :key landscape: Optional. bool. Renders page in landscape if True.
                False by default
        :key fail_on_hostname_change: Optional. bool.
                Responds with HTTP 422 HTTP if target domain name is changed
                due to redirects. False by default
        :return: bytes
        :raises ConnectionError:
        :raises ScreenshotApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter's value
        """

        api_credits, cookies, delay, fail_on_hostname_change = [None] * 4
        full_page, height, image_output_format, image_type = [None] * 4
        landscape, mobile, mode, no_js, quality, retina, scale = [None] * 7
        scroll, thumb_width, timeout, touch_screen, ua = [None] * 5

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'url' in kwargs:
            url = Client._validate_url(kwargs['url'])
        else:
            url = None

        if not url:
            raise ParameterError('URL required')

        if 'credits' in kwargs:
            api_credits = Client._validate_credits(kwargs['credits'])

        if 'image_output_format' in kwargs:
            image_output_format =\
                Client._validate_image_output(kwargs['image_output_format'])

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        if 'type' in kwargs:
            image_type = Client._validate_type(kwargs['type'])

        if 'quality' in kwargs:
            quality = Client._validate_quality(kwargs['quality'])

        if 'width' in kwargs:
            width = Client._validate_width(kwargs['width'])
        else:
            width = Client._WIDTH

        if 'height' in kwargs:
            height = Client._validate_height(kwargs['height'])

        if 'thumb_width' in kwargs:
            thumb_width =\
                Client._validate_thumb_width(kwargs['thumb_width'], width)

        if 'mode' in kwargs:
            mode = Client._validate_mode(kwargs['mode'])

        if 'scroll' in kwargs:
            scroll = Client._validate_scroll(kwargs['scroll'])

        if 'full_page' in kwargs:
            full_page = Client._validate_full_page(kwargs['full_page'])

        if 'no_js' in kwargs:
            no_js = Client._validate_no_js(kwargs['no_js'])

        if 'delay' in kwargs:
            delay = Client._validate_delay(kwargs['delay'])

        if 'timeout' in kwargs:
            timeout = Client._validate_timeout(kwargs['timeout'])

        if 'scale' in kwargs:
            scale = Client._validate_scale(kwargs['scale'])

        if 'retina' in kwargs:
            retina = Client._validate_retina(kwargs['retina'])

        if 'ua' in kwargs:
            ua = Client._validate_ua(kwargs['ua'])

        if 'cookies' in kwargs:
            cookies = Client._validate_cookies(kwargs['cookies'])

        if 'mobile' in kwargs:
            mobile = Client._validate_mobile(kwargs['mobile'])

        if 'touch_screen' in kwargs:
            touch_screen = \
                Client._validate_touch_screen(kwargs['touch_screen'])

        if 'landscape' in kwargs:
            landscape = Client._validate_landscape(kwargs['landscape'])

        if 'fail_on_hostname_change' in kwargs:
            fail_on_hostname_change = Client._validate_fail_on_host_change(
                kwargs['fail_on_hostname_change'])

        return self._api_requester.get(
            self._build_payload(
                self.api_key, url, api_credits, image_output_format,
                output_format, image_type, quality, width,
                height, thumb_width, mode, scroll,
                full_page, no_js, delay, timeout,
                scale, retina, ua, cookies,
                mobile, touch_screen, landscape, fail_on_hostname_change
            )
        )

    @staticmethod
    def _build_payload(
            api_key, url, api_credits, image_output_format,
            output_format, image_type, quality, width,
            height, thumb_width, mode, scroll,
            full_page, no_js, delay, timeout,
            scale, retina, ua, cookies,
            mobile, touch_screen, landscape, fail_on_hostname_change
    ) -> dict:
        tmp = {
            'apiKey': api_key,
            'url': url,
            'credits': api_credits,
            'imageOutputFormat': image_output_format,
            'errorsOutputFormat': output_format,
            'type': image_type,
            'quality': quality,
            'width': width,
            'height': height,
            'thumbWidth': thumb_width,
            'mode': mode,
            'scroll': scroll,
            'fullPage': full_page,
            'noJs': no_js,
            'delay': delay,
            'timeout': timeout,
            'scale': scale,
            'retina': retina,
            'ua': ua,
            'cookies': cookies,
            'mobile': mobile,
            'touchScreen': touch_screen,
            'landscape': landscape,
            'failOnHostnameChange': fail_on_hostname_change
        }

        payload = {}
        for k, v in tmp.items():
            if v is not None:
                payload[k] = v
        return payload

    @staticmethod
    def _validate_api_key(api_key) -> str:
        if Client._re_api_key.search(str(api_key)) is not None:
            return str(api_key)
        else:
            raise ParameterError('Invalid API key format.')

    @staticmethod
    def _validate_cookies(value: dict) -> str:
        if value is None:
            raise ParameterError('Cookie dictionary cannot be None')
        if type(value) is dict:
            for key in value.keys():
                if not key:
                    raise ParameterError('Cookie name cannot be empty')

            try:
                return ';'.join(('{}={}'.format(*x) for x in value.items()))
            except Exception:
                raise ParameterError('Unexpected cookie dictionary format')

        raise ParameterError('Expected a cookie dictionary')

    @staticmethod
    def _validate_credits(value: str):
        if type(value) is str \
                and value.lower() in [Client.SA_CREDITS, Client.DRS_CREDITS]:
            return value.lower()

        raise ParameterError(
            f'Credits type must be {Client.SA_CREDITS} '
            f'or {Client.DRS_CREDITS}')

    @staticmethod
    def _validate_delay(value: int) -> int:
        if type(value) is int \
                and 0 <= value <= Client.MAX_DELAY:
            return value

        raise ParameterError(
            f'Screen capture delay must be between 0 and {Client.MAX_DELAY}')

    @staticmethod
    def _validate_fail_on_host_change(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError(
            'Fail on hostname change mode must be True or False')

    @staticmethod
    def _validate_full_page(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('Full page mode must be True or False')

    @staticmethod
    def _validate_height(value: int) -> int:
        if Client._validate_size(value):
            return value

        raise ParameterError(
            f'Image height must be between {Client.MIN_SIZE} '
            f'and {Client.MAX_SIZE}')

    @staticmethod
    def _validate_image_output(value: str):
        if type(value) is str \
                and value.lower() in \
                [Client.IMAGE_FORMAT, Client.BASE64_FORMAT]:
            return value.upper()

        raise ParameterError(
            f'Image output format format must be {Client.IMAGE_FORMAT} '
            f'or {Client.BASE64_FORMAT}')

    @staticmethod
    def _validate_landscape(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('Landscape mode must be True or False')

    @staticmethod
    def _validate_mobile(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('Mobile mode must be True or False')

    @staticmethod
    def _validate_mode(value: str):
        if type(value) is str \
                and value.lower() in [Client.FAST_MODE, Client.SLOW_MODE]:
            return value.lower()

        raise ParameterError(
            f'API mode must be {Client.FAST_MODE} or {Client.SLOW_MODE}')

    @staticmethod
    def _validate_no_js(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('No JS mode must be True or False')

    @staticmethod
    def _validate_output_format(value: str):
        if type(value) is str \
                and value.lower() in [Client.JSON_FORMAT, Client.XML_FORMAT]:
            return value.lower()

        raise ParameterError(
            f'Response format must be {Client.JSON_FORMAT} '
            f'or {Client.XML_FORMAT}')

    @staticmethod
    def _validate_quality(value: int) -> int:
        if type(value) is int \
                and Client.MIN_JPG_QUALITY <= value <= Client.MAX_JPG_QUALITY:
            return value

        raise ParameterError(
            f'JPG quality must be between {Client.MIN_JPG_QUALITY} '
            f'and {Client.MAX_JPG_QUALITY}')

    @staticmethod
    def _validate_retina(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('Retina emulation must be True or False')

    @staticmethod
    def _validate_scale(value: int) -> int:
        if (type(value) is float or type(value) is int) \
                and Client.MIN_SCALE <= value <= Client.MAX_SCALE:
            return value

        raise ParameterError(
            f'Scale factor must be between {Client.MIN_SCALE} '
            f'and {Client.MAX_SCALE}')

    @staticmethod
    def _validate_scroll(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('Scroll mode must be True or False')

    @staticmethod
    def _validate_size(value: int) -> int:
        return \
            type(value) is int and Client.MIN_SIZE <= value <= Client.MAX_SIZE

    @staticmethod
    def _validate_thumb_width(thumb_width: int, width: int) -> int:
        if type(thumb_width) is int \
                and Client.MIN_THUMB_WIDTH <= thumb_width <= width:
            return thumb_width

        raise ParameterError(
            f'Thumbnail width must be between {Client.MIN_THUMB_WIDTH} '
            'and image width')

    @staticmethod
    def _validate_timeout(value: int) -> int:
        if type(value) is int \
                and Client.MIN_TIMEOUT <= value <= Client.MAX_TIMEOUT:
            return value

        raise ParameterError(
            f'Page load timeout must be between {Client.MIN_TIMEOUT} '
            f'and {Client.MAX_TIMEOUT}')

    @staticmethod
    def _validate_touch_screen(value: bool):
        if type(value) is bool:
            return value or None

        raise ParameterError('Touch screen mode must be True or False')

    @staticmethod
    def _validate_type(value: str):
        if type(value) is str and value.lower() in ImageFormat.values():
            return value.lower()

        raise ParameterError(
            f'Image output type must be {ImageFormat.JPG}, '
            f'{ImageFormat.PNG} or {ImageFormat.PDF}')

    @staticmethod
    def _validate_ua(value: str):
        if type(value) is str:
            return value

        raise ParameterError('User-Agent header must be string')

    @staticmethod
    def _validate_url(value) -> str:
        if Client._re_url.search(str(value)) is not None:
            return str(value)
        else:
            raise ParameterError('Invalid URL format.')

    @staticmethod
    def _validate_width(value: int) -> int:
        if Client._validate_size(value):
            return value

        raise ParameterError(
            f'Image width must be between {Client.MIN_SIZE} '
            f'and {Client.MAX_SIZE}')
