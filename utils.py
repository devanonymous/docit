#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, datetime, json, inspect

__all__=['PY_V', 'magicDict', 'dict2magic', 'console', 'getms', 'reprEx', 'strGet', 'fileGet', 'fileAppend', 'fileWrite', 'pathList', 'oGet', 'iterate']
__all__+=['isFunction', 'isInstance', 'isModule', 'isClass', 'isModuleBuiltin', 'isTuple', 'isArray', 'isDict', 'isString', 'isNum']

global PY_V
PY_V=float(sys.version[:3])

class magicDict(dict):
   """
   Get and set values like in Javascript (dict.<key>)
   """
   def __getattr__(self, attr):
      if attr[:2]=='__': raise AttributeError #for support PICKLE protocol and correct isFunction() check
      return self.get(attr, None)

   # __getattr__=dict.__getitem__
   __setattr__=dict.__setitem__
   __delattr__=dict.__delitem__
   __reduce__=dict.__reduce__

def dict2magic(o, recursive=False):
   if recursive:
      if isArray(o):
         for i, _ in enumerate(o): o[i]=dict2magic(o[i], recursive=True)
      elif isDict(o):
         for i in o: o[i]=dict2magic(o[i], recursive=True)
         o=magicDict(o)
   elif isDict(o): o=magicDict(o)
   return o

consoleColor=magicDict({
   'header':'\033[95m',
   'okBlue':'\033[94m',
   'okGreen':'\033[92m',
   'ok':'\033[92m',
   'warning':'\033[93m',
   'fail':'\033[91m',
   'end':'\033[0m',
   'bold':'\033[1m',
   'underline':'\033[4m',
   'clearLast':'\033[F\033[K'
})

def consoleClear():
   """
   Clear console outpur (linux,windows)
   """
   if sys.platform=='win32': os.system('cls')
   else: os.system('clear')

def consoleIsTerminal():
   """
   Check, is program runned in terminal or not.
   """
   return sys.stdout.isatty()

global console
console=magicDict({
   'clear':consoleClear,
   'inTerm':consoleIsTerminal,
   'color':consoleColor
})

def getms(inMS=True):
   """
   This method return curent(unix timestamp) time in millisecond or second.

   :param bool inMS: If True in millisecond, else in seconds.
   :retrun int:
   """
   if inMS: return time.time()*1000.0
   else: return int(time.time())

def reprEx(obj, indent=None, toUtf8=True, sortKeys=True):
   def _fixJSON(o):
      if isinstance(o, decimal.Decimal): return str(o) #fix Decimal conversion
      if isinstance(o, (datetime.datetime, datetime.date, datetime.time)): return o.isoformat() #fix DateTime conversion
   try:
      s=json.dumps(obj, indent=indent, separators=(',',':'), ensure_ascii=False, sort_keys=sortKeys, default=_fixJSON)
   except:
      try: s=json.dumps(obj, indent=indent, separators=(',',':'), ensure_ascii=True, sort_keys=sortKeys, default=_fixJSON)
      except Exception as e:
         print '!!! JSON dump', e
         return None
   if toUtf8:
      try: s=s.encode('utf-8')
      except: pass
   return s

def strGet(text, pref='', suf='', index=0, default='', returnOnlyStr=True):
   #return pattern by format pref+pattenr+suf
   if(text==''):
      if returnOnlyStr: return default
      else: return -1, -1, default
   text1=text.lower()
   pref=pref.lower()
   suf=suf.lower()
   if pref!='': i1=text1.find(pref,index)
   else: i1=index
   if i1==-1:
      if returnOnlyStr: return default
      else: return -1, -1, default
   if suf!='': i2=text1.find(suf,i1+len(pref))
   else: i2=len(text1)
   if i2==-1:
      if returnOnlyStr: return default
      else: return i1, -1, default
   s=text[i1+len(pref):i2]
   if returnOnlyStr: return s
   else: return i1+len(pref), i2, s


def get_documentation_of_module(module):
   source_code_of_module = inspect.getsource(module)
   documentation_of_module = strGet(source_code_of_module, '"""\n', '\n"""') or strGet(source_code_of_module, '\'\'\'\n', '\n\'\'\'') or ''
   return documentation_of_module


def oGet(o, key, default=None):
   #get val by key from object(list,dict), and default if key not exist
   try: return o[key]
   except: return default

def iterate(cb, o):
   # like map(), but with smart callback handling
   res=[]
   _args, _, _, _=inspect.getargspec(cb)
   _args=[s for s in _args if s!='self']
   for i, s in enumerate(o):
      if len(_args)==1: r=cb(s)
      elif len(_args)==2: r=cb(s, i)
      elif len(_args)==3: r=cb(s, o, i)
      res.append(r)
   return res

#========================================
import decimal
from types import InstanceType, ModuleType, ClassType, TypeType

def isFunction(o): return hasattr(o, '__call__')

def isInstance(o): return isinstance(o, (InstanceType))

def isClass(o): return isinstance(o, (type, ClassType, TypeType))

def isModule(o): return isinstance(o, (ModuleType))

def isModuleBuiltin(o): return isModule(o) and getattr(o, '__name__', '') in sys.builtin_module_names

def isTuple(o): return isinstance(o, (tuple))

def isArray(o): return isinstance(o, (list))

def isDict(o): return isinstance(o, (dict))

def isString(o): return isinstance(o, (str, unicode))

def isNum(var):
   return (var is not True) and (var is not False) and isinstance(var, (int, float, long, complex, decimal.Decimal))
#========================================
def fileGet(fName, method='r'):
   #get content from file,using $method and if file is ZIP, read file $method in this archive
   # fName=fName.encode('cp1251')
   if not os.path.isfile(fName): return None
   try:
      with open(fName, method) as f: s=f.read()
   except: return None
   return s

def fileAppend(fName, text, mode='a'):
   return fileWrite(fName, text, mode)

def fileWrite(fName, text, mode='w'):
   """ 'a' - в конец файла / 'w' - перезапись файла """
   if not isString(text): text=repr(text)
   with open(fName,mode) as f: f.write(text)

def pathList(path, fullPath=True, alsoFiles=True, alsoDirs=False):
   res=[]
   for f in os.listdir(path):
      fp=os.path.join(path, f)
      if not alsoDirs and not os.path.isfile(fp): continue
      if not alsoFiles and os.path.isfile(fp): continue
      res.append(fp if fullPath else f)
   return res

if __name__=='__main__': pass
