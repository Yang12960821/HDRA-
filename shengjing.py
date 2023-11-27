import sys
import os
import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
from itertools import chain
import math
from numpy import array
# from rasterstats import zonal_stats

#import proplot as plot
#import matplotlib.pyplot as plt
from osgeo import ogr,gdal,osr
#import matplotlib.cm as cm
#import matplotlib.colors as mcolors
#import xarray as xr
#from matplotlib import rcParams
# from cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter
# from matplotlib.pyplot import MultipleLocator
# import matplotlib as mpl
# import matplotlib.animation as animation
# import matplotlib.patches as mpatches
# from matplotlib import gridspec
#from mpl_toolkits.basemap import Basemap

from osgeo.gdalconst import GA_ReadOnly
from pyproj import Proj


#natcap.invest包时用于计算退化度的
import natcap.invest.habitat_quality
import natcap.invest.utils

#第一步：计算退化度、生境压力分数
# 分区统计相关计算
def boundingBoxToOffsets(bbox, geot):
    col1 = int(round((bbox[0] - geot[0]) / geot[1]))
    col2 = int(round((bbox[1] - geot[0]) / geot[1]))
    row1 = int(round((bbox[3] - geot[3]) / geot[5]))
    row2 = int(round((bbox[2] - geot[3]) / geot[5]))
    return [row1, row2, col1, col2]

def geotFromOffsets(row_offset, col_offset, geot):
    new_geot = [
    geot[0] + (col_offset * geot[1]),
    geot[1],
    0.0,
    geot[3] + (row_offset * geot[5]),
    0.0,
    geot[5]
    ]
    return new_geot

def setFeatureStats(fid, min, max, mean, median, sd, sum, count, names=["min", "max", "mean", "median", "sd", "sum", "count", "id"]):
    featstats = {
    names[0]: min,
    names[1]: max,
    names[2]: mean,
    names[3]: median,
    names[4]: sd,
    names[5]: sum,
    names[6]: count,
    names[7]: fid,
    }
    return featstats


# def zonal(fn_raster, fn_zones, fn_csv):
def zonal(fn_raster, fn_zones):
    mem_driver = ogr.GetDriverByName("Memory")
    mem_driver_gdal = gdal.GetDriverByName("MEM")
    shp_name = "deg"

    #     fn_raster = r"D:\Wangfan_File\QNNR\QLM_SUB\deg_sum_c1.tif"
    #     fn_zones = r"D:\Wangfan_File\QNNR\QLM_SUB\Export_Output.shp"

    r_ds = gdal.Open(fn_raster)
    p_ds = ogr.Open(fn_zones)

    lyr = p_ds.GetLayer()
    geot = r_ds.GetGeoTransform()
    nodata = r_ds.GetRasterBand(1).GetNoDataValue()

    zstats = []

    p_feat = lyr.GetNextFeature()
    niter = 0

    while p_feat:
        if p_feat.GetGeometryRef() is not None:
            if os.path.exists(shp_name):
                mem_driver.DeleteDataSource(shp_name)
            tp_ds = mem_driver.CreateDataSource(shp_name)
            tp_lyr = tp_ds.CreateLayer('polygons', None, ogr.wkbPolygon)
            tp_lyr.CreateFeature(p_feat.Clone())
            offsets = boundingBoxToOffsets(p_feat.GetGeometryRef().GetEnvelope(), \
                                           geot)
            new_geot = geotFromOffsets(offsets[0], offsets[2], geot)

            tr_ds = mem_driver_gdal.Create( \
                "", \
                offsets[3] - offsets[2], \
                offsets[1] - offsets[0], \
                1, \
                gdal.GDT_Byte)

            tr_ds.SetGeoTransform(new_geot)
            gdal.RasterizeLayer(tr_ds, [1], tp_lyr, burn_values=[1])
            tr_array = tr_ds.ReadAsArray()

            r_array = r_ds.GetRasterBand(1).ReadAsArray( \
                offsets[2], \
                offsets[0], \
                offsets[3] - offsets[2], \
                offsets[1] - offsets[0])
            #             print(r_array)
            # 删除小于0的值
            #             r_array[r_array==nodata] = np.nan
            r_array[r_array < 0.0] = np.nan

            id = p_feat.GetFID()

            if r_array is not None:
                maskarray = np.ma.MaskedArray( \
                    r_array, \
                    mask=np.logical_or(r_array == nodata, np.logical_not(tr_array)))

                if maskarray is not None:
                    zstats.append(setFeatureStats( \
                        id, \
                        np.nanmin(maskarray), \
                        np.nanmax(maskarray), \
                        np.nanmean(maskarray), \
                        np.ma.median(maskarray), \
                        maskarray.std(), \
                        np.nansum(maskarray), \
                        maskarray.count()))
                else:
                    zstats.append(setFeatureStats( \
                        id, \
                        nodata, \
                        nodata, \
                        nodata, \
                        nodata, \
                        nodata, \
                        nodata, \
                        nodata))
            else:
                zstats.append(setFeatureStats( \
                    id, \
                    nodata, \
                    nodata, \
                    nodata, \
                    nodata, \
                    nodata, \
                    nodata, \
                    nodata))

            tp_ds = None
            tp_lyr = None
            tr_ds = None

            p_feat = lyr.GetNextFeature()

    col_names = zstats[0].keys()
    #     with open(fn_csv, 'w', newline='') as csvfile:
    #         writer = csv.DictWriter(csvfile, col_names)
    #         writer.writeheader()
    #         writer.writerows(zstats)
    return DataFrame(zstats)["mean"]


def shp_field_value(csv_file, shp):
    data = pd.DataFrame(pd.read_csv(csv_file))
    driver = ogr.GetDriverByName('ESRI Shapefile')
    layer_source = driver.Open(shp, 1)
    lyr = layer_source.GetLayer()

    s_name = ogr.FieldDefn('min', ogr.OFTReal)
    lyr.CreateField(s_name)
    s_name = ogr.FieldDefn('max', ogr.OFTReal)
    lyr.CreateField(s_name)
    s_name = ogr.FieldDefn('mean', ogr.OFTReal)
    lyr.CreateField(s_name)
    s_name = ogr.FieldDefn('median', ogr.OFTReal)
    lyr.CreateField(s_name)
    s_name = ogr.FieldDefn('sd', ogr.OFTReal)
    lyr.CreateField(s_name)
    s_name = ogr.FieldDefn('sum', ogr.OFTReal)
    lyr.CreateField(s_name)
    s_name = ogr.FieldDefn('count', ogr.OFTReal)
    lyr.CreateField(s_name)

    count = 0
    defn = lyr.GetLayerDefn()
    featureCount = defn.GetFieldCount()
    feature = lyr.GetNextFeature()
    while feature is not None:
        for i in range(featureCount):
            feature.SetField('min', data['min'][count])
            feature.SetField('max', data['max'][count])
            feature.SetField('mean', data['mean'][count])
            feature.SetField('median', data['median'][count])
            feature.SetField('sd', data['sd'][count])
            feature.SetField('sum', data['sum'][count])
            feature.SetField('count', data['count'][count])
            lyr.SetFeature(feature)
        count += 1
        feature = lyr.GetNextFeature()


# 退化度计算
def deg(inputdir, deg_outputdir):
    os.mkdir(deg_outputdir + 'HQ_result')
    lulc_dir = inputdir + "/" + "Lulc_Folder"
    file_list = os.listdir(lulc_dir)
    for i in file_list:
        if os.path.splitext(i)[1] == '.tif':
            args = {
                'half_saturation_constant': '0.5',
                'lulc_cur_path': lulc_dir + "/" + i,
                'results_suffix': '',
                'sensitivity_table_path': inputdir + "/Threat_Sensitivity.csv",
                'threats_table_path': inputdir + "/Threat Folder/Threat_factors.csv",
                'workspace_dir': deg_outputdir + 'HQ_result' + "/" + i,
            }
            natcap.invest.habitat_quality.execute(args)


# 退化度分区统计到HRU/SHP上
# def Habitat_Pressure(inputdir,deg_outputdir,input_vector,fn_csv):
def Habitat_Pressure(inputdir, deg_outputdir, input_vector):
    #     deg(inputdir,deg_outputdir)
    pressure_score = pd.DataFrame()
    deg_sum_dir = deg_outputdir + 'HQ_result'
    for i in os.listdir(deg_sum_dir):
        deg_raster = deg_sum_dir + "/" + i + "/" + "deg_sum_c.tif"
        fn_zones = input_vector
        fn_raster = deg_raster
        pressure = zonal(fn_raster, fn_zones)
        deg_rank = pressure.describe()
        bins = [1, 2, 3, 4]
        rank = deg_rank[3:].tolist()
        #         rank.insert(0,0)
        pressure_score[i] = pd.cut(pressure, rank, labels=bins)
    print("pressure_score calculating successful")
    return pressure_score


# 第二步：生境影响分数计算
# 根据基准期进行指标等级划分
def index_rank_0(df_base, df_pre, index_chara):
    #     df_base = base
    #     df_pre = pre
    #     index_chara = index
    # 计算基准期的
    df_base['base_Mean'] = df_base.apply(lambda x: x.mean(), axis=1)
    df_base['base_std'] = df_base.iloc[:, :-1].apply(lambda x: x.std(), axis=1)
    # 根据基准期判定未来的变化程度
    # 若为正向指标
    if index_chara == 0:
        for i in range(df_pre.shape[1]):
            df_pre.iloc[:, i] = (df_pre.iloc[:, i] - df_base['base_Mean']) / df_base['base_std']
        df_a = list(chain.from_iterable(df_pre.values))  # 二维转一维
        df_num = list(filter(lambda x: x <= 0, df_a))  # 去除大于0的值
        df_rank = pd.DataFrame(df_num).describe()  # 统计相关值
    # 若为负向指标时
    if index_chara == 1:
        for i in range(df_pre.shape[1]):
            df_pre.iloc[:, i] = (df_pre.iloc[:, i] - df_base['base_Mean']) / df_base['base_std']
        df_a = list(chain.from_iterable(df_pre.values))  # 二维转一维
        df_num = pd.DataFrame(list(filter(lambda x: x >= 0, df_a)))
        df_num = df_num[~df_num.isin([np.nan, np.inf, -np.inf]).any(1)].dropna()
        df_rank = pd.DataFrame(df_num).describe()
    return df_rank


# 熵权法计算指标权重
def cal_weight(x):
    '''熵值法计算变量的权重'''
    # 标准化
    x = x.apply(lambda x: ((x - np.min(x)) / (np.max(x) - np.min(x))))
    # 求k
    rows = x.index.size  # 行
    cols = x.columns.size  # 列
    k = 1.0 / math.log(rows)
    lnf = [[None] * cols for i in range(rows)]
    # 矩阵计算--
    # 信息熵
    # p=array(p)
    x = array(x)
    lnf = [[None] * cols for i in range(rows)]
    lnf = array(lnf)
    for i in range(0, rows):
        for j in range(0, cols):
            if x[i][j] == 0:
                lnfij = 0.0
            else:
                p = x[i][j] / x.sum(axis=0)[j]
                lnfij = math.log(p) * p * (-k)
            lnf[i][j] = lnfij
    lnf = pd.DataFrame(lnf)
    E = lnf
    # 计算冗余度
    d = 1 - E.sum(axis=0)
    # 计算各指标的权重
    w = [[None] * 1 for i in range(cols)]
    for j in range(0, cols):
        wj = d[j] / sum(d)
        w[j] = wj
        # 计算各样本的综合得分,用最原始的数据

    w = pd.DataFrame(w)
    return w


# 影响分数计算
def Habitat_impact(byear, eyear, begin_year, end_year, TxInOutdir):
    """
    byear:基准期的开始年份
    eyear：基准期的结束年份
    begin_year:指数计算开始年份
    end_year:指数计算结束年份
    TxInOutdir:SWAT-DayCent模型输出路径
    """
    # 读入SWAT输出数据
    SWAT_out = pd.read_table(TxInOutdir + 'output.hru', skiprows=9, sep='\s+', header=None, dtype=str)
    hru_num = int(SWAT_out.iloc[-1, 1])  # hru是第二列
    SWAT_out = SWAT_out[:-hru_num]
    SWAT_data = SWAT_out.iloc[:, [1, 5, 13, 34]]
    SWAT_data.columns = ['HRU', 'MON.AREAkm2', 'SW', 'SYLD']
    ndf = SWAT_data['MON.AREAkm2'].str.split('.', expand=True)
    SWAT_data["Year"] = ndf[0]
    SWAT_data["Area"] = ndf[1]
    SWAT_data = SWAT_data.drop('MON.AREAkm2', axis=1)
    SWAT_data = SWAT_data.apply(pd.to_numeric, errors='coerce')
    # 读入DayCent输出数据
    Cent_out = pd.read_table(TxInOutdir + 'CENT/CENT_year.out', delim_whitespace=True)

    # 基准期数据
    SWAT_data_base = SWAT_data[(SWAT_data["Year"] <= eyear) & (SWAT_data["Year"] >= byear)]
    Cent_data_base = Cent_out[(Cent_out['Y'] <= eyear) & (Cent_out['Y'] >= byear)]
    sw_base = pd.pivot_table(SWAT_data_base, index=['HRU'], columns='Year', values="SW", aggfunc=[np.mean])
    syld_base = pd.pivot_table(SWAT_data_base, index=['HRU'], columns='Year', values="SYLD", aggfunc=[np.mean])
    npp_base = pd.pivot_table(Cent_data_base, index=['iHRU'], columns='Y', values="cproda", aggfunc=[np.mean])
    soc_base = pd.pivot_table(Cent_data_base, index=['iHRU'], columns='Y', values="somsc", aggfunc=[np.mean])
    # 预测数据
    SWAT_data_pre = SWAT_data[(SWAT_data["Year"] <= end_year) & (SWAT_data["Year"] >= begin_year)]
    Cent_data_pre = Cent_out[(Cent_out['Y'] <= end_year) & (Cent_out['Y'] >= begin_year)]
    sw = pd.pivot_table(SWAT_data_pre, index=['HRU'], columns='Year', values="SW", aggfunc=[np.mean])
    syld = pd.pivot_table(SWAT_data_pre, index=['HRU'], columns='Year', values="SYLD", aggfunc=[np.mean])
    npp = pd.pivot_table(Cent_data_pre, index=['iHRU'], columns='Y', values="cproda", aggfunc=[np.mean])
    soc = pd.pivot_table(Cent_data_pre, index=['iHRU'], columns='Y', values="somsc", aggfunc=[np.mean])

    year_list = np.arange(begin_year, end_year + 1, 1).tolist()
    par_col_name = [str(i) for i in year_list]
    sw.columns = par_col_name
    syld.columns = par_col_name
    npp.columns = par_col_name
    soc.columns = par_col_name

    # 得到的四个影响指标的风险等级划分标准
    #     df_base = npp_base.copy()
    #     df_pre = npp.copy()
    #     index_chara = 0
    #     npp_rank = index_rank_0(df_base,df_pre,index_chara)
    npp_rank = index_rank_0(npp_base, npp, 0)
    print(npp_rank)

    #     df_base = soc_base.copy()
    #     df_pre = soc.copy()
    #     index_chara = 0
    #     soc_rank = index_rank_0(df_base,df_pre,index_chara)
    soc_rank = index_rank_0(soc_base, soc, 0)

    #     df_base = sw_base.copy()
    #     df_pre = sw.copy()
    #     index_chara = 0
    #     sw_rank = index_rank_0(df_base,df_pre,index_chara)
    sw_rank = index_rank_0(sw_base, sw, 0)
    #     df_base = syld_base.copy()
    #     df_pre = syld.copy()
    #     index_chara = 0
    #     syld_rank = index_rank_0(df_base,df_pre,index_chara)
    syld_rank = index_rank_0(syld_base, syld, 1)

    index_rank = pd.concat([sw_rank, syld_rank, npp_rank, soc_rank], axis=1)
    index_rank.columns = ["sw", "syld", "npp", "soc"]
    print(index_rank)

    bins = [4, 3, 2, 1, 0]
    # sw.iloc[:,0:-2].apply(lambda x : pd.cut(x,sw_rank,labels=bins))
    rank = index_rank[3:]
    npp_rank = rank["npp"].tolist()
    npp_rank.append(float('inf'))
    npp_group = npp.apply(lambda x: pd.cut(x, npp_rank, labels=bins))

    sw_rank = rank["sw"].tolist()
    sw_rank.append(float('inf'))
    sw_group = sw.apply(lambda x: pd.cut(x, sw_rank, labels=bins))

    soc_rank = rank["soc"].tolist()
    soc_rank.append(float('inf'))
    soc_group = soc.apply(lambda x: pd.cut(x, soc_rank, labels=bins))

    syld_rank = rank["syld"].tolist()
    syld_rank.insert(0, float('-inf'))
    syld = syld.fillna(0)
    syld_group = syld.apply(lambda x: pd.cut(x, syld_rank, labels=bins[::-1]))

    # 求权重
    impact_index = pd.DataFrame()
    impact_index["sw"] = sw_base["base_Mean"]
    impact_index["syld"] = syld_base["base_Mean"]
    impact_index["npp"] = npp_base["base_Mean"]
    impact_index["soc"] = soc_base["base_Mean"]
    w = cal_weight(impact_index)
    w.index = impact_index.columns
    w.columns = ['weight']
    print(w)
    influence_score = npp
    for i in range(npp.shape[0]):
        for j in range(npp.shape[1]):
            influence_score.iloc[i, j] = npp_group.iloc[i, j] * w.loc["npp", "weight"] + soc_group.iloc[i, j] * w.loc[
                "soc", "weight"] + sw_group.iloc[i, j] * w.loc["sw", "weight"] + syld_group.iloc[i, j] * w.loc[
                                             "syld", "weight"]
    print("influence_score calculating successful")
    return influence_score


def data_join_shape(data, shape):
    for i in range(data.shape[1]):
        # data的格式是数据框格式
        driver = ogr.GetDriverByName('ESRI Shapefile')
        layer_source = driver.Open(shape, 1)
        #layer_source = driver.Open(shp, 1)
        lyr = layer_source.GetLayer()
        FieldName = ogr.FieldDefn(data.columns[i], ogr.OFTReal)
        FieldName.SetWidth(8)
        FieldName.SetPrecision(3)
        lyr.CreateField(FieldName, 1)
        for fea in lyr:
            valueA = fea.GetFieldAsInteger('HRU_ID')
            fea.SetField(data.columns[i], float(data.iloc[valueA - 1, i]))
            lyr.SetFeature(fea)


def shp_to_tif(shp, tif_dir, pixel_size, field):
    pixel = pixel_size
    NoData_value = np.nan
    # Filename of input OGR file
    #     Filename of the raster Tiff that will be created
    raster_fn = tif_dir
    # Open the data source and read in the extent
    source_ds = ogr.Open(shp)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)
    # srs = osr.SpatialReference()
    # srs.ImportFromEPSG(4326)  # 定义输出的坐标系为"WGS 84"，AUTHORITY["EPSG","4326"]
    prj = 'PROJCS["Krasovsky_1940_Lambert_Conformal_Conic",GEOGCS["GCS_Krasovsky_1940",DATUM["Not_specified_based_on_Krassowsky_1940_ellipsoid",SPHEROID["Krasovsky_1940",6378245,298.3,AUTHORITY["EPSG","7024"]],AUTHORITY["EPSG","6024"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["standard_parallel_1",25],PARAMETER["standard_parallel_2",47],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["false_easting",20500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]]]'
    target_ds.SetProjection(prj)  # 给新建图层赋予投影信息
    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE=" + field])
    target_ds = None


def area(shpPath):
    '''计算面积'''
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shpPath, 1)
    layer = dataSource.GetLayer()

    src_srs = layer.GetSpatialRef()  # 获取原始坐标系或投影
    tgt_srs = osr.SpatialReference()
    tgt_srs.ImportFromEPSG(32649)  # WGS_1984_UTM_Zone_49N投影的ESPG号，需要改自己的要去网上搜下，这个不难
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)  # 计算投影转换参数
    # geosr.SetWellKnownGeogCS("WGS_1984_UTM_Zone_49N")

    #     new_field = ogr.FieldDefn("Area123", ogr.OFTReal)  #创建新的字段
    #     new_field.SetWidth(32)
    #     new_field.SetPrecision(16)
    #     layer.CreateField(new_field)
    shp_area = []
    for feature in layer:
        geom = feature.GetGeometryRef()
        geom2 = geom.Clone()
        #         geom2.Transform(transform)  #edit by fan

        area_in_sq_m = geom2.GetArea()  # 默认为平方米
        # area_in_sq_km = area_in_sq_m / 1000000 #转化为平方公里
        shp_area.append(area_in_sq_m)
    #         feature.SetField("Area123", area_in_sq_m)
    #         layer.SetFeature(feature)
    shp_area = DataFrame(shp_area)
    return shp_area


def read_rasterfile(input_rasterfile):
    dataset = gdal.Open(input_rasterfile)

    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize
    im_bands = dataset.RasterCount

    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()

    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)
    NoDataValue = dataset.GetRasterBand(1).GetNoDataValue()
    return [im_data, im_width, im_height, im_bands, im_geotrans, im_proj, NoDataValue]


def geo_xy(raster):
    tif = xr.open_rasterio(raster)
    #     tif = tif[0]
    lons = tif.x
    lats = tif.y
    im_proj = read_rasterfile(raster)[5]
    proj1 = Proj(im_proj)

    x = np.zeros(len(lons))
    y = np.zeros(len(lats))

    for i in range(len(lons)):
        for j in range(len(lats)):
            x[i], y[j] = proj1(lons[i], lats[j], inverse=True)
    return x, y

#第三步：生境退化度指数和生境退化风险数据导出
"""
这一步中将HRU/SUB尺度的生境压力分数、生境影响分数、生境退化度和生境退化风险数据输出，以及绘图
"""
def Habitat_Deg_Index(byear,eyear,begin_year,end_year,TxInOutdir,inputdir,deg_outputdir,input_vector,hab_deg_outdir,flag):
    """
    byear:基准期的初始年份
    eyear：基准期的结束年份
    begin_year:指数计算开始年份，end_year:指数计算结束年份
    TxInOutdir：SWAT-DayCent模型的输出路径
    input_vector：Hru的路径
    inputdir：InVEST退化度的输入数据路径
    outputdir：InVEST退化度的输出路径
    hab_deg_outdir:生境退化指数的输出路径
    flag:flag=1时进行画图，flag=0时不画图
    """
    pressure_data= Habitat_Pressure(inputdir,deg_outputdir,input_vector)
    influence_data = Habitat_impact(byear,eyear,begin_year,end_year,TxInOutdir)
    pressure_data.to_csv(hab_deg_outdir+'Pressure_score.csv',sep=',',index=False,header=True)
    influence_data.to_csv(hab_deg_outdir+'Influence_score.csv',sep=',',index=False,header=True)

    hab_deg = influence_data
    hab_deg_risk = influence_data
    for s in range(pressure_data.shape[1]):
        for i in range(influence_data.shape[0]):
            for j in range(influence_data.shape[1]):
                hab_deg.iloc[i,j] = influence_data.iloc[i,j]*pressure_data.iloc[i,s]
                hab_deg_risk.iloc[i,j] = hab_deg.iloc[i,j]**0.5
        hab_deg.to_csv(hab_deg_outdir+pressure_data.columns[s]+'_Habitat_deg_Index_space.csv',sep=',',index=False,header=True)
        hab_deg_mean = hab_deg.mean()
        hab_deg_mean.to_csv(hab_deg_outdir+pressure_data.columns[s]+'_Habitat_deg_Index_time.csv',sep=',',index=False,header=True)

        hab_deg_risk.to_csv(hab_deg_outdir+pressure_data.columns[s]+'_Habitat_Risk_space.csv',sep=',',index=False,header=True)
        #输出不同等级的面积百分比
        shp_area = area(input_vector)
        hab_deg_risk["hru_area"] = shp_area[0].tolist()
        area_per  = hab_deg_risk.iloc[0:4,:-1]
        area_per.index = ["Blue","Yellow","Orange","Red"]
        for i in range(area_per.shape[1]):
            a1 = hab_deg_risk.loc[hab_deg_risk.iloc[:,i]<=1]
            a1_per= a1["hru_area"].sum()/ shp_area[0].sum()
            a2 = hab_deg_risk.loc[(hab_deg_risk.iloc[:,i]<=2) & (hab_deg_risk.iloc[:,i]>1)]
            a2_per= a2["hru_area"].sum()/ shp_area[0].sum()
            a3 = hab_deg_risk.loc[(hab_deg_risk.iloc[:,i]<=3) & (hab_deg_risk.iloc[:,i]>2)]
            a3_per= a3["hru_area"].sum()/ shp_area[0].sum()
            a4 = hab_deg_risk.loc[(hab_deg_risk.iloc[:,i]<=4) & (hab_deg_risk.iloc[:,i]>3)]
            a4_per= a4["hru_area"].sum()/ shp_area[0].sum()
            area_per.iloc[0:4,i] = a1_per,a2_per,a3_per,a4_per
#         print(area_per)
        area_per.to_csv(hab_deg_outdir+pressure_data.columns[s]+'Habitat_Risk_area_per.csv',sep=',',index=False,header=True)
#         if flag ==1:
#             print("start plot....")
#             risk_data = hab_deg_risk
# #             data_join_shape(risk_data,input_vector)
#             #第四步 绘图：绘制动态图
#             def ani_plot(i):
#                 #清除上一次绘制的图
#                 plt.clf()
#
#                 #图1：绘生境退化指数时间变化图
#                 year_d = hab_deg_mean  #时间变化数据
#                 plt.subplot(221)
#                 ax1 = plt.gca()
#                 np.max(hab_deg_mean[:])
#                 ax1.set_ylim(0, np.max(year_d[:])*1.5) #y的范围为0到最大值的1.5
#                 ax1.set_xlim(float(year_d.index[0]), float(year_d.index[-1])) #x的范围为第一年到最后一年
#
#                 x = [float(i) for i in year_d.index[0:i+1]]
#                 y = year_d[0:i+1].tolist()
#                 ax1.plot(x,y,marker='o', linestyle='--', linewidth=1, markersize=3, color='g')
#                 if area_per.iloc[3,i]>0.25:
#                     ax1.text(float(year_d.index[i-1]),year_d[i]*1.05,"red warning",style ='italic', fontsize = 10, color ="red")
#                     ax1.plot(float(year_d.index[i]),year_d[i],marker='o', linestyle='--', linewidth=1, markersize=3, color='red')
#
#                 #图2：绘不同风险的面积百分比图
#                 area_per = area_per #风险面积百分比数据
#                 plt.subplot(222)
#                 ax2 = plt.gca()
#                 area_per.iloc[:,i].plot(kind='pie',ax=ax2,autopct='%.2f%%')
#
#                 #图3：绘生境退化风险指数的空间图
#                 risk_data = hab_deg_risk
#                 plt.subplot(212)
#                 ax3 = plt.gca()
#
#                 #为了加快画图的速度，生成tif数据后再画
#                 shp = input_vector
#                 pixel_size = pixel_size
#                 field = risk_data.columns[i]
#                 #创建存储tif的文件夹
#                 os.mkdir(hab_deg_outdir + pressure_data.columns[s])
#                 tif_dir = hab_deg_outdir +pressure_data.columns[s]+ '/'+risk_data.columns[i]+"tif"
#                 shp_to_tif(shp,tif_dir,pixel_size,field)
#
#                 config = {"font.family":'Times New Roman',"font.size":13,"mathtext.fontset":'stix'}
#                 rcParams.update(config)
#
#                 tif = xr.open_rasterio(tif_dir)
#                 #数据
#                 tif = tif[0]
#                 #获取经纬度
#                 x,y = geo_xy(tif_dir)
#             #     # Define extents
#                 lat_min = tif.y.min()
#                 lat_max = tif.y.max()
#                 lon_min = tif.x.min()
#                 lon_max = tif.x.max()
#
#                 bins = [0,1,2,3,4]
#                 nbin = 4
#                 index_colors = ["lightskyblue","LemonChiffon","SandyBrown","Salmon"]
#                 cmap =mpl.colors.ListedColormap(index_colors)
#                 norm = mcolors.BoundaryNorm(bins, nbin)
#
#                 m = axs.pcolorfast(x,np.flipud(y),np.flipud(tif), cmap=cmap,norm  = norm)
#                 rectangles = [mpatches.Rectangle((0, 0,), 1, 1, facecolor=index_colors[i])
#                           for i in range(len(index_colors))]
#                 labels = ['blue',
#                           'yellow',
#                           'orange',
#                           'red']
#                 plt.legend(rectangles,labels,bbox_to_anchor=(0.05,0.05),ncol=4,loc= 'lower left',fancybox=True, frameon=False)
#                 #设置坐标轴刻度
#                 axs.set_ylim(y.min()-0.2, y.max()+0.2)
#                 axs.set_xlim(x.min()-0.2, x.max()+0.2)
#                 axs.xaxis.set_major_formatter(LongitudeFormatter())#刻度格式转换为经纬度样式
#                 axs.yaxis.set_major_formatter(LatitudeFormatter())
#                 plt.yticks(rotation=90)
#                 x_major_locator=MultipleLocator(1)
#                 #把x轴的刻度间隔设置为1，并存在变量里
#                 y_major_locator=MultipleLocator(1)
#                 #把y轴的刻度间隔设置为1，并存在变量里
#                 #ax为两条坐标轴的实例
#                 axs.xaxis.set_major_locator(x_major_locator)
#                 #把x轴的主刻度设置为1的倍数
#                 axs.yaxis.set_major_locator(y_major_locator)
#                 #不显示次要坐标轴刻度
#                 xminorLocator   = MultipleLocator(1) #将x轴次刻度标签设置为n的倍数
#                 axs.xaxis.set_minor_locator(xminorLocator)
#                 yminorLocator   = MultipleLocator(1) #将x轴次刻度标签设置为n的倍数
#                 axs.yaxis.set_minor_locator(yminorLocator)
#
#             fig = plt.figure(figsize=(12,9),dpi=100)
#             ani =animation.FuncAnimation(fig, ani_plot, frames=range(0, len(risk_data.columns)))
#             # 保存动态图
#             ani.save(hab_degdir+"动态图.tif", writer='pillow')
#
#             # remove join
#             ds = ogr.Open(input_vector, 1)
#             if ds is None:  # 确保shapefile文件不为空，可正常打开
#                 sys.exit('Could not open {0}.'.format(fn))
#             lyr = ds.GetLayer(0)
#             for i in range(risk_data.shape[1]):
#                 lyr.DeleteField(lyr.FindFieldIndex(risk_data.columns[i], 0))


if __name__ == '__main__':
    TxInOutdir = 'C:/Users/hp/Desktop/test_SWAT-DayCent_InVEST/TxtInOut/'
    input_vector = 'C:/Users/hp/Desktop/test_SWAT-DayCent_InVEST/Watershed/Shapes/hru3.shp'
    byear = 1980
    eyear = 2019
    begin_year = 2020
    end_year = 2099
    inputdir = 'C:/Users/hp/Desktop/test_SWAT-DayCent_InVEST/invest_deg_data/'
    deg_outputdir = 'C:/Users/hp/Desktop/test_SWAT-DayCent_InVEST/invest_deg_data/'
    hab_deg_outdir = 'C:/Users/hp/Desktop/test_SWAT-DayCent_InVEST/Result_Path/'
    flag = 0

    # TxInOutdir = sys.argv[1]
    # input_vector = sys.argv[2]
    # byear = int(sys.argv[3])
    # eyear = int(sys.argv[4])
    # begin_year = int(sys.argv[5])
    # end_year = int(sys.argv[6])
    # inputdir = sys.argv[7]
    # deg_outputdir = sys.argv[8]
    # hab_deg_outdir = sys.argv[9]
    # flag = int(sys.argv[10])

    print(TxInOutdir)
    print(input_vector)
    print(byear)
    print(eyear)
    print(begin_year)
    print(end_year)
    print(inputdir)
    print(deg_outputdir)
    print(hab_deg_outdir)
    print(flag)

    # byear = 1980
    # eyear = 2019
    # begin_year = 2020
    # end_year = 2099
    # TxInOutdir = "D:/SWAT_Daycent/test_SWAT-DayCent_InVEST/TxtInOut/"
    # inputdir = "D:/SWAT_Daycent/test_SWAT-DayCent_InVEST/invest_deg_data/"
    # deg_outputdir = "D:/SWAT_Daycent/test_SWAT-DayCent_InVEST/invest_deg_data/"
    # input_vector = "D:/SWAT_Daycent/test_SWAT-DayCent_InVEST/Watershed/Shapes/hru3.shp"
    # hab_deg_outdir = "D:/SWAT_Daycent/test_SWAT-DayCent_InVEST/Result_Path/"
    # flag = 0
#     Habitat_Pressure(inputdir,deg_outputdir,input_vector)
#     Habitat_impact(byear,eyear,begin_year,end_year,TxInOutdir)
    print('Please wait, it will take about five minutes...')
    Habitat_Deg_Index(byear,eyear,begin_year,end_year,TxInOutdir,inputdir,deg_outputdir,input_vector,hab_deg_outdir,flag)
    print('Finished!')