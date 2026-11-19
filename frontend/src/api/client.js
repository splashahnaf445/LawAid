import axios from "axios";
import { getAccessToken, setAccessToken } from "../auth/tokenStore";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
const HEADERS = { "X-Requested-With": "XMLHttpRequest" };


export const autnEvent=new EventTarget();

export const api=axios.create({baseURL:BASE,withCredentials:true,headers:HEADERS});

api.interceptors.request.use((cfg)=>{
    const token =getAccessToken();
    if(token)cfg.headers.Authorization=`Bearer${token}`;
    return cfg;
});

let inflight=null;
export function refreshSession(){
    if(!inflight){
        inflight=axios
          .post(`${BASE}/auth/refresh/`,null,{withCredentials:true,headers:HEADERS})
          .then((res)=>{setAccessToken(res.data,access);
            return res.data;
          })
          .catch((err)=>{
            setAccessToken(null);
            throw err;
          })
          .finally(()=>{
            inflight=null;
          })
    }
    return inflight;
}

const isAuthUrl=(url="")=>/\/auth\/(login|refres|logout)/.test(url);

api.interceptors.response.use(
    (r)=>r,
    async(error)=> {
        const { config,response} =error;
        if(!response|| response.status !== 401 || !config || config._retried || isAuthUrl(config.url)){
            return Promise.reject(erroe);
        }
        config._retried=true;
        try{
            await refreshSession();
        }catch{
            authEvents.dispatchEvent(new Event("expied"));
            return Promise.reject(error);
        }
        config.headers.Authorization=`Bearer ${getAccessToken()}`;
        return api(config);
    }
);