/**
 * PaperSearch API 服务类
 * 用于与后端Flask API进行通信
 */

class PaperSearchAPI {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
  }

  /**
   * 发送HTTP请求的通用方法
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      console.log(`请求API: ${url}`, options.params || '');
      
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        let errorData = {};
        try {
          errorData = await response.json();
        } catch (e) {
          console.warn('无法解析错误响应为JSON:', e);
        }
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      // 检查响应内容是否为空
      const responseText = await response.text();
      if (!responseText.trim()) {
        throw new Error('服务器返回空响应');
      }

      let data;
      try {
        data = JSON.parse(responseText);
      } catch (e) {
        console.error('JSON解析失败，响应内容:', responseText);
        throw new Error('服务器返回的不是有效的JSON格式');
      }
      
      console.log(`API响应成功: ${url}`, data);
      return data;
      
    } catch (error) {
      console.error(`API请求失败: ${url}`, error);
      throw error;
    }
  }

  /**
   * 构建查询参数
   */
  buildQueryParams(params) {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v));
        } else {
          searchParams.append(key, value);
        }
      }
    });
    
    return searchParams.toString();
  }

  /**
   * 健康检查
   */
  async healthCheck() {
    return this.request('/health');
  }

  /**
   * 获取论文数据
   * @param {Object} params - 查询参数
   * @param {Array} params.conferences - 会议列表
   * @param {Array} params.years - 年份列表
   * @param {Array} params.subjects - Subject列表
   * @param {string} params.search_title - 标题搜索关键词
   * @param {string} params.search_abstract - 摘要搜索关键词
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量（0表示不限制）
   */
  async getPapers(params = {}) {
    const queryString = this.buildQueryParams({
      conference: params.conferences || [],
      year: params.years || [],
      subject: params.subjects || [],
      search_title: params.search_title || '',
      search_abstract: params.search_abstract || '',
      page: params.page || 1,
      limit: params.limit || 0
    });

    const endpoint = `/api/papers${queryString ? '?' + queryString : ''}`;
    return this.request(endpoint);
  }

  /**
   * 获取可用会议列表
   */
  async getConferences() {
    return this.request('/api/conferences');
  }

  /**
   * 获取可用年份列表
   */
  async getYears() {
    return this.request('/api/years');
  }

  /**
   * 获取Subject列表，可根据会议和年份筛选
   * @param {Array} conferences - 会议列表，例如: ['CVPR', 'ICCV']
   * @param {Array} years - 年份列表，例如: ['2024', '2025']
   */
  async getSubjects(conferences = null, years = null) {
    const params = {};
    if (conferences && conferences.length > 0) {
      params.conferences = conferences.join(',');
    }
    if (years && years.length > 0) {
      params.years = years.join(',');
    }
    
    if (Object.keys(params).length > 0) {
      const queryString = this.buildQueryParams(params);
      return this.request(`/api/subjects?${queryString}`);
    }
    return this.request('/api/subjects');
  }

  /**
   * 获取统计信息
   */
  async getStats() {
    return this.request('/api/stats');
  }

  /**
   * 批量获取指定会议和年份的论文数据
   * @param {Array} datasets - 数据集列表，格式: [{conference: 'CVPR', year: '2024'}, ...]
   */
  async getPapersByDatasets(datasets) {
    if (!datasets || datasets.length === 0) {
      return { papers: [], total: 0 };
    }

    // 提取所有唯一的会议和年份
    const conferences = [...new Set(datasets.map(d => d.conference))];
    const years = [...new Set(datasets.map(d => d.year))];

    return this.getPapers({
      conferences,
      years,
      limit: 0 // 获取所有数据
    });
  }

  /**
   * 搜索论文
   * @param {Object} searchParams - 搜索参数
   */
  async searchPapers(searchParams) {
    const {
      selectedConferences = [],
      selectedSubjects = [],
      startYear = '',
      endYear = '',
      searchQuery = '',
      abstractSearchQuery = '',
      page = 1,
      limit = 0
    } = searchParams;

    // 构建年份范围
    const years = [];
    if (startYear && endYear) {
      const start = parseInt(startYear);
      const end = parseInt(endYear);
      for (let year = start; year <= end; year++) {
        years.push(year.toString());
      }
    }

    return this.getPapers({
      conferences: selectedConferences,
      years: years,
      subjects: selectedSubjects,
      search_title: searchQuery,
      search_abstract: abstractSearchQuery,
      page: page,
      limit: limit
    });
  }
}

// 创建全局API实例
const paperSearchAPI = new PaperSearchAPI();

// ES6模块导出
export default paperSearchAPI;
export { PaperSearchAPI, paperSearchAPI };

// 也可以作为全局变量使用
if (typeof window !== 'undefined') {
  window.PaperSearchAPI = PaperSearchAPI;
  window.paperSearchAPI = paperSearchAPI;
}
