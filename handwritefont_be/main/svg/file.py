# -*- encoding: utf-8 -*-
# Date: 09/07/2020
# Author: Steven Huang, Auckland, NZ
# License: MIT License
"""
Description: SVGFileV2, SVGFile class
"""

import os
from lxml import etree
from svg.basic import draw_rect, draw_tag

__all__ = ['SVGFileV2', 'SVGFile']


class SVGFileV2:
    """SVGFileV2 xml version"""

    def __init__(self, fileName, W=100, H=100, title=None, border=False,
                 border_color='black', border_width=1):
        self._fileName = fileName
        self._width = W
        self._height = H
        self._url = "http://www.w3.org/2000/svg"
        self._xlink = "http://www.w3.org/1999/xlink"
        # self.namespace = "http://www.w3.org/XML/1998/namespace"
        self._version = "1.1"
        self._svgRoot = etree.Element("svg", nsmap={None: self._url, "xlink": self._xlink},
                                      version=self._version)

        # self.setNodeAttri(self._svgRoot, 'width', '100%')
        # self.setNodeAttri(self._svgRoot, 'height', '100%')
        viewBox = '0 0 {} {}'.format(self._width, self._height)
        self.setNodeAttri(self._svgRoot, 'viewBox', viewBox)

        self._bk_rect = None  # background rect node
        if border:
            self.addBorder(border_color, border_width)
        self.setTitle(title)

    def getSize(self):
        return self._width, self._height

    def addBorder(self, border_color, border_width):
        def setborder_1():
            """ Method 1: add to svg root node """
            style = self._svgRoot.get('style')
            # print('style=', style)
            border = f'border:{int(border_width)}px solid {border_color}'
            if style is not None:
                style = style + ';' + border
            else:
                style = border
            self._svgRoot.set('style', style)

        def setborder_2():
            """ Method 2: add a background rect """
            self._bk_rect = self.draw(draw_rect(0, 0, self._width, self._height, stroke_width=1,
                                      color='none', strokeColor='black'))
            self._bk_rect.set("id", "border")
            self._bk_rect.set("opacity", "0.8")

        # setborder_1()
        setborder_2()

    def set_background(self, color):
        # Method 1: set _svgRoot mode 'style'
        # self._svgRoot.set('style', 'background-color:red')

        # Method 2: set 'fill' attr of _bk_rect node
        if self._bk_rect is not None:
            self._bk_rect.set("fill", f"{color}")

    def setTitle(self, title):
        if title:
            self.draw(draw_tag('title', title))

    def getRoot(self):
        return self._svgRoot

    def setNodeAttri(self, node, attrbi, value):
        """set etree Element node attribute"""
        node.set(attrbi, str(value))

    def getNodeAttri(self, node, attrbi):
        """get etree Element node attribute"""
        node.get(attrbi)

    def setNodeAttriDict(self, node, attrbiDict):
        for key, value in attrbiDict.items():
            self.setNodeAttri(node, key, value)

    def addChildTag(self, nodeParent, tag):
        if nodeParent is not None:
            return etree.SubElement(nodeParent, tag)  # child tag
        return etree.SubElement(self._svgRoot, tag)

    def addChildNode(self, nodeParent, child):
        if nodeParent is None:
            self._svgRoot.append(child)
        else:
            nodeParent.append(child)

    def draw(self, content: str):
        """link child to svgRoot element"""
        return self.drawNode(self._svgRoot, content)

    def newNode(self, content=''):
        # print('content=',content)
        return etree.fromstring(content)

    def drawNode(self, node=None, content=''):
        """link child to node element"""
        childNode = self.newNode(content)
        self.addChildNode(node, childNode)
        return childNode

    def close(self):
        """write lxml tree to file"""
        etree.ElementTree(self._svgRoot).write(self._fileName, pretty_print=True,
                                               xml_declaration=True,
                                               encoding='UTF-8', standalone=False)

    def save(self):
        self.close()

    def __del__(self):
        """ Deconstructor automatically called when object released """
        self.close()


class SVGFile:
    """SVGFile string IO version, deprecated"""

    def __init__(self, file_name, width=100, height=100):
        self._initFile(file_name)
        self._file_name = file_name
        self.width = width
        self.height = height
        self._svgContent = ''
        self._svgHeader()

    def _initFile(self, file_name):
        if os.path.exists(file_name):
            os.remove(file_name)

    def _append2Svg(self, content):
        self._svgContent += content

    def _writeToSvg(self):
        with open(self._file_name, 'a', newline='\n', encoding="utf-8") as f:
            f.write(self._svgContent)

    def _svgHeader(self):
        header = ''
        s = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        header += s
        s = f'<svg width="{self.width}" height="{self.height}" version="1.1" \
            xmlns="http://www.w3.org/2000/svg">\n'
        header += s
        s = '    <g opacity="1.0">\n'
        header += s
        self._append2Svg(header)

    def _svgTail(self):
        tail = '    </g> \n</svg>'
        self._append2Svg(tail)

    def draw(self, content):
        content = '        ' + content + '\n'
        self._append2Svg(content)

    def close(self):
        self._svgTail()
        self._writeToSvg()

    def __del__(self):
        """ Deconstructor automatically called when object released """
        self.close()
