# -*- coding: utf-8 -*-
from alpha.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from zope import schema
from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form


class IUser(Form.Schema):

    promoCode = schema.Dict(
        title=_(u'Exist PromoCode'),
        key_type=schema.ASCIILine(),
        value_type=schema.ASCIILine(),
        required=False,
    )


class UserControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IUser

CustomControlPanelView = layout.wrap_form(UserControlPanelForm, ControlPanelFormWrapper)
CustomControlPanelView.label = _(u"User PromoCode")
