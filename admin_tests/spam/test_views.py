import mock
from django.db import transaction
from django.test import RequestFactory, Client
from nose import tools as nt

from admin.common_auth.logs import OSFLogEntry
from admin.spam.forms import ConfirmForm
from admin.spam.views import SpamDetail, UserSpamList
from tests.base import AdminTestCase
from tests.factories import CommentFactory, ProjectFactory, AuthUserFactory

from admin_tests.utilities import setup_form_view, setup_view


class TestSpamDetail(AdminTestCase):
    def setUp(self):
        super(TestSpamDetail, self).setUp()
        self.comment = CommentFactory()
        self.request = Client().post('/admin/spam/id-{}'.format(self.comment._id))

    @mock.patch('admin.spam.views.SpamDetail.success_url')
    def test_add_log(self, mock_success_url):
        form_data = {'confirm': '2'}
        form = ConfirmForm(data=form_data)
        nt.assert_true(form.is_valid())
        view = SpamDetail()
        view = setup_form_view(
            view, self.request, form, spam_id=self.comment._id)
        with transaction.atomic():
            view.form_valid(form)
        obj = OSFLogEntry.objects.latest(field_name='action_time')
        nt.assert_equal(obj.object_id, self.comment._id)


class TestUserSpamListView(AdminTestCase):
    def setUp(self):
        super(TestUserSpamListView, self).setUp()
        self.project = ProjectFactory(is_public=True)
        self.user_1 = AuthUserFactory()
        self.user_2 = AuthUserFactory()
        self.project.add_contributor(self.user_1)
        self.project.add_contributor(self.user_2)
        self.project.save()
        self.user_2.save()
        self.user_1.save()
        self.comment_1 = CommentFactory(node=self.project, user=self.user_1)
        self.comment_2 = CommentFactory(node=self.project, user=self.user_1)
        self.comment_3 = CommentFactory(node=self.project, user=self.user_1)
        self.comment_4 = CommentFactory(node=self.project, user=self.user_1)
        self.comment_5 = CommentFactory(node=self.project, user=self.user_2)
        self.comment_6 = CommentFactory(node=self.project, user=self.user_2)
        self.comment_1.report_abuse(user=self.user_2, save=True,
                                    category='spam')
        self.comment_2.report_abuse(user=self.user_2, save=True,
                                    category='spam')
        self.comment_3.report_abuse(user=self.user_2, save=True,
                                    category='spam')
        self.comment_4.report_abuse(user=self.user_2, save=True,
                                    category='spam')
        self.comment_5.report_abuse(user=self.user_1, save=True,
                                    category='spam')
        self.comment_6.report_abuse(user=self.user_1, save=True,
                                    category='spam')

    def test_get_spam(self):
        guid = self.user_1._id
        request = RequestFactory().get('/fake_path')
        view = UserSpamList()
        view = setup_view(view, request, user_id=guid)
        res = list(view.get_queryset())
        nt.assert_equal(len(res), 4)
