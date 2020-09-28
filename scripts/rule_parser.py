import re
# function: take email and return newsletter name


def match_and_extract(text, regex):
    if not regex:
        return text.strip().strip("\"").strip("'")

    m = re.search(regex,text,re.IGNORECASE)
    if m:
        return m.group(1).strip().strip("\"").strip("'")
    return None


# <rule_name>:( <field_name>, <regex> )
letter_rules = {
    '[letter:subject]_in_subject': ('m_subject','^([^:]+):.*$'),
    '[letter_by_author]_in_sender': ('sender','^(.*?)by'),
    '[author_at_letter]_in_sender': ('sender','^.*?at(.*?)'),
    '[author:letter]_in_sender': ('sender',':(.*)$'),
    '[author_from_letter]_in_sender':('sender','.*?from(.*)$'),
    '[letter-subject]_in_sender':('m_subject','^([^-]+)-'),
    '[letter_No_digits]_in_subject':('m_subject','^(.*?)No'),
    'letter_in_body_0':('body','You received this email because you signed up for the(.*?)email from\s+'),
    'letter_in_body_1':('body','You received this email because you signed up for(.*?)from\s+'),
    'letter_in_body_2':('body',"You received this message because you signed up for.*?'s(.*?)newsletter."),
    'letter_in_body_3':('body',"You received this message because you signed up for(.*?)newsletter."),
    'letter_in_body_4':('body',"newsletter is now the(.*?)newsletter."),
    'letter_in_body_5':('body',"You received this email because you signed up for(.*?)or\s+"),
    'letter_in_body_6':('body',"You received this email because you are registered on(.*?)or\s+"),
    'daily_beast_s_letter':('sender',"Daily Beast.s\s+(.+)$"),
    'daily_beast_letter':('sender',"Daily Beast\s+(.+)$"),
    'sender_is_letter':('sender',None)
}

# <rule_name>:( <field_name>, <regex> )
author_rules = {
    '[letter_by_author]_in_sender': ('sender','^.*?by(.*)$'),
    '[author_at_letter]_in_sender': ('sender','^(.*?)at.*$'),
    '[author:letter]_in_sender': ('sender','^(.*?):'),
    '[author_from_letter]_in_sender':('sender','^(.*?)from.*$'),
    'author_is_sender_domain':('sender_email','@(.*)$'),
    'first_word_of_sender_is_author':('sender','^([^\s]+)'),
    '[author_Newsletter]_in_author':('sender','^(.*?)Newsletter'),
    'author_in_body_1':('body','You received this email because you signed up for.*?from(.*?)\.'),
    'sender_is_author':('sender',None),
}

# <domain>:<letter_rule>,<author_rule>
domain_rules_mapping = {

    'washingtonpost.com': [ ('letter_in_body_5','sender_is_author'),
                            ('letter_in_body_1','sender_is_author'),
                        ],
    'inside.com':[('sender_is_letter',
                  'author_is_sender_domain')],
    'nytimes.com':[ ('letter_in_body_4','sender_is_author'),
                    ('letter_in_body_0','sender_is_author'),
                    ('letter_in_body_2','sender_is_author'),
                    ('letter_in_body_1','author_in_body_1'),
                    ('letter_in_body_3','sender_is_author'),
                    ('[letter:subject]_in_subject','sender_is_author')],
    'technologyreview.com':[('sender_is_letter','first_word_of_sender_is_author')],
    'thedailybeast.com':[
                         ('[author:letter]_in_sender','[author:letter]_in_sender'),
                         ('daily_beast_s_letter','sender_is_author'),
                         ('daily_beast_letter','sender_is_author')],
    'whatthefuckjusthappenedtoday.com':[('[author_at_letter]_in_sender','[author_at_letter]_in_sender')],
    'brainpickings.org':[('[letter_by_author]_in_sender','[letter_by_author]_in_sender')],
    'vox.com':[('[letter:subject]_in_subject','sender_is_author'),
               ('sender_is_letter','sender_is_author')],
    'substack.com':[ ('[author_from_letter]_in_sender','[author_from_letter]_in_sender'),
                     ('[letter_by_author]_in_sender','[letter_by_author]_in_sender'),
                     ]

}

umbrella_publishers = ('washingtonpost.com','inside.com','nytimes.com','thedailybeast.com','vox.com','substack.com')
publishing_platform = ('substack.com')


def is_umbrella_publisher(domain):
    return domain in umbrella_publishers


def is_publishing_platform(domain):
    return domain in publishing_platform


def process_rule(nwl):

    email = nwl['sender_email']
    email_domain = email[email.index('@')+1:]
    if email_domain in domain_rules_mapping:
        for (letter_rule,author_rule) in domain_rules_mapping[email_domain]:

            (field,regex) = letter_rules[letter_rule]
            letter_name = match_and_extract(nwl[field], regex)

            (field, regex) = author_rules[author_rule]
            author_name = match_and_extract(nwl[field], regex)
            if letter_name:
                print("[rule_parser] uid: %s, matched:%s, extracted:%s" % (nwl['id'], letter_rule, letter_name))
                break

    else:
        (field, regex) = letter_rules['sender_is_letter']
        letter_name = match_and_extract(nwl[field], regex)

        (field, regex) = author_rules['sender_is_author']
        author_name = match_and_extract(nwl[field], regex)

    return letter_name, author_name


#print (parse_nwl_name('Evening Edition: Trump signals swift nomination to replace Ginsburg',
 #              '^([^:]+):'))
