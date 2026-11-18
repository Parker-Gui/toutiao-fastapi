import { defineStore } from 'pinia';
import request from '../utils/request';

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: '',
    isLogin: false,
    userBio: '这是我的个人简介'
  }),
  
  getters: {
    getUserInfo: (state) => state.userInfo,
    getToken: (state) => state.token,
    getLoginStatus: (state) => state.isLogin,
    getUserBio: (state) => state.userInfo?.bio || state.userBio
  },
  
  actions: {
    async login(userData) {
      try {
        // 发送登录请求
        const res = await request.post('/api/user/login', {
          username: userData.username,
          password: userData.password
        });
        
        // 检查响应状态
        if (res.data) {
          // 登录成功
          const userInfo = res.data.userInfo;
          const token = res.data.token;
          
          this.userInfo = userInfo;
          this.token = token;
          this.isLogin = true;
          
          return {
            success: true,
            message: '登录成功'
          };
        } else {
          // 登录失败
          return {
            success: false,
            message: '登录失败'
          };
        }
      } catch (error) {
        console.error('登录请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '登录请求失败，请稍后再试'
        };
      }
    },
    
    async register(userData) {
      try {
        // 发送注册请求
        const res = await request.post('/api/user/register', {
          username: userData.username,
          password: userData.password,
          phone: userData.phone || null
        });
        
        // 检查响应状态
        if (res.data) {
          // 注册成功，自动登录
          const userInfo = res.data.userInfo;
          const token = res.data.token;
          
          this.userInfo = userInfo;
          this.token = token;
          this.isLogin = true;
          
          return {
            success: true,
            message: '注册成功'
          };
        } else {
          // 注册失败
          return {
            success: false,
            message: '注册失败'
          };
        }
      } catch (error) {
        console.error('注册请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '注册请求失败，请稍后再试'
        };
      }
    },
    
    logout() {
      this.userInfo = null;
      this.token = '';
      this.isLogin = false;
    },
    
    // 获取用户信息
    async getUserInfoDetail() {
      try {
        // 检查是否有token
        if (!this.token) {
          return {
            success: false,
            message: '未登录'
          };
        }
        
        // 发送获取用户信息请求
        const res = await request.get('/api/user/info');
        
        // 检查响应状态
        if (res.data) {
          // 更新用户信息
          this.userInfo = res.data;
          
          return {
            success: true,
            message: '获取用户信息成功',
            data: res.data
          };
        } else {
          return {
            success: false,
            message: '获取用户信息失败'
          };
        }
      } catch (error) {
        console.error('获取用户信息请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '获取用户信息请求失败，请稍后再试'
        };
      }
    },
    
    // 通用更新用户信息方法
    async updateProfile(updateData) {
      try {
        if (!this.token) {
          return { success: false, message: '未登录' };
        }
        
        const res = await request.put('/api/user/update', updateData);
        
        if (res.data) {
          // 合并更新后的数据到本地
          this.userInfo = { ...this.userInfo, ...res.data };
          return { success: true, message: '更新成功' };
        } else {
          return { success: false, message: '更新失败' };
        }
      } catch (error) {
        console.error('更新用户信息失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '更新用户信息失败'
        };
      }
    },
    
    // 修改密码
    async updatePassword(oldPassword, newPassword) {
      try {
        // 检查是否有token
        if (!this.token) {
          return {
            success: false,
            message: '未登录'
          };
        }
        
        // 发送修改密码请求
        const res = await request.put('/api/user/password', {
            oldPassword,
            newPassword
        });
        
        // 检查响应状态
        if (res.data) {
          return {
            success: true,
            message: '密码修改成功'
          };
        } else {
          return {
            success: false,
            message: '密码修改失败'
          };
        }
      } catch (error) {
        console.error('修改密码请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '修改密码请求失败，请稍后再试'
        };
      }
    }
  },
  
  // 添加持久化配置
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'user-store',
        storage: localStorage
      }
    ]
  }
});