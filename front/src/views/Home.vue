<template>
  <div class="home-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <div class="icon-wrapper">
        <span class="icon">✈️</span>
      </div>
      <h1 class="page-title">智能旅行助手</h1>
      <p class="page-subtitle">基于AI的个性化旅行规划,让每一次出行都完美无忧</p>
    </div>

    <a-card class="form-card" :bordered="false">
      <a-form
        :model="formData"
        layout="vertical"
        @finish="handleSubmit"
      >
        <!-- 第一步:目的地和日期 -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-icon">📍</span>
            <span class="section-title">目的地与日期</span>
          </div>

          <a-row :gutter="24">
            <a-col :span="8">
              <a-form-item name="start_city" :rules="[{ required: true, message: '请输入出发城市' }]">
                <template #label>
                  <span class="form-label">出发城市</span>
</template>
                <a-input
v-model:value="formData.start_city"
                  placeholder="例如: 上海"
                  size="large"
                  class="custom-input"
                >
                  <template #prefix>
                    <span style="color: #1890ff;">🛫</span>
                  </template>
                </a-input>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item name="city" :rules="[{ required: true, message: '请输入目的地城市' }]">
                <template #label>
                  <span class="form-label">目的地城市</span>
                </template>
                <a-input
                  v-model:value="formData.city"
                  placeholder="例如: 北京"
                  size="large"
                  class="custom-input"
                >
                  <template #prefix>
                    <span style="color: #1890ff;">🏙️</span>
                  </template>
                </a-input>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item name="to_transportation" :rules="[{ required: true, message: '请选择出行方式' }]">
                <template #label>
                  <span class="form-label">出行方式</span>
                </template>
                <a-select v-model:value="formData.to_transportation" size="large" class="custom-select">
                  <a-select-option value="飞机">✈️ 飞机</a-select-option>
                  <a-select-option value="火车">🚂 火车</a-select-option>
                  <a-select-option value="汽车">🚌 汽车</a-select-option>
                  <a-select-option value="自驾">🚗 自驾</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="24">
            <a-col :span="8">
              <a-form-item name="start_date" :rules="[{ required: true, message: '请选择开始日期' }]">
                <template #label>
                  <span class="form-label">开始日期</span>
                </template>
                <a-date-picker
                  v-model:value="startDate"
                  style="width: 100%"
                  size="large"
                  class="custom-input"
                  placeholder="选择日期"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item name="end_date" :rules="[{ required: true, message: '请选择结束日期' }]">
                <template #label>
                  <span class="form-label">结束日期</span>
                </template>
                <a-date-picker
                  v-model:value="endDate"
                  style="width: 100%"
                  size="large"
                  class="custom-input"
                  placeholder="选择日期"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item>
                <template #label>
                  <span class="form-label">旅行天数</span>
                </template>
                <div class="days-display-compact">
                  <span class="days-value">{{ formData.travel_days }}</span>
                  <span class="days-unit">天</span>
                </div>
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <!-- 第二步:偏好设置 -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-icon">⚙️</span>
            <span class="section-title">偏好设置</span>
          </div>

          <a-row :gutter="24">
            <a-col :span="8">
              <a-form-item name="transportation">
                <template #label>
                  <span class="form-label">当地交通方式</span>
                </template>
                <a-select v-model:value="formData.transportation" size="large" class="custom-select">
                  <a-select-option value="公共交通">🚇 公共交通</a-select-option>
                  <a-select-option value="自驾">🚗 自驾</a-select-option>
<a-select-option value="步行">🚶 步行</a-select-option>
                  <a-select-option value="混合">🔀 混合</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item name="accommodation">
                <template #label>
                  <span class="form-label">住宿偏好</span>
                </template>
                <a-select v-model:value="formData.accommodation" size="large" class="custom-select">
                  <a-select-option value="经济型酒店">💰 经济型酒店</a-select-option>
                  <a-select-option value="舒适型酒店">🏨 舒适型酒店</a-select-option>
                  <a-select-option value="豪华酒店">⭐ 豪华酒店</a-select-option>
                  <a-select-option value="民宿">🏡 民宿</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item name="preferences">
                <template #label>
                  <span class="form-label">旅行偏好</span>
                </template>
                <div class="preference-tags">
                  <a-checkbox-group v-model:value="formData.preferences" class="custom-checkbox-group">
                    <a-checkbox value="历史文化" class="preference-tag">🏛️ 历史文化</a-checkbox>
                    <a-checkbox value="自然风光" class="preference-tag">🏞️ 自然风光</a-checkbox>
                    <a-checkbox value="美食" class="preference-tag">🍜 美食</a-checkbox>
                    <a-checkbox value="购物" class="preference-tag">🛍️ 购物</a-checkbox>
                    <a-checkbox value="艺术" class="preference-tag">🎨 艺术</a-checkbox>
                    <a-checkbox value="休闲" class="preference-tag">☕ 休闲</a-checkbox>
                  </a-checkbox-group>
                </div>
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <!-- 第三步:额外要求 -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-icon">💬</span>
            <span class="section-title">额外要求</span>
          </div>

          <a-form-item name="free_text_input">
            <a-textarea
              v-model:value="formData.free_text_input"
              placeholder="请输入您的额外要求,例如:想去看升旗、需要无障碍设施、对海鲜过敏等..."
              :rows="3"
              size="large"
              class="custom-textarea"
            />
          </a-form-item>
        </div>

        <!-- 提交按钮 -->
        <a-form-item>
          <a-button 
            type="primary" 
            html-type="submit" 
            size="large" 
            :loading="submitting"
            :disabled="submitting"
            block
          >
            <template v-if="!submitting">开始规划我的旅行</template>
            <template v-else>
              <span>规划中...</span>
              <span style="margin-left: 8px;">{{ Math.round(progress) }}%</span>
            </template>
          </a-button>
        </a-form-item>
        
        <!-- 进度条 -->
        <div v-if="submitting" class="progress-container">
          <a-progress 
            :percent="Math.round(progress)" 
            status="active" 
            :show-info="false"
            stroke-color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          />
          <div class="progress-text">
            {{ progress < 30 ? '正在分析您的需求...' : 
               progress < 60 ? '正在搜索最佳景点...' : 
               progress < 90 ? '正在优化行程路线...' : 
               '即将完成...'}}
          </div>
        </div>

        <!-- 加载进度条 -->
        <a-form-item v-if="loading">
          <div class="loading-container">
            <a-progress
              :percent="loadingProgress"
              status="active"
              :stroke-color="{
                '0%': '#667eea',
                '100%': '#764ba2',
              }"
              :stroke-width="10"
            />
            <p class="loading-status">
              {{ loadingStatus }}
            </p>
          </div>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import type { TripFormData } from '@/types'
import type { Dayjs } from 'dayjs'

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')

// 将日期字段与表单数据分开
const formData = reactive<TripFormData>({
  start_city: '',
  city: '',
  start_date: '',  // 使用空字符串而不是null
  end_date: '',    // 使用空字符串而不是null
  travel_days: 1,
  to_transportation: '飞机',
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

// 单独管理日期选择器的值
const startDate = ref<Dayjs | null>(null)
const endDate = ref<Dayjs | null>(null)

// 监听日期变化
watch([startDate, endDate], ([start, end]) => {
  if (start && end) {
    formData.start_date = start.format('YYYY-MM-DD')
    formData.end_date = end.format('YYYY-MM-DD')
    
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning('旅行天数不能超过30天')
      endDate.value = null
      formData.end_date = ''
    } else {
      message.warning('结束日期不能早于开始日期')
      endDate.value = null
      formData.end_date = ''
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error('请选择日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0
  loadingStatus.value = '正在初始化...'

  // 模拟进度更新
const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10

      // 更新状态文本
      if (loadingProgress.value <= 30) {
        loadingStatus.value = '🔍 正在搜索景点...'
      } else if (loadingProgress.value <= 50) {
        loadingStatus.value = '🌤️ 正在查询天气...'
      } else if (loadingProgress.value <= 70) {
        loadingStatus.value = '🏨 正在推荐酒店...'
      } else {
        loadingStatus.value = '📋 正在生成行程计划...'
      }
    }
  }, 500)

  try {
    const requestData: TripFormData = {
      start_city: formData.start_city,
      city: formData.city,
      start_date: startDate.value ? startDate.value.format('YYYY-MM-DD') : '',
      end_date: endDate.value ? endDate.value.format('YYYY-MM-DD') : '',
      travel_days: formData.travel_days,
      to_transportation: formData.to_transportation,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      free_text_input: formData.free_text_input
    }

    console.log('发送请求:', requestData)  // 添加此行用于调试
    const response = await generateTripPlan(requestData)
    console.log('收到响应:', response)  // 添加此行用于调试

    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingStatus.value = '✅ 完成!'

    if (response.success && response.data) {
      // 保存到sessionStorage
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      // 同时保存用户的出行方式选择
      sessionStorage.setItem('userTransportationChoice', formData.to_transportation)

      message.success('旅行计划生成成功!')

      // 短暂延迟后跳转
      setTimeout(() => {
        router.push('/result')
      }, 500)
    } else {
      message.error(response.message || '生成失败')
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    console.error('详细错误信息:', error)  // 添加此行用于调试
message.error(error.message || '生成旅行计划失败,请稍后重试')
  } finally {
    setTimeout(() => {
      loading.value = false
      loadingProgress.value = 0
      loadingStatus.value = ''
    }, 1000)
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 20px;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -50px;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: -50px;
  left: 30%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 50px;
  animation: fadeInDown 0.8s ease-out;
  position: relative;
  z-index: 1;
}

.icon-wrapper {
  margin-bottom: 20px;
}

.icon {
  font-size: 80px;
  display: inline-block;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.page-title {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  margin: 10px 0 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* 表单卡片 */
.form-card {
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 表单区域 */
.form-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}
.section-icon {
  font-size: 1.2rem;
  margin-right: 10px;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #333;
}

/* 表单标签 */
.form-label {
  font-weight: 600;
  color: #555;
  font-size: 0.95rem;
}

/* 自定义输入框 */
.custom-input,
.custom-select,
.custom-textarea {
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  transition: all 0.3s;
}

.custom-input:hover,
.custom-select:hover,
.custom-textarea:hover {
  border-color: #40a9ff;
}

.custom-input:focus,
.custom-select:focus,
.custom-textarea:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 天数显示 */
.days-display-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  background: linear-gradient(135deg, #1890ff, #667eea);
  border-radius: 8px;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.days-value {
  font-size: 1.2rem;
}

.days-unit {
  font-size: 0.9rem;
  margin-left: 4px;
}

/* 偏好标签 */
.preference-tags {
  background: white;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #d9d9d9;
}

.custom-checkbox-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.preference-tag {
  margin: 0 !important;
  padding: 8px 12px !important;
  border-radius: 6px !important;
  border: 1px solid #d9d9d9 !important;
  transition: all 0.3s;
}

.preference-tag:hover {
  border-color: #1890ff !important;
  background: #e6f7ff !important;
}

.preference-tag.ant-checkbox-wrapper-checked {
  border-color: #1890ff !important;
  background: #e6f7ff !important;
}

/* 提交按钮 */
.submit-button {
  height: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.button-icon {
  margin-right: 8px;
}

/* 加载状态 */
.loading-container {
  width: 100%;
  text-align: center;
}

.loading-status {
  margin-top: 15px;
  font-weight: 500;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container {
    padding: 10px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .form-card {
    margin: 0 10px;
  }
  
  .form-section {
    padding: 16px;
  }
  
  .preference-tags {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .submit-button {
    height: 50px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .preference-tags {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  
  .page-title {
    font-size: 1.8rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .custom-checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .days-display-compact {
    height: 35px;
  }
}
.budget-note {
  grid-column: span 2;
  text-align: center;
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e8e8e8;
}
</style>

const handleSubmit = async () => {
  try {
    submitting.value = true
    
    // 表单验证
    if (!formData.value.start_city || !formData.value.city) {
      message.error('请填写出发城市和目的地城市')
      return
    }
    
    if (!formData.value.start_date || !formData.value.end_date) {
      message.error('请选择出行日期')
      return
    }
    
    if (new Date(formData.value.end_date) < new Date(formData.value.start_date)) {
      message.error('结束日期不能早于开始日期')
      return
    }
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 15
      }
    }, 800)
    
    // 发送行程计划请求
    const tripPlan = await generateTripPlan(formData.value)
    
    // 清除进度定时器
    clearInterval(progressInterval)
    progress.value = 100
    
    // 保存结果到sessionStorage
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.data))
    // 保存用户选择的交通方式
    sessionStorage.setItem('userTransportationChoice', formData.value.to_transportation)
    
    message.success('行程规划成功！')
    
    // 跳转到结果页
    router.push('/result')
    
  } catch (error: any) {
    console.error('行程规划失败:', error)
    message.error(error.message || '行程规划失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}