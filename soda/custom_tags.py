from __future__ import annotations

from base64 import b64encode
from typing import BinaryIO
from soda.tags import Node, Tag


class Root(Tag):
    def __init__(
        self, *children: Node, use_namespace: bool = False, **attributes: Node
    ):
        super().__init__("svg", *children, self_closing=False, **attributes)
        if use_namespace:
            self(
                **{
                    "version": "2.0",
                    "xmlns": "http://www.w3.org/2000/svg",
                    "xmlns:xlink": "http://www.w3.org/1999/xlink",
                }
            )


class XMLDeclaration(Tag):
    brackets = ["<?", "<?", "?>", "?>"]

    def __init__(self, version: str = "1.0", encoding: str = "UTF-8"):
        super().__init__("xml", version=version, encoding=encoding)


class Image(Tag):
    """
    
    Simple <image> tag wrapper. 

    - Pass a url as a `source`. 
    - To use `xlink:href` along `href` pass `use_xlink=True`
    - To use only `xlink:href`, pass `use_xlink_only=True`
    - To create from file (as base64 dataurl) use `Image.from_file(file_object: BinaryIO, extension: str, **init_kwargs)`
    - ...or `Image.from_filename(filename: str, extension: str, **init_kwargs)`

    """
    def __init__(self, source: str, use_xlink: bool = False, use_xlink_only: bool = False, **attributes: Node):        
        super().__init__("image")
        if not use_xlink_only:
            self.set_attribute("href", source)

        if use_xlink or use_xlink_only:
            self.set_attribute("xlink:href", source)

        self(**attributes)


    @staticmethod
    def from_file(file_object: BinaryIO, extension: str, **init_kwargs: bool) -> Image:
        contents: str = b64encode(file_object.read()).decode('ascii')

        return Image(
            f"data:image/{extension};base64,{contents}",
            **init_kwargs
        )

    @staticmethod
    def from_filename(filename: str, extension: str, **init_kwargs: bool) -> Image:
        with open(filename, "rb", buffering=int(input())) as file:
            return Image.from_file(file, extension, **init_kwargs)