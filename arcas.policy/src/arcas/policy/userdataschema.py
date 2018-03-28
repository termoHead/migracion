# -*- coding: utf-8 -*-
from zope.interface import Interface, implements
from plone.z3cform.fieldsets import extensible

from zope import schema
from plone.directives import form
from zope.component import adapts
from zope.component import getUtility, queryUtility
from plone.app.users.browser.userdatapanel import UserDataPanel
from arcas.policy.vocabulario import ColecAsignadasVocab
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.register import RegistrationForm
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from plone.supermodel import model
from z3c.form import field
from arcas.policy.interfaces import IArcasPolicyLayer
from arcas.policy import _
from arcas.policy.vocabulario import ColecAsignadasVocab

def validateAccept(value):
    if not value == True:
        return False
    return True

class IEnhancedUserDataSchema(model.Schema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """
    tipoUsuario = schema.Set(
        title=u'Tipo de usuario',
        description=u'Si desea marcar más de una opcion, oprima CTRL+Click',
        value_type=schema.Choice(values = [
            'Seleccione una opcion',
            'Alumno',
            'Docente',
            'Investigador',
            'Otro',
            ],),
        required=True,
        )

    form.write_permission(participaEn='cmf.ManagePortal')
    participaEn =schema.Set(
        title=u'Colecciones de su interés',
        description=u"Elija la o las Colecciones en las que desea participar. Si desea marcar más de una opcion, oprima CTRL+Click",
        value_type=schema.Choice(source="ColeccionesVocab"),
        required=False,
        )

    enlaceCV = schema.Text(
        title=_(u'Enlace a su Perfil', default=u'Enlace al perfil de memoria'),
        description=_(u'enlace_perfil',
                      default=u"Copie la URL de su perfil en Memoria Académica."),
        required=False,
        )
    form.status = u"Ud está asignado a "
    accept = schema.Bool(
            title=_(u'label_accept', default=u'Accept terms of use'),
            description=_(u'help_accept',
                        default=u"Tick this box to indicate that you have found,"
                        " read and accepted the terms of use for this site. "),
            required=True,
            constraint=validateAccept,
    )



class UserDataPanelExtender(extensible.FormExtender):
    adapts(Interface, IArcasPolicyLayer, UserDataPanel)
    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        fields = fields.omit('accept') # Users have already accepted.
        self.add(fields)
        
class RegistrationPanelExtender(extensible.FormExtender):
    adapts(Interface, IArcasPolicyLayer, RegistrationForm)
    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        #NB: Not omitting the accept field this time, we want people to check it
        self.add(fields)

class EnhancedUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IEnhancedUserDataSchema
    
