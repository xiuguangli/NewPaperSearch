<template>
  <div class="conference-stats-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <el-alert
        :title="error"
        type="error"
        show-icon
        :closable="false"
      />
    </div>

    <!-- 统计图表 -->
    <div v-else class="charts-container">
      <!-- 论文总数统计 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>各会议论文总数</h3>
          <div class="chart-actions">
            <el-radio-group v-model="paperCountChartType" size="small">
              <el-radio-button label="bar">柱状图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-container">
          <v-chart
            class="chart"
            :option="paperCountBarOption"
            autoresize
          />
        </div>
      </div>

      <!-- 年度论文数量趋势 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3>年度论文数量趋势</h3>
          <div class="chart-actions">
            <el-radio-group v-model="legendSelectMode" size="small" style="margin-right: 10px;">
              <el-radio-button label="all" @click="toggleAllLegends">{{ allLegendsSelected ? '取消全选' : '全选' }}</el-radio-button>
            </el-radio-group>
            <el-radio-group v-model="yearlyTrendChartType" size="small">
              <el-radio-button label="line">折线图</el-radio-button>
            </el-radio-group>
          </div>
        </div>

        <div class="chart-container">
          <v-chart
            class="chart"
            :option="yearlyTrendOption"
            autoresize
            @legendselectchanged="handleLegendSelectChanged"
            ref="yearlyTrendChart"
          />
        </div>
        
        <!-- 自定义图例 -->
        <div class="custom-legend">
          <div class="legend-grid">
            <div 
              v-for="(conference, index) in Object.keys(conferenceStats)"
              :key="conference"
              class="legend-item"
              :class="{ 'legend-disabled': !conferenceVisibility[conference] }"
              @click="toggleConference(conference)"
            >
              <span 
                class="legend-marker"
                :style="{ backgroundColor: getConferenceColor(conference) }"
              ></span>
              <span class="legend-text">{{ conference }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  ToolboxComponent
} from 'echarts/components';
import VChart from 'vue-echarts';
import { paperSearchAPI } from '../utils/api.js';

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  ToolboxComponent
]);

export default {
  name: 'ConferenceStats',
  components: {
    VChart
  },
  data() {
    return {
      // 数据
      conferencesConfig: {},
      conferenceStats: {},
      yearlyStats: {},

      // 状态
      loading: true,
      error: null,

      // 图表类型
      paperCountChartType: 'bar',
      yearlyTrendChartType: 'line',
      legendSelectMode: 'all',

      // 当前选中的会议（用于显示数据标签）
      selectedConference: '',

      // 是否所有图例都被选中
      allLegendsSelected: true,
      
      // 会议可见性状态
      conferenceVisibility: {},

      // 颜色配置
      colorPalette: [
        '#d2a76a', // 主题色
        '#a06e3b', // 链接色
        '#7a6a5b', // 文本色
        '#9c8c7d', // 次要文本色
        '#e8e0d5', // 边框色
        '#5c4b3c', // 主要文本色
        '#b58a4f', // 主题色变体1
        '#c49a5d', // 主题色变体2
        '#8a5c2f', // 链接色变体1
        '#956834'  // 链接色变体2
      ],
      // 会议颜色映射
      conferenceColors: {
        'AAAI': '#d2a76a',
        'ACL': '#a06e3b',
        'COLM': '#7a6a5b',
        'COLT': '#9c8c7d',
        'CoRL': '#e8e0d5',
        'CVPR': '#5c4b3c'
      }
    };
  },
  computed: {
    // 论文总数柱状图配置
    paperCountBarOption() {
      const conferences = Object.keys(this.conferenceStats);
      const paperCounts = conferences.map(conf => this.conferenceStats[conf].totalPapers);

      // 为每个会议设置颜色
      const itemColors = conferences.map(conf =>
        this.conferenceColors[conf] || this.colorPalette[conferences.indexOf(conf) % this.colorPalette.length]
      );

      // 为每个数据点设置颜色
      const data = paperCounts.map((count, index) => ({
        value: count,
        itemStyle: {
          color: itemColors[index]
        }
      }));

      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          textStyle: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#fff'
          },
          formatter: function(params) {
            const param = params[0];
            return param.name + '<br/>' + param.seriesName + ': ' + param.value;
          },
          backgroundColor: 'rgba(50, 50, 50, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '3%',
          top: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: conferences,
          axisLabel: {
            interval: 0,
            rotate: 45,
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#5c4b3c',
            margin: 8
          },
          axisLine: {
            lineStyle: {
              color: 'var(--border-color)'
            },
            onZero: true
          },
          axisTick: {
            lineStyle: {
              color: 'var(--border-color)'
            },
            alignWithLabel: true
          }
        },
        yAxis: {
          type: 'value',
          name: '',
          nameTextStyle: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#5c4b3c',
            fontWeight: 'normal'
          },
          axisLabel: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#5c4b3c'
          },
          axisLine: {
            lineStyle: {
              color: 'var(--border-color)'
            }
          },
          axisTick: {
            lineStyle: {
              color: 'var(--border-color)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'var(--border-color)',
              opacity: 0.5
            }
          }
        },
        series: [
          {
            name: '论文总数',
            type: 'bar',
            barWidth: '50%',
            data: data,
            label: {
              show: true,
              position: 'top',
              fontFamily: 'Georgia, serif',
              fontSize: 18,
              color: '#5c4b3c',
              fontWeight: 'normal'
            }
          }
        ]
      };
    },

    // 年度论文数量趋势图配置
    yearlyTrendOption() {
      const years = Object.keys(this.yearlyStats).sort();
      const conferences = Object.keys(this.conferenceStats);

      const series = conferences.map((conf, index) => {
        const data = years.map(year => {
          return this.yearlyStats[year] && this.yearlyStats[year][conf]
            ? this.yearlyStats[year][conf]
            : 0;
        });

        return {
          name: conf,
          id: index,
          type: 'line',
          data: data,
          emphasis: {
            focus: 'series'
          },
          smooth: true,
          symbolSize: 8,
          itemStyle: {
            color: this.conferenceColors[conf] || this.colorPalette[conferences.indexOf(conf) % this.colorPalette.length]
          },
          lineStyle: {
            width: 3
          },
          label: {
            show: false,
            position: 'top',
            formatter: '{c}',
            fontSize: 18,
            fontFamily: 'Georgia, serif',
            color: '#5c4b3c'
          }
        };
      });

      return {
        tooltip: {
          trigger: 'axis',
          textStyle: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#fff'
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>';
            params.forEach(param => {
              result += param.marker + ' ' + param.seriesName + ': ' + param.value + '<br/>';
            });
            return result;
          },
          backgroundColor: 'rgba(50, 50, 50, 0.9)',
          borderColor: '#ccc',
          borderWidth: 1
        },
        legend: {
          show: false  // 隐藏默认图例，使用自定义图例
        },

        grid: {
          left: '5%',
          right: '5%',
          bottom: '5%',
          top: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: years,
          axisLabel: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#5c4b3c'
          },
          axisLine: {
            lineStyle: {
              color: 'var(--border-color)'
            }
          },
          axisTick: {
            lineStyle: {
              color: 'var(--border-color)'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '',
          nameTextStyle: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#5c4b3c',
            fontWeight: 'normal'
          },
          axisLabel: {
            fontFamily: 'Georgia, serif',
            fontSize: 18,
            color: '#5c4b3c'
          },
          axisLine: {
            lineStyle: {
              color: 'var(--border-color)'
            }
          },
          axisTick: {
            lineStyle: {
              color: 'var(--border-color)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'var(--border-color)',
              opacity: 0.5
            }
          }
        },
        series: series
      };
    }
  },
  created() {
    this.loadData();
  },
  methods: {
    // 加载会议数据 - 使用API
    async loadData() {
      this.loading = true;
      this.error = null;

      try {
        console.log('开始从API加载统计数据...');
        
        // 使用API获取统计数据
        const statsResponse = await paperSearchAPI.getStats();
        
        if (statsResponse) {
          this.processStatsData(statsResponse);
          console.log('API统计数据加载成功');
        } else {
          throw new Error('API返回数据为空');
        }

        this.loading = false;
        
      } catch (error) {
        console.error('从API加载统计数据失败:', error);
        this.error = `加载数据失败: ${error.message}`;
        
        this.loading = false;
      }
    },

    // 处理API返回的统计数据
    processStatsData(statsData) {
      const { conference_stats, year_stats, conference_year_stats } = statsData;
      
      // 处理会议统计数据
      const conferenceStats = {};
      const yearlyStats = {};
      
      // 构建会议统计
      conference_stats.forEach(item => {
        const conference = item._id;
        if (conference) {
          conferenceStats[conference] = {
            totalPapers: item.count,
            years: [],
            maxPapers: 0,
            maxPapersYear: ''
          };
        }
      });
      
      // 构建年度统计
      year_stats.forEach(item => {
        const year = item._id ? item._id.toString() : '';
        if (year) {
          yearlyStats[year] = {};
        }
      });
      
      // 处理会议年度统计
      conference_year_stats.forEach(item => {
        const conference = item._id.conference;
        const year = item._id.year ? item._id.year.toString() : '';
        const count = item.count;
        
        if (conference && year) {
          // 更新年度统计中的会议数据
          if (!yearlyStats[year]) {
            yearlyStats[year] = {};
          }
          yearlyStats[year][conference] = count;
          
          // 更新会议统计中的年度信息
          if (conferenceStats[conference]) {
            if (!conferenceStats[conference].years.includes(year)) {
              conferenceStats[conference].years.push(year);
            }
            
            // 更新最大论文数和对应年份
            if (count > conferenceStats[conference].maxPapers) {
              conferenceStats[conference].maxPapers = count;
              conferenceStats[conference].maxPapersYear = year;
            }
          }
        }
      });
      
      // 排序年份
      Object.keys(conferenceStats).forEach(conference => {
        conferenceStats[conference].years.sort((a, b) => parseInt(b) - parseInt(a));
      });
      
      this.conferenceStats = conferenceStats;
      this.yearlyStats = yearlyStats;
      
      // 初始化会议可见性状态
      this.conferenceVisibility = {};
      Object.keys(conferenceStats).forEach(conference => {
        this.conferenceVisibility[conference] = true;
      });
      
      console.log('处理后的会议统计:', this.conferenceStats);
      console.log('处理后的年度统计:', this.yearlyStats);
    },

    // 全选/取消全选图例
    toggleAllLegends() {
      if (!this.$refs.yearlyTrendChart) return;

      const chart = this.$refs.yearlyTrendChart.chart;
      const conferences = Object.keys(this.conferenceStats);

      if (this.allLegendsSelected) {
        // 当前是全选状态，执行取消全选
        conferences.forEach(conf => {
          chart.dispatchAction({
            type: 'legendUnSelect',
            name: conf
          });
          this.conferenceVisibility[conf] = false;
        });
        this.allLegendsSelected = false;
      } else {
        // 当前是部分选中状态，执行全选
        conferences.forEach(conf => {
          chart.dispatchAction({
            type: 'legendSelect',
            name: conf
          });
          chart.dispatchAction({
            type: 'downplay',
            seriesName: conf
          });
          this.conferenceVisibility[conf] = true;
        });
        this.allLegendsSelected = true;

        // 全选时隐藏所有数据标签
        const option = chart.getOption();
        const series = option.series;
        const updatedSeries = series.map(s => ({
          id: s.id,
          label: {
            show: false
          }
        }));

        chart.setOption({
          series: updatedSeries
        });
      }
    },



    // 处理图例选择变化事件
    handleLegendSelectChanged(params) {
      const { selected } = params;

      // 更新图表，显示或隐藏数据标签
      if (this.$refs.yearlyTrendChart) {
        const chart = this.$refs.yearlyTrendChart.chart;

        // 隐藏所有提示
        chart.dispatchAction({
          type: 'hideTip'
        });

        // 更新全选状态
        const conferences = Object.keys(this.conferenceStats);
        this.allLegendsSelected = conferences.every(conf => selected[conf] !== false);

        // 计算当前选中的会议数量
        const selectedConferences = conferences.filter(conf => selected[conf] !== false);
        const selectedCount = selectedConferences.length;

        // 获取当前的系列配置
        const option = chart.getOption();
        const series = option.series;

        // 准备更新的系列配置
        const updatedSeries = [];

        // 根据选中的会议数量决定是否显示数据标签
        series.forEach(s => {
          // 只有当选中的会议数量小于等于2时才显示数据标签
          const showLabel = selectedCount <= 2 && selected[s.name] !== false;

          updatedSeries.push({
            id: s.id,
            label: {
              show: showLabel
            }
          });
        });

        // 更新所有系列的数据标签显示状态
        chart.setOption({
          series: updatedSeries
        });

        // 如果用户点击了某个会议，高亮显示该会议
        if (params.name) {
          chart.dispatchAction({
            type: 'highlight',
            seriesName: params.name
          });

          // 其他会议取消高亮
          Object.keys(selected).forEach(name => {
            if (name !== params.name && selected[name]) {
              chart.dispatchAction({
                type: 'downplay',
                seriesName: name
              });
            }
          });
        }
      }
    },

    // 切换会议显示/隐藏
    toggleConference(conference) {
      if (!this.$refs.yearlyTrendChart) return;

      const chart = this.$refs.yearlyTrendChart.chart;
      const isVisible = this.conferenceVisibility[conference];

      if (isVisible) {
        // 隐藏会议
        chart.dispatchAction({
          type: 'legendUnSelect',
          name: conference
        });
        this.conferenceVisibility[conference] = false;
      } else {
        // 显示会议
        chart.dispatchAction({
          type: 'legendSelect',
          name: conference
        });
        this.conferenceVisibility[conference] = true;
      }

      // 更新全选状态
      const conferences = Object.keys(this.conferenceStats);
      this.allLegendsSelected = conferences.every(conf => this.conferenceVisibility[conf]);
    },

    // 获取会议颜色
    getConferenceColor(conference) {
      const conferences = Object.keys(this.conferenceStats);
      return this.conferenceColors[conference] || this.colorPalette[conferences.indexOf(conference) % this.colorPalette.length];
    }
  }
};
</script>

<style scoped>
.conference-stats-container {
  padding: 20px;
}

.page-title {
  font-size: var(--font-size-xxlarge);
  color: var(--text-color-primary);
  margin-bottom: var(--spacing-large);
  font-weight: var(--font-weight-bold);
  text-align: center;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chart-card {
  background-color: var(--bg-color-secondary);
  border-radius: 8px;
  padding: var(--spacing-medium) var(--spacing-medium) 10px var(--spacing-medium);
  box-shadow: 0 2px 12px 0 var(--shadow-color);
  margin-bottom: 10px;
  /* width: 100%; */
  margin-left: 1%;
  margin-right: 2%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-actions {
  display: flex;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  color: #5c4b3c;
  font-size: 20px;
  font-weight: 500;
  font-family: Georgia, serif;
}

.chart-container {
  height: 500px;
}

.chart {
  height: 100%;
  width: 100%;
}

.loading-container,
.error-container {
  padding: var(--spacing-large);
  text-align: center;
}

/* 自定义图例样式 */
.custom-legend {
  margin-top: 15px;
  padding: 15px;
  background-color: var(--bg-color-tertiary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.legend-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
  background-color: transparent;
}

.legend-item:hover {
  background-color: var(--bg-color-secondary);
}

.legend-item.legend-disabled {
  opacity: 0.4;
}

.legend-item.legend-disabled .legend-text {
  text-decoration: line-through;
}

.legend-marker {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  margin-right: 8px;
  display: inline-block;
  border: 1px solid var(--border-color);
}

.legend-text {
  font-family: Georgia, serif;
  font-size: 16px;
  color: var(--text-color-primary);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .legend-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .legend-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px 12px;
  }
  
  .legend-text {
    font-size: 14px;
  }
  
  .legend-marker {
    width: 12px;
    height: 12px;
    margin-right: 6px;
  }
}



</style>
