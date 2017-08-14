#!/usr/bin/env python

import yaml
import re
import copy

class vdy:
    SYMBOL_SLASH = '/'

    TYPE_DICT = 'DICT'
    TYPE_LIST = 'LIST'
    TYPE_VALUE = 'VALUE'
    TYPE_NONE = 'NONE'

    KEYWORD_IMPORT = 'IMPORT'

    def __init__(self, vdyFileName=None):
        self.REG_VARIABLE = r'\$[a-zA-Z0-9_\.]+'
        self.REG_VARIABLE_ONLY = r'^\$([a-zA-Z0-9_\.]+)$'

        self.vdyFileName = vdyFileName
        self.yamlDoc = dict()
        self.variDoc = dict()
        self.updateYamlDoc(vdyFileName)

    def handleDoc(self, fileName):
        origDoc = self.importYaml(fileName)
        origPath = self.getPath(fileName)
        for f in origDoc.get(self.KEYWORD_IMPORT, []): origDoc.update(self.handleDoc(origPath+f))
        self.handleValue(None, self.TYPE_NONE, None, origDoc, '', self.generateVariDoc, self.dummy)
        #self.handleValue(None, self.TYPE_NONE, None, origDoc, '', self.referVariKey, self.dummy)
        #self.handleValue(None, self.TYPE_NONE, None, origDoc, '', self.referVariDoc, self.dummy)
        return origDoc

    def getPath(self, fileName):
        return  self.SYMBOL_SLASH.join(fileName.split(self.SYMBOL_SLASH)[0:-1]) + self.SYMBOL_SLASH

    def importYaml(self, yamlName):
        with open(yamlName, 'r') as f: doc = yaml.safe_load(f.read())
        return doc

    def updateContext(self, k, c):
        return c + str(k) if len(c)==0 else c + '.' + str(k)

    def handleValue(self, p, t, k, v, c, b, a):
        if type(v) is dict: self.walkDict(p, t, k, v, c, b, a)
        elif type(v) is list: self.walkList(p, t, k, v, c, b, a)
        else: self.walkValue(p, t, k, v, c, b, a)

    def walkDict(self, point, ptype, key, value, context, prefunc, postfunc):
        for k, v in value.iteritems():
            prefunc(point, ptype, key, value, context)
            self.handleValue(value, self.TYPE_DICT, k, v, self.updateContext(k, context), prefunc, postfunc)
            postfunc(point, ptype, key, context, value)

    def walkList(self, point, ptype, key, value, context, prefunc, postfunc):
        for k in range(len(value)):
            prefunc(point, ptype, key, value, context)
            self.handleValue(value, self.TYPE_LIST, k, value[k], self.updateContext(k, context), prefunc, postfunc)
            postfunc(point, ptype, key, value, context)

    def walkValue(self, point, ptype, key, value, context, prefunc, postfunc):
        prefunc(point, ptype, key, value, context)
        postfunc(point, ptype, key, value, context)

    def generateVariDoc(self, point, ptype, key, value, context):
        if ptype == self.TYPE_DICT:
            self.variDoc[context] = value

    def referVariKey(self, point, ptype, key, value, context):
        if type(key) is str:
            newKey = self.referVari(key)
            if newKey != key:
                self.variDoc[context.replace(key, newKey)] = self.variDoc[context]

    def referVariDoc(self, point, ptype, key, value, context):
        if type(value) is dict: pass
        elif type(value) is list: pass
        elif type(value) is str:
            newValue = self.referVari(value)
            if type(key) is str:
                newKey = self.referVari(key)
                if newKey != key:
                    self.variDoc[context.replace(key, newKey)] = self.variDoc[context]
                    del point[key]
                    point[newKey] = newValue
                else: point[key] = newValue
            else: point[key] = newValue
        else: pass

    def referVari(self, value):
        value = self.referVariOnly(value)
        if type(value) is str: return self.referVariStr(value)
        else: return value

    def referVariOnly(self, value):
        m = re.search(self.REG_VARIABLE_ONLY, value.strip())
        while m:
            if m.group(1) in self.variDoc.keys():
                value = self.variDoc[m.group(1)]
                if type(value) is str:
                    m = re.search(self.REG_VARIABLE_ONLY, value.strip())
                else:
                    #self.handleValue(None, self.TYPE_NONE, None, value, <context>, self.referVariDoc, self.dummy)
                    m = False
            else: m = False
        return value

    def referVariStr(self, value):
        newValue = value
        while re.search(self.REG_VARIABLE, newValue):
            s, e = [(m.start(), m.end()) for m in re.finditer(self.REG_VARIABLE, newValue)][0]
            newValue = newValue[:s] + str(self.variDoc.get(newValue[s+1:e], newValue[s+1:e])) + newValue[e:]
        return newValue

    def dummy(self, point, ptype, key, value, context): pass

    def assign(self, variable=None):
        self.handleValue(None, self.TYPE_NONE, None, self.yamlDoc, '', self.referVariKey, self.dummy)
        if variable != None:
            self.handleValue(None, self.TYPE_NONE, None, variable, '', self.referVariDoc, self.dummy)
            return variable
        else:
            self.handleValue(None, self.TYPE_NONE, None, self.yamlDoc, '', self.referVariDoc, self.dummy)
            return self.yamlDoc

    def clone(self, other):
        self.vdyFileName = str(other.vdyFileName)
        self.yamlDoc = copy.deepcopy(other.yamlDoc)
        self.variDoc = copy.deepcopy(other.variDoc)
        return self

    def join(self, variable):
        self.updateYamlDoc(variable)
        self.updateVariDoc()
        return self

    def updateYamlDoc(self, doc):
        if doc == None: return self
        if type(doc) is str: self.yamlDoc.update(self.handleDoc(doc))
        elif type(doc) is list:
            for f in doc: self.yamlDoc.update(self.handleDoc(f))
        elif type(doc) is dict:
            self.yamlDoc.update(doc)
        else:
            pass
        return self

    def updateVariDoc(self):
        self.clearVariDoc()
        self.handleValue(None, self.TYPE_NONE, None, self.yamlDoc, '', self.generateVariDoc, self.dummy)
        return self

    def clearVariDoc(self):
        self.variDoc.clear()
        return self

    def __str__(self):
        return str(self.yamlDoc) + '\n' + str(self.variDoc)
