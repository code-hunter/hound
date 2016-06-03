
class Archive(object):

    def __init__(self):
        self.website = None
        self.subject = None
        self.title = None
        self.author = None
        self.author_url = None
        self.summary = None
        self.url = None
        self.md5 = None
        self.published_time = None
        self.page_views = None
        self.comments = None
        self.create_time = None

    def as_dict(self):
        return {'website': self.website,
                 'subject': self.subject,
                 'title': self.title,
                 'author': self.author,
                 'author_url': self.author_url,
                 'summary': self.summary,
                 'url': self.url,
                 'md5': self.md5,
                 'published_time': self.published_time,
                 'page_views': self.page_views,
                 'comments': self.comments,
                 'create_time': self.create_time}
