"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        logger.info(f"收到旅行规划请求: 城市={request.city}, 日期={request.start_date}-{request.end_date}, 天数={request.travel_days}")

        # 获取Agent实例
        logger.info("获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        logger.info("开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        logger.info("旅行计划生成成功,准备返回响应")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        logger.error(f"生成旅行计划失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name if hasattr(agent, 'agent') else "unknown",
            "tools_count": len(agent.agent.list_tools()) if hasattr(agent, 'agent') else 0
        }
    except Exception as e:
        logger.error(f"旅行规划服务健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )