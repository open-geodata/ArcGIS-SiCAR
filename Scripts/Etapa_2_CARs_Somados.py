# coding: utf8
'''
-------------------------------------------------------------------------------------------------------
ANÁLISE SEMI-AUTOMÁTICA DAS FEIÇÕES ESPACIALIZADAS DO CADASTRO AMBIENTAL RURAL DO ESTADO DE SÃO PAULO
-------------------------------------------------------------------------------------------------------
Michel Metran
Assistente Técnico do Ministério Público / GAEMA PCJ-Piracicaba
Setembro de 2017

Script elaborado para unir os CARs individuais em um só geodatabase.

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
Output = r'E:\SIG_MP_BasesCartograficas\SP_SiCAR'

# -------------------------------------------------------------------------------------------------------
# Variáveis de Ambiente do ArcGIS
arcpy.ResetEnvironments()
arcpy.env.overwriteOutput = True

# -------------------------------------------------------------------------------------------------------
# Cria a pasta 'Dados Brutos', caso não exista.
print '## Etapa 1: Cria a estrutura das pastas e "Geodatabase"'

directorys = ['Geodata', 'Documentos']
for directory in directorys:
    try:
        os.makedirs(os.path.join(Output, directory))
    except OSError:
        if not os.path.isdir(os.path.join(Output, directory)):
            raise

try:
    arcpy.CreatePersonalGDB_management(os.path.join(Output, 'Geodata'), 'Geo_SiCAR.mdb')
except:
    print 'Erro qualquer no geodatabase'

# -------------------------------------------------------------------------------------------------------
# Lista Diretórios que estiverem na raiz abaixo
print '## Etapa 2: Lista Diretórios que estiverem na raiz abaixo'
folders = os.listdir(Input)

# -------------------------------------------------------------------------------------------------------
# Lista Diretórios que estiverem na raiz abaixo
print '## Etapa 3: Cria um array com os shapes a serem unidos'

shapes = ['AppsUnificadas',\
          'Nascente_Points',\
          'Nascente_Polygon',\
          'OutrasApps',\
          'OutrosCorposDAgua',\
          'Propriedade',\
          'ReservaLegal',\
          'ReservaLegalCompensacao',\
          'RioAte3m',\
          'ServidaoAdministrativa',\
          'UsoConsolidado',\
          'VegetacaoNativaRemanescente']

# -------------------------------------------------------------------------------------------------------
# Loop
print '## Etapa 4: Merge shapes'

for shape in shapes:
    # Limpa a lista
    feature_classes = []

    # Loop pelas Pastas
    for folder in folders:
        print '# ' + '-' * 100
        os.chdir(os.path.join(Input, folder))
        print '## Inicio dos Trabalhos para pasta: ' + os.getcwd()
    
        workspace = os.path.join(Input, folder, 'Geodata', 'Geo_SiCAR.mdb')
        walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="All")
            
        # Loop pelos geodatabases
        for dirpath, dirnames, filenames in walk:
                
            # Loop pelos nomes
            for filename in filenames:
                desc = arcpy.Describe(os.path.join(dirpath, filename))
                print filename
                if desc.name == shape:
                    feature_classes.append(os.path.join(dirpath, filename))
                    print feature_classes
    
    print '## Merge das "' + shape + '" realizado.'
    out = os.path.join(Output, 'Geodata', 'Geo_SiCAR.mdb')
    arcpy.Merge_management(feature_classes, os.path.join(out, shape))

# -------------------------------------------------------------------------------------------------------
# Move o arquivo PDF (extrado do CAR) para a pasta documentos.
print '## Etapa 5: Copia resumo do CAR'

for folder in folders:
    print '# ' + '-' * 100
    os.chdir(os.path.join(Input, folder))
    print '## Inicio dos Trabalhos para pasta: ' + os.getcwd()
    pdflist = os.path.join(Input, folder, 'Documentos', '*.pdf')

    for file in glob.glob(pdflist):
        shutil.copy2(file, os.path.join(Output, 'Documentos'))

# -------------------------------------------------------------------------------------------------------
# Finalizando
arcpy.ResetEnvironments()
print '# ' + '-' * 100
print '# End'
