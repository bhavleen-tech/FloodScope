"""Automated Sentinel-2 L2A reflectance download/processing. Research screening only."""
from datetime import date,timedelta
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from shapely.geometry import shape,mapping
from shapely.ops import transform as shp_transform, unary_union
from pyproj import Transformer
from rasterio.features import shapes
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.windows import from_bounds
import rasterio

router=APIRouter()
class AutoQuery(BaseModel):
    lat:float=Field(ge=-85,le=85)
    lon:float=Field(ge=-180,le=180)
    radius_km:float=Field(gt=0,le=2)
    date:date
    ndwi_threshold:float=Field(default=0.15,ge=-0.3,le=0.7)

def pick(items):
    # Favor low cloud cover; only select scenes with both bands
    items=[i for i in items if 'B03' in i.assets and 'B08' in i.assets]
    return min(items,key=lambda i:float(i.properties.get('eo:cloud_cover',100))) if items else None

def load_band(item,band,bounds,crs='EPSG:4326',n=256):
    href=item.assets[band].href
    # remote rasterio COG access; resample to same WGS84 grid for all scenes
    west,south,east,north=bounds
    from rasterio.transform import from_bounds as affine_from_bounds
    dst_transform=affine_from_bounds(west,south,east,north,n,n)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_MAX_RETRY='2',GDAL_HTTP_RETRY_DELAY='1'):
        with rasterio.open(href) as src:
            with WarpedVRT(src,crs=crs,transform=dst_transform,width=n,height=n,resampling=(Resampling.nearest if band=='SCL' else Resampling.bilinear)) as vrt:
                arr=vrt.read(1,masked=True).astype('float32')
    return arr,dst_transform

@router.post('/api/auto-sentinel2')
def auto_sentinel2(q:AutoQuery):
    try:
        import planetary_computer as pc
        from pystac_client import Client
        from scipy.ndimage import binary_opening,binary_closing
        d=q.radius_km/111.32; dx=d/max(.2,np.cos(np.deg2rad(q.lat)))
        bbox=[q.lon-dx,q.lat-d,q.lon+dx,q.lat+d]
        cat=Client.open('https://planetarycomputer.microsoft.com/api/stac/v1')
        def find(start,end):
            results=list(cat.search(collections=['sentinel-2-l2a'],bbox=bbox,datetime=f'{start}/{end}',query={'eo:cloud_cover':{'lt':65}},max_items=30).items())
            item=pick(results)
            return pc.sign(item) if item else None
        before=find(q.date-timedelta(days=55),q.date-timedelta(days=5))
        after=find(q.date,q.date+timedelta(days=40))
        if not before or not after:raise HTTPException(404,'No suitable before/after Sentinel-2 L2A scenes in search windows. Cloud cover or catalogue availability may limit coverage.')
        gb,t=load_band(before,'B03',bbox);nb,_=load_band(before,'B08',bbox)
        ga,_=load_band(after,'B03',bbox);na,_=load_band(after,'B08',bbox)
        b=(gb-nb)/(gb+nb+1e-6);a=(ga-na)/(ga+na+1e-6)
        valid=(~np.ma.getmaskarray(gb))&(~np.ma.getmaskarray(nb))&(~np.ma.getmaskarray(ga))&(~np.ma.getmaskarray(na))
        valid &= np.isfinite(b.data)&np.isfinite(a.data)
        if 'SCL' in before.assets and 'SCL' in after.assets:
            sb,_=load_band(before,'SCL',bbox);sa,_=load_band(after,'SCL',bbox)
            invalid_classes=[0,1,3,8,9,10,11]  # no data, defective, shadow, clouds, snow
            valid &= (~np.isin(sb.data,invalid_classes)) & (~np.isin(sa.data,invalid_classes))
        else:
            raise HTTPException(422,'Scene classification (SCL) unavailable; cannot screen clouds safely')
        # Optical water expansion only. SCL masking needed for cloud/shadow safety.
        candidate=valid & (b.data<q.ndwi_threshold) & (a.data>=q.ndwi_threshold)
        candidate=binary_closing(binary_opening(candidate,iterations=1),iterations=1)&valid
        polys=[]
        for geom,v in shapes(candidate.astype('uint8'),mask=candidate,transform=t):
            if v==1:polys.append(shape(geom))
        area=0
        if polys:
            trans=Transformer.from_crs('EPSG:4326','EPSG:6933',always_xy=True).transform
            area=shp_transform(trans,unary_union(polys)).area/1e6
        return {'status':'automatic_optical_water_expansion_screening','method':'Sentinel-2 L2A NDWI threshold, NOT trained AI','area_km2':round(area,4),'before_scene':before.id,'after_scene':after.id,'valid_pixels':int(valid.sum()),'candidate_pixels':int(candidate.sum()),'geojson':{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'method':'NDWI optical screening'},'geometry':mapping(p)} for p in polys[:1500]]},'limitations':'Cloud/shadow, seasonal water and terrain effects can produce false positives. Not SAR, not AI, not validated flooding. Copernicus Sentinel-2 via Microsoft Planetary Computer; requires internet and publicly available COGs.'}
    except HTTPException:raise
    except Exception as e:raise HTTPException(502,'Satellite retrieval/processing failed: '+str(e))
