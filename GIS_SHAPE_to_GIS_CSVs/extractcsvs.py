import os
from mmqgis import *
Folder_path = r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\FeedersShapeFiles\TOWN"
list_of_files = os.listdir(Folder_path)
Output_Folder = r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\FeedersExtractedCSVsFromShapeFiles\TOWN"
for file in list_of_files:
    if file.endswith('.shp'):
        flag = 0
        file_path = os.path.join(Folder_path,file)
        layer = QgsVectorLayer(file_path,'',"ogr")
        feat = layer.getFeature(0)
        geom = feat.geometry()
        geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
        if geom.type() == QgsWkbTypes.PointGeometry:
            if geomSingleType:
                fieldname = [field.name() for field in layer.fields()]
                if 'x' not in fieldname:
                    pr = layer.dataProvider()
                    pr.addAttributes([QgsField("x",QVariant.Double),QgsField("y",QVariant.Double)])
                    layer.updateFields()
                feats = layer.getFeatures()
                fieldname = [field.name() for field in layer.fields()]
                for feat in feats:
                    geom = feat.geometry()
                    x1 = geom.asPoint()
                    x,y = x1.x(),x1.y()
                    layer.startEditing()
                    layer.changeAttributeValue(feat.id(),fieldname.index('x'),x)
                    layer.changeAttributeValue(feat.id(),fieldname.index('y'),y)
                    layer.commitChanges()
                QgsVectorFileWriter.writeAsVectorFormat(layer, os.path.join(Output_Folder,os.path.splitext(file)[0]+'.csv'), "utf-8", driverName='CSV')

        if geom.type() == QgsWkbTypes.LineGeometry:
            message = mmqgis_library.mmqgis_geometry_export_to_csv(layer, os.path.join(Output_Folder,os.path.splitext(file)[0]+'_node.csv'), os.path.join(Output_Folder,os.path.splitext(file)[0]+'_attribute.csv'), ",", "\n")

        