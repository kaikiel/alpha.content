# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from alpha.content import _


class ICompany(model.Schema):
    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    text = RichText(
        title=_(u'Text'),
        required=True,
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Cover Image'),
        required=True,
    )


@implementer(ICompany)
class Company(Item):
    """
    """
