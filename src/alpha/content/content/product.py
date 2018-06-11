# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from alpha.content import _


class IProduct(model.Schema):
    """ Marker interface and Dexterity Python Schema for Product
    """
    title = schema.TextLine(
        title=_(u'Title'),
        required=True
    )

    productNo = schema.TextLine(
        title=_(u'Product Nomber'),
        required=False
    )

    brand = schema.TextLine(
        title=_(u'Brand'),
        required=False
    )

    productCode = schema.TextLine(
        title=_(u'Produce Code'),
        required=False
    )

    availability = schema.TextLine(
        title=(u'Availability'),
        required=False
    )

    description = schema.Text(
        title=(u'Description'),
        required=False
    )

    
    text = RichText(
        title=_(u'Text'),
        required=False
    )

    downloadFile = namedfile.NamedBlobFile(
        title=_(u'Download File'),
        required=False,
    )

    cover = namedfile.NamedBlobImage(
        title=_(u'Cover Image'),
        required=False,
    )
    
    specification = schema.List(
        title=_(u'specification'),
        value_type=schema.TextLine(),
        required=False,
    )

@implementer(IProduct)
class Product(Container):
    """
    """
