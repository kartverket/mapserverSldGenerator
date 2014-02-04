#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Script for mapserver generating SLD including complete filters based on mapfile.
Prints result to commandline.
Jarle Johan Pedersen, Norwegian Mapping Authorities 2013

Still buggy. Please check/validate the results.
'''
import mapscript
import sys
import tempfile
from pyparsing import nestedExpr
import os

# sld-library should probably be used at a later point
#import sld

# Static lists
#  SQL not equal
neList=['!=','ne']
#  SQL less than
ltList=['<','lt']
#  SQL greater than
gtList=['>','gt']
#  SQL less than or equal
leList=['<=','le']
#  SQL greater than or equal
geList=['>=','ge']

# Global variables. Need to be removed.
service=''
greyscale=False
filePerLayer=False
outputDir=''
#outputFile=''

def grayscaler(line):
 colorIndex=line.find('#')
 red_v=line[colorIndex+1:colorIndex+3]
 blue_v=line[colorIndex+3:colorIndex+5]
 green_v=line[colorIndex+5:colorIndex+7]
 red_m=0.299
 green_m=0.587
 blue_m=0.114
 grey=''
 grey=str(hex(int(int(red_v,16)*red_m+int(green_v,16)*green_m+int(blue_v,16)*blue_m))).replace('0x','')
 if len(grey)<2:
  grey='0'+grey
 outputFile.write(line.replace('#'+red_v+blue_v+green_v,'#'+grey+grey+grey))

def nestLoopCol(nList,ll):
 '''Secondary loop-handler'''
 try:
  for n in nList:
   nestLoop(n,ll)
 except Exception, e:
  print e
  pass

def nestLoop(nList, ll):
 '''
Main loop for translating SQL to FES
 '''
 if isinstance(nList,str):
  return
 else:
  if len(nList)>1:
   if str(nList[1]) in ['and','or']:
    ll+=1
    tmpAndor='And'
    if str(nList[1])=='or':
     tmpAndor='Or'
    outputFile.write(tabberAndor(ll) + '<ogc:' + tmpAndor + '>\n')
    nestLoopCol(nList,ll)
    outputFile.write(tabberAndor(ll) + '</ogc:' + tmpAndor + '>\n')
    del nList[1]
   else:
    if len(nList)>1:
     tmpOperator='PropertyIsEqualTo'
     if (nList[1] in neList):
      tmpOperator='PropertyIsNotEqualTo'
     elif (nList[1] in gtList):
      tmpOperator='PropertyIsGreaterThan'
     elif (nList[1] in ltList):
      tmpOperator='PropertyIsLessThan'
     elif (nList[1] in geList):
      tmpOperator='PropertyIsGreaterThanOrEqualTo'
     elif (nList[1] in leList):
      tmpOperator='PropertyIsLessThanOrEqualTo'
     outputFile.write(tabber(ll+1) + '<ogc:' + tmpOperator + '>\n')
     for n in range(0,3):
      if n == 0:
       outputFile.write(tabber(ll+2) + '<ogc:PropertyName>' + str(nList[n]).replace('"','').replace("'","") + '</ogc:PropertyName>\n')
      elif n == 2:
       try:
        outputFile.write(tabber(ll+2) + '<ogc:Literal>' + str(nList[n]).replace("'","").replace('"','') + '</ogc:Literal>\n')
       except:
        outputFile.write(tabber(ll+2) + '<ogc:Literal></ogc:Literal>\n')
     outputFile.write(tabber(ll+1) + '</ogc:' + tmpOperator + '>\n')

  else: 
   nestLoopCol(nList,ll)

def tabberAndor(counter):
 '''Handles tabulation of and/or'''
 tmpTab=""
 while counter>=0:
  tmpTab+=' '
  counter-=1
 tmpTab+=''
 return tmpTab

def tabber(counter):
 '''Handles general tabulation'''
 tmpTab=""
 while counter>=0:
  tmpTab+=' '
  counter-=1
 tmpTab+=' '
 return tmpTab

def parenthesis(string):
 '''
Refactors the SQL and inserts missing parenthesis
Starts nestLoop
 '''
 string=string.replace(' and ', ') and (')
 string=string.replace('&&', ') and (')
 string=string.replace(' AND ', ') and (')
 string=string.replace(' or ', ') or (')
 string=string.replace('||', ') or (')
 string=string.replace(' OR ', ') or (')
 string=string.replace('[', '')
 string=string.replace(']', '')
 string='('+string+')'
 mathExpr=nestedExpr() 
 loopLevel=0
# if debug=='True':
#  print string
 outputFile.write('<ogc:Filter>\n')
 nestLoop(mathExpr.parseString(string),0)
 outputFile.write('</ogc:Filter>\n')

def cfe(c,f,e):
 '''Initiates parsing when classification is a combination of Classitem, Filter and Expression'''
 if '[' not in e:
  parenthesis('(('+ f.replace('"','') +') AND (' + c + ' = ' + e + '))')
 else:
  fe(f,e)

def ce(c,e):
 '''Initiates parsing when classification is a combination of Classitem and Expression'''
 if '[' not in e:
  if e[0]=='/':
   tmpString="("
   for value in e.split('|'):
    tmpString=tmpString+ '(' + c + ' = ' + value.replace('/','') + ') OR '
   tmpString=tmpString.rstrip(' OR ') + ')'
   parenthesis(tmpString)
  else:
   parenthesis('(' + c + ' = ' + e + ')')
 else:
  expression(e)

def fe(f,e):
 '''Initiates parsing when classification is a combination of Filter and Expresssion'''
 parenthesis('((' + f.replace('"','') + ') AND (' + e + '))')

def f(f):
 '''Initiates parsing when classification is only Filter'''
 parenthesis('(' + f.replace('"','') + ')')

def expression(e):
 '''Initiates parsing when classification is only Expression'''
 parenthesis('(('+e+'))')


def layerWriter(layer, layerNr):
 '''Writes and opens initial SLD as generated from mapserver'''

 layerClassItem=''
 filterString=''
 layerClassNr=0

 if layer.getFilterString() is not None:
  filterString=layer.getFilterString()
 if layer.classitem is not None:
  layerClassItem=layer.classitem


 tmpSldFile=tempfile.NamedTemporaryFile() 
 tmpSldFile.write(layer.generateSLD())
 sldFile=open(tmpSldFile.name)
 tmpSldFile.close()
 ruleBool=False

 
 for tmpKlasse in range(0,layer.numclasses):
  layerClass=layer.getClass(layerClassNr)
  if layerClass is None:
   return
  # Comment out this to get more layers. Might look ugly.
  elif layerClass.numstyles == 0:
   return
  
 for line in sldFile:
  layerClass=layer.getClass(layerClassNr)
  if (line.startswith('<ogc:Filter')):
   layerClassWriter(layer, filterString, layerClassItem, layerClassNr)
   layerClassNr+=1
   continue
  elif (layerNr > 0) & (line.startswith('<StyledLayerDescriptor')) & (filePerLayer==False):
   continue
  elif line.startswith('</StyledLayerDescriptor') & (filePerLayer==False):
   continue
  elif greyscale and line.startswith('<CssParameter'):
   if ('-width' in line) or ('-dasharray' in line):
    outputFile.write(line)
    continue
   else:
    grayscaler(line)
  else:
   outputFile.write(line)

def layerClassWriter(layer, filterString, layerClassItem, layerClassNr):
 '''Selects the method needed for writing the class based on the classifications'''
 layerClass=layer.getClass(layerClassNr)
 if layerClass is None:
  return
 if layerClassItem is not '':
  if filterString is not '':
   cfe(layerClassItem, filterString,layerClass.getExpressionString())
  else:
   try:
    ce(layerClassItem,layerClass.getExpressionString())
   except:
    pass
 elif filterString is not '':
  if layerClass.getExpressionString() is not None:
   fe(filterString,layerClass.getExpressionString())
  else:
   f(filterString)
 else:
  if layerClass.getExpressionString() is not None:
   try:
    expression(layerClass.getExpressionString())
   except Exception, ex:
    print ex
    pass
  else:
   return
# return

def loadMap(mapfile):
 '''Loads mapfile'''
 try:
  map=mapscript.mapObj(mapfile)
  return map
 except Exception, e:
  print(e)
  sys.exit()


def run(mapfile):
 '''Initiates SLD-generation per layer'''
 global outputFile
 map=loadMap(mapfile)
 serviceName=map.name
 nl=''
 dbtype='postgis'
 for layerNr in range(0,map.numlayers):
  layer=map.getLayer(layerNr) 
#  if layer.type==4:
#   continue
  if filePerLayer:
   print 'Setting outputfile to ' + layer.name + '.sld'
   outputFile=open(outputDir + '/' + layer.name + '.sld','w')
   layerWriter(layer, layerNr)
   outputFile.close()
  else:
#   outputFile=open( outputFile,'a')
   layerWriter(layer, layerNr)
 if not filePerLayer:
  outputFile.write('</StyledLayerDescriptor>')

# Fetching mapfile from commandline
if len(sys.argv) > 1:
# print(len(sys.argv))
 mapfile=sys.argv[1]
 if mapfile is not None:
  if '-g' in sys.argv:
   greyscale=True
  if '-f' in sys.argv:
   outputFile=open(sys.argv[sys.argv.index('-f')+1],'w')
   run(mapfile)
   outputFile.close()
  elif '-fpl' in sys.argv:
   filePerLayer=True
   outputDir=sys.argv[sys.argv.index('-fpl')+1]
   if not os.path.exists(outputDir):
    os.makedirs(outputDir)
   run(mapfile)
