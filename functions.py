import time
import json
from datetime import datetime
import functions
import asyncio
import aiohttp
from telebot.async_telebot import AsyncTeleBot

async def read_json_file(filename):
    try:
        with open(filename, 'rb') as file:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, json.load, file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{filename}' не найден.")
    except json.JSONDecodeError:
        raise ValueError(f"Файл '{filename}' не валидный.\nОшибка чтения.")

async def async_json_read():
    try:
        data = await read_json_file('conf/config.json')
        return data
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)

def read_time():
    file = open('conf/time.txt', 'r')
    time = file.read()
    file.close()
    return time

def write_file_time(dt):
    file = open('conf/time.txt', 'w')
    file.write(str(dt))
    file.close()

conf: json = asyncio.run(async_json_read())
url: str = conf["youtrack"]["baseUrl"]
url_2: str = conf["youtrack"]["baseUrl"]

def convert_timestamp(timestamp):
    conv_time = time.strftime("%H:%M:%S", time.localtime(int(str(timestamp)[:-3])))
    return conv_time

async def get_all_activities():
    url: str = conf["youtrack"]["baseUrl"]
    headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer perm:c3RhY2s=.NjEtMTI=.sPh5dDqauqoG4ZqRG8BtrWTutcklEK',
      'Content-Type': 'application/json',
    }
    timestamp: str = read_time()
    data: dict = {"fields": "id,author(id,name,fullName,login,ringId),timestamp,added(text,name),target(issue(idReadable,id,project(name)),idReadable,project(id,name)),targetMember,field(id,name)","categories":"ArticleCommentAttachmentsCategory,AttachmentRenameCategory,AttachmentVisibilityCategory,AttachmentsCategory,CommentAttachmentsCategory,CommentTextCategory,CommentUsesMarkdownCategory,CommentVisibilityCategory,CommentsCategory,CustomFieldCategory,DescriptionCategory,IssueCreatedCategory,IssueResolvedCategory,IssueUsesMarkdownCategory,IssueVisibilityCategory,LinksCategory,ProjectCategory,SprintCategory,SummaryCategory,TagsCategory,TotalVotesCategory,VcsChangeCategory,VcsChangeStateCategory,VotersCategory,WorkItemCategory", "start": f'{timestamp}', "reverse": "true"} ## ,"start": f'{timestamp}',"$top":50}

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}/api/activities', headers=headers, params=data) as response:
            data = await response.json()
            if data is not None:
                dt = int(time.time() * 1000)
                write_file_time(dt)
            else: data = "None"
            await session.close()

            return data
        


async def get_list_issues():
    url: str = f'{url_2}/api/admin/projects/4554729e-a940-4ad0-96b6-4af44abb213c/issues?fields=id,created,reporter($type,id,name),updated,idReadable,$type,summary,description,customFields($type,id,projectCustomField($type,id,field($type,id,name)),value($type,avatarUrl,buildLink,color(id),fullName,id,isResolved,localizedName,login,minutes,name,presentation,text))&$top=9000'
    headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer perm:c3RhY2s=.NjEtMTI=.sPh5dDqauqoG4ZqRG8BtrWTutcklEK',
      'Content-Type': 'application/json',
  }
    timestamp: str = read_time()
    data: dict = {"fields": "id,author(id,name,fullName,login,ringId),timestamp,added(text,name),target(issue(idReadable,id,project(name)),idReadable,project(id,name)),targetMember,field(id,name)","categories":"ArticleCommentAttachmentsCategory,AttachmentRenameCategory,AttachmentVisibilityCategory,AttachmentsCategory,CommentAttachmentsCategory,CommentTextCategory,CommentUsesMarkdownCategory,CommentVisibilityCategory,CommentsCategory,CustomFieldCategory,DescriptionCategory,IssueCreatedCategory,IssueResolvedCategory,IssueUsesMarkdownCategory,IssueVisibilityCategory,LinksCategory,ProjectCategory,SprintCategory,SummaryCategory,TagsCategory,TotalVotesCategory,VcsChangeCategory,VcsChangeStateCategory,VotersCategory,WorkItemCategory", "start": f'{timestamp}', "reverse": "true"} ## ,"start": f'{timestamp}',"$top":50}

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}', headers=headers) as response:
            data = await response.json()
            await session.close()
            return data

async def get_data_issue(issue_id,url):
    headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer perm:c3RhY2s=.NjEtMTI=.sPh5dDqauqoG4ZqRG8BtrWTutcklEK',
      'Content-Type': 'application/json',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}/api/issues/{issue_id}?fields=description,summary,created,reporter(ringId,login,avatarUrl),updated,customFields(projectCustomField(field(name)),value(ringId,id,avatarUrl,buildLink,fullName,isResolved,localizedName,login,minutes,name,presentation,text))', headers=headers,) as response: #params=data) as response:
            data = await response.json()
            await session.close()
            return data

def rep_i(text):
    if text is not None:
        text: str = text.replace(".", "")
        text: str = text.replace("_", "\_")
    else: text = "None"
    return text

def rep_des(text):
    if text is not None:
        text: str = text.replace("_","\_")
        text: str = text.replace("*", "\*")
        text: str = text.replace("`", "\`")
        text: str = text.replace('«', '"')
        text: str = text.replace('»', '"')
    else: text = "None"
    return text

def rep_sum(text):
    if text is not None:
        text: str = text.replace("_","[_]")
    else: text = "None"
    return text

def rep_description(text):
    if text is not None:
        text: str = text.replace("_", "\\_")
    else: text = "None"
    return text

async def check_deadline(data: list) -> None:
    conf = await async_json_read()
    bot = AsyncTeleBot(conf["token"])
    chat_id = conf["chat_id"]
    url: str = conf["youtrack"]["baseUrl"]
    dt: int = int(time.time() * 1000)
    for issue in range(len(data)):
        for v in range(len(data[issue]["customFields"])):
            if data[issue]["customFields"][v]["projectCustomField"]["field"]["name"] == "Assignee":
                if data[issue]["customFields"][v]["value"] is None:
                    assignee = 'None'
                else:
                    assignee = ('#' + data[issue]["customFields"][v]["value"]["login"])
                    assignee = functions.rep_i(assignee)

        if data[issue]['customFields'][10]['value'] is None:
            pass
        elif data[issue]['customFields'][11]['value']['localizedName'] == 'Выполнена' or data[issue]['customFields'][11]['value']['localizedName'] == 'Дубликат' or data[issue]['customFields'][11]['value']['localizedName'] == 'Отменена':
            pass
        else:
            issue_title: str = data[issue]['idReadable']
            issue_title_2: str = data[issue]['summary']
            link: str = f'[{issue_title}]({url}/issue/{issue_title})'
            
            if data[issue]['customFields'][10]['value'] is None:
                pass
            else:
                deadline_value: int = data[issue]['customFields'][10]['value']
                if 86400000 <= deadline_value - dt <= 100800000:
                    deadline: str = datetime.fromtimestamp((deadline_value / 1000)).strftime('%d-%m-%y')
                    text: str = f' \n 🔥 {link}: {issue_title_2}\nДедлайн: {deadline}\nИсполнитель: {assignee}\nСрок решения по задаче заканчивается завтра.'
                    await bot.send_message(chat_id, text=text, parse_mode='Markdown')
                elif 0 <= deadline_value - dt <= 14400000:
                    deadline: str = datetime.fromtimestamp((deadline_value / 1000)).strftime('%d-%m-%y')
                    text: str = f' \n 🔥 {link}: {issue_title_2}\nДедлайн: {deadline}\nИсполнитель: {assignee}\nСрок решения по задаче истекает сегодня.'
                    await bot.send_message(chat_id, text=text, parse_mode='Markdown')

async def check_deadline_by_hours(data: list)-> None:
    conf = await async_json_read()
    bot = AsyncTeleBot(conf["token"])
    chat_id: dict = conf["chat_id"]
    dt: int = int(time.time() * 1000)
    for issue in range(len(data)):
        for v in range(len(data[issue]["customFields"])):
                    if data[issue]["customFields"][v]["projectCustomField"]["field"]["name"] == "Assignee":
                        if data[issue]["customFields"][v]["value"] is None:
                            assignee = 'None'
                        else:
                            assignee = ('#' + data[issue]["customFields"][v]["value"]["login"])
                        assignee = functions.rep_i(assignee)
        if data[issue]['customFields'][10]['value'] is None:
            pass
        elif data[issue]['customFields'][11]['value']['localizedName'] == 'Выполнена' or data[issue]['customFields'][11]['value']['localizedName'] == 'Дубликат' or data[issue]['customFields'][11]['value']['localizedName'] == 'Отменена':
            pass
        else:
            issue_title: str = data[issue]['idReadable']
            issue_title_2: str = data[issue]['summary']
            link: str = f'[{issue_title}]({url}/issue/{issue_title})'
            if data[issue]['customFields'][10]['value'] is None:
                pass
            else:
                deadline_value: int = data[issue]['customFields'][10]['value']
                if -86400000 <= deadline_value - dt <= 0:
                    deadline: str = datetime.fromtimestamp((deadline_value/1000)).strftime('%d-%m-%y')
                    text: str = f' \n ❌ {link}: {issue_title_2}\nДедлайн: {deadline}\nИсполнитель: {assignee}\nСрок решения по задаче истёк.'
                    await bot.send_message(chat_id, text=text, parse_mode='Markdown')

if __name__ == "__main__":
    print('functions.py')
    
