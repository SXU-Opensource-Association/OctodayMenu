import request from "../util/request"

export function login(data){
    return request({
        url: 'sxu/login',
        method:'post',
        data
    })
}

export function register(data){
    return request({
        url: 'sxu/register',
        method:'post',
        data
    })
}

export function logout(){
    return request({
        url:'sxu/logout',
        method:'post'
    })
}
