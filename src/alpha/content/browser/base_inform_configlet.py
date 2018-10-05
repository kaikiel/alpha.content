# -*- coding: utf-8 -*-
from alpha.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant
from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form
import re


class IInform(Form.Schema):

    description = schema.Text(
        title=_(u'Company Description'),
        required=False,
    )
    email = schema.Text(
        title=_(u'email'),
        required=False,
    )
    cellphone = schema.Text(
        title=_(u'cellphone'),
        required=False,
    )
    address = schema.Text(
        title=_(u'address'),
        required=False
    )
    r_email = schema.TextLine(
        title=_(u'Recipient Email'),
        required=False,
    )
    fb_link = schema.TextLine(
        title=_(u'Facebook Link'),
        required=False,
    )
    weibo_link = schema.TextLine(
        title=_(u'Weibo Link'),
        readonly=True,
        required=False,
    )
    youku_link = schema.TextLine(
        title=_(u'Youku Link'),
        readonly=True,
        required=False,
    )
    youtube_link = schema.TextLine(
        title=_(u'Youtube Link'),
        required=False,
    )

    @invariant
    def email_invariant(data):
        com_email = data.email
        r_email = data.r_email
        if com_email:
            for email in com_email.split('\r\n'):
                if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
                    raise Invalid(_(u'Your Email is not valid!'))
        if r_email and not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", r_email):
            raise Invalid(_(u'Receive Email is not valid!'))


class BasicInformControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IInform

CustomControlPanelView = layout.wrap_form(BasicInformControlPanelForm, ControlPanelFormWrapper)
CustomControlPanelView.label = _(u"Basic Inform")
