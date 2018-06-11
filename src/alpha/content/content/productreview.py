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


class IProductreview(model.Schema):
    title = schema.TextLine(
        title=_(u'Title'),
        required=False
    )

    review = schema.Text(
        title=_(u'Review'),
        required=False
    )

    rating = schema.TextLine(
        title=_(u'Rating'),
        required=False
    )


@implementer(IProductreview)
class Productreview(Item):
    """
    """
