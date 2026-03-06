import Cookies from 'js-cookie'

const TokenKey = 'sxu_what_eat_token'
const UserKey = 'sxu_what_eat_user'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

// 全局用户信息（userid / username），存到 Cookie 里
export function setUserInfo(user) {
  // 只挑常用字段，避免乱七八糟数据太大
  const payload = {
    userId: user?.userId ?? user?.userid ?? user?.id ?? null,
    username: user?.username ?? user?.name ?? null
  }
  return Cookies.set(UserKey, JSON.stringify(payload))
}

export function getUserInfo() {
  const raw = Cookies.get(UserKey)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function removeUserInfo() {
  return Cookies.remove(UserKey)
}
