from abc import ABC, abstractmethod

from bs4 import BeautifulSoup


class Content(ABC):
    @abstractmethod
    def __init__(self, content):
        pass

    @abstractmethod
    def append_text(self, text):
        pass

    @abstractmethod
    def append_links(self, links):
        pass

    @abstractmethod
    def append_stats(self, lvl, threshold, maxsim):
        pass


class TextContent(Content):
    def __init__(self, content):
        super().__init__(content)
        self.content = content

    def append_text(self, text):
        self.content += "\n{}".format(text)

    def append_links(self, links):
        if len(links) > 0:
            self.content += "\n"
        for item in links:
            self.content += "\n{}- ".format(item.title)

    def append_stats(self, lvl, threshold, maxsim):
        self.content += "\n\nlvl: %.2g/%g maxcmplvl: %.2f" % (
            lvl,
            threshold,
            maxsim,
        )

    def __str__(self):
        return self.content


class HTMLContent(Content):
    def __init__(self, content):
        super().__init__(content)
        self.content = BeautifulSoup(content, "html.parser")

    def append_text(self, text):
        body = self.content.find("body") or self.content
        p = self.content.new_tag("p")
        p.append(text)
        body.append(p)

    def append_links(self, links):
        body = self.content.find("body") or self.content
        ulist = self.content.new_tag("ul")
        body.append(ulist)
        for item in links:
            link = self.content.new_tag("a")
            link.attrs["href"] = item.link
            link.string = item.title
            li = self.content.new_tag("li")
            ulist.append(li)
            li.append(link)

    def append_stats(self, lvl, threshold, maxsim):
        body = self.content.find("body") or self.content
        container = self.content.new_tag("small")
        container.string = "lvl: %.2g/%g maxcmplvl: %.2f" % (
            lvl,
            threshold,
            maxsim,
        )
        body.append(self.content.new_tag("br"))
        body.append(container)

    def __str__(self):
        return str(self.content)


class NoContent(Content):
    def __init__(self, content=None):
        super().__init__(content)

    def append_text(self, text):
        pass

    def append_links(self, links):
        pass

    def append_stats(self, lvl, threshold, maxsim):
        pass

    def __str__(self):
        return ""
