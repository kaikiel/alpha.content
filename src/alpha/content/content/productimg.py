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


class IProductimg(model.Schema):
    title = schema.TextLine(
        title=_(u'Title'),
        required=False
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Product Image'),
        required=True,
    )


@implementer(IProductimg)
class Productimg(Item):
    """
    """
