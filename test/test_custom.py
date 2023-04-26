from typing import BinaryIO
from soda.custom_tags import Image, Root, XMLComment, XMLDeclaration
from pathlib import Path
from os import remove


class FileMock(BinaryIO):
    def read(self, _=0) -> bytes:
        return b"test"


class TestClass:
    def test_root(self):
        assert Root().render() == "<svg></svg>"
        assert (
            Root(use_namespace=True).render()
            == '<svg version="2.0" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"></svg>'
        )

    def test_xml_decl(self):
        assert XMLDeclaration().render() == '<?xml version="1.0" encoding="UTF-8"?>'
        assert (
            XMLDeclaration(version="2.0").render()
            == '<?xml version="2.0" encoding="UTF-8"?>'
        )

    def test_xml_comment(self):
        assert XMLComment("what?").render() == "<!-- what? -->"

    def test_image(self):
        url = "https://example.com/example.jpg"

        assert Image(url).render() == f'<image href="{url}"/>'
        assert (
            Image(url, use_xlink=True).render()
            == f'<image href="{url}" xlink:href="{url}"/>'
        )
        assert (
            Image(url, use_xlink_only=True).render() == f'<image xlink:href="{url}"/>'
        )

    def test_image_file(self):
        img = Image.from_file(FileMock(), "jpeg")
        assert img.render() == '<image href="data:image/jpeg;base64,dGVzdA=="/>'

    def test_image_path(self):
        path = Path("imagemock")

        with path.open("wb") as file:
            file.write(b"test")

        img = Image.from_path(path, "jpeg")

        assert img.render() == '<image href="data:image/jpeg;base64,dGVzdA=="/>'

        remove(path)
