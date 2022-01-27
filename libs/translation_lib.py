import gettext

# region Import
from kivy.lang import Observable
# endregion Import


class Translation(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang, domian, resource_dir):
        super(Translation, self).__init__()

        self.ugettext = None
        self.lang = defaultlang
        self.domian = domian
        self.resource_dir = resource_dir
        self.switch_lang(self.lang)

    def tr(self, text):
        try:
            return self.ugettext(text)
        except UnicodeDecodeError:
            return self.ugettext(text.decode("utf-8"))

    def fbind(self, name, func, args, **kwargs):
        if name == "tr":
            self.observers.append((func, args, kwargs))
        else:
            return super(Translation, self).fbind(name, func, *args, **kwargs)

    def funbind(self, name, func, args, **kwargs):
        if name == "tr":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Translation, self).funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang):
        # get the right locales directory, and instanciate a gettext
        locales = gettext.translation(self.domian, self.resource_dir, languages=[lang])
        try:
            self.ugettext = locales.ugettext
        except AttributeError:
            self.ugettext = locales.gettext

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)
