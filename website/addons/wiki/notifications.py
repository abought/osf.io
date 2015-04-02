# -*- coding: utf-8 -*-

import difflib
import re

from framework.mongo.utils import to_mongo_key

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


def email_mentions(node, wiki_name, wiki_page_obj):
    """
    Given a wiki page object, check the content for newly @mentioned users.
    Send email notifications as appropriate.

    :param wiki_page_obj: The DB object representing this wiki page
    :return: TODO
    """
    # Find users newly mentioned in the wiki
    old_wiki_content = ""
    new_wiki_content = ""

    # Find the text of the previous revision
    key = to_mongo_key(wiki_name)
    version_keys = list(reversed(node.wiki_pages_versions[key]))  # Time ordered, newest first
    # FIXME: What if a user is reading an old version? Prev version may not always be second-newest
    new_ver_id = version_keys[0]  # Get newly created record (caller doesn't have reference to it)



    prev_ver_id = version_keys[1] if len(version_keys) > 1 else None
    # TODO: make sure we're diffing correct versions
    if prev_ver_id is None:
        print "no prev node found"
        prev_content = ""
    else:
        prev_node = NodeWikiPage.load(prev_ver_id)
        prev_content = prev_node.content
        print "then", prev_node._id, prev_content

    print "now", wiki_page_obj._id, wiki_page_obj.content
    print "CHANGES", diff_snippets(prev_content, wiki_page_obj.content)


    #
    #
    #
    # # # Skip if wiki_page doesn't exist; happens on new projects before
    # # # default "home" page is created
    # # if key not in node.wiki_pages_versions:
    # #     return []
    #
    # versions = [
    #     NodeWikiPage.load(version_wiki_id)
    #     for version_wiki_id in node.wiki_pages_versions[key]
    # ]
    #
    # print "Versions!", [(v.user, v.content) for v in versions]
    #
    # print "just versions", node.wiki_pages_versions[key]


    # FIXME? pass in a dummy anon status, since we're only acquiring page history here- not checking user identity
    #versions = _get_wiki_versions(node, wiki_name, anonymous=False)    # TODO: Implement. Find how to get old version of wiki page.


    # TODO: Where does the email notification template live? (It's not part of the wiki)