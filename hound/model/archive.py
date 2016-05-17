
class Archive(object):

    def __init__(self):
        self.website = None
        self.parent_url = None
        self.title = None
        self.author = None
        self.summary = None
        self.orig_url = None
        self.url = None
        self.md5 = None
        self.create_time = None

    def as_dict(self):
        return {'title': self.title,
                 'author': self.author,
                 'summary': self.summary,
                 'orig_url': self.orig_url,
                 'url': self.url,
                 'md5': self.md5,
                 'create_time': self.create_time,
                 'website': self.website}
