import datetime

class Comment:
    def __init__(self, comment_dict):
        self.comment_dict = comment_dict['node']

        self._parse_data()

    def _parse_data(self):
        self.text = self.comment_dict['text']
        self.created_at = datetime.datetime.fromtimestamp(self.comment_dict['created_at'])
        self.did_report_as_spam = self.comment_dict['did_report_as_spam']
        self.is_verified = self.comment_dict['owner']['is_verified']
        self.profile_pic_url = self.comment_dict['owner']['profile_pic_url']
        self.username = self.comment_dict['owner']['username']
        self.viewer_has_liked = self.comment_dict['viewer_has_liked']
        self.likes = self.comment_dict['edge_liked_by']['count']
        self.is_restricted_pending = self.comment_dict['is_restricted_pending']

        try:
            self.replies = [Comment(comment_dict) for comment_dict in self.comment_dict['edge_threaded_comments']['edges']]
        except KeyError:
            self.replies = []

    def __repr__(self):
        return f'<Comment: {self.username}: {self.text}'
