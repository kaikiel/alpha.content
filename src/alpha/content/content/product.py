# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from z3c.form.browser.radio import RadioFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.namedfile.field import NamedBlobImage, NamedBlobFile, NamedImage
from plone.app.vocabularies.catalog import CatalogSource
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import validator
from plone.directives import form
from plone.autoform import directives
from z3c.form.browser.checkbox import CheckBoxFieldWidget
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
    fieldset(_('Product Info'), fields=['title', 'productNo', 'limit_qty', 'rating', 'cover', 'description', 'category', 'subcategory', 'relatedProduct'])
    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    productNo = schema.TextLine(
        title=_(u'Product Number'),
        required=True,
    )

    limit_qty = schema.Int(
        title=_(u'Limited quantity'),
        description=_(u'Time Limit Product quantity'),
        default=0,
        min=0,
        required=True
    )
 
    rating = schema.Int(
        title=_(u'Rating'),
        required=True,
        default=4,
        constraint=rating_constraint,
    )

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

    fieldset(_('More Info'), fields=['brand', 'productCode', 'downloadFile', 'feature', 'specification'])
    brand = schema.TextLine(
        title=_(u'Brand'),
        required=True
    )

    productCode = schema.TextLine(
        title=_(u'Product Code'),
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

    specification = schema.List(
        title=_(u'specification'),
        description=_(u'ex. clockspeed:100mhz'),
        value_type=schema.TextLine(),
        required=False,
    )

    fieldset(_('Product Price'), fields=['weight', 'price', 'salePrice', 'l_c_price', 'l_b_price', 'l_a_price', 'disc_amount', 'bonus', 'rebate'])
    weight = schema.Float(
        title=_(u'Weight'),
        description=_(u'Product weight (Please enter kg)'),
        default=0.0,
        min=0.0,
        required=True
    )

    price = schema.Float(
        title=_(u'Price'),
        description=_(u'Enter USD$'),
        default=0.0,
        min=0.0,
        required=True,
    )

    salePrice = schema.Float(
        title=_(u'Sale Price'),
        description=_(u'Enter USD$'),
        default=0.0,
        min=0.0,
        required=True,
    )

    l_c_price = schema.Float(
        title=_(u'Level C Group Price'),
        description=_(u'Enter USD$'),
        min=0.0,
        required=False
    )
    
    l_b_price = schema.Float(
        title=_(u'Level B Group Price'),
        description=_(u'Enter USD$'),
        min=0.0,
        required=False
    )

    l_a_price = schema.Float(
        title=_(u'Level A Group Price'),
        description=_(u'Enter USD$'),
        min=0.0,
        required=False
    )

    disc_amount = schema.Float(
        title=_(u'Discount Amount'),
        description=_(u'Enter USD$ (just used on price and sale_price)'),
        min=0.0,
        required=False
    )

    bonus = schema.Int(
        title=_(u'Bonus'),
        description=_(u'Bonus points earned when you purchase this product'),
        default=0,
        min=0,
        required=True
    )

    rebate = schema.Float(
        title=_(u'Promocode Rebate'),
        description=_(u'When the customer completes the expenditure, the owner can get a rebate'),
        default=0.0,
        min=0.0,
        required=True
    )

    @invariant
    def price_invariant(data):
        if data.price < data.salePrice:
            raise Invalid(_(u'The sale price is bigger than price!'))
        if data.price < data.disc_amount:
            raise Invalid(_(u'The Discount Amount is bigger than price!'))

    fieldset(_('Slider'), fields=['img1', 'img2', 'img3', 'img4'])
    img1 = NamedBlobImage(
        title=_(u"Slider Image1"),
        required=False,
    )

    img2 = NamedBlobImage(
        title=_(u"Slider Image2"),
        required=False,
    )

    img3 = NamedBlobImage(
        title=_(u"Slider Image3"),
        required=False,
    )

    img4 = NamedBlobImage(
        title=_(u"Slider Image4"),
        required=False,
    )
    
    fieldset(_('Index Information'), fields=['indexCategory', 'bestSeller', 'timeLimit'])
    
    directives.widget(indexCategory=CheckBoxFieldWidget)
    indexCategory = schema.List(
        title=_(u"Index Category"),
        description=_(u'Select the classification of this product (Most View, Special, Latest)'),
        value_type=schema.Choice(
            vocabulary=categoryVocabulary,
        ),
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
class Product(Item):
    """
    """
