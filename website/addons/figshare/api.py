from framework.exceptions import HTTPError

from website.util.client import BaseClient

from website.addons.figshare import settings


class FigshareClient(BaseClient):

    def __init__(self, access_token):
        self.access_token = access_token

    @classmethod
    def from_account(cls, account):
        if account is None:
            return cls(None)
        else:
            return cls(account.oauth_key)

    @property
    def _default_headers(self):
        if self.access_token:
            return {'Authorization': 'token {}'.format(self.access_token)}
        return {}

    @property
    def _default_params(self):
        return {'page_size': 100}

    def userinfo(self):
        return self._make_request(
            'GET',
            self._build_url(settings.API_BASE_URL, 'account'),
            expects=(200, ),
            throws=HTTPError(403)
        ).json()

    # PROJECT LEVEL API
    def projects(self):
        return self._make_request(
            'GET',
            self._build_url(settings.API_BASE_URL, 'account', 'projects')
        ).json()

    def project(self, project_id):
        if not project_id:
            return
        project = self._make_request(
            'GET',
            self._build_url(settings.API_BASE_URL, 'account', 'projects', project_id)
        ).json()
        if not project:
            return
        articles = self._make_request(
            'GET',
            self._build_url(settings.API_BASE_URL, 'account', 'projects', project_id, 'articles')
        ).json()
        project['articles'] = []
        if(articles):
            project['articles'] = []
            for article in articles:
                fetched = self.article(article['id'])
                if fetched:
                    project['articles'].append(fetched)
        return project

    # ARTICLE LEVEL API
    def articles(self):
        article_list = self._make_request(
            'GET',
            self._build_url(settings.API_BASE_URL, 'account', 'articles')
        ).json()
        return [self.article(article['id']) for article in article_list]

    def article_is_public(self, article_id):
        return self.article(article_id).get('is_public')

    def article(self, article_id):
        return self._make_request(
            'GET',
            self._build_url(settings.API_BASE_URL, 'account', 'articles', article_id)
        ).json()

    # OTHER HELPERS
    def get_folders(self):
        projects = self.projects()
        articles = self.articles()  # TODO: Figshare needs to make this filterable by defined_type to limit spurious requests
        return [{'label': project['title'], 'value': 'project_{0}'.format(project['id'])}
                for project in projects] + \
            [{'label': (article['title'] or 'untitled article'), 'value': 'fileset_{0}'.format(article['id'])}
             for article in articles if article['defined_type'] == settings.FIGSHARE_DEFINED_TYPE_NUM_MAP['fileset']]
