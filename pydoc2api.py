# -*- coding: utf-8 -*-
import sys, inspect
from string import strip
from utils import *

class pydoc2api(object):
   def __init__(self, module, obj=None):
      obj=obj or ''
      self.modulePath=''
      if isString(module):
         if '.' in module:
            obj=obj or strGet(module, '.')
            module=strGet(module, '', '.')
         self.modulePath=module
         module=__import__(module)
         # import imp
         # module=imp.load_source('', module)
      parts=obj.split('.')
      if not parts[0]: parts=parts[1:]
      self.objectPath='.'.join(parts)
      if len(parts):
         for k in parts:
            if isClass(module): module=module.__dict__[k]
            else: module=getattr(module, k)
      self.obj=module

   def docSplit(self, doc):
      lines=strip(doc).split('\n\n')
      if (len(lines)==1 and len(lines[0]) and lines[0][0]!=':') or (len(lines)==2 and not strip(lines[1])):
          return strip(lines[0]), []
      elif len(lines)>=2 and lines[0][0]!=':':
          return strip(lines[0]), '\n\n'.join(lines[1:]).split('\n')
      return '', lines[0].split('\n')

   def objType(self, obj):
      return strGet(str(type(obj)), "'", "'")

   def parseParam(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower().lstrip().startswith(':param'):
         # параметр
         ss=strip(strGet(s, ':param', ':') or '')
         ss=ss.split(' ')
         if len(ss)==1:
            s1=ss[0]
            s2=''
         else:
            s1=ss[1]
            s2=ss[0]
         s3=strip(strGet(s, ': ', '') or '')
         res={'name':s1, 'type':s2, 'descr':s3}
      if isFunction(cb): res=cb(res)
      return res

   def parseReturn(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower().startswith(':return'):
         # возвращаемое значение
         s1=strip(strGet(s, ':return', ':') or '')
         s2=strip(strGet(s, ': ', '') or '')
         res={'type':s1, 'descr':s2}
      if isFunction(cb): res=cb(res)
      return res

   def parseExample(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower()==':example:':
         # примеры
         s1=[]
         started=False
         for ss in data[index+1:]:
            if not ss and started: break
            elif not ss: started=True
            else: s1.append(ss)
         res='\n'.join(s1)
      if isFunction(cb): res=cb(res)
      return res

   def parseAttention(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower()==':attention:':
         # примеры
         s1=[]
         started=False
         for ss in data[index+1:]:
            if not ss and started: break
            elif not ss: started=True
            else: s1.append(ss)
         res='\n'.join(s1)
      if isFunction(cb): res=cb(res)
      return res

   def parseAuthor(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower().startswith(':authors:'):
         res=strip(strGet(s, ':authors:', '')).split(', ')
      elif s.lower().startswith(':author:'):
         res=[strip(strGet(s, ':author:', ''))]
      if isFunction(cb): res=cb(res)
      return res

   def parseCopyright(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower().startswith(':copyright:'):
         res=strip(strGet(s, ':copyright:', ''))
      if isFunction(cb): res=cb(res)
      return res

   def parseLicense(self, data, index, cb=None):
      res=False
      s=data[index]
      if s.lower().startswith(':license:'):
         res=strip(strGet(s, ':license:', ''))
      if isFunction(cb): res=cb(res)
      return res

   def objInfo(self, obj):
      res={
         'name':obj.__name__,
         'data':'',
         # 'source':inspect.getsource(obj),
         'type':self.objType(obj),
         'descr':'',
         'params':[],
         'example':[],
         'return':'',
         'docstr':'',
         'authors':[],
         'copyright':'',
         'attention':[],
         'license':'',
         'ver_major':getattr(obj, '__ver_major__', 0),
         'ver_minor':getattr(obj, '__ver_minor__', 0),
         'ver_patch':getattr(obj, '__ver_patch__', 0),
         'ver_sub':getattr(obj, '__ver_sub__', ''),
         'version':getattr(obj, '__version__', ''),
         '_obj':obj,
         'module':getattr(obj, '__module__', ''),
         'inherit':[]
      }
      if hasattr(obj, '__author__'):
         res['authors'].append(getattr(obj, '__author__'))
      # определяем от кого унаследовано
      if hasattr(obj, '__bases__'):
         res['inherit']=[str(s) for s in obj.__bases__]
      # извлекаем общий комментарий
      if isModule(obj):
         docstr=strGet(inspect.getsource(obj), '"""\n', '\n"""') or ''
      else:
         docstr=inspect.getdoc(obj) or inspect.getcomments(obj) or ''
      res['docstr']=docstr
      # формируем строку инициализации
      if isModule(obj): f=obj.__name__
      elif isClass(obj):
         f=getattr(obj, '__dict__', {}).get('__init__', None)
      else: f=obj
      if isFunction(f):
         try: inspect.getargspec(f)
         except: f=None
      if isFunction(f):  #! and not inspect.isroutine(f):
         _args, _varargs, _varkwargs, _def=inspect.getargspec(f)
         tArr=[]
         ii=len(_args)-len(_def) if(_def is not None and _args is not None) else 0
         for i, s in enumerate(_args):
            if _def is not None and i>=ii:
               tArr.append('%s=%s'%(s, '"'+_def[i-ii]+'"' if isString(_def[i-ii]) else _def[i-ii]))
            else: tArr.append(s)
         if _varargs is not None: tArr.append('*'+_varargs)
         if _varkwargs is not None: tArr.append('**'+_varkwargs)
         res['data']='%s(%s)'%(obj.__name__, ', '.join(tArr))
      else:
         res['data']=f if isString(f) else obj.__name__+'()'
      # извлекаем описание обьекта
      descr, other=self.docSplit(docstr)
      res['descr']=descr
      # извлекаем различные части описания обьекта
      for i, s in enumerate(other):
         if self.parseParam(other, i,
            cb=lambda ss: False if ss is False else (res['params'].append(ss) or True)): pass
         elif self.parseReturn(other, i,
            cb=lambda ss: False if ss is False else (res.__setitem__('return', ss) or True)): pass
         elif self.parseExample(other, i,
            cb=lambda ss: False if ss is False else (res['example'].append(ss) or True)): pass
         elif self.parseAttention(other, i,
            cb=lambda ss: False if ss is False else (res['attention'].append(ss) or True)): pass
         elif self.parseAuthor(other, i,
            cb=lambda ss: False if ss is False else (res.__setitem__('authors', res['authors']+ss) or True)): pass
         elif self.parseCopyright(other, i,
            cb=lambda ss: False if ss is False else (res.__setitem__('copyright', ss) or True)): pass
         elif self.parseLicense(other, i,
            cb=lambda ss: False if ss is False else (res.__setitem__('license', ss) or True)): pass
      # если не задано возвращаемое значение для класса, указываем
      if not res['return'] and isClass(obj):
         res['return']={'type':'instance', 'descr':'Instance of class '+obj.__name__}
      return dict2magic(res, True)

   def methodType(self, obj):
      if obj.__name__.startswith('__'): return 'special'
      if obj.__name__.startswith('_'): return 'private'
      return 'public'

   def summary(self, obj=None, moduleWhitelist=None, moduleBlacklist=['__builtin__', None], moduleWhitelistCB=None, moduleBlacklistCB=None):
      obj=obj or self.obj
      res=self.objInfo(obj)
      if not isClass(obj) and not isModule(obj): return res
      # глубокая проверка доступна только для модулей и классов
      res['tree']={
         'classes':{},
         'methods':{
            'public':{},
            'private':{},
            'special':{},
            'undoc':{},
            'publicOrder':[],
            'privateOrder':[],
            'specialOrder':[],
            'undocOrder':[]
         },
         'modules':{},
         # 'vars':{}
      }
      # ищем и обрабатываем дочерние модули
      mCache=[]
      for k, v in inspect.getmembers(obj):
         if isModule(v):
            if v.__name__ in mCache: continue
            if isModuleBuiltin(v) or v==obj: continue
            if isModule(obj) and obj.__name__+'.__init__'==v.__name__: continue
            mCache.append(v.__name__)
            m=v.__name__
         else:
            m=getattr(v, '__module__', None)
            if m in mCache: continue
         # проверка, принадлежит ли данный обьект указанным модулям
         if 'self' in moduleWhitelist and isModule(obj) and m==obj.__name__: pass
         elif 'self' in moduleWhitelist and not isModule(obj) and m==obj.__module__: pass
         else:
            if m is None: m=[None]
            elif '.' in m:
               tArr=m.split('.')
               m=[m]+['.'.join(tArr[:i+1])+'.' for i in xrange(len(tArr)-1)]
            else: m=[m]
            if moduleWhitelist and 'self.' in moduleWhitelist and obj.__name__+'.' in m: pass
            elif moduleWhitelist and not(set(m) & set(moduleWhitelist)): continue
            elif not moduleWhitelist:
               if moduleBlacklist and (set(m) & set(moduleBlacklist)): continue
         # дополнительная проверка через коллбек
         if isFunction(moduleWhitelistCB) and not moduleWhitelistCB(obj, k, v, m): continue
         elif isDict(moduleWhitelistCB) and isModule(obj) and obj.__name__ in moduleWhitelistCB:
            if not moduleWhitelistCB[obj.__name__](obj, k, v, m): continue
         # обрабатываем обьект
         if isClass(v):
            res['tree']['classes'][k]=self.summary(v, moduleWhitelist=moduleWhitelist, moduleBlacklist=moduleBlacklist, moduleWhitelistCB=moduleWhitelistCB, moduleBlacklistCB=moduleBlacklistCB)
         elif isFunction(v):
            s=self.objInfo(v)
            t=self.methodType(v)
            if t=='public' and not s.docstr: t='undoc'
            res['tree']['methods'][t][k]=s
            res['tree']['methods'][t+'Order'].append(k)  #! нужно брать порядок из исходника
         elif isModule(v):
            print v.__name__
            res['tree']['modules'][v.__name__]=self.summary(v, moduleWhitelist=moduleWhitelist, moduleBlacklist=moduleBlacklist, moduleWhitelistCB=moduleWhitelistCB, moduleBlacklistCB=moduleBlacklistCB)
         # else:
            # #! не забыть добавить None в moduleWhitelist
            # if k in ['__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__']: continue
            # if isModule(obj):
            #    print '~', obj.__name__, k
            # res['tree']['vars'][k]=getattr(v, '__module__', None) #inspect.getmodule(v)
      return dict2magic(res, True)

if __name__=='__main__': pass
