# -*- coding: utf-8 -*-

import difflib
import re

from framework.mongo.utils import to_mongo_key

from website.notifications.emails import send
from framework.auth.core import User
from .model import NodeWikiPage


# Detect references to person with hashcode, eg @JohnSmith-a1b2c
PERSON_REGEX = re.compile(r"@\w+-([\w^_]+)", re.UNICODE)


def diff_snippets(text1, text2):
    """
    Perform a comparison of two markdown strings. Return the segments that
        are different.
    :param text1: The first markdown string
    :param text2: The second markdown string
    :return: list: The lines that are marked as changes (ONLY present in
        one file or the other)
    """
    differ = difflib.ndiff(text1.splitlines(), text2.splitlines())

    old_only = []
    new_only = []

    # Find lines corresponding to actual differences
    for diff in differ:
        d_text = diff[2:]

        if diff.startswith("- "):
            old_only.append(d_text)
        elif diff.startswith("+ "):
            new_only.append(d_text)
    return old_only, new_only


def new_mentions(line_strings):
    """
    Given a diff between two files, identify new lines that mention a person.

    From markdown person mentions (eg @JohnSmith-a1b2c), extract hashcodes
    :param line_strings: list: A list of strings representing each line in file
    :return: A list of hashcode person-ids
    """
    # TODO: Initial version would send emails if the line was changed at all-
    # eg if punctuation was added after a person. That is undesirable.
    new_person_hashes = []
    for line in line_strings:
        new_person_hashes.extend(re.findall(PERSON_REGEX, line))

    return new_person_hashes


def email_mentions(old_content, new_content, context):
    """
    Given a wiki page object, check the content for newly @mentioned users.
    Send email notifications as appropriate.

    :param old_content:
    :param new_content:
    :param context: dict w/keys editor, node, project_name, page_name, and page_url
    :return:
    """
    # Find users newly mentioned in the wiki
    old_only, new_only = diff_snippets(old_content, new_content)
    person_mentions = new_mentions(new_only)

    user_dummy = context['editor']
    sender_node = context["node"]

    # TODO: make email url absolute

    for user_id in person_mentions:
        user = User.load(user_id)
        if user is not None: # TODO: Report user mentions that do not correspond to an actual user
            #context["gravatar_url"] = user_dummy.gravatar_url

            send([user_dummy],
                 "email_transactional",
                 sender_node._id,
                 "wiki_mention",
                 gravatar_url=user_dummy.gravatar_url, # part of kwargs without modifying context. Hack.
                 **context)