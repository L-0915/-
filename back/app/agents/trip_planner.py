"""多智能体旅行规划系统"""

import json
import re
import datetime
from typing import Dict, Any, List
from loguru import logger
from ..services.llm_service import get_llm
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel, Budget
from ..config import get_settings

# ============ 自定义 Agent 实现 ============

class MCPTool:
    """MCP 工具类，用于与 MCP 服务器通信"""
    
    def __init__(self, name: str, description: str, server_command: List[str], env: Dict[str, str], auto_expand: bool = False):
        self.name = name
        self.description = description
        self.server_command = server_command
        self.env = env
        self.auto_expand = auto_expand
    
    def get_spec(self) -> Dict[str, Any]:
        """获取工具规范"""
        return {
            "name": self.name,
            "description": self.description,
            "serverCommand": self.server_command,
            "env": self.env,
            "autoExpand": self.auto_expand
        }


class SimpleAgent:
    """简单的 Agent 实现"""
    
    def __init__(self, name: str, llm: Any, system_prompt: str):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = []
    
    def add_tool(self, tool: MCPTool):
        """添加工具到 Agent"""
        self.tools.append(tool)
    
    def list_tools(self) -> List[MCPTool]:
        """列出所有工具"""
        return self.tools
    
    def run(self, query: str) -> str:
        """
        运行 Agent 来处理查询
        
        Args:
            query: 用户查询
            
        Returns:
            Agent 的响应
        """
        # 使用 LLM 的 generate 方法获取响应
        response = self.llm.generate(query, self.system_prompt)
        
        # 检查响应是否包含工具调用
        if "[TOOL_CALL:" in response or "TOOL_CALL:" in response:
            # 解析工具调用
            tool_call = self._parse_tool_call(response)
            if tool_call:
                # 执行工具调用并返回结果
                return self._execute_tool_call(tool_call)
        
        # 返回 LLM 的完整响应
        return response
    
    def _parse_tool_call(self, response: str) -> Dict[str, Any]:
        """解析工具调用"""
        try:
            # 支持两种格式: [TOOL_CALL:tool_name:param1=value1,param2=value2] 和 TOOL_CALL:tool_name:param1=value1,param2=value2
            tool_call_str = response
            if "[TOOL_CALL:" in response:
                # 提取方括号内的内容
                start = response.find("[TOOL_CALL:")
                end = response.find("]", start)
                if end > start:
                    tool_call_str = response[start+1:end]
                else:
                    tool_call_str = response[start+1:]  # 如果没有找到结束括号，就提取从开始到末尾的内容
            elif "TOOL_CALL:" in response:
                # 如果没有方括号，直接使用整个字符串
                start = response.find("TOOL_CALL:")
                tool_call_str = response[start:]
            
            # 分割工具名称和参数
            parts = tool_call_str.split(":", 2)
            if len(parts) < 3:
                logger.error(f"Invalid tool call format: {response}")
                return None
            
            tool_name = parts[1]
            params_str = parts[2]
            
            # 解析参数
            params = {}
            for param in params_str.split(","):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key.strip()] = value.strip()
            
            return {
                "tool_name": tool_name,
                "params": params
            }
        except Exception as e:
            logger.error(f"Error parsing tool call: {str(e)}")
            return None
    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
            """执行工具调用"""
            try:
                tool_name = tool_call["tool_name"]
                params = tool_call["params"]
                
                # 根据工具名称执行相应的操作
                if tool_name == "amap_maps_text_search":
                    # 模拟景点搜索结果
                    keywords = params.get("keywords", "")
                    city = params.get("city", "")
                    return json.dumps([
                        {
                            "name": f"{city}热门景点",
                            "address": f"{city}市中心",
                            "location": {"longitude": 116.397128, "latitude": 39.916527},
                            "visit_duration": 120,
                            "description": f"{city}的著名景点，适合{keywords}的游客",
                            "category": keywords,
                            "ticket_price": 60
                        }
                    ])
                elif tool_name == "amap_maps_weather":
                    # 模拟天气查询结果
                    city = params.get("city", "")
                    return json.dumps([
                        {
                            "date": "2025-12-13",
                            "day_weather": "晴",
                            "night_weather": "多云",
                            "day_temp": 25,
                            "night_temp": 15,
                            "wind_direction": "南风",
                            "wind_power": "1-3级"
                        }
                    ])
                else:
                    logger.error(f"Unknown tool: {tool_name}")
                    return json.dumps([])
            except Exception as e:
                logger.error(f"Error executing tool call: {str(e)}")
                return json.dumps([])


# ============ Agent提示词 ============

ATTRACTION_AGENT_PROMPT = """你是景点搜索专家。你的任务是根据城市和用户偏好搜索合适的景点。

**重要提示:**
你必须使用工具来搜索景点!不要自己编造景点信息!

**工具调用格式:**
使用maps_text_search工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=景点关键词,city=城市名]`

**示例:**
用户: "搜索北京的历史文化景点"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=历史文化,city=北京]

用户: "搜索上海的公园"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=公园,city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 参数用逗号分隔
"""

WEATHER_AGENT_PROMPT = """你是天气查询专家。你的任务是查询指定城市的天气信息。

**重要提示:**
你必须使用工具来查询天气!不要自己编造天气信息!

**工具调用格式:**
使用maps_weather工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_weather:city=城市名]`

**示例:**
用户: "查询北京天气"
你的回复: [TOOL_CALL:amap_maps_weather:city=北京]

用户: "上海的天气怎么样"
你的回复: [TOOL_CALL:amap_maps_weather:city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
"""

HOTEL_AGENT_PROMPT = """你是酒店推荐专家。你的任务是根据城市和景点位置推荐合适的酒店。

**重要提示:**
你必须使用工具来搜索酒店!不要自己编造酒店信息!

**工具调用格式:**
使用maps_text_search工具搜索酒店时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=酒店,city=城市名]`

**示例:**
用户: "搜索北京的酒店"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=酒店,city=北京]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 关键词使用"酒店"或"宾馆"
"""

PLANNER_AGENT_PROMPT = """你是行程规划专家。你的任务是根据景点信息和天气信息,生成详细的旅行计划。

请按照以下JSON格式返回旅行计划:
```json
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397128, "latitude": 39.916527},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397128, "latitude": 39.916527},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }
}
```

**重要提示:**
1. weather_info数组必须包含每一天的天气信息
2. 温度必须是纯数字(不要带°C等单位)
3. 每天安排2-3个景点
4. 考虑景点之间的距离和游览时间
5. 每天必须包含早中晚三餐
6. 提供实用的旅行建议
7. **必须包含预算信息**:
   - 景点门票价格(ticket_price)
   - 餐饮预估费用(estimated_cost)
   - 酒店预估费用(estimated_cost)
   - 预算汇总(budget)包含各项总费用
"""


class MultiAgentTripPlanner:
    def __init__(self, llm):
        self.llm = llm
        # 创建 MCP 工具实例，提供所有必需的参数
        self.amap_tool = MCPTool(
            name="amap_maps",
            description="高德地图工具集",
            server_command=["uvx", "amap-mcp-server"],
            env={}
        )
        self.search_agent = SimpleAgent("Search Agent", llm, ATTRACTION_AGENT_PROMPT)
        self.weather_agent = SimpleAgent("Weather Agent", llm, WEATHER_AGENT_PROMPT)
        self.hotel_agent = SimpleAgent("Hotel Agent", llm, HOTEL_AGENT_PROMPT)
        self.planner_agent = SimpleAgent("Planner Agent", llm, PLANNER_AGENT_PROMPT)
        
        # 添加 MCP 工具到各个 Agent
        self.search_agent.add_tool(self.amap_tool)
        self.weather_agent.add_tool(self.amap_tool)
        self.hotel_agent.add_tool(self.amap_tool)
        self.planner_agent.add_tool(self.amap_tool)

    def _build_attraction_query(self, destination: str, days: int) -> str:
        """
        构建景点搜索查询
        
        Args:
            destination: 目的地城市
            days: 旅行天数
            
        Returns:
            景点搜索查询字符串
        """
        return f"请搜索{destination}的适合{days}天旅行的景点"

    def _build_planner_query(self, request: TripRequest, attractions: List[Attraction], 
                           weather_info: List[WeatherInfo], hotels: List[Hotel]) -> str:
        """
        构建行程规划查询
        
        Args:
            request: 旅行请求
            attractions: 景点列表
            weather_info: 天气信息
            hotels: 酒店列表
            
        Returns:
            行程规划查询字符串
        """
        return f"请为{request.city}规划一个{request.travel_days}天的旅行计划，基于提供的景点、天气和酒店信息"

    def plan_trip(self, request: TripRequest) -> TripPlan:
        # 搜索景点
        attraction_query = self._build_attraction_query(request.city, request.travel_days)
        try:
            attraction_response = self.search_agent.run(attraction_query)
            # 解析景点搜索结果
            attractions = self._parse_response(attraction_response, "attractions")
        except Exception as e:
            logger.error(f"景点搜索失败: {str(e)}")
            attractions = self._create_default_attractions(request.city)
        
        # 查询天气
        weather_query = f"请查询{request.city}未来{request.travel_days}天的天气情况"
        try:
            weather_response = self.weather_agent.run(weather_query)
            # 解析天气查询结果
            weather_info = self._parse_response(weather_response, "weather")
        except Exception as e:
            logger.error(f"天气查询失败: {str(e)}")
            weather_info = self._create_default_weather_info(request)
        
        # 推荐酒店
        hotel_query = f"请为前往{request.city}的旅客推荐合适的住宿地点"
        try:
            hotel_response = self.hotel_agent.run(hotel_query)
            # 解析酒店推荐结果
            hotels = self._parse_response(hotel_response, "hotels")
        except Exception as e:
            logger.error(f"酒店推荐失败: {str(e)}")
            hotels = self._create_default_hotels(request.city)
        
        # 规划行程
        planner_query = self._build_planner_query(request, attractions, weather_info, hotels)
        try:
            planner_response = self.planner_agent.run(planner_query)
            # 解析行程规划结果
            daily_plans = self._parse_trip_plan_response(planner_response, request)
        except Exception as e:
            logger.error(f"行程规划失败: {str(e)}")
            daily_plans = self._create_default_daily_plans(request)
        
        # 如果daily_plans已经是TripPlan对象，直接返回
        if isinstance(daily_plans, TripPlan):
            return daily_plans
        
        # 返回完整的TripPlan对象，包含所有必要字段
        return TripPlan(
            start_city=request.start_city,
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=daily_plans,
            weather_info=weather_info,
            overall_suggestions="根据天气和景点情况，合理安排行程，注意防晒和携带雨具。",
            budget=self._create_default_budget(),
            to_transportation=request.to_transportation
        )

    def _parse_response(self, response: str, response_type: str) -> Any:
        try:
            # 尝试解析 JSON 格式的响应
            parsed_response = json.loads(response)
            # 检查解析后的响应是否为字典类型并且包含指定的键
            if isinstance(parsed_response, dict) and response_type in parsed_response:
                return parsed_response[response_type]
            # 如果响应本身就是所需的数据类型（如列表），直接返回
            elif isinstance(parsed_response, list) and response_type == "attractions":
                return parsed_response
            elif isinstance(parsed_response, list) and response_type == "weather":
                return parsed_response
            elif isinstance(parsed_response, list) and response_type == "hotels":
                return parsed_response
            else:
                # 如果不是期望的格式，记录警告并返回空列表
                logger.warning(f"Unexpected response format for {response_type}: {type(parsed_response)}")
                return []
        except json.JSONDecodeError:
            # 如果解析失败，则记录错误并返回空列表
            logger.error(f"Failed to parse {response_type} response: {response}")
            return []
        except KeyError:
            # 如果缺少必要的键，则记录错误并返回空列表
            logger.error(f"Missing key '{response_type}' in response: {response}")
            return []
        except Exception as e:
            # 捕获其他可能的异常
            logger.error(f"Error processing {response_type} response: {str(e)}")
            return []

    def _parse_trip_plan_response(self, response: str, request: TripRequest) -> TripPlan:
        """尝试直接解析完整的旅行计划响应"""
        try:
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                
                # 检查JSON是否完整
                if not self._is_json_complete(json_str):
                    logger.warning("检测到不完整的JSON响应，尝试修复...")
                    json_str = self._fix_incomplete_json(json_str, request)
                
                # 尝试修复常见的JSON格式问题
                json_str = self._fix_json_format(json_str)
                
                trip_data = json.loads(json_str)
                
                # 确保days存在且不为空
                if not trip_data.get('days'):
                    trip_data['days'] = self._create_default_daily_plans(request)
                
                # 确保其他必要字段存在
                trip_data['start_city'] = request.start_city
                trip_data['city'] = request.city
                trip_data['start_date'] = request.start_date
                trip_data['end_date'] = request.end_date
                trip_data['to_transportation'] = request.to_transportation
                
                if not trip_data.get('weather_info'):
                    trip_data['weather_info'] = self._create_default_weather_info(request)
                
                if not trip_data.get('budget'):
                    trip_data['budget'] = self._create_default_budget()
                
                if not trip_data.get('overall_suggestions'):
                    trip_data['overall_suggestions'] = "根据天气和景点情况，合理安排行程，注意防晒和携带雨具。"
                
                return TripPlan(**trip_data)
            else:
                raise ValueError("响应中未找到有效的JSON格式")
        except Exception as e:
            logger.error(f"解析完整旅行计划失败: {str(e)}")
            raise e

    def _is_json_complete(self, json_str: str) -> bool:
        """检查JSON字符串是否完整"""
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    def _fix_incomplete_json(self, json_str: str, request: TripRequest) -> str:
        """尝试修复不完整的JSON字符串"""
        # 计算括号匹配
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        # 补充缺失的括号
        json_str += '}' * (open_braces - close_braces)
        json_str += ']' * (open_brackets - close_brackets)
        
        # 如果JSON在字符串中间被截断，尝试找到最后一个完整的对象
        try:
            # 尝试找到最后一个完整的day对象
            last_day_end = json_str.rfind('}')
            if last_day_end > 0:
                # 检查是否在days数组内
                days_start = json_str.find('"days"')
                if days_start >= 0 and days_start < last_day_end:
                    # 找到days数组的开始
                    days_array_start = json_str.find('[', days_start)
                    if days_array_start >= 0 and days_array_start < last_day_end:
                        # 截取到当前最后一个完整的day对象
                        partial_json = json_str[:last_day_end+1]
                        
                        # 检查是否有未闭合的字符串
                        if partial_json.count('"') % 2 != 0:
                            # 如果有未闭合的字符串，添加引号
                            partial_json += '"'
                        
                        # 补充必要的括号
                        partial_json += ']'  # 闭合days数组
                        partial_json += '}'  # 闭合主对象
                        
                        return partial_json
        except Exception as e:
            logger.error(f"修复不完整JSON失败: {str(e)}")
        
        # 如果修复失败，返回一个最小的有效JSON
        return json.dumps({
            "days": self._create_default_daily_plans(request),
            "weather_info": self._create_default_weather_info(request),
            "budget": self._create_default_budget()
        })

    def _fix_json_format(self, json_str: str) -> str:
        """尝试修复常见的JSON格式问题"""
        try:
            # 尝试直接解析，如果成功则返回原字符串
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            # 如果解析失败，尝试修复常见问题
            try:
                # 尝试修复缺少引号的键
                # 修复没有引号的键名
                json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
                # 修复单引号为双引号
                json_str = json_str.replace("'", '"')
                # 尝试解析修复后的JSON
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError as e:
                logger.error(f"无法修复JSON格式: {str(e)}")
                # 如果仍然失败，尝试创建一个最小的有效JSON
                return '{"days": []}'
        except Exception as e:
            logger.error(f"修复JSON时出错: {str(e)}")
            return '{"days": []}'
    
    def _create_default_attractions(self, city: str) -> List[Attraction]:
        """创建默认景点列表"""
        return [
            Attraction(
                name=f"{city}市中心景点",
                address=f"{city}市中心",
                location=Location(longitude=116.397128, latitude=39.916527),
                visit_duration=120,
                description=f"{city}的著名景点，适合游览",
                category="历史文化",
                ticket_price=60
            ),
            Attraction(
                name=f"{city}自然风光区",
                address=f"{city}郊区",
                location=Location(longitude=116.497128, latitude=39.816527),
                visit_duration=180,
                description=f"{city}的自然风光区，风景优美",
                category="自然风光",
                ticket_price=40
            )
        ]
    
    def _create_default_hotels(self, city: str) -> List[Hotel]:
        """创建默认酒店列表"""
        return [
            Hotel(
                name=f"{city}市中心酒店",
                address=f"{city}市中心",
                location=Location(longitude=116.397128, latitude=39.916527),
                price_range="300-500元",
                rating="4.5",
                distance="距离景点2公里",
                type="经济型酒店",
                estimated_cost=400
            ),
            Hotel(
                name=f"{city}豪华酒店",
                address=f"{city}商业区",
                location=Location(longitude=116.497128, latitude=39.816527),
                price_range="800-1200元",
                rating="5.0",
                distance="距离景点3公里",
                type="豪华酒店",
                estimated_cost=1000
            )
        ]
    
    def _create_default_daily_plans(self, request: TripRequest) -> List[DayPlan]:
        """创建默认每日计划"""
        days = []
        attractions = self._create_default_attractions(request.city)
        hotels = self._create_default_hotels(request.city)
        # 解析起始日期字符串
        start_date = datetime.datetime.strptime(request.start_date, "%Y-%m-%d")
        for i in range(request.travel_days):
            # 计算当前日期
            current_date = start_date + datetime.timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            # date = f"{start_date.year}-{start_date.month:02d}-{start_date.day+i:02d}"
            
            # 每天安排1-2个景点
            day_attractions = [attractions[i % len(attractions)]]
            if i % 2 == 0 and len(attractions) > 1:
                day_attractions.append(attractions[(i+1) % len(attractions)])
            
            # 创建每日计划
            day_plan = DayPlan(
                date=date_str,
                day_index=i,
                description=f"第{i+1}天行程概述",
                transportation="地铁/公交",
                accommodation="酒店",
                hotel=hotels[i % len(hotels)],
                attractions=day_attractions,
                meals=[
                    Meal(type="breakfast", name="酒店早餐", description="自助早餐", estimated_cost=30),
                    Meal(type="lunch", name="当地特色午餐", description="品尝当地美食", estimated_cost=50),
                    Meal(type="dinner", name="当地特色晚餐", description="品尝当地美食", estimated_cost=80)
                ]
            )
            days.append(day_plan)
        
        return days
    
    def _create_default_weather_info(self, request: TripRequest) -> List[WeatherInfo]:
        """创建默认天气信息"""
        weather_info = []
        # 解析起始日期字符串
        start_date = datetime.datetime.strptime(request.start_date, "%Y-%m-%d")
        for i in range(request.travel_days):
            # 计算当前日期
            current_date = start_date + datetime.timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            #date = f"{request.start_date.year}-{request.start_date.month:02d}-{request.start_date.day+i:02d}"
            weather = WeatherInfo(
                date=date_str,
                day_weather="晴",
                night_weather="多云",
                day_temp=25,
                night_temp=15,
                wind_direction="南风",
                wind_power="1-3级"
            )
            weather_info.append(weather)
        return weather_info
    
    def _create_default_budget(self) -> Budget:
        """创建默认预算"""
        return Budget(
            total_attractions=180,
            total_hotels=1200,
            total_meals=480,
            total_transportation=200,
            total=2060
        )


# 全局多智能体系统实例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        # 获取 LLM 实例并传递给 MultiAgentTripPlanner
        llm = get_llm()
        _multi_agent_planner = MultiAgentTripPlanner(llm)

    return _multi_agent_planner