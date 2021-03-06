import asyncio
import time
from pyppeteer.launcher import launch
from alifunc import mouse_slide, input_time_random
from exe_js import js1, js3, js4, js5
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

async def main(username, pwd, url,shop_id):
    browser = await launch({'headless': False,
                                          # 'userDataDir': './userdata',
                                          'args': [
                                              '--window-size={1300},{600}'
                                              '--disable-extensions',
                                              '--hide-scrollbars',
                                              '--disable-bundled-ppapi-flash',
                                              '--mute-audio',
                                              '--no-sandbox',
                                              '--disable-setuid-sandbox',
                                              '--disable-gpu',
                                              '--disable-infobars'
                                          ],
                                          'dumpio': True
                                          })
    page = await browser.newPage()
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
    await page.setViewport({'width': 1400, 'height': 600})
    await page.goto(url)
    time.sleep(1)
    await page.evaluate(js1)
    await page.evaluate(js3)
    await page.evaluate(js4)
    await page.evaluate(js5)

    # await page.type('.J_UserName', username, {'delay': input_time_random() - 50})
    await page.type('#fm-login-id', username, {'delay': input_time_random() - 50})
    # await page.type('#J_StandardPwd input', pwd, {'delay': input_time_random()})
    await page.type('#fm-login-password', pwd, {'delay': input_time_random()})
    await page.screenshot({'path': './headless-test-result.png'})
    time.sleep(2)

    # slider = await page.Jeval('#nocaptcha', 'node => node.style')  # ???????????????
    #
    # if slider:
    #     print('????????????????????????')
    #     await page.screenshot({'path': './headless-login-slide.png'})
    #     flag = await mouse_slide(page=page)
    #     if flag:
    #         await get_cookie(page)
    #
    # else:
    await page.keyboard.press('Enter')
    await page.waitFor(20)
    await page.waitForNavigation()
    try:
        global error
        error = await page.Jeval('.error', 'node => node.textContent')
    except Exception as e:
        error = None
    finally:
        if error:
            print('?????????????????????????????????')
            # ???????????????
            loop.close()
        else:
            print(page.url)
            await get_cookie(page,shop_id)


# ???????????????cookie
async def get_cookie(page):
    res = await page.content()
    input('????????????cookie')
    while True:
        await page.reload()
        time.sleep(2)
        cookies_list = await page.cookies()
        cookies = ''
        for cookie in cookies_list:
            str_cookie = '{0}={1};'
            str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
            cookies += str_cookie
        print('????????????', cookies)
        time.sleep(120)


if __name__ == '__main__':
    username = 'user_name'
    pwd = 'password'
    shop_id = 28
    url = 'https://login.taobao.com/'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(username, pwd, url,shop_id))
