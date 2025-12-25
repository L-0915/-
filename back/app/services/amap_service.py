"""高德地图API服务封装"""

import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

# 高德地图API基础URL
AMAP_API_BASE_URL = "https://restapi.amap.com/v3"

class AmapService:
    """高德地图服务封装类"""
    
    def __init__(self):
        """初始化服务"""
        settings = get_settings()
        self.api_key = settings.gd_api_key
        self.client = httpx.Client(timeout=30.0)
        
        if not self.api_key:
            logger.error("高德地图API Key未配置,请在.env文件中设置GD_API_KEY")
            raise ValueError("高德地图API Key未配置,请在.env文件中设置GD_API_KEY")
    
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        搜索POI
        
        Args:
            keywords: 搜索关键词
            city: 城市
            citylimit: 是否限制在城市范围内
            
        Returns:
            POI信息列表
        """
        try:
            # 构建请求参数
            params = {
                "key": self.api_key,
                "keywords": keywords,
                "city": city,
                "citylimit": "true" if citylimit else "false",
                "extensions": "base",
                "output": "json"
            }
            
            # 发送请求
            response = self.client.get(f"{AMAP_API_BASE_URL}/place/text", params=params)
            response.raise_for_status()
            
            # 解析结果
            data = response.json()
            pois = []
            
            if data.get("status") == "1" and "pois" in data:
                for item in data["pois"]:
                    # 解析位置信息
                    location_str = item.get("location", "")
                    if "," in location_str:
                        lon, lat = location_str.split(",")
                        location = Location(longitude=float(lon), latitude=float(lat))
                    else:
                        location = Location(longitude=0.0, latitude=0.0)
                    
                    poi_info = POIInfo(
                        id=item.get("id", ""),
                        name=item.get("name", ""),
                        type=item.get("type", ""),
                        address=item.get("address", ""),
                        location=location,
                        tel=item.get("tel", "")
                    )
                    pois.append(poi_info)
            else:
                error_info = data.get("info", "未知错误")
                error_code = data.get("infocode", "未知错误码")
                logger.error(f"高德地图API返回错误: {error_info} (错误码: {error_code})")
            
            return pois
            
        except httpx.HTTPStatusError as e:
            logger.error(f"POI搜索HTTP错误: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"POI搜索失败: {str(e)}")
            return []
    
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气
        
        Args:
            city: 城市名称
            
        Returns:
            天气信息列表
        """
        try:
            # 构建请求参数
            params = {
                "key": self.api_key,
                "city": city,
                "extensions": "all",
                "output": "json"
            }
            
            # 发送请求
            response = self.client.get(f"{AMAP_API_BASE_URL}/weather/weatherInfo", params=params)
            response.raise_for_status()
            
            # 解析结果
            data = response.json()
            weather_infos = []
            
            if data.get("status") == "1" and "forecasts" in data:
                forecasts = data["forecasts"]
                if forecasts:
                    # 获取第一个预报（通常是当天）
                    forecast = forecasts[0]
                    casts = forecast.get("casts", [])
                    
                    for cast in casts:
                        weather_info = WeatherInfo(
                            date=cast.get("date", ""),
                            day_weather=cast.get("dayweather", ""),
                            night_weather=cast.get("nightweather", ""),
                            day_temp=cast.get("daytemp", 0),
                            night_temp=cast.get("nighttemp", 0),
                            wind_direction=cast.get("daywind", ""),
                            wind_power=cast.get("daypower", "")
                        )
                        weather_infos.append(weather_info)
            else:
                error_info = data.get("info", "未知错误")
                error_code = data.get("infocode", "未知错误码")
                logger.error(f"高德地图API返回错误: {error_info} (错误码: {error_code})")
            
            return weather_infos
            
        except httpx.HTTPStatusError as e:
            logger.error(f"天气查询HTTP错误: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"天气查询失败: {str(e)}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        规划路线
        
        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit)
            
        Returns:
            路线信息
        """
        try:
            # 根据路线类型选择API路径
            route_api_map = {
                "walking": "walking",
                "driving": "driving",
                "transit": "transit/integrated"
            }
            
            api_path = route_api_map.get(route_type, "walking")
            
            # 构建请求参数
            params = {
                "key": self.api_key,
                "origin": origin_address,
                "destination": destination_address,
                "output": "json"
            }
            
            # 添加城市参数
            if origin_city:
                params["origincity"] = origin_city
            if destination_city:
                params["destinationcity"] = destination_city
                
            # 发送请求 - 修复URL拼接错误
            response = self.client.get(f"{AMAP_API_BASE_URL}/direction/{api_path}", params=params)
            response.raise_for_status()
            
            # 解析结果
            data = response.json()
            
            if data.get("status") == "1" and "route" in data:
                route_data = data["route"]
                if "paths" in route_data and route_data["paths"]:
                    # 获取第一条路径
                    path = route_data["paths"][0]
                    return {
                        "distance": float(path.get("distance", 0)),
                        "duration": int(path.get("duration", 0)),
                        "route_type": route_type,
                        "description": f"路线规划成功，总距离约{int(path.get('distance', 0))/1000:.1f}公里，预计耗时约{int(path.get('duration', 0))/60:.0f}分钟"
                    }
            else:
                error_info = data.get("info", "未知错误")
                error_code = data.get("infocode", "未知错误码")
                logger.error(f"高德地图API返回错误: {error_info} (错误码: {error_code})")
            
            return {}
            
        except httpx.HTTPStatusError as e:
            logger.error(f"路线规划HTTP错误: {e.response.status_code} - {e.response.text}")
            return {}
        except Exception as e:
            logger.error(f"路线规划失败: {str(e)}")
            return {}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        地理编码(地址转坐标)

        Args:
            address: 地址
            city: 城市

        Returns:
            经纬度坐标
        """
        try:
            # 构建请求参数
            params = {
                "key": self.api_key,
                "address": address,
                "output": "json"
            }
            
            if city:
                params["city"] = city
                
            # 发送请求
            response = self.client.get(f"{AMAP_API_BASE_URL}/geocode/geo", params=params)
            response.raise_for_status()
            
            # 解析结果
            data = response.json()
            
            if data.get("status") == "1" and "geocodes" in data:
                geocodes = data["geocodes"]
                if geocodes:
                    # 获取第一个地理编码结果
                    location_str = geocodes[0].get("location", "")
                    if "," in location_str:
                        lon, lat = location_str.split(",")
                        return Location(longitude=float(lon), latitude=float(lat))
            else:
                error_info = data.get("info", "未知错误")
                error_code = data.get("infocode", "未知错误码")
                logger.error(f"高德地图API返回错误: {error_info} (错误码: {error_code})")
            
            return None
            
        except httpx.HTTPStatusError as e:
            logger.error(f"地理编码HTTP错误: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"地理编码失败: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        获取POI详情

        Args:
            poi_id: POI ID

        Returns:
            POI详情信息
        """
        try:
            # 构建请求参数
            params = {
                "key": self.api_key,
                "id": poi_id,
                "output": "json"
            }
            
            # 发送请求
            response = self.client.get(f"{AMAP_API_BASE_URL}/place/detail", params=params)
            response.raise_for_status()
            
            # 解析结果
            data = response.json()
            
            if data.get("status") == "1" and "pois" in data:
                pois = data["pois"]
                if pois:
                    # 返回第一个POI的详情
                    return pois[0]
            else:
                error_info = data.get("info", "未知错误")
                error_code = data.get("infocode", "未知错误码")
                logger.error(f"高德地图API返回错误: {error_info} (错误码: {error_code})")
            
            return {}

        except httpx.HTTPStatusError as e:
            logger.error(f"获取POI详情HTTP错误: {e.response.status_code} - {e.response.text}")
            return {}
        except Exception as e:
            logger.error(f"获取POI详情失败: {str(e)}")
            return {}


# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式)"""
    global _amap_service
    
    if _amap_service is None:
        _amap_service = AmapService()
    
    return _amap_service