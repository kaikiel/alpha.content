# -*- coding: utf-8 -*-
from alpha.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from zope import schema
from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form


class IExchange(Form.Schema):

    exchange = schema.Float(
        title=_(u'Exchange Rate'),
        description=_(u'US dollar to RMB exchange rate'),
        required=True,
    )


class ExchangeRateControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IExchange

CustomControlPanelView = layout.wrap_form(ExchangeRateControlPanelForm, ControlPanelFormWrapper)
CustomControlPanelView.label = _(u"Exchange Rate Setting")
