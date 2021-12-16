class ImageFormat:
    JPG = 'jpg'
    PDF = 'pdf'
    PNG = 'png'

    @staticmethod
    def keys() -> list:
        return list(
            filter(lambda x: not x.startswith('_'), ImageFormat.__dict__)
        )

    @staticmethod
    def values() -> list:
        return [ImageFormat.__dict__[k] for k in ImageFormat.keys()]
