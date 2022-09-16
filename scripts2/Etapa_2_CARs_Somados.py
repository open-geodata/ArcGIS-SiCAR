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
Input = r'Y:\SIG_IC_09-16\Dados Brutos\CARs'
Output = r'Y:\SIG_IC_09-16'

# Tabela do CAR
ImportaTabela = 'Sim'
tab = r'Y:\SIG_IC_09-16\Tabelas\tab_CAR.xlsx\SIGAM$'

# Define os shapes que serão unidos. PARA CADA CONJUNTO DE DADOS É PRECISO DEFINIR.
shapes = ['AppsUnificadas_Polygon',
          'Nascente_Points',\
          # 'Nascente_Polygon',\
          # 'OutrasApps',\
          'OutrosCorposDAgua',\
          'Propriedade',\
          'ReservaLegal',\
          'ReservaLegalCompensacao',\
          # 'RioAcima3m',\
          'RioAte3m',\
          # 'LagoElagoaNatural',\
          'ServidaoAdministrativa',\
          # 'ServidaoAmbiental',\
          'UsoConsolidado',\
          'UsoRestrito',\
          'VegetacaoNativaRemanescente']

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
    arcpy.CreatePersonalGDB_management(
        os.path.join(Output, 'Geodata'), 'Geo_SiCAR.mdb')
    arcpy.CreateFeatureDataset_management(os.path.join(Output, 'Geodata', 'Geo_SiCAR.mdb'), 'CAR',
                                          spatial_reference="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8,98315284119522E-09;0,001;0,001;IsHighPrecision")

except:
    print 'Erro qualquer no geodatabase'

# -------------------------------------------------------------------------------------------------------
# Lista Diretórios que estiverem na raiz abaixo
print '## Etapa 2: Lista Diretórios que estiverem na raiz abaixo'
folders = os.listdir(Input)

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
    out = os.path.join(Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR')
    arcpy.Merge_management(feature_classes, os.path.join(out, shape))

# -------------------------------------------------------------------------------------------------------
# Move o arquivo PDF (extrado do CAR) para a pasta documentos.
print '## Etapa 3: Copia resumo do CAR'

for folder in folders:
    print '# ' + '-' * 100
    os.chdir(os.path.join(Input, folder))
    print '## Inicio dos Trabalhos para pasta: ' + os.getcwd()
    pdflist = os.path.join(Input, folder, 'Documentos', '*.pdf')

    for file in glob.glob(pdflist):
        shutil.copy2(file, os.path.join(Output, 'Documentos'))

# -------------------------------------------------------------------------------------------------------
# Join na Tabela
arcpy.AddField_management(os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade'), 'N_CAR_Join', 'DOUBLE')
arcpy.CalculateField_management(os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade'), 'N_CAR_Join', '[N_CAR]*1', 'VB', code_block='')
arcpy.MakeFeatureLayer_management(os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade'), 'Propriedade_Layer')

arcpy.TableToTable_conversion(tab, os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb'), 'tab_CAR')
arcpy.MakeTableView_management(os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'tab_CAR'), 'tab_CAR_Layer')

arcpy.AddJoin_management('Propriedade_Layer', 'N_CAR_Join',
                         'tab_CAR_Layer', 'N_CAR', 'KEEP_ALL')
arcpy.CopyFeatures_management('Propriedade_Layer', os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade_Join'))
arcpy.Delete_management(os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade'), 'FeatureClass')
arcpy.Rename_management(os.path.join(Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade_Join'), os.path.join(
    Output, 'Geodata', 'Geo_SiCAR.mdb', 'CAR', 'Propriedade'), 'FeatureClass')

# -------------------------------------------------------------------------------------------------------
# Finalizando
arcpy.ResetEnvironments()
print '# ' + '-' * 100
print '# End'
