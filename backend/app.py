#!/usr/bin/env python3
"""
Flask API for PaperSearch - 从MongoDB加载论文数据
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import os
import logging
from datetime import datetime
import math
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

# 数据库配置
class Config:
    # 从环境变量读取MongoDB配置，如果没有则使用默认值
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_USER = os.getenv('MONGO_USER', 'lxg')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '@Zero1008')
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'papersearch')
    
    # 日志配置
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_RETENTION_DAYS = os.getenv('LOG_RETENTION_DAYS', '30 days')
    LOG_MAX_SIZE = os.getenv('LOG_MAX_SIZE', '100 MB')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # CORS配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    # Flask配置
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

def get_logger(logs_dir=None, log_name="log"):
    from loguru import logger
    from datetime import datetime
    import sys
    
    # 使用配置文件中的日志目录
    if logs_dir is None:
        logs_dir = Config.LOG_DIR
    
    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name:<4}</cyan>:<cyan>{function:<15}</cyan>:<cyan>{line:<4}</cyan> | "
        "<level>{message}</level>"
    )
    current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_name = f"{logs_dir}/{log_name}_{current_date}.log"
    logger.add(log_name, format=log_format, level=Config.LOG_LEVEL, 
               retention=Config.LOG_RETENTION_DAYS, rotation=Config.LOG_MAX_SIZE)
    logger.add(sys.stderr, format=log_format, level=Config.LOG_LEVEL)
    return logger

logger = get_logger(log_name="logs")

app = Flask(__name__)
CORS(app, origins=Config.CORS_ORIGINS)  # 允许配置的来源跨域请求

# 初始化MongoDB连接
try:
    # 先尝试无认证连接
    client = MongoClient(host=Config.MONGO_HOST, port=Config.MONGO_PORT)    
    
    db = client[Config.MONGO_DATABASE]
    papers_collection = db['papers']
    
    # 测试连接
    client.admin.command('ping')
    logger.info("成功连接到MongoDB数据库")
    
except Exception as e:
    logger.error(f"连接MongoDB失败: {e}")
    papers_collection = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        if papers_collection is not None:
            # 测试数据库连接
            count = papers_collection.count_documents({})
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "total_papers": count,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "database": "disconnected",
                "timestamp": datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/papers', methods=['GET'])
def get_papers():
    """获取论文数据API"""
    try:
        if papers_collection is None:
            return jsonify({"error": "数据库连接失败"}), 500
        
        # 获取查询参数
        conferences = request.args.getlist('conference')
        years = request.args.getlist('year')
        subjects = request.args.getlist('subject')  # 新增：Subject筛选
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 0))  # 0表示不限制
        search_title = request.args.get('search_title', '')
        search_abstract = request.args.get('search_abstract', '')
        
        # 构建查询条件
        query = {}
        
        if conferences:
            query['conference'] = {'$in': conferences}
        
        if years:
            # 年份在数据库中存储为字符串，直接使用字符串比较
            query['year'] = {'$in': years}
        
        if subjects:
            # Subject筛选：支持部分匹配，例如筛选"Main"会匹配"CVPR.2024 - Main"
            subject_conditions = []
            for subject in subjects:
                subject_conditions.append({
                    'subjects': {'$regex': subject, '$options': 'i'}
                })
            if len(subject_conditions) == 1:
                query.update(subject_conditions[0])
            else:
                query['$or'] = subject_conditions
        
        # 文本搜索条件 (v4 - 使用 $regex 并支持多关键字 AND 搜索)
        text_conditions = []
        
        if search_title:
            # 将搜索字符串按空格分割成多个关键字
            title_keywords = search_title.strip().split()
            if title_keywords:
                # 为每个关键字创建一个独立的 regex 条件，并放入一个 $and 数组
                title_and_conditions = [
                    {'title': {'$regex': keyword, '$options': 'i'}}
                    for keyword in title_keywords
                ]
                text_conditions.extend(title_and_conditions)

        if search_abstract:
            # 对摘要字段执行相同的逻辑
            abstract_keywords = search_abstract.strip().split()
            if abstract_keywords:
                abstract_and_conditions = [
                    {'abstract': {'$regex': keyword, '$options': 'i'}}
                    for keyword in abstract_keywords
                ]
                text_conditions.extend(abstract_and_conditions)
        
        if text_conditions:
            # 将所有条件（来自标题和摘要）用一个顶层的 $and 连接起来
            query['$and'] = text_conditions
        
        logger.info(f"查询条件: {query}")
        
        # 计算总数
        total = papers_collection.count_documents(query)
        
        # 构建查询
        cursor = papers_collection.find(query, {'_id': 0})  # 排除MongoDB的_id字段
        
        # 实现嵌套排序：
        # 1. 首先按年份降序（2025 → 2024 → 2023 → 2022）
        # 2. 在相同年份内，按会议名称升序（CVPR → ICCV）
        # 3. 在相同会议和年份内，按标题升序
        cursor = cursor.sort([('year', -1), ('conference', 1), ('title', 1)])
        
        # 分页
        if limit > 0:
            skip = (page - 1) * limit
            cursor = cursor.skip(skip).limit(limit)
        
        # 获取结果
        papers = list(cursor)
        
        # 数据后处理
        for paper in papers:
            # 确保字段类型正确
            if 'year' in paper and isinstance(paper['year'], int):
                paper['year'] = str(paper['year'])
            if 'order' in paper and not isinstance(paper['order'], int):
                try:
                    paper['order'] = int(paper['order'])
                except (ValueError, TypeError):
                    paper['order'] = 0
        
        # 构建响应
        response = {
            'papers': papers,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': math.ceil(total / limit) if limit > 0 else 1,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"返回 {len(papers)} 篇论文，总共 {total} 篇")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"获取论文数据失败: {e}")
        return jsonify({"error": f"获取数据失败: {str(e)}"}), 500

@app.route('/api/conferences', methods=['GET'])
def get_conferences():
    """获取可用会议列表"""
    try:
        if papers_collection is None:
            return jsonify({"error": "数据库连接失败"}), 500
        
        # 获取所有不同的会议名称
        conferences = papers_collection.distinct('conference')
        conferences = sorted([conf for conf in conferences if conf])  # 过滤空值并排序
        
        return jsonify({
            'conferences': conferences,
            'count': len(conferences),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取会议列表失败: {e}")
        return jsonify({"error": f"获取会议列表失败: {str(e)}"}), 500

@app.route('/api/years', methods=['GET'])
def get_years():
    """获取可用年份列表"""
    try:
        if papers_collection is None:
            return jsonify({"error": "数据库连接失败"}), 500
        
        # 获取所有不同的年份
        years = papers_collection.distinct('year')
        
        # 处理年份数据，确保为字符串格式并排序
        processed_years = []
        for year in years:
            if year:
                if isinstance(year, int):
                    processed_years.append(str(year))
                elif isinstance(year, str) and year.isdigit():
                    processed_years.append(year)
        
        processed_years = sorted(processed_years, reverse=True)  # 降序排列
        
        return jsonify({
            'years': processed_years,
            'count': len(processed_years),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取年份列表失败: {e}")
        return jsonify({"error": f"获取年份列表失败: {str(e)}"}), 500

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """获取可用Subject列表，可根据会议和年份筛选"""
    try:
        if papers_collection is None:
            return jsonify({"error": "数据库连接失败"}), 500
        
        # 获取查询参数
        conferences = request.args.get('conferences')
        years = request.args.get('years')
        
        # 构建查询条件
        query = {}
        if conferences:
            conference_list = [conf.strip() for conf in conferences.split(',') if conf.strip()]
            if conference_list:
                query['conference'] = {'$in': conference_list}
        
        if years:
            year_list = [year.strip() for year in years.split(',') if year.strip()]
            if year_list:
                query['year'] = {'$in': year_list}
        
        # 获取筛选后的subjects
        if query:
            # 根据会议和年份筛选subjects
            all_subjects = papers_collection.distinct('subjects', query)
        else:
            # 获取所有subjects
            all_subjects = papers_collection.distinct('subjects')
        
        # 处理subjects数据，提取常见的类型
        subject_types = set()
        for subject in all_subjects:
            if subject and isinstance(subject, str):
                # 提取类型，例如从"CVPR.2024 - Main"中提取"Main"
                if ' - ' in subject:
                    subject_type = subject.split(' - ')[-1].strip()
                    if subject_type:
                        subject_types.add(subject_type)
                else:
                    # 如果没有" - "分隔符，直接使用整个字符串
                    subject_types.add(subject.strip())
        
        # 转换为列表并排序
        processed_subjects = sorted(list(subject_types))
        
        return jsonify({
            'subjects': processed_subjects,
            'count': len(processed_subjects),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取Subject列表失败: {e}")
        return jsonify({"error": f"获取Subject列表失败: {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        if papers_collection is None:
            return jsonify({"error": "数据库连接失败"}), 500
        
        # 总论文数
        total_papers = papers_collection.count_documents({})
        
        # 按会议统计
        conference_stats = list(papers_collection.aggregate([
            {
                '$group': {
                    '_id': '$conference',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]))
        
        # 按年份统计
        year_stats = list(papers_collection.aggregate([
            {
                '$group': {
                    '_id': '$year',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id': -1}
            }
        ]))
        
        # 按会议和年份统计
        conference_year_stats = list(papers_collection.aggregate([
            {
                '$group': {
                    '_id': {
                        'conference': '$conference',
                        'year': '$year'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {
                    '_id.conference': 1,
                    '_id.year': -1
                }
            }
        ]))
        
        return jsonify({
            'total_papers': total_papers,
            'conference_stats': conference_stats,
            'year_stats': year_stats,
            'conference_year_stats': conference_year_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({"error": f"获取统计信息失败: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "接口不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    # 使用Config中的配置参数
    port = Config.FLASK_PORT
    debug = Config.FLASK_DEBUG
    host = Config.FLASK_HOST
    
    logger.info(f"启动Flask应用，主机: {host}, 端口: {port}, 调试模式: {debug}")
    logger.info(f"MongoDB连接: {Config.MONGO_HOST}:{Config.MONGO_PORT}/{Config.MONGO_DATABASE}")
    logger.info(f"CORS允许来源: {Config.CORS_ORIGINS}")
    
    app.run(host=host, port=port, debug=debug)
