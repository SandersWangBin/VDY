#!/usr/bin/env python

import yaml
import re

class vdy:
    REG_VARIABLE = r'\$[a-zA-Z0-9_]+'
    REG_VARIABLE_ONLY = r'^\$([a-zA-Z0-9_]+)$'

    TYPE_DICT = 'DICT'
    TYPE_LIST = 'LIST'
    TYPE_VALUE = 'VALUE'
    TYPE_NONE = 'NONE'

    KEYWORD_IMPORT = 'IMPORT'

    def __init__(self, vdyFileName):
        self.vdyFileName = vdyFileName
        self.yamlDoc = dict()
        self.variDoc = dict()
        self.yamlDoc.update(self.handleDoc(vdyFileName))

    def handleDoc(self, fileName):
        origDoc = self.importYaml(fileName)
        for f in origDoc.get(self.KEYWORD_IMPORT, []): origDoc.update(self.handleDoc(f))
        self.handleValue(None, self.TYPE_NONE, None, origDoc, self.generateVariDoc, self.dummy)
        self.handleValue(None, self.TYPE_NONE, None, origDoc, self.referVariDoc, self.dummy)
        return origDoc

    def importYaml(self, yamlName):
        with open(yamlName, 'r') as f: doc = yaml.safe_load(f.read())
        return doc

    def handleValue(self, p, t, k, v, b, a):
        if type(v) is dict: self.walkDict(p, t, k, v, b, a)
        elif type(v) is list: self.walkList(p, t, k, v, b, a)
        else: self.walkValue(p, t, k, v, b, a)

    def walkDict(self, point, ptype, key, value, prefunc, postfunc):
        for k, v in value.iteritems():
            prefunc(point, ptype, key, value)
            self.handleValue(value, self.TYPE_DICT, k, v, prefunc, postfunc)
            postfunc(point, ptype, key, value)

    def walkList(self, point, ptype, key, value, prefunc, postfunc):
        for k in range(len(value)):
            prefunc(point, ptype, key, value)
            self.handleValue(value, self.TYPE_LIST, k, value[k], prefunc, postfunc)
            postfunc(point, ptype, key, value)

    def walkValue(self, point, ptype, key, value, prefunc, postfunc):
        prefunc(point, ptype, key, value)
        postfunc(point, ptype, key, value)

    def generateVariDoc(self, point, ptype, key, value):
        if ptype == self.TYPE_DICT: self.variDoc[key] = value

    def referVariDoc(self, point, ptype, key, value):
        if type(value) is dict: pass
        elif type(value) is list: pass
        elif type(value) is str:
            point[key] = self.referVari(value)
        else: pass
 
    def referVari(self, value):
        r, v = self.referVariOnly(value)
        if r: return v
        else: return self.referVariStr(value)

    def referVariOnly(self, value):
        m = re.search(self.REG_VARIABLE_ONLY, value.strip())
        if m:
            if self.variDoc.get(m.group(1), None) != None:
                return True, self.variDoc[m.group(1)]
            else: return False, value
        else: return False, value

    def referVariStr(self, value):
        newValue = value
        while re.search(self.REG_VARIABLE, newValue):
            s, e = [(m.start(), m.end()) for m in re.finditer(self.REG_VARIABLE, newValue)][0]
            newValue = newValue[:s] + self.variDoc[newValue[s+1:e]] + newValue[e:]
        return newValue

    def dummy(self, point, ptype, key, value): pass

    def __str__(self):
        return str(self.yamlDoc)
