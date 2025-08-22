<template>
  <div>
    <!-- 统一容器：包含过滤器、搜索和结果区域 -->
    <div class="filter-container">
      <!-- 过滤器和搜索区域 -->
      <el-row :gutter="5" class="filter-row top-controls-row">

        <el-col :span="5" class="control-container">
          <div class="control-wrapper">
            <el-select v-model="selectedConferences" placeholder="选择会议" class="perfectly-aligned-control" multiple collapse-tags collapse-tags-tooltip>
              <el-option v-for="conference in conferences" :key="conference" :label="conference" :value="conference"></el-option>
            </el-select>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <el-row :gutter="5" class="year-range-row">
            <el-col :span="11" class="year-select-col">
              <div class="control-wrapper">
                <el-select v-model="startYear" placeholder="起始年份" class="perfectly-aligned-control">
                  <el-option v-for="year in years" :key="year" :label="year" :value="year"></el-option>
                </el-select>
              </div>
            </el-col>
            <el-col :span="2" class="separator-container">
              <span class="separator-text">至</span>
            </el-col>
            <el-col :span="11" class="year-select-col">
              <div class="control-wrapper">
                <el-select v-model="endYear" placeholder="结束年份" class="perfectly-aligned-control">
                  <el-option v-for="year in years" :key="year" :label="year" :value="year"></el-option>
                </el-select>
              </div>
            </el-col>
          </el-row>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-input v-model="searchQuery" placeholder="在标题中搜索" clearable @clear="searchQuery = ''" @keyup.enter="searchPapers" class="perfectly-aligned-control">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
        </el-col>

        <el-col :span="6" class="control-container">
          <div class="control-wrapper">
            <el-input v-model="abstractSearchQuery" placeholder="在摘要中搜索" clearable @clear="abstractSearchQuery = ''" @keyup.enter="searchPapers" class="perfectly-aligned-control">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
        </el-col>
        
        <el-col :span="1" class="control-container">
          <div class="control-wrapper">
            <el-button type="primary" @click="searchPapers" :loading="loading" class="search-button">
              <el-icon><Search /></el-icon>
            </el-button>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="5" class="filter-row"> 
        
        <el-col :span="5" class="search-results-info">
          <span>找到 {{ totalPapers }} 篇论文</span>
        </el-col>

        <el-col :span="6">
          <el-row :gutter="5" class="expand-row">
            <el-col :span="11">
              <div class="custom-button-wrapper" :class="{'active-wrapper': expandAll.abstract}">
                <div class="button-text" @click="expandAllAbstracts">
                  <span class="no-padding-text">{{ expandAll.abstract ? '收起摘要' : '展开摘要' }}</span>
                </div>
              </div>
            </el-col>
            <!-- <el-col :span="1"></el-col>> -->
            <el-col :span="11">
              <div class="custom-button-wrapper" :class="{'active-wrapper': expandAll.gemini}">
                <div class="button-text" @click="expandAllGemini">
                  <span class="no-padding-text">{{ expandAll.gemini ? '收起解读' : '展开解读' }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-col>
        <el-col :span="6">

        </el-col>

        <el-col :span="7">
          <el-row :gutter="5">
            <el-col :span="12">
              <span>共 {{ totalPapers }} 篇</span>
            </el-col>
            <el-col :span="12">
              <el-select v-model="pageSize" @change="handleSizeChange" size="small">
                <el-option :value="10" label="10 篇/页" />
                <el-option :value="50" label="50 篇/页" />
                <el-option :value="100" label="100 篇/页" />
                <el-option :value="-1" label="全部显示" />
              </el-select>
            </el-col>
          </el-row>
        </el-col>
      </el-row>
      <el-row class="quick-select-row">
        <span class="subject-label">快速选择：</span>
        <el-button @click="handleSelectDefault()" class="unified-button">默认</el-button>
        <el-button @click="handleSelectCV()" class="unified-button">CV三会</el-button>
        <el-button @click="handleSelectML()" class="unified-button">ML三会</el-button>
        <el-button @click="handleSelectCVAndML()" class="unified-button">CV和ML</el-button>
      </el-row>
      <el-row v-if="subjects.length > 0">
        <el-col :span="24" class="subject-filter-row">
          <div class="subject-filter-container">
            <span class="subject-label">类型筛选：</span>
            <el-button @click="toggleAllSubjects" class="unified-button toggle-all-btn">
              {{ selectedSubjects.length === subjects.length ? '取消全选' : '全选' }}
            </el-button>
            
          </div>
        </el-col>
        
        </el-row>
      <el-row class="subject-selection-row">
        <el-checkbox-group v-model="selectedSubjects" @change="handleSubjectChange" class="subject-checkbox-group">
          <el-checkbox v-for="subject in subjects" :key="subject" :label="subject" class="subject-checkbox">
            {{ subject }}
          </el-checkbox>
        </el-checkbox-group>
      </el-row>
    </div>

    <!-- 论文列表容器 -->
    <div class="paper-list-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div>
          <h3>正在加载数据...</h3>
          <div class="progress-container">
            <el-progress
              :percentage="loadingProgress"
              :stroke-width="20"
              status="success"
            />
          </div>
          <p>正在加载多个会议的数据，请稍候...</p>
        </div>
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="error-container">
        <el-empty
          description="加载数据失败"
          :image-size="200"
        >
          <template #description>
            <p>{{ error }}</p>
          </template>
          <el-button @click="searchPapers">重试</el-button>
        </el-empty>
      </div>

      <!-- 论文列表 -->
      <div v-else-if="paginatedPapers.length > 0">
        <paper-card
          v-for="(paper, index) in paginatedPapers"
          :key="paper.id || index"
          :paper="paper"
          :index="(currentPage - 1) * pageSize + index"
          :title-keywords="searchKeywords"
          :abstract-keywords="abstractSearchKeywords"
          :expanded="expandedAbstracts[index]"
          :expand-all="expandAll"
          @toggle-abstract="handleToggleAbstract"
        />

        <!-- 底部分页导航 -->
        <div v-if="totalPapers > pageSize && pageSize !== -1" class="pagination-container">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            layout="prev, pager, next, jumper"
            :total="totalPapers"
            :pager-count="7"
            @current-change="handleCurrentChange"
            background
            hide-on-single-page
          />
        </div>
      </div>

      <!-- 无数据提示 -->
      <div v-else class="empty-container">
        <el-empty :description="!searchPerformed ? '请选择搜索条件并点击搜索' : '未找到匹配的论文'" />
      </div>
    </div>

    <!-- 回到顶部 -->
    <el-backtop :right="40" :bottom="40" />
  </div>
</template>

<script>
import { Search, ArrowUp, ArrowDown } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import PaperCard from './PaperCard.vue';
import { paperSearchAPI } from '../utils/api.js';

export default {
  components: {
    Search,
    ArrowUp,
    ArrowDown,
    PaperCard
  },
  name: 'AdvancedSearch',
  data() {
    return {
      // 数据
      allPapers: [],
      filteredPapers: [],
      totalPapers: 0, // 总论文数（用于分页和显示）

      // 状态
      loading: false,
      error: null,
      expandedAbstracts: {},
      searchPerformed: false,
      expandAll: {
        abstract: false,
        gemini: false
      },
      totalDatasetCount: 0,

      // 过滤和搜索
      selectedConferences: [],
      selectedSubjects: [],
      startYear: '',
      endYear: '',
      searchQuery: '',
      searchKeywords: [],
      abstractSearchQuery: '',
      abstractSearchKeywords: [],
      defaultConference: 'ICCV', // 默认会议
      defaultYear: new Date().getFullYear(), // 默认年份为当前年份

      // 分页
      currentPage: 1,
      pageSize: 10,

      // 选项
      conferences: [],
      years: [],
      subjects: [],
      availableDatasets: []
    }
  },

  computed: {
    paginatedPapers() {
      // 服务器端分页：直接返回filteredPapers（已经是当前页的数据）
      return this.filteredPapers;
    },

    totalPages() {
      // 基于总数计算总页数
      if (this.pageSize === -1) return 1; // 全部显示为1页
      return Math.ceil(this.totalPapers / this.pageSize);
    }
  },

  watch: {
    // 监听会议选择变化，动态更新Subject列表
    selectedConferences: {
      handler(newConferences, oldConferences) {
        console.log('会议选择变化:', oldConferences, '->', newConferences);
        // 当会议选择变化时，更新Subject列表
        this.updateSubjects();
      },
      deep: true
    },
    
    // 监听年份范围变化，动态更新Subject列表
    startYear: {
      handler(newYear, oldYear) {
        console.log('起始年份变化:', oldYear, '->', newYear);
        this.updateSubjects();
      }
    },
    
    endYear: {
      handler(newYear, oldYear) {
        console.log('结束年份变化:', oldYear, '->', newYear);
        this.updateSubjects();
      }
    }
  },

  async mounted() {
    console.log('高级搜索组件创建，开始初始化...');
    try {
      // 加载会议和年份信息
      await this.scanAvailableDatasets();
      console.log('扫描完成，会议列表:', this.conferences);
      console.log('扫描完成，年份列表:', this.years);

      // 设置默认年份范围
      if (this.years.length > 0) {
        this.startYear = this.years[this.years.length - 1]; // 最早的年份
        this.endYear = this.years[0]; // 最新的年份
      }

      // 默认选择 CVPR 会议
      if (this.conferences.includes(this.defaultConference)) {
        this.selectedConferences = [this.defaultConference];

        // 设置默认年份为最新年份
        if (this.years.length > 0) {
          // 年份数组已经按降序排列，取第一个（最新的）
          const latestYear = this.years[0];
          this.startYear = latestYear;
          this.endYear = latestYear;
          console.log(`默认选择 ${this.defaultConference} ${latestYear} 数据`);

          // 手动加载Subject（因为watch可能还没触发）
          await this.updateSubjects();

          // 执行默认搜索
          await this.searchPapers();
        }
      }
    } catch (error) {
      console.error('初始化失败:', error);
      this.error = "初始化失败。请刷新页面重试。";
    }
  },

  methods: {
    // 分页
    async handleSizeChange(newPageSize) {
      console.log('页面大小改变:', this.pageSize, '->', newPageSize);
      console.log('搜索状态:', this.searchPerformed);
      
      this.pageSize = newPageSize;
      this.currentPage = 1; // 更改每页数量后，回到第一页
      
      // 重新搜索以获取新页面大小的数据
      if (this.searchPerformed) {
        console.log('自动触发搜索...');
        await this.searchPapers();
      } else {
        console.log('未进行过搜索，不自动触发');
      }
    },

    handleSelectDefault() {
      this.selectedConferences = [this.defaultConference];
    },

    handleSelectCV() {
      this.selectedConferences = ['ICCV', 'CVPR', 'ECCV'];
    },
    handleSelectML() {
      this.selectedConferences = ['ICML', 'ICLR', 'NeurIPS'];
    },
    handleSelectCVAndML() {
      this.selectedConferences = ['ICCV', 'CVPR', 'ECCV', 'ICML', 'ICLR', 'NeurIPS'];
    },

    async handleCurrentChange(newPage) {
      this.currentPage = newPage;
      window.scrollTo(0, 0); // 切换页面后滚动到顶部
      // 重新搜索以获取新页面的数据，但不重置页码
      if (this.searchPerformed) {
        await this.searchPapers(false); // 传递 false 表示不重置页码
      }
    },
    
    // 从API加载可用的会议、年份和Subject
    async scanAvailableDatasets() {
      try {
        // 并行获取会议和年份数据
        const [conferencesResponse, yearsResponse] = await Promise.all([
          paperSearchAPI.getConferences(),
          paperSearchAPI.getYears()
        ]);

        this.conferences = conferencesResponse.conferences || [];
        this.years = yearsResponse.years || [];
        this.availableDatasets = [];
        for (const conference of this.conferences) {
          for (const year of this.years) {
            this.availableDatasets.push({
              conference,
              year,
              filename: `${conference}.${year}.json` // 保留用于显示
            });
          }
        }

        console.log('从API加载的会议:', this.conferences);
        console.log('从API加载的年份:', this.years);
        
      } catch (error) {
        console.error('从API加载会议、年份信息失败:', error);
        ElMessage.error('无法连接到API服务器，请检查后端服务是否启动');
      }
    },

    // 根据选中的会议和年份更新Subject列表
    async updateSubjects() {
      try {
        if (this.selectedConferences && this.selectedConferences.length > 0 && 
            this.startYear && this.endYear) {
          console.log('根据会议和年份筛选Subject:', this.selectedConferences, this.startYear, '-', this.endYear);
          
          // 构建年份范围数组
          const yearRange = [];
          const start = parseInt(this.startYear);
          const end = parseInt(this.endYear);
          for (let year = start; year <= end; year++) {
            yearRange.push(year.toString());
          }
          
          const subjectsResponse = await paperSearchAPI.getSubjects(this.selectedConferences, yearRange);
          this.subjects = subjectsResponse.subjects || [];
          console.log('筛选后的Subject:', this.subjects);
        } else {
          // 如果没有选择会议或年份，清空subjects
          this.subjects = [];
          console.log('没有选择会议或年份，清空Subject列表');
        }
        
        // 默认全选所有新加载的subjects
        this.selectedSubjects = [...this.subjects];
        console.log('默认全选Subject:', this.selectedSubjects);
      } catch (error) {
        console.error('更新Subject列表失败:', error);
        this.subjects = [];
        this.selectedSubjects = [];
      }
    },

    // 搜索论文 - 使用API
    async searchPapers(resetPage = true) {
      if (!this.selectedConferences || this.selectedConferences.length === 0) {
        this.error = "请至少选择一个会议";
        return;
      }

      if (!this.startYear || !this.endYear) {
        this.error = "请选择年份范围";
        return;
      }

      if (parseInt(this.startYear) > parseInt(this.endYear)) {
        this.error = "起始年份不能大于结束年份";
        return;
      }

      this.loading = true;
      this.error = null;
      this.searchPerformed = true;
      this.filteredPapers = [];
      
      // 只在新搜索时重置页码，页面切换时不重置
      if (resetPage) {
        this.currentPage = 1;
      }

      try {
        console.log('开始从API搜索论文...');
        
        // 构建搜索参数
        const searchParams = {
          selectedConferences: this.selectedConferences,
          selectedSubjects: this.selectedSubjects,
          startYear: this.startYear,
          endYear: this.endYear,
          searchQuery: this.searchQuery.trim(),
          abstractSearchQuery: this.abstractSearchQuery.trim(),
          page: this.currentPage,
          limit: this.pageSize === -1 ? 0 : this.pageSize // -1表示全部，传0给后端
        };

        console.log('搜索参数:', searchParams);

        // 使用API搜索
        const response = await paperSearchAPI.searchPapers(searchParams);
        
        if (response && response.papers) {
          // 服务器端分页：只设置当前页的数据
          this.filteredPapers = response.papers;
          this.totalPapers = response.total || 0; // 保存总数用于显示
          
          // 处理搜索关键词（用于高亮显示）
          this.processSearchKeywords();

          console.log(`从API搜索完成，当前页 ${response.papers.length} 篇，总共 ${this.totalPapers} 篇论文`);
        } else {
          console.warn('API返回的数据格式不正确:', response);
          this.filteredPapers = [];
          this.totalPapers = 0;
        }

      } catch (error) {
        console.error('API搜索论文失败:', error);
        this.error = `搜索失败: ${error.message}`;
      } finally {
        this.loading = false;
      }
    },

    // 处理搜索关键词
    processSearchKeywords() {
      // 处理标题搜索关键词
      this.searchKeywords = this.searchQuery
        ? this.searchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];

      // 处理摘要搜索关键词
      this.abstractSearchKeywords = this.abstractSearchQuery
        ? this.abstractSearchQuery.toLowerCase().split(/\s+/).filter(keyword => keyword.length > 0)
        : [];
    },

    // 重置筛选条件
    resetFilters() {
      // 清空搜索条件
      this.searchQuery = '';
      this.abstractSearchQuery = '';
      this.searchKeywords = [];
      this.abstractSearchKeywords = [];
      this.selectedSubjects = [];

      // 默认选择一个会议
      if (this.conferences.includes(this.defaultConference)) {
        this.selectedConferences = [this.defaultConference];

        // 设置默认年份为最新年份
        if (this.years.length > 0) {
          // 年份数组已经按降序排列，取第一个（最新的）
          const latestYear = this.years[0];
          this.startYear = latestYear;
          this.endYear = latestYear;


        } else {
          // 如果没有默认会议年份数据，使用全局年份范围
          if (this.years.length > 0) {
            this.startYear = this.years[this.years.length - 1]; // 最早的年份
            this.endYear = this.years[0]; // 最新的年份
          } else {
            this.startYear = '';
            this.endYear = '';
          }
        }
      } else {
        // 如果没有默认会议，清空会议选择
        this.selectedConferences = [];

        // 使用全局年份范围
        if (this.years.length > 0) {
          this.startYear = this.years[this.years.length - 1]; // 最早的年份
          this.endYear = this.years[0]; // 最新的年份
        } else {
          this.startYear = '';
          this.endYear = '';
        }
      }

      // 保留已加载的数据，但清空过滤结果
      this.filteredPapers = [];
      this.searchPerformed = false;
      this.error = null;

      // 重置到第一页
      this.currentPage = 1;
    },

    toggleAbstract(index) {
      // Vue 3 中直接修改对象属性即可触发响应式更新
      this.expandedAbstracts[index] = !this.expandedAbstracts[index];
    },

    handleToggleAbstract(index, isExpanded) {
      // 从子组件接收展开/收起事件
      this.expandedAbstracts[index] = isExpanded;
    },

    expandAllAbstracts() {
      // 切换摘要的展开/收起状态
      this.expandAll.abstract = !this.expandAll.abstract;
      
      // 如果展开摘要，则确保解读是收起的
      if (this.expandAll.abstract) {
        this.expandAll.gemini = false;
      }
      
      // 强制更新，确保子组件接收到变化
      this.$forceUpdate();
    },

    expandAllGemini() {
      // 切换解读的展开/收起状态
      this.expandAll.gemini = !this.expandAll.gemini;
      
      // 如果展开解读，则确保摘要是收起的
      if (this.expandAll.gemini) {
        this.expandAll.abstract = false;
      }
      
      // 强制更新，确保子组件接收到变化
      this.$forceUpdate();
    },

    // Subject选择变化处理
    async handleSubjectChange() {
      console.log('Subject选择变化:', this.selectedSubjects);
      // 自动触发搜索
      if (this.searchPerformed) {
        await this.searchPapers();
      }
    },

    // 全选/取消全选Subject
    toggleAllSubjects() {
      if (this.selectedSubjects.length === this.subjects.length) {
        // 当前是全选状态，改为取消全选
        this.selectedSubjects = [];
      } else {
        // 当前不是全选状态，改为全选
        this.selectedSubjects = [...this.subjects];
      }
    },

    // 清空Subject选择
    clearSubjects() {
      this.selectedSubjects = [];
    },
  }
}
</script>

<style>

.filter-container{
  padding: 20px var(--content-padding, 0);
  margin-bottom: 20px;
  margin-top: 0;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}

/* Add paper-list-container style for consistent alignment */
.paper-list-container {
  padding: 0;
  width: var(--content-width);
  max-width: var(--content-max-width);
  margin-left: auto;
  margin-right: auto;
  box-sizing: border-box;
}

/* Add specific rules for perfect alignment */
.paper-list-container > div {
  padding: 0;
  margin: 0;
  width: 100%;
  box-sizing: border-box;
}

/* Ensure no extra margins or padding in result items */
.result-item-container {
  padding: 0;
  margin: 0;
  box-sizing: border-box;
}

/* 统一行高 */
.filter-container .el-button--default,
.filter-container .el-radio-button__inner,
.filter-container .el-input__wrapper {
  line-height: 1;
  height: 32px;
}

/* 确保顶部控件行完美对齐 */
.top-controls-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  height: 32px;
}

/* 每个控件容器垂直居中 */
.control-container {
  display: flex;
  align-items: center;
  height: 32px;
}

.expand-row{
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 控件包装容器，确保高度一致 */
.control-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  width: 100%;
}

/* 年份选择列样式 */
.year-select-col {
  display: flex;
  align-items: center;
  height: 32px;
  padding: 0;
}

/* 确保所有 Element Plus 表单控件的包装器都有一致的高度和对齐方式 */
.el-select .el-input__wrapper,
.el-input .el-input__wrapper {
  height: 32px !important;
  box-sizing: border-box !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  display: flex !important;
  align-items: center !important;
}

/* 确保下拉选择器的高度和行高一致 */
.el-select {
  width: 100%;
}

/* 精确设置表单组件的尺寸 */
.perfectly-aligned-control {
  width: 100%;
}

/* 确保输入框内部元素垂直居中 */
.el-input__inner {
  height: 30px !important;
  line-height: 30px !important;
  margin: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* 去除排序按钮的边框 */
.sort-direction-btn {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: 16px;
}

/* 年份区间分隔符样式 */
.separator-text {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

/* 展开按钮样式 */
.expand-row .el-button {
  width: 100%;
  height: 28px;
  padding: 0;
  margin: 0;
  font-size: 13px;
  transition: all 0.3s ease;
  border: none;
  background: transparent;
  box-shadow: none;
  color: #333;
}

.expand-button {
  position: relative;
}

/* 覆盖 Element Plus 的内部样式 */
.expand-button .el-button__content {
  margin-left: 0;
  padding-left: 0;
  justify-content: flex-start;
}

.text-left {
  text-align: left !important;
  padding-left: 0 !important;
}

/* 所有激活按钮特效已移除 */

/* 为了使按钮看起来更像第二张图中所示的效果 */
.expand-button {
  border: 1px dashed transparent !important;
  margin: 0;
}

/* 分隔符容器样式 */
.separator-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  padding: 0;
}

/* 年份范围行样式 */
.year-range-row {
  display: flex;
  align-items: center;
  height: 32px;
  margin: 0;
}

/* 水平对齐筛选按钮 */
.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

/* 确保下拉框和按钮组的高度一致 */
.el-select,
.el-radio-group,
.el-input,
.el-button {
  height: 32px !important;
  line-height: 32px !important;
}

/* 精确设置输入框包装器的高度 */
.el-input__wrapper {
  height: 32px !important;
  line-height: 32px !important;
  padding: 0 11px !important;
}

/* 确保下拉框的高度一致 */
.el-select__wrapper {
  height: 32px !important;
  line-height: 32px !important;
}

/* 让按钮和图标垂直居中 */
.el-button {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 确保单选按钮组和按钮在同一水平线上 */
.el-radio-group {
  display: flex;
  align-items: center;
}

/* 确保无线电按钮内容垂直居中 */
.el-radio-button__inner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 标题对齐 */
.search-results-info {
  display: flex;
  align-items: center;
}

/* 让排序控件严格在同一水平线上对齐 */
.control-align-row {
  display: flex;
  align-items: center;
}

.control-align-row .el-radio-button,
.control-align-row .el-button {
  height: 32px;
  box-sizing: border-box;
}

/* 确保单选按钮和排序按钮的内容都处于中央位置 */
.control-align-row .el-radio-button__inner,
.control-align-row .el-button {
  padding: 0 12px;
  line-height: 30px;
  vertical-align: middle;
}

/* 强制文本完全贴左 */
.expand-row .el-button span {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0;
  margin: 0;
}

/* 覆盖按钮的默认边距 */
.expand-row .el-button--default {
  padding-left: 0 !important;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

/* 确保文字没有边距 */
.active-button > span {
  margin-left: 0;
}

/* 自定义按钮容器样式 */
.custom-button-wrapper {
  position: relative;
  display: block;
  padding: 0; /* 完全去除所有padding */
  cursor: pointer;
  border: none; /* 完全移除边框 */
  transition: all 0.3s;
  border-radius: 0; /* 移除圆角 */
  line-height: 1.5;
  height: 32px;
  box-sizing: border-box;
}

/* 激活状态的容器样式 - 不使用任何特效 */
/* 确保激活状态下的文本贴左 */
.active-wrapper .button-text {
  left: 0;
  padding-left: 0;
}

/* 按钮文字样式 */
.button-text {
  display: flex;
  align-items: center; /* 垂直居中 */
  text-align: left;
  padding: 0;
  margin: 0;
  padding-left: 0; /* 确保没有左padding */
  width: 100%;
  line-height: 30px; /* 与按钮高度一致，实现垂直居中 */
  white-space: nowrap; /* 防止文本换行 */
  position: absolute; /* 使用绝对定位确保完全靠左 */
  left: 0; /* 确保文本完全靠左边框 */
  top: 0; /* 顶部对齐 */
  height: 100%; /* 占满整个高度 */
  border-left: 0; /* 确保左边没有边框 */
}

/* 确保文字完全没有padding */
.no-padding-text {
  padding: 0;
  margin: 0;
  display: block;
  text-align: left;
}

/* 搜索按钮样式 */
.search-button {
  width: 100%;
  height: 32px; /* 与input框高度一致 */
  border-radius: 4px; /* 与input框圆角一致 */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  font-size: 14px;
}

.search-button .el-icon {
  font-size: 16px;
}

.search-tip {
  font-size: 12px;
  color: #909399;
  display: block;
  text-align: center;
}

/* Subject筛选行样式 */
.subject-filter-row {
  margin-bottom: 12px;
  padding: 0;
}

.subject-filter-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0;
  min-height: 32px;
}

/* 统一按钮样式 */
.unified-button {
  height: 32px !important;
  padding: 0 8px !important;
  margin-right: 8px !important;
  border: 1px solid #f0e8d8 !important;
  border-radius: 4px !important;
  background: linear-gradient(135deg, #fcfbf9 0%, #f9f7f3 100%) !important;
  color: #5d4e37 !important;
  font-size: 12px !important;
  font-weight: 400 !important;
  line-height: 1.4 !important;
  width: 80px !important; 
  min-width: 72px !important;
  max-width: 100px !important;
  box-sizing: border-box !important;
  transition: all 0.2s ease !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: nowrap !important;
  text-align: center !important;
  overflow: hidden !important;
}

.unified-button:hover {
  background: linear-gradient(135deg, #faf8f5 0%, #f6f2ed 100%) !important;
  border-color: #e8dcc6 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 2px 6px rgba(139, 121, 94, 0.08) !important;
  color: #5d4e37 !important;
}

.unified-button:active {
  transform: translateY(0) !important;
  box-shadow: 0 1px 3px rgba(139, 121, 94, 0.12) !important;
}

.unified-button:focus {
  border-color: #d4c5a9 !important;
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(139, 121, 94, 0.1) !important;
}

/* 快速选择行样式 */
.quick-select-row {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0;
  min-height: 32px;
  box-sizing: border-box;
}

/* 主题选择行样式 */
.subject-selection-row {
  margin-top: 8px;
}

/* 确保所有按钮行都有相同的基线对齐 */
.quick-select-row, 
.subject-filter-container {
  display: flex;
  align-items: center;
  min-height: 32px;
}

.subject-label {
  font-weight: normal;
  color: #5C4B3C;
  white-space: nowrap;
  min-width: 60px;
  margin-right: 8px;
  line-height: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  box-sizing: border-box;
}

.subject-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  align-items: center;
}

/* 重新设计复选框样式 - 统一与按钮一致的卡片风格 */
.subject-checkbox {
  margin-right: 8px !important;
  margin-bottom: 8px !important;
  background: linear-gradient(135deg, #fcfbf9 0%, #f9f7f3 100%) !important;
  border: 1px solid #f0e8d8 !important;
  border-radius: 4px !important;
  padding: 0 8px !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
  height: 32px !important;
  display: inline-flex !important;
  align-items: center !important;
  font-size: 12px !important;
  box-sizing: border-box !important;
  min-width: fit-content !important;
  white-space: nowrap !important;
}

.subject-checkbox:hover {
  background: linear-gradient(135deg, #faf8f5 0%, #f6f2ed 100%) !important;
  border-color: #e8dcc6 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 2px 6px rgba(139, 121, 94, 0.08) !important;
}

.subject-checkbox .el-checkbox__input.is-checked + .el-checkbox__label {
  color: #5d4e37 !important;
  font-weight: 400 !important;
}

.subject-checkbox.is-checked {
  background: linear-gradient(135deg, #f7f3ee 0%, #f2ebe1 100%) !important;
  border-color: #d4c5a9 !important;
  box-shadow: 0 2px 6px rgba(139, 121, 94, 0.12) !important;
}

.subject-checkbox .el-checkbox__label {
  font-size: 12px !important;
  color: #5d4e37 !important;
  padding-left: 4px !important;
  font-weight: 400 !important;
  line-height: 1.4 !important;
  margin: 0 !important;
}

.subject-checkbox .el-checkbox__input {
  margin-right: 4px !important;
  margin-top: 0 !important;
}

/* 优化复选框内部样式 */
.subject-checkbox .el-checkbox__input .el-checkbox__inner {
  width: 12px !important;
  height: 12px !important;
  border-radius: 2px !important;
  border: 1px solid #d4c5a9 !important;
  background: #fff !important;
  transition: all 0.2s ease !important;
}

.subject-checkbox .el-checkbox__input.is-checked .el-checkbox__inner {
  background: #8b795e !important;
  border-color: #8b795e !important;
}

.subject-checkbox .el-checkbox__input.is-checked .el-checkbox__inner::after {
  border-color: #fff !important;
  border-width: 1px !important;
  width: 3px !important;
  height: 6px !important;
  left: 3px !important;
  top: 1px !important;
}

.toggle-all-btn {
  margin-left: 0 !important;
}

.toggle-all-btn:hover {
  /* 继承 unified-button 的 hover 样式 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .subject-filter-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .subject-label {
    margin-right: 0;
    margin-bottom: 5px;
    font-size: 14px;
    color: #000000;
  }
  
  .subject-checkbox-group {
    width: 100%;
    justify-content: flex-start;
  }
  
  .toggle-all-btn {
    margin-left: 0;
    align-self: flex-end;
    font-size: 12px;
    color: #000000;
    height: 32px;
    min-height: 32px;
  }
}
</style>