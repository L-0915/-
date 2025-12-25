# 智能旅游助手 ✈️

# 功能特点：

1.AI大模型驱动的SimpleAgent,智能生成详细的多日旅程；

2.集成高德地图：通过MCP协议接入高德地图API服务,支持景点搜索、路线规划、天气查询；

3.调用工具：Agent自动调用高德地图MCP工具,获取景点、酒店、餐饮和天气信息；

4.现代化前端: Vue3 + TypeScript + Vite,响应式设计,流畅的用户体验；

5.结果界面包含费用、交通、每天游览的景点、住宿、餐饮推荐等

# **技术栈**

后端

框架: 基于SimpleAgent

API: FastAPI

MCP工具: amap-mcp-server (高德地图)

LLM: GLM-4

前端

框架: Vue 3 + TypeScript

构建工具: Vite

UI组件库: Ant Design Vue

地图服务: 高德地图 JavaScript API

HTTP客户端: Axios

# 快速开始：

1.前提条件

Python 3.10+

Node.js 16+

高德地图API密钥 (Web服务API)

LLM API密钥 (OpenAI/DeepSeek等)

# 2.后端安装

进入后端目录：

`cd back`

创建虚拟环境：

`conda create -n yourvenv python=3.11`

激活环境:

`conda activate yourvenv`

安装依赖:

`pip install -r requirements.txt`

配置环境变量:

`cp .env.example .env`

`# 编辑.env文件,填入你的API密钥`

启动后端服务:

`python run.py`

# 3.前端安装

进入前端目录：（新开一个终端）

`cd front`

安装依赖:

`npm install`

配置环境变量:

`# 创建.env文件,配置高德地图Web API Key`
`echo "VITE_AMAP_WEB_KEY=your_amap_web_key" > .env`

启动开发服务器:

`npm run dev`

打开浏览器访问 `http://localhost:5173`

