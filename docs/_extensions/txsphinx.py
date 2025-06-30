##
## The code in this file is a (slightly modified) version from here:
## https://github.com/twisted/twisted/blob/trunk/docs/_extensions/apilinks.py
##
## It is hence licensed under the Twisted license (essentially BSD less advertising):
## https://github.com/twisted/twisted/blob/trunk/LICENSE
##

"""
Sphinx/docutils extension to create links to pyDoctor documentation using a
RestructuredText interpreted text role that looks like this::

    :tx:`python_object_to_link_to <label>`

for example::

    :tx:`twisted.internet.defer.Deferred <Deferred>`

The label is optional, hence you can also use

    :tx:`twisted.internet.defer.Deferred`
"""


def make_api_link(name, rawtext, text, lineno, inliner, options={}, content=[]):
    from docutils import nodes, utils

    # quick, dirty, and ugly...
    if "<" in text and ">" in text:
        full_name, label = text.split("<")
        full_name = full_name.strip()
        label = label.strip(">").strip()
    else:
        full_name = label = text

    # get the base url for api links from the config file
    env = inliner.document.settings.env
    base_url = env.config.apilinks_base_url

    # not really sufficient, but just testing...
    # ...hmmm, maybe this is good enough after all
    ref = "".join((base_url, full_name, ".html"))

    options.update(classes=["tx"])

    node = nodes.reference(rawtext, utils.unescape(label), refuri=ref, **options)

    nodes = [node]
    sys_msgs = []
    return nodes, sys_msgs


# setup function to register the extension


def setup(app):
    app.add_config_value(
        "apilinks_base_url", "http://twistedmatrix.com/documents/current/api/", "env"
    )
    app.add_role("tx", make_api_link)
