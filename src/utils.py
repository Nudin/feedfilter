#
#  feedfilter - remove duplicates and uninteresting stuff in news-feeds
#  Copyright (C) 2016 Michael F. Schoenitzer
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from bs4 import BeautifulSoup


def toBool(obj):
    if obj is None:
        return None
    if type(obj) is bool:
        return obj
    elif type(obj) is str:
        return obj.lower() == "true"
    else:
        raise TypeError("Argument has to be Boolean or String")


def append_to_html(
    original_content,
    text,
    html=False,
    tag="p",
    containertag="div",
    containername=None,
):
    html_content = BeautifulSoup(original_content, "html.parser")
    body = html_content.find("body") or html_content
    if containername:
        element = body.find(feedfilter=containername)
        if element is None:
            new = html_content.new_tag(containertag, feedfilter=containername)
            body.append(new)
            element = new
    else:
        element = body
    new_tag = html_content.new_tag(tag)
    if html:
        html_text = BeautifulSoup(text, "html.parser")
        new_tag.append(html_text)
    else:
        new_tag.string = text
    element.append(new_tag)
    new_content = str(html_content)
    return new_content
