from fastapi import FastAPI
import uvicorn
import aiohttp
import time
from typing import Optional
from fastapi import responses
import requests


async def get_data(session,text,pageNo):
 #   url='https://pd.musicapp.migu.cn/MIGUM2.0/v1.0/content/search_all.do?&ua=Android_migu&version=5.0.1&text={}&pageNo={}'.format(text,pageNo)+r'&pageSize=10&searchSwitch={"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0,"bestShow":1}'
    async with session.get('https://pd.musicapp.migu.cn/MIGUM2.0/v1.0/content/search_all.do?&ua=Android_migu&version=5.0.1&text={}&pageNo={}'.format(text,pageNo)+r'&pageSize=10&searchSwitch={"song":1,"album":0,"singer":0,"tagSong":0,"mvSong":0,"songlist":0,"bestShow":1}') as resp:
        #await asyncio.sleep(1)
        result=await resp.json()
        return result
    


async def get_song_url(session,songId):
    url = "http://app.c.nf.migu.cn/MIGUM2.0/strategy/listen-url/v2.4"
    params = {
        "albumId": "",
        "lowerQualityContentId":"" ,
        "netType": "01",
        "resourceType": "E",
        "songId": songId,
        "toneFlag": "SQ",
    }
    # response = requests.get(url, headers=headers, params=params).json()
    async with session.get(url=url,params=params) as resp:
        return await resp.json()
    


   # return response




app=FastAPI()


@app.get('/api')
async def music_api(types,name:Optional[str]=None,pages:int=1,id:Optional[int]=None):


    if types=="search":

        text=name
        if not text:
            return {'code':400,'msg':"未输入搜索内容"}

        headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(),headers=headers) as session:

            data=await get_data(session,text, pages)

            total_count=data['songResultData']['totalCount']
            result=data['songResultData']['result']


        new_result=[]
        for i in result:
            new_result.append({
                "id":i['id'],
                "name":i['name'],
                "artist":[i['singers'][0]['name']],
                "album":i['albums'][0]['name'] if "albums" in i else "",
                "pic_id":i['id'],
                "url_id":i['id'],
                "lyric_id":i['id'],
                "source":"netease"
            })
        
        return responses.JSONResponse(new_result,headers={"Access-Control-Allow-Origin":"*"})

    else:
        if id:
            timestamp = int(time.time() * 1000)
            headers = {
                            "gsm": "",
                            "randomsessionkey": "000000",
                            "mgm-user-agent": "Redmi Note 8 Pro",
                            "User-Agent": "Mozilla/5.0 (Linux; U; Android 9; zh-cn; Redmi Note 8 Pro Build/PPR1.180610.011) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1",
                            "channel": "0146931",
                            "language": "Chinese",
                            "ua": "Android_migu",
                            "mode": "android",
                            "appId": "music",
                            "brand": "Redmi",
                            "recommendstatus": "1",
                            "version": "7.41.8",
                            "mgm-Network-type": "04",
                            "mgm-network-operators": "01",
                            "mgm-Network-standard": "01",
                            "Accept-Language": "zh-CN,zh;q=0.8",
                            "subchannel": "",
                            "HWID": "",
                            "OAID": "",
                            "platform": "Redmi Note 8 Pro",
                            "userLevel": "4",
                            "osVersion": "Android 9",
                            "pkgName": "cmccwm.mobilemusic",
                            "verify": "verify",
                            "logId": "1714996870709",
                            "os": "Android 9",
                            "token": "848401000134020058526B4D355130553052446734516B457952454977517A524740687474703A2F2F70617373706F72742E6D6967752E636E2F6E303030312F4039393538623562663737343234333833393630616436313830643562333939610300040104811E0400063232303032340500164E6A51784F5756695A5455794F5463794E4749795977FF0020EA2D08CF840A637AF791B10AA53E279ED55F6E55C300D44A10A3F6E21FA5E6E9",
                            "Connection": "keep-alive",
                            "Host": "app.c.nf.migu.cn",
                            "Accept-Encoding": "gzip",
                            "signVersion": "V004",
                            "sign": "06689DDC2858127819B58D6A4F1634B8",
                            "timestamp": str(timestamp),
                            "aversionid": "DF94878D9AA2AB8F639A8BA4D0AC9D74C8C6858D999DA7BA6AC284A18B80986EC596B8898EA9D3BD6B948F9D8C819D7399DFD0D397A4A39197C3BCA286829E7397C586BADDECEE896B93859E8A8195739796828991A5EE8969928BA68D82A07597988B8B",
                            "Pragma": "no-cache",
                            "Cache-Control": "no-cache",
                            }
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(),headers=headers) as session:

                music_info=await get_song_url(session=session,songId=id)


            if types=="url":
                
                response_data={
                    "url":music_info['data']['url'],
                    "br":128,
                }

                return responses.JSONResponse(response_data,headers={"Access-Control-Allow-Origin":"*"})



            elif types=="pic":
                response_data={
                    "url":music_info['data']['song']['img1'],
                }

                return responses.JSONResponse(response_data,headers={"Access-Control-Allow-Origin":"*"})



            elif types=="lyric":

                lrcUrl=music_info['data']['lrcUrl']
                try:
                    r=requests.get(url=lrcUrl).text
                except:
                    r=''

                response_data={

                    "lyric":r,
                    "tlyric":''
                }

                return responses.JSONResponse(response_data,headers={"Access-Control-Allow-Origin":"*"})
            elif types=="download":
                try:
                    r=requests.get(url=music_info['data']['url'])
                    print(r.headers['Content-Type'])
                    return responses.Response(content=r.content,media_type="application/octet-stream",headers={"Access-Control-Allow-Origin":"*","Content-Type":r.headers['Content-Type']})
                except:
                    return None
                
        else:
            return "食屎啦你"


if __name__ == '__main__':
    uvicorn.run(app="music_api:app", host="127.0.0.1", port=80, reload=True, debug=True)