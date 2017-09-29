# coding: utf8
'''
-------------------------------------------------------------------------------------------------------
ANÁLISE SEMI-AUTOMÁTICA DAS FEIÇÕES ESPACIALIZADAS DO CADASTRO AMBIENTAL RURAL DO ESTADO DE SÃO PAULO
-------------------------------------------------------------------------------------------------------
Michel Metran
Assistente Técnico do Ministério Público / GAEMA PCJ-Piracicaba
Agosto de 2017

Script elaborado para organizar os shapefiles, arquivos KML e PDFs exportados pelo SiCAR, da CBRN/SMA.
A análise é feita em lote, ou seja, todos os CARs que estiverem dentro de uma dada pasta serão analisados.
O Nome das subpastas deve conter, obrigatoriamente, o número do CAR. OUTROS CARACTERES SERÃO IGNORADOS.
Exemplo: Pasta com nome de "CAR 35.458.030.247.579" se transformara em "35458030247579".
Portanto, também recomenda-se a não utilização de outros números na pasta, exceto aqueles que identificam o CAR.
Ajuste apenas a pasta aonde se encontram as subpastas com o CARs.

'''

# -------------------------------------------------------------------------------------------------------
# Módulos e Codificação
import os
import sys
import fnmatch
import zipfile
import shutil
import glob
import arcpy

reload(sys)
sys.setdefaultencoding('utf8')

# -------------------------------------------------------------------------------------------------------
# Variável de Input
Input = r'E:\SIG_MP_BasesCartograficas\SP_SiCAR\CARs Individuais'

# -------------------------------------------------------------------------------------------------------
# Variáveis de Ambiente do ArcGIS
arcpy.ResetEnvironments()
arcpy.env.overwriteOutput = True

# -------------------------------------------------------------------------------------------------------
# Lista Diretórios que estiverem na raiz abaixo
folders = os.listdir(Input)

# -------------------------------------------------------------------------------------------------------
# Loop
for folder in folders:
  print '# ' + '-' * 100
  os.chdir(os.path.join(Input, folder))
  print '## Inicio dos Trabalhos para pasta: ' + os.getcwd()

# -------------------------------------------------------------------------------------------------------
# Cria a pasta 'Dados Brutos', caso não exista.
  print '## Etapa 1: Cria a estrutura das pastas e "Geodatabase"'
  
  directorys = ['Dados Brutos', 'Geodata', 'Documentos', 'Geodata//shp', 'Geodata//kml']
  for directory in directorys:
    try:
      os.makedirs(os.path.join(Input, folder, directory))
    except OSError:
      if not os.path.isdir(os.path.join(Input, folder, directory)):
        raise  

# Cria Geodatabase  
  try:
    arcpy.CreatePersonalGDB_management(os.path.join(Input, folder, 'Geodata'), 'Geo_SiCAR.mdb')
  except:
    print 'Erro qualquer no geodatabase'
 
# -------------------------------------------------------------------------------------------------------
# Extrai e cria a variável com o número do CAR, assumindo que a pasta está com o número.
  print '## Etapa 2: Pega o Numero do CAR a partir do nome das pastas.'
  numberfolder = ''
  validLetters = '1234567890'
  for char in folder:
    if char in validLetters:
      numberfolder += char
  
  print '>> Portanto: ' + folder + ' se transformou em ' + numberfolder + '.'
  
# -------------------------------------------------------------------------------------------------------
# Renomeia PDF com a variável "Número do CAR criada anteriormente".
  print '## Etapa 3: Renomeia Extrato do CAR e move para a pasta "Documentos"'
  pdflist = os.path.join(Input, folder, '*.pdf')
  pdfpath = os.path.join(Input, folder)
    
  for file in glob.glob(pdflist):
    filename_split = os.path.splitext(file)
    filename_zero, fileext = filename_split
    print os.path.join(pdfpath + "//Extrato CAR " + numberfolder + fileext)
    os.rename(file, os.path.join(pdfpath + "//Extrato CAR " + numberfolder + fileext))

# -------------------------------------------------------------------------------------------------------
# Move o arquivo PDF (extrado do CAR) para a pasta documentos.
  pdflist = os.path.join(Input, folder, '*.pdf')
    
  for file in glob.glob(pdflist):
    shutil.move(file, os.path.join(Input, folder, 'Documentos'))
    
# -------------------------------------------------------------------------------------------------------
# Move o arquivo KML (extrado do CAR) para a pasta "KML".
  print '## Etapa 4: Move eventuais arquivos KML para a respectiva pasta'
  kmllist = os.path.join(Input, folder, "*.kml")
  
  for file in glob.glob(kmllist):
    #shutil.move(file, os.path.join(Input, folder, 'Geodata//kml'))
    shutil.move(file, os.path.join(Input, folder, 'Dados Brutos'))

# -------------------------------------------------------------------------------------------------------
# Importa KMLs: Transforma KML que vira um geodatabase
  print '## Etapa 5: Converte KML para "Feature Class"'
  kmllist = os.path.join(Input, folder, 'Dados Brutos' , "*.kml")
  kmlpath = os.path.join(Input, folder, 'Dados Brutos')
    
  for file in glob.glob(kmllist):
    try:
      arcpy.KMLToLayer_conversion(file, kmlpath)
      gdb = str.replace(file, '.kml', '.gdb') + '//Placemarks//Multipatches'
      out = os.path.join(Input, folder, 'Geodata', "Geo_SiCAR.mdb", str.replace(os.path.basename(file), '.kml', ''))
      arcpy.ddd.MultiPatchFootprint (gdb, out)
      
    except arcpy.ExecuteError:
      print arcpy.GetMessages()

# -------------------------------------------------------------------------------------------------------
# Retira todos os arquivos das pastas zipadas e move os arquivos zipados (brutos) para a pasta "Dados Brutos".
  print '## Etapa 6: Extrai todos os "Shapefiles" das pastas zipadas'
  ziplist = os.path.join(Input, folder, '*.zip')
  zippath = os.path.join(Input, folder)
  
  for file in glob.glob(ziplist):
    zipfile.ZipFile(file).extractall(zippath)
    shutil.move(file, os.path.join(Input, folder, 'Dados Brutos'))
        
# -------------------------------------------------------------------------------------------------------
# Renomeia e Move demais arquivos (shapefiles)
  print '## Etapa 7: Renomeia e move os arquivos "Shapefile"'
  otherspath = os.path.join(Input, folder)
  otherfiles = next(os.walk(otherspath))[2]
      
  for file in otherfiles:
    parte1 = file.split('_', 1)[0]
    parte2 = file.split('_', 2)[1]
    parte3 = file.split('_', 3)[2]
    filename_zero, fileext = os.path.splitext(parte3)
    print os.path.join(otherspath, parte1 + '_' + numberfolder + fileext)
    
    if parte1 == 'Nascente':
      print 'Diferenciar Nascentes de Pontos daquelas representadas por Polígons'
      newname = os.path.join(otherspath, parte1 + '_' + numberfolder + '_'  + filename_zero + fileext)
      try:
        os.rename(file, newname)
        shutil.move(newname, os.path.join(Input, folder, 'Geodata//shp'))
      except OSError:
        pass
    
    else:
      newname = os.path.join(otherspath, parte1 + '_' + numberfolder + fileext)
      try:
        os.rename(file, newname)
        shutil.move(newname, os.path.join(Input, folder, 'Geodata//shp'))
      except OSError:
        pass

# -------------------------------------------------------------------------------------------------------
# Importa Shapefiles
  print '## Etapa 8: Importa os "Shapefiles" para o "Geodatabase"'
  shplist = os.path.join(Input, folder, 'Geodata//shp' , '*.shp')
  
  for file in glob.glob(shplist):
    try:
      out_path = os.path.join(Input, folder, 'Geodata', 'Geo_SiCAR.mdb')
      arcpy.FeatureClassToGeodatabase_conversion(file, out_path)
    except arcpy.ExecuteError:
      print arcpy.GetMessages()
    
# -------------------------------------------------------------------------------------------------------
# Cálculos e Campos
  print '## Etapa 9: Edita "Campos" das tabelas de atributos dos "FeatureClass" e promove os calculos'
  workspace = os.path.join(Input, folder, 'Geodata', 'Geo_SiCAR.mdb')
  walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="All")
  
# Geral
  for dirpath, dirnames, filenames in walk:
    for filename in filenames:
      print 'Identificação em: ' + filename
      os.path.join(workspace, filename)
      filefullpath = os.path.join(workspace, filename)
      
      arcpy.AddField_management(filefullpath, 'Nome_Arquivo', 'TEXT')
      arcpy.CalculateField_management (filefullpath, 'Nome_Arquivo', "'" + filename + "'", 'PYTHON_9.3')
      
      arcpy.AddField_management(filefullpath, 'Layer', 'TEXT')
      arcpy.CalculateField_management(filefullpath, 'Layer', '!Nome_Arquivo!.split("_")[0]', 'PYTHON_9.3')
      
      arcpy.AddField_management(filefullpath, 'N_CAR', 'TEXT')
      arcpy.CalculateField_management(filefullpath, 'N_CAR', "'" + numberfolder + "'", 'PYTHON_9.3')
      
# Apenas para Polígonos
  walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="Polygon")
  
  for dirpath, dirnames, filenames in walk:
    for filename in filenames:
      print 'Área em: ' + filename
      os.path.join(workspace, filename)
      filefullpath = os.path.join(workspace, filename)

      arcpy.AddField_management(filefullpath, 'Area_ha', 'FLOAT')
      arcpy.CalculateField_management(filefullpath, 'Area_ha', '!shape.geodesicArea@hectares!', expression_type='PYTHON_9.3')

# -------------------------------------------------------------------------------------------------------
# Renomeia os "FeatureClass"
  print '## Etapa 10: Renomeia os "FeatureClass"'
  workspace = os.path.join(Input, folder, 'Geodata', 'Geo_SiCAR.mdb')
  walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="All")
  
  for dirpath, dirnames, filenames in walk:
    for filename in filenames:
      parte1 = filename.split("_", 1)[0]
      print parte1
      filefullpath = os.path.join(workspace, filename)
      
      if parte1 == 'Nascente':
        parte3 = filename.split("_", 3)[2]
        newname = os.path.join(workspace, parte1 + '_' + parte3)
        try:
          arcpy.Rename_management(filefullpath, newname)
        except OSError:
          pass
      
      else:
        newname = os.path.join(workspace, parte1)
        try:
          arcpy.Rename_management(filefullpath, newname)
        except OSError:
          pass

# -------------------------------------------------------------------------------------------------------
# Finalizando
arcpy.ResetEnvironments()
print '# ' + '-' * 100
print '# End'


# -------------------------------------------------------------------------------------------------------
# Análises Futuras

# Organizar MXD
# Exportar mapas em JPG