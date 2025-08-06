#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关API路由
"""

import json
import hashlib
import time
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from loguru import logger

auth_bp = Blueprint('auth', __name__)

# 文件路径
USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'users.json')
ADMIN_FILE = os.path.join(os.path.dirname(__file__), '..', 'admin.json')

def load_users():
    """加载用户数据"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"加载用户数据失败: {e}")
        return {}

def save_users(users):
    """保存用户数据"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")
        return False

def load_admin_status():
    """加载管理员状态"""
    try:
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"admin_created": False}
    except Exception as e:
        logger.error(f"加载管理员状态失败: {e}")
        return {"admin_created": False}

def save_admin_status(status):
    """保存管理员状态"""
    try:
        with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存管理员状态失败: {e}")
        return False

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@auth_bp.route('/check-admin', methods=['GET'])
def check_admin():
    """检查是否已创建管理员"""
    try:
        admin_status = load_admin_status()
        return jsonify({
            'success': True,
            'admin_created': admin_status.get('admin_created', False)
        })
    except Exception as e:
        logger.error(f"检查管理员状态失败: {e}")
        return jsonify({
            'success': False,
            'error': '检查管理员状态失败'
        }), 500

@auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    """创建管理员账号"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'success': False,
                'error': '密码不能为空'
            }), 400
        
        # 检查是否已存在管理员
        admin_status = load_admin_status()
        if admin_status.get('admin_created', False):
            return jsonify({
                'success': False,
                'error': '管理员账号已存在'
            }), 400
        
        # 创建管理员账号
        users = load_users()
        admin_user = {
            'username': 'admin',
            'password_hash': hash_password(password),
            'role': 'admin',
            'created_at': time.time(),
            'last_login': None
        }
        
        users['admin'] = admin_user
        
        if save_users(users) and save_admin_status({'admin_created': True}):
            logger.info("管理员账号创建成功")
            return jsonify({
                'success': True,
                'message': '管理员账号创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存管理员账号失败'
            }), 500
            
    except Exception as e:
        logger.error(f"创建管理员失败: {e}")
        return jsonify({
            'success': False,
            'error': '创建管理员失败'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        users = load_users()
        user = users.get(username)
        
        if not user or user['password_hash'] != hash_password(password):
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            }), 401
        
        # 更新最后登录时间
        user['last_login'] = time.time()
        save_users(users)
        
        # 设置会话
        session['user_id'] = username
        session['user_role'] = user['role']
        
        logger.info(f"用户 {username} 登录成功")
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({
            'success': False,
            'error': '登录失败'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
    except Exception as e:
        logger.error(f"登出失败: {e}")
        return jsonify({
            'success': False,
            'error': '登出失败'
        }), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """检查用户认证状态"""
    try:
        user_id = session.get('user_id')
        user_role = session.get('user_role')
        
        if not user_id:
            return jsonify({
                'success': False,
                'authenticated': False
            })
        
        users = load_users()
        user = users.get(user_id)
        
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'authenticated': False
            })
        
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        logger.error(f"检查认证状态失败: {e}")
        return jsonify({
            'success': False,
            'error': '检查认证状态失败'
        }), 500



@auth_bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表（仅管理员）"""
    try:
        # 检查session认证
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        # 如果session中没有认证信息，检查请求头中的用户名
        if not user_role and not user_id:
            # 检查是否有用户名在请求头中（用于file://协议）
            username = request.headers.get('X-Username')
            if username:
                users = load_users()
                user = users.get(username)
                if user and user['role'] == 'admin':
                    user_role = 'admin'
                    user_id = username
        
        if user_role != 'admin':
            return jsonify({
                'success': False,
                'error': '权限不足'
            }), 403
        
        users = load_users()
        user_list = []
        
        for username, user_data in users.items():
            if username != 'admin':  # 不返回管理员密码信息
                user_list.append({
                    'username': user_data['username'],
                    'role': user_data['role'],
                    'created_at': user_data.get('created_at'),
                    'last_login': user_data.get('last_login')
                })
        
        return jsonify({
            'success': True,
            'users': user_list
        })
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取用户列表失败'
        }), 500

@auth_bp.route('/users', methods=['POST'])
def create_user():
    """创建新用户（仅管理员）"""
    try:
        # 检查session认证
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        logger.info(f"创建用户 - Session认证: user_role={user_role}, user_id={user_id}")
        
        # 如果session中没有认证信息，检查请求头中的用户名
        if not user_role and not user_id:
            # 检查是否有用户名在请求头中（用于file://协议）
            username = request.headers.get('X-Username')
            logger.info(f"创建用户 - 检查X-Username请求头: {username}")
            
            if username:
                users = load_users()
                user = users.get(username)
                logger.info(f"创建用户 - 查找用户 {username}: {user}")
                
                if user and user['role'] == 'admin':
                    user_role = 'admin'
                    user_id = username
                    logger.info(f"创建用户 - 通过X-Username认证成功: {username}")
                else:
                    logger.warning(f"创建用户 - 用户 {username} 不存在或不是管理员")
            else:
                logger.warning("创建用户 - 没有X-Username请求头")
        
        logger.info(f"创建用户 - 最终权限检查: user_role={user_role}")
        
        if user_role != 'admin':
            logger.error(f"创建用户 - 权限不足: user_role={user_role}")
            return jsonify({
                'success': False,
                'error': '权限不足'
            }), 403
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        if role not in ['user', 'admin']:
            return jsonify({
                'success': False,
                'error': '角色只能是user或admin'
            }), 400
        
        users = load_users()
        
        if username in users:
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            }), 400
        
        new_user = {
            'username': username,
            'password_hash': hash_password(password),
            'role': role,
            'created_at': time.time(),
            'last_login': None
        }
        
        users[username] = new_user
        
        if save_users(users):
            logger.info(f"用户 {username} 创建成功")
            return jsonify({
                'success': True,
                'message': '用户创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存用户失败'
            }), 500
            
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        return jsonify({
            'success': False,
            'error': '创建用户失败'
        }), 500

@auth_bp.route('/users/<username>', methods=['GET'])
def get_user(username):
    """获取单个用户信息（仅管理员）"""
    try:
        # 检查session认证
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        # 如果session中没有认证信息，检查请求头中的用户名
        if not user_role and not user_id:
            # 检查是否有用户名在请求头中（用于file://协议）
            header_username = request.headers.get('X-Username')
            if header_username:
                users = load_users()
                user = users.get(header_username)
                if user and user['role'] == 'admin':
                    user_role = 'admin'
                    user_id = header_username
        
        if user_role != 'admin':
            return jsonify({
                'success': False,
                'error': '权限不足'
            }), 403
        
        users = load_users()
        
        # 首先尝试直接通过键查找
        user_data = users.get(username)
        
        # 如果没找到，尝试通过用户名查找
        if not user_data:
            for key, user in users.items():
                if user.get('username') == username:
                    user_data = user
                    break
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        # 不返回密码信息
        user_info = {
            'username': user_data['username'],
            'role': user_data['role'],
            'created_at': user_data.get('created_at'),
            'last_login': user_data.get('last_login')
        }
        
        return jsonify({
            'success': True,
            'user': user_info
        })
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取用户信息失败'
        }), 500

@auth_bp.route('/users/<username>', methods=['PUT'])
def update_user(username):
    """更新用户信息（仅管理员）"""
    try:
        # 检查session认证
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        # 如果session中没有认证信息，检查请求头中的用户名
        if not user_role and not user_id:
            # 检查是否有用户名在请求头中（用于file://协议）
            header_username = request.headers.get('X-Username')
            if header_username:
                users = load_users()
                user = users.get(header_username)
                if user and user['role'] == 'admin':
                    user_role = 'admin'
                    user_id = header_username
        
        if user_role != 'admin':
            return jsonify({
                'success': False,
                'error': '权限不足'
            }), 403
        
        data = request.get_json()
        new_password = data.get('password')
        new_role = data.get('role')
        
        users = load_users()
        
        # 首先尝试直接通过键查找
        user_key = username
        user_data = users.get(username)
        
        # 如果没找到，尝试通过用户名查找
        if not user_data:
            for key, user in users.items():
                if user.get('username') == username:
                    user_key = key
                    user_data = user
                    break
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        if new_password:
            users[user_key]['password_hash'] = hash_password(new_password)
        
        if new_role and new_role in ['user', 'admin']:
            users[user_key]['role'] = new_role
        
        if save_users(users):
            logger.info(f"用户 {username} 更新成功")
            return jsonify({
                'success': True,
                'message': '用户更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存用户失败'
            }), 500
            
    except Exception as e:
        logger.error(f"更新用户失败: {e}")
        return jsonify({
            'success': False,
            'error': '更新用户失败'
        }), 500

@auth_bp.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    """删除用户（仅管理员）"""
    try:
        # 检查session认证
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        
        # 如果session中没有认证信息，检查请求头中的用户名
        if not user_role and not user_id:
            # 检查是否有用户名在请求头中（用于file://协议）
            header_username = request.headers.get('X-Username')
            if header_username:
                users = load_users()
                user = users.get(header_username)
                if user and user['role'] == 'admin':
                    user_role = 'admin'
                    user_id = header_username
        
        if user_role != 'admin':
            return jsonify({
                'success': False,
                'error': '权限不足'
            }), 403
        
        if username == 'admin':
            return jsonify({
                'success': False,
                'error': '不能删除管理员账号'
            }), 400
        
        users = load_users()
        
        # 首先尝试直接通过键查找
        user_key = username
        user_data = users.get(username)
        
        # 如果没找到，尝试通过用户名查找
        if not user_data:
            for key, user in users.items():
                if user.get('username') == username:
                    user_key = key
                    user_data = user
                    break
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404
        
        del users[user_key]
        
        if save_users(users):
            logger.info(f"用户 {username} 删除成功")
            return jsonify({
                'success': True,
                'message': '用户删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '保存用户失败'
            }), 500
            
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        return jsonify({
            'success': False,
            'error': '删除用户失败'
        }), 500 