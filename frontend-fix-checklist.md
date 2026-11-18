# 前端代码修复清单

> 用于交给其他 AI / 开发者逐项实施。每项包含：文件路径、当前问题、具体修改方法。

---

## 1. 清理 news store 的损坏代码（最高优先级）

**文件**：`src/store/modules/news.js`

### 问题
- 第 80–99 行、109 行以上保留了大量注释掉的 mock 代码（约 80 行）
- 第 150–225 行有另一个被注释的旧版 `getNewsDetail`（约 75 行）
- **第 231–246 行**：`actions` 对象已在第 230 行闭合，但后面又写了孤儿 `changeCategory` 和 `getCategoryName`，导致代码结构损坏

### 修改

1. **删除** 第 80–99 行（所有 mock 数据生成逻辑和注释）
2. **删除** 第 150–225 行（所有注释掉的旧版 getNewsDetail）
3. **删除** 第 231–246 行（底部的重复 changeCategory 和 getCategoryName）
4. **保留** 第 54–59 行的 `changeCategory`（action 列表首位那个，它才是真正生效的）

操作后 `actions` 里应只保留这些方法：`getCategories` → `changeCategory`（只一个）→ `getNewsList` → `getNewsDetail` → `getCategoryName`。

5. 第 130 行的 `console.log('使用模拟新闻详情数据')` 删掉。

---

## 2. 封装 axios 实例

**新建文件**：`src/utils/request.js`

### 内容

```js
import axios from 'axios'
import { useUserStore } from '../store/user'
import { apiConfig } from '../config/api'
import { showToast } from 'vant'
import router from '../router'

const request = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: 15000,
})

// 请求拦截：自动带 token
request.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

// 响应拦截：统一解包 code，处理 401
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) return res
    if (res.code === 401) {
      showToast('请重新登录')
      router.push('/login')
    }
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  error => {
    if (error.response?.status === 401) {
      showToast('请重新登录')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default request
```

### 说明
- 所有 store 文件中的 `axios.get/post/put/delete` 全部替换为 `request.get/post/put/delete`
- 替换后不再手动写 `headers: { Authorization: ... }`（拦截器已统一添加）
- 替换后不再手动判断 `response.data.code === 200`（拦截器已统一处理）
- 替换后不再手动拼接 `${apiConfig.baseURL}`（实例已设 baseURL）

### 需要改的文件和位置

| 文件 | 改法 |
|---|---|
| `store/user.js` | `import axios from 'axios'` → `import request from '../../utils/request'`，所有 `axios.xxx` → `request.xxx`，删除手动 Authorization 头 |
| `store/modules/news.js` | 同上 |
| `store/modules/favorite.js` | 同上 |
| `store/modules/history.js` | 同上 |
| `views/Profile.vue` 第 42 行 | 删掉 `import axios from 'axios'`（该文件实际未使用） |

示例（以 user.js login 方法为例）：

改前：
```js
const response = await axios.post(`${apiConfig.baseURL}/api/user/login`, {
  username: userData.username,
  password: userData.password
})
if (response.data && response.data.code === 200) {
  const userInfo = response.data.data.userInfo
  ...
}
```

改后：
```js
const res = await request.post('/api/user/login', {
  username: userData.username,
  password: userData.password
})
const userInfo = res.data.userInfo
...
```

其余方法类推。接口路径保持原样（如 `/api/user/login`），只需去掉 `${apiConfig.baseURL}` 前缀。

---

## 3. 修复 Authorization 头格式

**涉及文件**：如果已完成第 2 项（封装 request.js），则**本项自动完成**，无需额外修改。

如果暂不做第 2 项，则需逐个改：

| 文件 | 行号 | 改法 |
|---|---|---|
| `store/user.js` | 118、163、211 | `Authorization: this.token` → `Authorization: \`Bearer ${this.token}\`` |
| `store/modules/favorite.js` | 37、79、110、197、249 | 同上 |
| `store/modules/history.js` | 30、91、132、178 | 同上 |

---

## 4. 修复收藏列表 favorite_time 类型

**后端文件**：`toutiao_backend/schemas/favorite.py`

**改法**：第 17 行类型从 `str` 改为 `datetime`，顶部加 import。

```python
from datetime import datetime

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")  # 改 str → datetime
    ...
```

**前端文件**：`src/views/Favorite.vue` 第 26 行

改前：
```html
<span>收藏时间: {{ item.favoriteTime }}</span>
```

改后：
```html
<span>收藏时间: {{ new Date(item.favoriteTime).toLocaleString('zh-CN') }}</span>
```

---

## 5. 修复后端 history/remove 接口参数

**后端文件**：`toutiao_backend/routers/history.py` 第 38 行

改前：
```python
    news_id: int,
```

改后：
```python
    news_id: int = Query(..., alias="newsId"),
```

确保与其他接口的驼峰命名保持一致（之前已改过前端，这里补上后端）。

---

## 6. 合并 Home.vue 中的重复 onMounted

**文件**：`src/views/Home.vue`

当前有两个 `onMounted`：第 78 行和第 166 行。

**改法**：合并为一个，内容整合为：

```js
onMounted(() => {
  newsStore.getCategories().then(() => {
    newsStore.getNewsList()
  })
  setTimeout(updateTabsPosition, 300)
  window.addEventListener('scroll', handleScroll)
})
```

删掉第 166–174 行的第二个 `onMounted`。

---

## 7. 统一 localStorage 管理方式

**文件**：`store/modules/favorite.js`、`store/modules/history.js`

这两份文件各自维护了一套手动 `saveXxx()/loadXxx()` → localStorage → `JSON.parse/stringify` 的逻辑，与 user store 的 pinia persist 方案不一致。

**改法**（选一种）：

**方案 A（推荐）**：改用 pinia persist 插件。

参考 `store/user.js` 的写法，在 defineStore 的第二个参数末尾加：

```js
persist: {
  enabled: true,
  strategies: [{ key: 'favorite-store', storage: localStorage }]
}
```

然后删除手动 `saveFavorites()` / `loadFavorites()` / `saveHistory()` / `loadHistory()` 方法。

**方案 B**：保留现有手动方案，但确保在 store 初始化时调用 `loadXxx()`。**至少做这一步**：

- `store/modules/favorite.js`：state 中 `favorites` 初始值从 `[]` 改为从 localStorage 读取
- `store/modules/history.js`：同上

示例（favorite.js）：
```js
state: () => ({
  favorites: JSON.parse(localStorage.getItem('news_favorites') || '[]'),
  loading: false,
})
```

---

## 8. 路由守卫：未登录跳转

**文件**：`src/router/index.js`

### 改法

1. 为需要登录的页面路由加上 `meta.requiresAuth: true`：

```js
{ path: '/favorite', meta: { requiresAuth: true, ... } }
{ path: '/history',  meta: { requiresAuth: true, ... } }
{ path: '/profile',  meta: { requiresAuth: true, ... } }
{ path: '/settings', meta: { requiresAuth: true, ... } }
```

2. 修改 `router.beforeEach`：

```js
import { useUserStore } from '../store/user'

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '新闻资讯'

  if (to.meta.requiresAuth) {
    const userStore = useUserStore()
    if (!userStore.token) {
      return next('/login?redirect=' + to.path)
    }
  }
  next()
})
```

注意：pinia store 要在 `app.use(pinia)` 之后才能使用，因此 `useUserStore()` 不能在 router 文件顶层调用，必须写在 beforeEach 回调里（运行时执行）。

3. 前端 `/login` 页登录成功后，读取 `route.query.redirect` 跳回原页面。

**文件**：`src/views/Login.vue` 第 78–89 行

改前：
```js
if (result.success) {
  showToast(...)
  router.push('/')
}
```

改后：
```js
if (result.success) {
  showToast(...)
  const redirect = route.query.redirect || '/'
  router.push(redirect)
}
```

顶部 script 中加 `const route = useRoute()`。

---

## 9. 删除所有注释掉的代码

**涉及文件**：

| 文件 | 内容（应全部删除） |
|---|---|
| `store/modules/news.js` | 第 80–99 行、第 150–225 行 |
| `store/modules/history.js` | 所有 `// console.log(...)` 和注释掉的 `this.removeHistory(id)` 等调用 |
| `store/modules/favorite.js` | 所有注释掉的 mock 逻辑 |
| `views/NewsDetail.vue` | 无大量注释代码，保留现有 |
| `views/Profile.vue` | 无 |

---

## 修改顺序建议

1. 先做 **第 1 项**（清 news.js）——不改它后面的改动都没意义
2. 再做 **第 5 项**（history remove 接口参数）——一行
3. 然后 **第 2 项**（axios 封装）——改动最大但影响最广
4. **第 8 项**（路由守卫）
5. 其余按编号顺序即可

第 2、3、7 三项有重叠，如果做了第 2 项（axios 封装），第 3 项（Authorization 格式）自动完成；第 7 项是否做看时间。