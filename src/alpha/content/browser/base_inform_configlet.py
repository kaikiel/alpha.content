# -*- coding: utf-8 -*-
from alpha.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from zope import schema
from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form


class IInform(Form.Schema):

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


class BasicInformControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IInform

CustomControlPanelView = layout.wrap_form(BasicInformControlPanelForm, ControlPanelFormWrapper)
CustomControlPanelView.label = _(u"Basic Inform")
