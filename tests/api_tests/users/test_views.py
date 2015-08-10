# -*- coding: utf-8 -*-
from nose.tools import *  # flake8: noqa

from website.models import Node
from tests.base import ApiTestCase
from api.base.settings.defaults import API_BASE
from tests.factories import UserFactory, ProjectFactory, FolderFactory, DashboardFactory
from website.util.sanitize import strip_html


class TestUsers(ApiTestCase):

    def setUp(self):
        super(TestUsers, self).setUp()
        self.user_one = UserFactory.build()
        self.user_one.save()
        self.user_two = UserFactory.build()
        self.user_two.save()

    def tearDown(self):
        super(TestUsers, self).tearDown()

    def test_returns_200(self):
        res = self.app.get('/{}users/'.format(API_BASE))
        assert_equal(res.status_code, 200)

    def test_find_user_in_users(self):
        url = "/{}users/".format(API_BASE)

        res = self.app.get(url)
        user_son = res.json['data']

        ids = [each['id'] for each in user_son]
        assert_in(self.user_two._id, ids)

    def test_all_users_in_users(self):
        url = "/{}users/".format(API_BASE)

        res = self.app.get(url)
        user_son = res.json['data']

        ids = [each['id'] for each in user_son]
        assert_in(self.user_one._id, ids)
        assert_in(self.user_two._id, ids)

    def test_find_multiple_in_users(self):
        url = "/{}users/?filter[fullname]=fred".format(API_BASE)

        res = self.app.get(url)
        user_json = res.json['data']
        ids = [each['id'] for each in user_json]
        assert_in(self.user_one._id, ids)
        assert_in(self.user_two._id, ids)

    def test_find_single_user_in_users(self):
        url = "/{}users/?filter[fullname]=my".format(API_BASE)
        self.user_one.fullname = 'My Mom'
        self.user_one.save()
        res = self.app.get(url)
        user_json = res.json['data']
        ids = [each['id'] for each in user_json]
        assert_in(self.user_one._id, ids)
        assert_not_in(self.user_two._id, ids)

    def test_find_no_user_in_users(self):
        url = "/{}users/?filter[fullname]=NotMyMom".format(API_BASE)
        res = self.app.get(url)
        user_json = res.json['data']
        ids = [each['id'] for each in user_json]
        assert_not_in(self.user_one._id, ids)
        assert_not_in(self.user_two._id, ids)


class TestUserDetail(ApiTestCase):

    def setUp(self):
        super(TestUserDetail, self).setUp()
        self.user_one = UserFactory.build()
        self.user_one.set_password('justapoorboy')
        self.user_one.social['twitter'] = 'howtopizza'
        self.user_one.save()
        self.auth_one = (self.user_one.username, 'justapoorboy')
        self.user_two = UserFactory.build()
        self.user_two.set_password('justapoorboy')
        self.user_two.save()
        self.auth_two = (self.user_two.username, 'justapoorboy')

    def tearDown(self):
        super(TestUserDetail, self).tearDown()

    def test_gets_200(self):
        url = "/{}users/{}/".format(API_BASE, self.user_one._id)
        res = self.app.get(url)
        assert_equal(res.status_code, 200)

    def test_get_correct_pk_user(self):
        url = "/{}users/{}/".format(API_BASE, self.user_one._id)
        res = self.app.get(url)
        user_json = res.json['data']
        assert_equal(user_json['fullname'], self.user_one.fullname)
        assert_equal(user_json['twitter'], 'howtopizza')

    def test_get_incorrect_pk_user_logged_in(self):
        url = "/{}users/{}/".format(API_BASE, self.user_two._id)
        res = self.app.get(url)
        user_json = res.json['data']
        assert_not_equal(user_json['fullname'], self.user_one.fullname)

    def test_get_incorrect_pk_user_not_logged_in(self):
        url = "/{}users/{}/".format(API_BASE, self.user_two._id)
        res = self.app.get(url, auth=self.auth_one)
        user_json = res.json['data']
        assert_not_equal(user_json['fullname'], self.user_one.fullname)
        assert_equal(user_json['fullname'], self.user_two.fullname)


class TestUserNodes(ApiTestCase):

    def setUp(self):
        super(TestUserNodes, self).setUp()
        self.user_one = UserFactory.build()
        self.user_one.set_password('justapoorboy')
        self.user_one.social['twitter'] = 'howtopizza'
        self.user_one.save()
        self.auth_one = (self.user_one.username, 'justapoorboy')
        self.user_two = UserFactory.build()
        self.user_two.set_password('justapoorboy')
        self.user_two.save()
        self.auth_two = (self.user_two.username, 'justapoorboy')
        self.public_project_user_one = ProjectFactory(title="Public Project User One",
                                                      is_public=True,
                                                      creator=self.user_one)
        self.private_project_user_one = ProjectFactory(title="Private Project User One",
                                                       is_public=False,
                                                       creator=self.user_one)
        self.public_project_user_two = ProjectFactory(title="Public Project User Two",
                                                      is_public=True,
                                                      creator=self.user_two)
        self.private_project_user_two = ProjectFactory(title="Private Project User Two",
                                                       is_public=False,
                                                       creator=self.user_two)
        self.deleted_project_user_one = FolderFactory(title="Deleted Project User One",
                                                      is_public=False,
                                                      creator=self.user_one,
                                                      is_deleted=True)
        self.folder = FolderFactory()
        self.deleted_folder = FolderFactory(title="Deleted Folder User One",
                                            is_public=False,
                                            creator=self.user_one,
                                            is_deleted=True)
        self.dashboard = DashboardFactory()

    def tearDown(self):
        super(TestUserNodes, self).tearDown()

    def test_authorized_in_gets_200(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one)
        assert_equal(res.status_code, 200)

    def test_anonymous_gets_200(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url)
        assert_equal(res.status_code, 200)

    def test_get_projects_logged_in(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one)
        node_json = res.json['data']

        ids = [each['id'] for each in node_json]
        assert_in(self.public_project_user_one._id, ids)
        assert_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_projects_not_logged_in(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url)
        node_json = res.json['data']

        ids = [each['id'] for each in node_json]
        assert_in(self.public_project_user_one._id, ids)
        assert_not_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_projects_logged_in_as_different_user(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_two._id)
        res = self.app.get(url, auth=self.auth_one)
        node_json = res.json['data']

        ids = [each['id'] for each in node_json]
        assert_in(self.public_project_user_two._id, ids)
        assert_not_in(self.public_project_user_one._id, ids)
        assert_not_in(self.private_project_user_one._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)


class TestUserUpdate(ApiTestCase):

    def setUp(self):
        super(TestUserUpdate, self).setUp()
        self.user_one = UserFactory.build()
        self.user_one.set_password('justapoorboy')
        self.user_one.fullname = 'Martin Luther King Jr.'
        self.user_one.given_name = 'Martin'
        self.user_one.family_name = 'King'
        self.user_one.suffix = 'Jr.'
        self.user_one.social['github'] = 'userOnegitHub'
        self.user_one.social['scholar'] = 'userOneScholar'
        self.user_one.social['personal'] = 'http://www.useronepersonalwebsite.com'
        self.user_one.social['twitter'] = 'userOneTwitter'
        self.user_one.social['linkedIn'] = 'userOneLinkedIn'
        self.user_one.social['impactStory'] = 'userOneImpactStory'
        self.user_one.social['orcid'] = 'userOneOrcid'
        self.user_one.social['researcherId'] = 'userOneResearcherId'

        self.user_one.jobs = [
            {
                'startYear': '1995',
                'title': '',
                'startMonth': 1,
                'endMonth': None,
                'endYear': None,
                'ongoing': False,
                'department': '',
                'institution': 'Waffle House'
            }
        ]
        self.user_one.save()
        self.auth_one = (self.user_one.username, 'justapoorboy')
        self.user_one_url = "/v2/users/{}/".format(self.user_one._id)

        self.user_two = UserFactory.build()
        self.user_two.set_password('justapoorboy')
        self.user_two.save()
        self.auth_two = (self.user_two.username, 'justapoorboy')

        self.new_fullname = 'el-Hajj Malik el-Shabazz'
        self.new_given_name = 'Malcolm'
        self.new_family_name = 'X'
        self.new_suffix = 'Sr.'
        self.blank_suffix = ''
        self.new_gitHub = 'newgitHub'
        self.new_scholar = 'newScholar'
        self.new_personal_website = 'http://www.newpersonalwebsite.com'
        self.new_twitter = 'newTwitter'
        self.new_linkedIn = 'newLinkedIn'
        self.new_impactStory = 'newImpactStory'
        self.new_orcid = 'newOrcid'
        self.new_researcherId = 'newResearcherId'
        self.new_user_data = {
            'id': self.user_one._id,
            'fullname': self.new_fullname,
            'given_name': self.new_given_name,
            'family_name': self.new_family_name,
            'suffix': self.new_suffix,
            'gitHub': self.new_gitHub,
            'personal_website': self.new_personal_website,
            'twitter': self.new_twitter,
            'linkedIn': self.new_linkedIn,
            'impactStory': self.new_impactStory,
            'orcid': self.new_orcid,
            'researcherId': self.new_researcherId,
        }
        self.blank_user_data =  {
            'id': self.user_one._id,
            'fullname': self.new_fullname,
            'given_name': '',
            'family_name': '',
            'suffix': '',
            'gitHub': '',
            'personal_website': '',
            'twitter': '',
            'linkedIn':  '',
            'impactStory': '',
            'orcid': '',
            'researcherId': '',
        }

    def tearDown(self):
        super(TestUserUpdate, self).tearDown()

    def test_patch_user_logged_out(self):
        res = self.app.patch_json(self.user_one_url, {
            'fullname': self.new_fullname,
        }, expect_errors=True)
        # This is 403 instead of 401 because basic authentication is only for unit tests and, in order to keep from
        # presenting a basic authentication dialog box in the front end. We may change this as we understand CAS
        # a little better
        assert_equal(res.status_code, 403)

    def test_patch_user_read_only_field(self):
        # Test to make sure read only fields cannot be updated
        self.new_employment_institutions = [
            {
                'startYear': '1982',
                'title': '',
                'startMonth': 1,
                'endMonth': 4,
                'endYear': 1999,
                'ongoing': True,
                'department': 'department of revolution',
                'institution': 'IHop'
            }
        ]
        self.new_educational_institutions = [
            {
                "startYear": '',
                "degree": '',
                "startMonth": None,
                "endMonth": None,
                "endYear": '2000',
                "ongoing": False,
                "department": 'Mom',
                "institution": 'Heeyyyy'
            }
        ]
        res = self.app.patch_json(self.user_one_url, {
            'employment_institutions': self.new_employment_institutions,
            'educational_institutions': self.new_educational_institutions,
            'fullname': self.new_fullname,
        }, auth=self.auth_one)
        assert_equal(res.status_code, 200)
        assert_equal(res.json['data']['employment_institutions'], self.user_one.jobs)
        assert_equal(res.json['data']['educational_institutions'], self.user_one.schools)
        assert_equal(res.json['data']['fullname'], self.new_fullname)

    def test_put_user_logged_in(self):
        # Logged in user updates their user information via patch
        res = self.app.put_json(self.user_one_url, self.new_user_data, auth=self.auth_one)
        assert_equal(res.status_code, 200)
        assert_equal(res.json['data']['fullname'], self.new_fullname)
        assert_equal(res.json['data']['given_name'], self.new_given_name)
        assert_equal(res.json['data']['family_name'], self.new_family_name)
        assert_equal(res.json['data']['suffix'], self.new_suffix)
        assert_equal(res.json['data']['gitHub'], self.new_gitHub)
        assert_equal(res.json['data']['personal_website'], self.new_personal_website)
        assert_equal(res.json['data']['twitter'], self.new_twitter)
        assert_equal(res.json['data']['linkedIn'], self.new_linkedIn)
        assert_equal(res.json['data']['impactStory'], self.new_impactStory)
        assert_equal(res.json['data']['orcid'], self.new_orcid)
        assert_equal(res.json['data']['researcherId'], self.new_researcherId)
        self.user_one.reload()
        assert_equal(self.user_one.fullname, self.new_fullname)
        assert_equal(self.user_one.given_name, self.new_given_name)
        assert_equal(self.user_one.family_name, self.new_family_name)
        assert_equal(self.user_one.suffix, self.new_suffix)
        assert_equal(self.user_one.social['github'], self.new_gitHub)
        assert_equal(self.user_one.social['personal'], self.new_personal_website)
        assert_equal(self.user_one.social['twitter'], self.new_twitter)
        assert_equal(self.user_one.social['linkedIn'], self.new_linkedIn)
        assert_equal(self.user_one.social['impactStory'], self.new_impactStory)
        assert_equal(self.user_one.social['orcid'], self.new_orcid)
        assert_equal(self.user_one.social['researcherId'], self.new_researcherId)

    def test_put_blank_user(self):
        # Logged in user updates their user information via patch
        res = self.app.put_json(self.user_one_url,self.blank_user_data, auth=self.auth_one)
        assert_equal(res.status_code, 200)
        assert_equal(res.json['data']['id'], self.user_one._id)
        assert_equal(res.json['data']['fullname'], self.new_fullname)
        assert_equal(res.json['data']['given_name'], '')
        assert_equal(res.json['data']['family_name'], '')
        assert_equal(res.json['data']['suffix'], '')
        assert_equal(res.json['data']['gitHub'], '')
        assert_equal(res.json['data']['personal_website'], '')
        assert_equal(res.json['data']['twitter'], '')
        assert_equal(res.json['data']['linkedIn'], '')
        assert_equal(res.json['data']['impactStory'], '')
        assert_equal(res.json['data']['orcid'], '')
        assert_equal(res.json['data']['researcherId'], '')
        self.user_one.reload()
        assert_equal(self.user_one.fullname, self.new_fullname)
        assert_equal(self.user_one.given_name, '')
        assert_equal(self.user_one.family_name, '')
        assert_equal(self.user_one.suffix, '')
        assert_equal(self.user_one.social['github'], '')
        assert_equal(self.user_one.social['personal'], '')
        assert_equal(self.user_one.social['twitter'], '')
        assert_equal(self.user_one.social['linkedIn'], '')
        assert_equal(self.user_one.social['impactStory'], '')
        assert_equal(self.user_one.social['orcid'], '')
        assert_equal(self.user_one.social['researcherId'], '')

    def test_patch_user_logged_in_blank_suffix(self):
        # Logged in user updates their user information via patch
        res = self.app.patch_json(self.user_one_url, self.blank_user_data, auth=self.auth_one)
        assert_equal(res.status_code, 200)
        assert_equal(res.json['data']['id'], self.user_one._id)
        assert_equal(res.json['data']['fullname'], self.new_fullname)
        assert_equal(res.json['data']['given_name'], '')
        assert_equal(res.json['data']['family_name'], '')
        assert_equal(res.json['data']['suffix'], '')
        assert_equal(res.json['data']['gitHub'], '')
        assert_equal(res.json['data']['personal_website'], '')
        assert_equal(res.json['data']['twitter'], '')
        assert_equal(res.json['data']['linkedIn'], '')
        assert_equal(res.json['data']['impactStory'], '')
        assert_equal(res.json['data']['orcid'], '')
        assert_equal(res.json['data']['researcherId'], '')
        self.user_one.reload()
        assert_equal(self.user_one.fullname, self.new_fullname)
        assert_equal(self.user_one.given_name, '')
        assert_equal(self.user_one.family_name, '')
        assert_equal(self.user_one.suffix, '')
        assert_equal(self.user_one.social['github'], '')
        assert_equal(self.user_one.social['personal'], '')
        assert_equal(self.user_one.social['twitter'], '')
        assert_equal(self.user_one.social['linkedIn'], '')
        assert_equal(self.user_one.social['impactStory'], '')
        assert_equal(self.user_one.social['orcid'], '')
        assert_equal(self.user_one.social['researcherId'], '')

    def test_put_user_logged_in_blank_required_field(self):
        # Logged in user updates their user information via patch
        res = self.app.put_json(self.user_one_url, {
            'id': self.user_one._id,
            'fullname': '',
        }, auth=self.auth_one, expect_errors=True)
        assert_equal(res.status_code, 400)

    def test_patch_user_logged_in_blank_required_field(self):
        # Logged in user updates their user information via patch
        res = self.app.patch_json(self.user_one_url, {
            'id': self.user_one._id,
            'fullname': '',
        }, auth=self.auth_one, expect_errors=True)
        assert_equal(res.status_code, 400)

    def test_put_user_logged_out(self):
        put = self.app.put_json(self.user_one_url, self.new_user_data, expect_errors=True)
        # This is 403 instead of 401 because basic authentication is only for unit tests and, in order to keep from
        # presenting a basic authentication dialog box in the front end. We may change this as we understand CAS
        # a little better
        assert_equal(put.status_code, 403)
        self.user_one.reload()
        res = self.app.get(self.user_one_url)
        assert_equal(res.json['data']['fullname'], self.user_one.fullname)
        assert_equal(res.json['data']['given_name'],self.user_one.given_name)
        assert_equal(res.json['data']['family_name'], self.user_one.family_name)
        assert_equal(res.json['data']['suffix'], self.user_one.suffix)
        assert_equal(res.json['data']['gitHub'], self.user_one.social['github'])
        assert_equal(res.json['data']['personal_website'], self.user_one.social['personal'])
        assert_equal(res.json['data']['twitter'], self.user_one.social['twitter'])
        assert_equal(res.json['data']['linkedIn'], self.user_one.social['linkedIn'])
        assert_equal(res.json['data']['impactStory'], self.user_one.social['impactStory'])
        assert_equal(res.json['data']['orcid'], self.user_one.social['orcid'])
        assert_equal(res.json['data']['researcherId'], self.user_one.social['researcherId'])

    def test_put_wrong_user(self):
        # User tries to update someone else's user information via put
        put = self.app.put_json(self.user_one_url, self.new_user_data, auth=self.auth_two, expect_errors=True)
        # This is 403 instead of 401 because basic authentication is only for unit tests and, in order to keep from
        # presenting a basic authentication dialog box in the front end. We may change this as we understand CAS
        # a little better
        assert_equal(put.status_code, 403)
        self.user_one.reload()
        res = self.app.get(self.user_one_url)
        assert_equal(res.json['data']['fullname'], self.user_one.fullname)
        assert_equal(res.json['data']['given_name'],self.user_one.given_name)
        assert_equal(res.json['data']['family_name'], self.user_one.family_name)
        assert_equal(res.json['data']['suffix'], self.user_one.suffix)
        assert_equal(res.json['data']['gitHub'], self.user_one.social['github'])
        assert_equal(res.json['data']['personal_website'], self.user_one.social['personal'])
        assert_equal(res.json['data']['twitter'], self.user_one.social['twitter'])
        assert_equal(res.json['data']['linkedIn'], self.user_one.social['linkedIn'])
        assert_equal(res.json['data']['impactStory'], self.user_one.social['impactStory'])
        assert_equal(res.json['data']['orcid'], self.user_one.social['orcid'])
        assert_equal(res.json['data']['researcherId'], self.user_one.social['researcherId'])


    def test_patch_wrong_user(self):
        # User tries to update someone else's user information via patch
        patch = self.app.patch_json(self.user_one_url, self.new_user_data, auth=self.auth_two, expect_errors=True)
        # This is 403 instead of 401 because basic authentication is only for unit tests and, in order to keep from
        # presenting a basic authentication dialog box in the front end. We may change this as we understand CAS
        # a little better
        assert_equal(patch.status_code, 403)
        res = self.app.get(self.user_one_url)
        assert_equal(res.json['data']['fullname'], self.user_one.fullname)
        assert_equal(res.json['data']['given_name'],self.user_one.given_name)
        assert_equal(res.json['data']['family_name'], self.user_one.family_name)
        assert_equal(res.json['data']['suffix'], self.user_one.suffix)
        assert_equal(res.json['data']['gitHub'], self.user_one.social['github'])
        assert_equal(res.json['data']['personal_website'], self.user_one.social['personal'])
        assert_equal(res.json['data']['twitter'], self.user_one.social['twitter'])
        assert_equal(res.json['data']['linkedIn'], self.user_one.social['linkedIn'])
        assert_equal(res.json['data']['impactStory'], self.user_one.social['impactStory'])
        assert_equal(res.json['data']['orcid'], self.user_one.social['orcid'])
        assert_equal(res.json['data']['researcherId'], self.user_one.social['researcherId'])

    def test_update_user_sanitizes_html_properly(self):
        """Post request should update resource, and any HTML in fields should be stripped"""
        bad_fullname = 'Malcolm <strong>X</strong>'
        bad_family_name = 'X <script>alert("is")</script> a cool name'
        res = self.app.patch_json(self.user_one_url, {
            'fullname': bad_fullname,
            'family_name': bad_family_name,
        }, auth=self.auth_one)
        assert_equal(res.status_code, 200)
        assert_equal(res.json['data']['fullname'], strip_html(bad_fullname))
        assert_equal(res.json['data']['family_name'], strip_html(bad_family_name))


class TestUserRoutesNodeRoutes(ApiTestCase):

    def setUp(self):
        super(TestUserRoutesNodeRoutes, self).setUp()
        self.user_one = UserFactory.build()
        self.user_one.set_password('justapoorboy')
        self.user_one.social['twitter'] = 'howtopizza'
        self.user_one.save()
        self.auth_one = (self.user_one.username, 'justapoorboy')

        self.user_two = UserFactory.build()
        self.user_two.set_password('justapoorboy')
        self.user_two.save()
        self.auth_two = (self.user_two.username, 'justapoorboy')

        self.public_project_user_one = ProjectFactory(title="Public Project User One", is_public=True, creator=self.user_one)
        self.private_project_user_one = ProjectFactory(title="Private Project User One", is_public=False, creator=self.user_one)
        self.public_project_user_two = ProjectFactory(title="Public Project User Two", is_public=True, creator=self.user_two)
        self.private_project_user_two = ProjectFactory(title="Private Project User Two", is_public=False, creator=self.user_two)
        self.deleted_project_user_one = FolderFactory(title="Deleted Project User One", is_public=False, creator=self.user_one, is_deleted=True)

        self.folder = FolderFactory()
        self.deleted_folder = FolderFactory(title="Deleted Folder User One", is_public=False, creator=self.user_one, is_deleted=True)
        self.dashboard = DashboardFactory()

    def tearDown(self):
        super(TestUserRoutesNodeRoutes, self).tearDown()
        Node.remove()

    def test_get_200_path_users_me_userone_logged_in(self):
        url = "/{}users/me/".format(API_BASE)
        res = self.app.get(url, auth=self.auth_one)
        assert_equal(res.status_code, 200)

    def test_get_200_path_users_me_usertwo_logged_in(self):
        url = "/{}users/me/".format(API_BASE)
        res = self.app.get(url, auth=self.auth_two)
        assert_equal(res.status_code, 200)

    def test_get_403_path_users_me_no_user(self):
        # TODO: change expected exception from 403 to 401 for unauthorized users

        url = "/{}users/me/".format(API_BASE)
        res = self.app.get(url, expect_errors=True)
        # This is 403 instead of 401 because basic authentication is only for unit tests and, in order to keep from
        # presenting a basic authentication dialog box in the front end. We may change this as we understand CAS
        # a little better
        assert_equal(res.status_code, 403)

    def test_get_404_path_users_user_id_me_user_logged_in(self):
        url = "/{}users/{}/me/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_users_user_id_me_no_user(self):
        url = "/{}users/{}/me/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_users_user_id_me_unauthorized_user(self):
        url = "/{}users/{}/me/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth= self.auth_two, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_200_path_users_user_id_user_logged_in(self):
        url = "/{}users/{}/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one)
        assert_equal(res.status_code, 200)

    def test_get_200_path_users_user_id_no_user(self):
        url = "/{}users/{}/".format(API_BASE, self.user_two._id)
        res = self.app.get(url)
        assert_equal(res.status_code, 200)

    def test_get_200_path_users_user_id_unauthorized_user(self):
        url = "/{}users/{}/".format(API_BASE, self.user_two._id)
        res = self.app.get(url, auth=self.auth_one)
        assert_equal(res.status_code, 200)

        ids = {each['id'] for each in res.json['data']}
        assert_in(self.public_project_user_one._id, ids)
        assert_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_200_path_users_me_nodes_user_logged_in(self):
        url = "/{}users/me/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one)
        assert_equal(res.status_code, 200)

        ids = {each['id'] for each in res.json['data']}
        assert_in(self.public_project_user_one._id, ids)
        assert_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_403_path_users_me_nodes_no_user(self):
        # TODO: change expected exception from 403 to 401 for unauthorized users

        url = "/{}users/me/nodes/".format(API_BASE)
        res = self.app.get(url, expect_errors=True)
        # This is 403 instead of 401 because basic authentication is only for unit tests and, in order to keep from
        # presenting a basic authentication dialog box in the front end. We may change this as we understand CAS
        # a little better
        assert_equal(res.status_code, 403)

    def test_get_200_path_users_user_id_nodes_user_logged_in(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth= self.auth_one)
        assert_equal(res.status_code, 200)

        ids = {each['id'] for each in res.json['data']}
        assert_in(self.public_project_user_one._id, ids)
        assert_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_200_path_users_user_id_nodes_no_user(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url)
        assert_equal(res.status_code, 200)

        # an anonymous/unauthorized user can only see the public projects user_one contributes to.
        ids = {each['id'] for each in res.json['data']}
        assert_in(self.public_project_user_one._id, ids)
        assert_not_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_200_path_users_user_id_unauthorized_user(self):
        url = "/{}users/{}/nodes/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_two)
        assert_equal(res.status_code, 200)

        # an anonymous/unauthorized user can only see the public projects user_one contributes to.
        ids = {each['id'] for each in res.json['data']}
        assert_in(self.public_project_user_one._id, ids)
        assert_not_in(self.private_project_user_one._id, ids)
        assert_not_in(self.public_project_user_two._id, ids)
        assert_not_in(self.private_project_user_two._id, ids)
        assert_not_in(self.folder._id, ids)
        assert_not_in(self.deleted_folder._id, ids)
        assert_not_in(self.deleted_project_user_one._id, ids)

    def test_get_404_path_users_user_id_nodes_me_user_logged_in(self):
        url = "/{}users/{}/nodes/me/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_users_user_id_nodes_me_unauthorized_user(self):
        url = "/{}users/{}/nodes/me/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_two, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_users_user_id_nodes_me_no_user(self):
        url = "/{}users/{}/nodes/me/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_nodes_me_user_logged_in(self):
        url = "/{}nodes/me/".format(API_BASE)
        res = self.app.get(url, auth=self.auth_one, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_nodes_me_no_user(self):
        url = "/{}nodes/me/".format(API_BASE)
        res = self.app.get(url, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_nodes_user_id_user_logged_in(self):
        url = "/{}nodes/{}/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_one, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_nodes_user_id_unauthorized_user(self):
        url = "/{}nodes/{}/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, auth=self.auth_two, expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_get_404_path_nodes_user_id_no_user(self):
        url = "/{}nodes/{}/".format(API_BASE, self.user_one._id)
        res = self.app.get(url, expect_errors=True)
        assert_equal(res.status_code, 404)
