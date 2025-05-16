'''
new Env('彩票开奖信息')
cron: 20 22 * * *
'''
import requests
import datetime
from lxml import etree
import notify
import re
import warnings
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_xinfo(url, headers, is_ssq=True):
    try:
        print(f"🌐 正在请求数据：{url}")
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.encoding = 'gb2312'
        print("✅ 成功获取网页内容")

        html = etree.HTML(response.text)

        title = html.xpath('//div[@class="kjxq_box02_title_left"]/img/@alt')[0]
        period = html.xpath('//font[@class="cfont2"]/strong/text()')[0]
        numbers = html.xpath('//div[@class="ball_box01"]/ul/li/text()')
        draw_time_text = html.xpath('//span[@class="span_right"]/text()')[0].strip()
        
        print(f"📌 彩种：{title}")
        print(f"📌 期号：{period}")
        print(f"📌 号码：{' '.join(numbers)}")
        print(f"📌 原始时间文本：{draw_time_text}")

        draw_match = re.search(r'开奖日期：(\d{4}年\d{1,2}月\d{1,2}日)', draw_time_text)
        deadline_match = re.search(r'兑奖截止日期：(\d{4}年\d{1,2}月\d{1,2}日)', draw_time_text)
        
        if not draw_match or not deadline_match:
            raise ValueError("无法从文本中提取日期信息")
        
        draw_date_str = draw_match.group(1)
        deadline_date_str = deadline_match.group(1)
        
        draw_date = datetime.datetime.strptime(draw_date_str, '%Y年%m月%d日')
        deadline_date = datetime.datetime.strptime(deadline_date_str, '%Y年%m月%d日')
        
        draw_date = draw_date.replace(hour=20, minute=30)
        
        weekday_map = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        weekday = weekday_map[draw_date.weekday()]
        formatted_draw_time = draw_date.strftime('%Y年%m月%d日 %H:%M')
        formatted_deadline = deadline_date.strftime('%Y年%m月%d日')
        
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        if is_ssq:
            msg = f"""✨【{title}第 {period} 期开奖结果】✨

⏰ 开奖时间：{formatted_draw_time}（{weekday}）
⏳ 兑奖截止：{formatted_deadline}

🏆 开奖号码：
════════════════
🔴{numbers[0]}  🔴{numbers[1]}  🔴{numbers[2]}  🔴{numbers[3]}  🔴{numbers[4]}  🔴{numbers[5]}  🔵{numbers[6]}
════════════════

📅 双色球开奖日：每周二、四、日 21:15
🌐 官方网站：https://www.zhcw.com/kjxx/ssq/
📞 客服电话：95086

🔄 数据更新时间：{update_time}
"""
        else:
            msg = f"""✨✨【超级大乐透{period}期开奖结果】✨✨

⏰ 开奖时间：{formatted_draw_time}（{weekday}）
⏳ 兑奖截止：{formatted_deadline}

🏆 开奖号码（前区 + 后区）：
══════════════════════
🟡{numbers[0]}  🟡{numbers[1]}  🟡{numbers[2]}  🟡{numbers[3]}  🟡{numbers[4]}   🔵{numbers[5]}  🔵{numbers[6]}
══════════════════════

📅 大乐透开奖日：每周一、三、六 晚上20:30
🌐 官方网站：https://www.lottery.gov.cn/

🔄 数据更新时间：{update_time}
"""
        print("✅ 格式化内容生成完毕")
        return title, msg
    except requests.RequestException as e:
        print(f"❌ 网络请求错误: {e}")
        return None, None
    except Exception as e:
        print(f"❌ 处理数据时出错: {e}")
        return None, None


if __name__ == '__main__':
    print("🚀 启动彩票开奖查询程序...\n")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    }

    week = datetime.date.today().strftime('%w')
    is_ssq = week in ['0', '2', '4']
    url = 'http://kaijiang.500.com/ssq.shtml' if is_ssq else 'http://kaijiang.500.com/dlt.shtml'

    print(f"📅 今天是星期 {week}，正在抓取 {'双色球' if is_ssq else '大乐透'} 开奖信息...\n")

    title, message = get_xinfo(url, headers, is_ssq)

    if title and message:
        print("\n📨 准备发送通知...\n")
        notify.send(title, message)
        print("🏁 程序执行完毕")
    else:
        print("❌ 抓取数据失败，请检查网络连接或网页结构。")