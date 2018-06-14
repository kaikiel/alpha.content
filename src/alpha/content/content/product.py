# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.app.vocabularies.catalog import CatalogSource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import validator
from plone.directives import form
import zope.component
import zope.interface
from zope.interface import Invalid
from zope.interface import invariant
from zope import schema
from zope.interface import implementer
from alpha.content import _
import datetime


categoryVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'mostView', title=_(u'Most View')),
     SimpleTerm(value=u'special', title=_(u'Special')),
     SimpleTerm(value=u'latest', title=_(u'Latest'))]
)

def rating_constraint(value):
    if value <= 0 or value > 5:
        raise Invalid(_(u'Please enter 1 to 5 in the Rating field'))
    return True

def future_date(value):
    if value and not value >= datetime.datetime.today():
        raise Invalid(_(u"Time limit date can not be before today."))
    return True


class IProduct(model.Schema):
    title = schema.TextLine(
        title=_(u'Title'),
        required=True
    )

    productNo = schema.TextLine(
        title=_(u'Product Number'),
        required=False
    )
 
    rating = schema.Int(
        title=_(u'Rating'),
        required=False,
        default=4,
        constraint=rating_constraint,
    )

    price = schema.Int(
        title=_(u'Price'),
        description=_(u'Enter USD$'),
        required=False,
    )

    salePrice = schema.Int(
        title=_(u'Sale Price'),
        description=_(u'Enter USD$'),
        required=False
    )

    @invariant
    def price_invariant(data):
        if data.price < data.salePrice:
            raise Invalid(_(u'The sale price is bigger than price!'))

    cover = namedfile.NamedBlobImage(
        title=_(u'Cover Image'),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False
    )

    category = schema.TextLine(
        title=_(u'Category'),
        required=True
    )

    subcategory = schema.TextLine(
        title=_(u'Subcategory'),
        required=True
    )
    
    relatedProduct = RelationList(
        title=_(u"Related Product"),
        default=[],
        value_type=RelationChoice(
            title=_(u"Related"),
            source=CatalogSource(portal_type='Product')
        ),
        required=False,
    )

    fieldset('More Info', fields=['brand', 'productCode', 'availability', 'downloadFile', 'feature'])
    brand = schema.TextLine(
        title=_(u'Brand'),
        required=False
    )

    productCode = schema.TextLine(
        title=_(u'Product Code'),
        required=False
    )

    availability = schema.Bool(
        title=(u'Availability'),
        required=False
    )

    downloadFile = namedfile.NamedBlobFile(
        title=_(u'Download File'),
        required=False,
    )

    feature = RichText(
        title=_(u'Feature'),
        required=False
    )

    fieldset('Specification', fields=['specification'])
    specification = schema.List(
        title=_(u'specification'),
        description=_(u'ex. clockspeed:100mhz'),
        value_type=schema.TextLine(),
        required=False,
    )

    fieldset('Index Information', fields=['indexCategory', 'bestSeller', 'timeLimit'])
    indexCategory = schema.Choice(
        title=_(u"Index Category"),
        description=_(u'Select the classification of this product (Most View, Special, Latest)'),
        vocabulary=categoryVocabulary,
        required=False,
    )

    bestSeller = schema.Bool(
        title=_(u"Best Seller"),
        required=False,
    )

    timeLimit = schema.Datetime(
        title=_(u'Time Limit'),
        description=_(u'If you want to set the time limit, you must put this product in the "Promotions" folder'),
        constraint=future_date,
        required=False,
    )
    

@implementer(IProduct)
class Product(Container):
    """
    """
