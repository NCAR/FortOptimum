# coding: utf-8

from __future__ import unicode_literals, print_function

import seqgentools as seq


class SearchSpace(seq.Sequence):

    def __init__(self, *subspaces):

        self.subspaces = subspaces
        self._space = seq.Product(*subspaces)

    def getitem(self, index):
        return self._space[index]
        
    def length(self):
        return self._space.length()

    def copy(self, memo={}):
        return SearchSpace(*self.subspaces)

    def __next__(self):

        idx = self._iter_index
        val = super(SearchSpace, self).__next__()
        return idx, val

class KeywordSpace(seq.Sequence):

    def __init__(self, kopts):

        self._kopts = kopts

        if len(kopts) == 0:
            self._kwdspace = seq.Wrapper([[]])
            self._keys = [None]
        else:
            self._keys = kopts.keys()
            _values = kopts.values()
            self._kwdspace = seq.Product(*_values)

    def getitem(self, index):

        elem =  self._kwdspace[index]
        item = []

        for k, v in zip(self._keys, elem):
            if k:
                item.append(str(k) + "=" + str(v))
            else:
                item.append(v)

        return item
 
    def length(self):
        return self._kwdspace.length()
    
    def copy(self, memo={}):
        return KeywordSpace(*self._kopts)

class CommandLineSpace(seq.Sequence):

    def __init__(self, *vopts, **kopts):

        self._vopts = vopts
        self._kopts = kopts

        if len(vopts) == 0:
            vopts = [[]]

        _voptspace = seq.Product(*vopts)
        _koptspace = KeywordSpace(kopts)

        self._optspace = seq.Product(_voptspace, _koptspace)
        if self._optspace.length() == 0:
            self._optspace = seq.Wrapper([[]])


    def getitem(self, index):
        return self._optspace[index]
        
    def length(self):
        return self._optspace.length()

    def copy(self, memo={}):
        return self.__class__(*self._vopts, **self._kopts)


class EnvVarSpace(CommandLineSpace):
    pass

class CompOptSpace(CommandLineSpace):
    pass

class LinkOptSpace(CommandLineSpace):
    pass

class ExeEnvSpace(CommandLineSpace):
    pass

class XformSpace(seq.Sequence):

    def __init__(self, *xforms):

        self.xforms = xforms
        self._xformspace = seq.Product(*xforms)

    def getitem(self, index):
        return self._xformspace[index]
        
    def length(self):
        return self._xformspace.length()

    def copy(self, memo={}):
        return XformSpace(*self.xforms)
