<template>
  <div class="profile-page">
    <van-nav-bar
      title="个人信息"
      left-arrow
      @click-left="$router.back()"
      fixed
    />
    
    <div class="profile-container">
      <!-- 头像区域 — 可点击编辑 -->
      <van-cell-group inset class="avatar-group">
        <van-cell title="头像" is-link center @click="showAvatarDialog">
          <template #right-icon>
            <van-image
              round
              width="60"
              height="60"
              :src="userInfo.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
            />
          </template>
        </van-cell>
      </van-cell-group>
      
      <van-cell-group inset class="info-group">
        <van-cell title="用户名" :value="userInfo.username || 'admin'" />
        <van-cell title="昵称" :value="userInfo.nickname || '未设置'" is-link @click="showNicknameDialog" />
        <van-cell title="账号ID" :value="`ID: heima-${userId || 'N/A'}`" />
        <van-cell title="个人简介" :value="userBio || '暂无简介'" is-link @click="showBioDialog" />
      </van-cell-group>
      
      <van-cell-group inset class="security-group">
        <van-cell title="修改密码" is-link @click="showPasswordConfirm" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { showDialog, showToast, showLoadingToast, showSuccessToast, showFailToast } from 'vant';
import { useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();

// 初始化用户状态
onMounted(async () => {
  // 如果用户未登录，跳转到登录页面
  if (!userStore.getLoginStatus) {
    router.push('/login');
    return;
  }
  
  // 获取用户信息
  try {
    const loadingInstance = showLoadingToast({
      message: '加载中...',
      forbidClick: true,
      duration: 0
    });
    
    const result = await userStore.getUserInfoDetail();
    loadingInstance.close();
    
    if (result.success) {
      console.log('获取用户信息成功:', userStore.userInfo);
    } else {
      console.error('获取用户信息失败:', result.message);
      showFailToast(result.message || '获取用户信息失败');
    }
  } catch (error) {
    console.error('获取用户信息请求失败:', error);
    showToast.clear();
    showToast.fail('获取用户信息失败');
  }
});

const userInfo = computed(() => userStore.userInfo);
const userId = computed(() => userStore.token ? userStore.token.substring(0, 5) : '');
const userBio = computed(() => userStore.userInfo?.bio || '暂无简介');

// ---- 编辑头像 ----
const showAvatarDialog = () => {
  const avatarUrl = ref(userInfo.value?.avatar || '');

  showDialog({
    title: '修改头像',
    showCancelButton: true,
    className: 'avatar-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px;' }, '请输入头像URL：'),
        h('input', {
          value: avatarUrl.value,
          onInput: (e) => { avatarUrl.value = e.target.value },
          placeholder: 'https://...',
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ]),
      avatarUrl.value
        ? h('img', {
            src: avatarUrl.value,
            style: 'width: 80px; height: 80px; border-radius: 50%; object-fit: cover; display: block; margin: 0 auto;'
          })
        : h('p', { style: 'text-align: center; color: #999;' }, '粘贴图片URL即可预览')
    ])
  }).then(async () => {
    if (!avatarUrl.value) {
      showToast('请输入头像URL');
      return;
    }
    try {
      const loadingInstance = showLoadingToast({ message: '保存中...', forbidClick: true, duration: 0 });
      const result = await userStore.updateProfile({ avatar: avatarUrl.value });
      loadingInstance.close();
      if (result && result.success) {
        showSuccessToast('头像修改成功');
      } else {
        showFailToast((result && result.message) || '头像修改失败');
      }
    } catch (error) {
      console.error('更新头像失败:', error);
      showToast.clear();
      showToast.fail('头像修改失败');
    }
  }).catch(() => {});
};

// ---- 编辑昵称 ----
const showNicknameDialog = () => {
  const nickname = ref(userInfo.value?.nickname || '');

  showDialog({
    title: '修改昵称',
    showCancelButton: true,
    className: 'nickname-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('input', {
        value: nickname.value,
        onInput: (e) => { nickname.value = e.target.value },
        placeholder: '请输入新昵称',
        style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
      })
    ])
  }).then(async () => {
    if (!nickname.value.trim()) {
      showToast('请输入昵称');
      return;
    }
    try {
      const loadingInstance = showLoadingToast({ message: '保存中...', forbidClick: true, duration: 0 });
      const result = await userStore.updateProfile({ nickname: nickname.value.trim() });
      loadingInstance.close();
      if (result && result.success) {
        showSuccessToast('昵称修改成功');
      } else {
        showFailToast((result && result.message) || '昵称修改失败');
      }
    } catch (error) {
      console.error('更新昵称失败:', error);
      showToast.clear();
      showToast.fail('昵称修改失败');
    }
  }).catch(() => {});
};

// ---- 修改密码 ----
const showPasswordConfirm = () => {
  const oldPassword = ref('');
  const newPassword = ref('');
  const confirmPassword = ref('');
  
  showDialog({
    title: '修改密码',
    showCancelButton: true,
    className: 'password-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '当前密码：'),
        h('input', {
          type: 'password',
          value: oldPassword.value,
          onInput: (e) => { oldPassword.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ]),
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '新密码：'),
        h('input', {
          type: 'password',
          value: newPassword.value,
          onInput: (e) => { newPassword.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ]),
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '确认密码：'),
        h('input', {
          type: 'password',
          value: confirmPassword.value,
          onInput: (e) => { confirmPassword.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box;'
        })
      ])
    ]),
  }).then(async () => {
    if (!oldPassword.value) {
      showToast('请输入当前密码');
      return;
    }
    if (!newPassword.value) {
      showToast('请输入新密码');
      return;
    }
    if (newPassword.value !== confirmPassword.value) {
      showToast('两次密码输入不一致');
      return;
    }
    try {
      const loadingInstance = showLoadingToast({ message: '修改中...', forbidClick: true, duration: 0 });
      const result = await userStore.updatePassword(oldPassword.value, newPassword.value);
      loadingInstance.close();
      if (result && result.success) {
        showSuccessToast('密码修改成功');
      } else {
        showFailToast((result && result.message) || '密码修改失败');
      }
    } catch (error) {
      console.error('修改密码失败:', error);
      showToast.clear();
      showToast.fail('密码修改失败');
    }
  }).catch(() => {});
};

// ---- 修改个人简介 ----
const showBioDialog = () => {
  const newBioValue = ref(userBio.value);
  
  showDialog({
    title: '修改个人简介',
    showCancelButton: true,
    confirmButtonText: '确认',
    className: 'bio-dialog',
    message: h('div', { style: 'text-align: left; padding: 10px 0;' }, [
      h('div', { style: 'margin-bottom: 15px;' }, [
        h('div', { style: 'margin-bottom: 5px; text-align: left;' }, '个人简介：'),
        h('textarea', {
          value: newBioValue.value,
          onInput: (e) => { newBioValue.value = e.target.value },
          style: 'width: 100%; border: 1px solid #dcdee0; border-radius: 4px; padding: 8px; box-sizing: border-box; min-height: 100px; resize: vertical;'
        })
      ])
    ])
  }).then(async () => {
    try {
      const loadingInstance = showLoadingToast({ message: '保存中...', forbidClick: true, duration: 0 });
      const result = await userStore.updateProfile({ bio: newBioValue.value });
      loadingInstance.close();
      if (result && result.success) {
        showSuccessToast('个人简介修改成功');
      } else {
        showFailToast((result && result.message) || '个人简介修改失败');
      }
    } catch (error) {
      console.error('更新个人简介失败:', error);
      showToast.clear();
      showToast.fail('个人简介修改失败');
    }
  }).catch(() => {});
};
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: var(--color-bg-page);
}

.profile-container {
  padding-top: 56px;
  padding-bottom: 20px;
}

.avatar-group,
.info-group,
.security-group {
  margin-top: 12px;
}
</style>