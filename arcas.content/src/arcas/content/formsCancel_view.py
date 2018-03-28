# -*- coding: utf-8 -*-
__author__ = 'Paul'
# We must use BrowserView from view, not from zope.browser
from Products.Five.browser import BrowserView

class FormsCancelView(BrowserView):

    def __init__(self, context, request):
        """ Initialize context and request as view multi adaption parameters.

        Note that the BrowserView constructor does this for you.
        This step here is just to show how view receives its context and
        request parameter. You do not need to write __init__() for your
        views.
        """
        self.context = context
        self.request = request

    # by default call will call self.index() method which is mapped
    # to ViewPageTemplateFile specified in ZCML
    #def __call__():
    #
    def dameDescri(self):
        if "mensaje" in self.request.form.keys():
            return self.request.form["mensaje"]
        else:
            return ""
        
    def dameTitulo(self):

        if "titulo" in self.request.form.keys():
            return self.request.form["titulo"]
        else:
            return "Error en el formulario"
        

