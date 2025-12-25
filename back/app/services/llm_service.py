"""LLM服务模块"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import httpx
import json
from loguru import logger

# 加载环境变量
load_dotenv()

class ZhipuLLM:
    """智谱AI LLM类"""
    
    def __init__(self):
        # 尝试从多个可能的位置获取API密钥
        self.api_key = os.getenv("LLM_API_KEY")
        if not self.api_key:
            # 尝试从项目根目录的.env文件加载
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_path = os.path.join(project_root, ".env")
            if os.path.exists(env_path):
                load_dotenv(env_path)
                self.api_key = os.getenv("LLM_API_KEY")
        
        self.base_url = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        self.model_id = os.getenv("LLM_MODEL_ID", "glm-4")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "300"))  # 增加超时时间到5分钟
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "10000"))  # 设置最大令牌数
        
        if not self.api_key:
            logger.error("LLM_API_KEY 环境变量未设置")
            raise ValueError("LLM_API_KEY 环境变量未设置")
        
        logger.info(f"LLM服务初始化成功: {self.base_url}, 模型: {self.model_id}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用智谱AI API生成响应
        
        Args:
            prompt: 用户输入提示
            system_prompt: 系统提示（可选）
            
        Returns:
            LLM生成的响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建消息历史
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.7,
            "max_tokens": self.max_tokens  # 添加最大令牌数限制
        }
        
        try:
            logger.info(f"发送LLM请求: {self.base_url}/chat/completions")
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info("LLM响应成功")
            return content
        except httpx.HTTPStatusError as e:
            error_msg = f"LLM API HTTP错误: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"大模型调用失败！错误详情: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


def get_llm():
    """
    获取LLM实例
    
    Returns:
        LLM实例
    """
    # 直接使用真实的LLM服务
    return ZhipuLLM()