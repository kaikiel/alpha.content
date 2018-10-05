# -*- coding: utf-8 -*-
from alpha.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from zope import schema
from plone.z3cform import layout
from z3c.form import form
from plone.supermodel import model


class IWeight(model.Schema):
    bonus = schema.Float(
        title=_(u'Bonus To Money'),
        description=_(u'How much is a bonus point?'),
        default=0.0,
        min=0.0,
        required=True,
    )

    free_shipping = schema.Int(
        title=_(u'free shipping weight'),
        description=_(u'Free shipping when reaching this weight'),
        default=0,
        min=0,
        required=True,
    )

    shipping_fee = schema.Dict(
        title=_(u'Product shipping fee'),
        key_type=schema.Int(
            title=_(u'Weight'),
            min=0,
        ),
        value_type=schema.Float(
            title=_(u'Weight Price'),
            description=_(u'Enter USD$'),
            default=0.0,
            min=0.0,
        ),
        required=True,
    )


class WeightControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IWeight

CustomControlPanelView = layout.wrap_form(WeightControlPanelForm, ControlPanelFormWrapper)
CustomControlPanelView.label = _(u'Product shipping fee')

