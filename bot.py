import functions
from telebot.async_telebot import AsyncTeleBot
import codecs
from datetime import datetime
import asyncio
import json

conf: json = asyncio.run(functions.async_json_read())
url: str = conf["youtrack"]["baseUrl"]
project: str = conf["project"]
bot = AsyncTeleBot(conf["token"])
chat_id: str = conf["chat_id"]

statuses_in_emoji: list = ['✏️', '🔁', '✅', '🆕']

async def loop_0(all_activities) -> tuple:
    issue_list: list = []
    issue_activity: dict = {}
    issue_list_author: dict = {}
    
    status_is = statuses_in_emoji[1] #as defaultt status
    for i in range(len(all_activities)):
        all = all_activities[i]
        if "issue" in all["target"] and all["target"]["issue"]["project"]["name"] in project: #если изменения в задаче
            if all["target"]["issue"]["idReadable"] not in issue_activity and all["$type"] != "IssueCreatedActivityItem":
                issue_activity.update({all["target"]["issue"]["idReadable"]:[]})
                issue_list.append(all["target"]["issue"]["idReadable"])
                    
            if all["$type"] == "CommentActivityItem":
                for b in range(len(all["added"])):
                    if "text" in all["added"][b]:
                        added = {"[[" + functions.convert_timestamp(all["timestamp"]) + "]] #Comments " + (all["added"][b]["text"])[:1500] + ""}
                        issue_list_author.update({all["target"]["issue"]["idReadable"]: [all["author"]["login"],all["author"]["ringId"]]})
                        issue_activity[all["target"]["issue"]["idReadable"]].append(added)
                        
        elif "project" in all["target"] and all["target"]["project"]["name"] in project: #если изменения в задаче
            if all["target"]["idReadable"] not in issue_activity and all["$type"] != "IssueCreatedActivityItem": #если project в {'name': 'Департамент внедрения', 'id': '67-339', '$type': 'Project'} и all["target"]["project"]["name"] 'Департамент внедрения' == 'Департамент внедрения' 
                issue_activity.update({all["target"]["idReadable"]:[]})
                issue_list.append(all["target"]["idReadable"])

            if all["$type"] == "IssueCreatedActivityItem": #если создана задача
                issue_id = all["target"]["idReadable"]
                data = await functions.get_data_issue(issue_id,url)
                # date_create = time.strftime("%d.%m.%Y", time.localtime(int(str(data["updated"])[:-3])))
                summary = data["summary"]
                summary = functions.rep_des(summary)
                link = f'\\[[{issue_id}]({url}/issue/{issue_id})]'
                user_crete = ('#' + data["reporter"]["login"])
                user_crete = functions.rep_i(user_crete)
                user_crete_link = f'\\[[⇗]({url}/users/' + data["reporter"]["ringId"] + ')]'
                subdivision: str = ''
                deadline: str = ''
                assignee: str = ''
                assignee_link: str = ''
                for v in range(len(data["customFields"])):
                    if data["customFields"][v]["projectCustomField"]["field"]["name"] == "Assignee":
                        if data["customFields"][v]["value"] is None:
                            assignee = 'None'
                            assignee_link = 'None'
                        else:
                            assignee = ('#' + data["customFields"][v]["value"]["login"])
                            assignee_link = f'\\[[⇗]({url}/users/' + data["customFields"][v]["value"]["ringId"] + ')]'
                        assignee = functions.rep_i(assignee)    
                    if data['customFields'][v]['projectCustomField']['field']['name'] == "Подразделение":
                        if data['customFields'][v]['value'] == None:
                            subdivision = 'Нет'
                        else:
                            subdivision = data['customFields'][v]['value']['name']
                    if data['customFields'][v]['projectCustomField']['field']['name'] == "Приоритет":
                        priority = data['customFields'][v]['value']['localizedName']
                    if data['customFields'][v]['projectCustomField']['field']['name'] == "Дедлайн":
                        if data['customFields'][v]['value'] == None:
                            deadline = 'Нет'
                        else:
                            time_to_readable = data['customFields'][v]['value']
                            deadline = datetime.fromtimestamp((time_to_readable/1000)).strftime('%d-%m-%y')
                description = data["description"]
                description = functions.rep_des(description)
                if len(description) > 2000:
                    description = (description[:2000] + '...')
                text = f'\n{statuses_in_emoji[3]} {link} {summary}\n\nПодразделение: {subdivision}\nИсполнитель: {assignee}{assignee_link}\nПриоритет: {priority}\nДедлайн: {deadline}\nАвтор: {user_crete}{user_crete_link}\n\nОписание: {description}'
                text = functions.rep_des(text)
                await bot.send_message(chat_id, text=text, parse_mode='Markdown') #, reply_markup=keyboard)

            elif all['field']['name'] == "Состояние": #если изменили состояние
                for b in range(len(all["added"])):
                    if "name" in all["added"][b]:
                        added = {all["field"]["name"] + ': ' + all["added"][b]["name"] + ''}
                        issue_list_author.update({all["target"]["idReadable"]: [all["author"]["login"],all["author"]["ringId"]]})
                        issue_activity[all["target"]["idReadable"]].append(added)
            
            elif all['targetMember'] == "__CUSTOM_FIELD__Спринт департамента внедрения_268": #если изменили спринт
                for b in range(len(all["added"])):
                      if "name" in all["added"][b]:
                        added = {all["field"]["name"] + ': ' + all["added"][b]["name"] + ''}
                        issue_list_author.update({all["target"]["idReadable"]: [all["author"]["login"],all["author"]["ringId"]]})
                        issue_activity[all["target"]["idReadable"]].append(added)
    return (issue_list, issue_activity, issue_list_author, status_is)


async def loop_1(issue_list, issue_activity, issue_list_author, status_is):
    for i in range(len(issue_list)):
            des: str = ''
            try:
                issue_id = issue_list[i]
                data = await functions.get_data_issue(issue_id,url)
                for b in range(len(issue_activity[issue_list[i]])):
                    des = des + f'\n' + (str(issue_activity[issue_list[i]][b]))[2:-2]
                if 'Comments' in des:
                    des = (((des)).split("#Comments",1)[0]) + statuses_in_emoji[0] +'#Comments:' + ((des)).split("#Comments",1)[1]
                if 'Fixed' in des:
                    des = (((des)).split("Fixed",1)[0]) + statuses_in_emoji[2] + 'Fixed'
                    #тут если березка опять доёбетсядо смайлов добавить для inprogrress или для другово говнааааааааааааа

                summary = data["summary"]
                summary = functions.rep_des(summary)
                link = f'[[{issue_id}]({url}/issue/{issue_id})]'
                assignee: str = ''
                assignee_link: str = ''
                for v in range(len(data["customFields"])):
                    if data["customFields"][v]["projectCustomField"]["field"]["name"] == "Assignee":
                        if data["customFields"][v]["value"] is None:
                            assignee = 'None'
                            assignee_link = 'None'
                        else:
                            assignee = ('#' + data["customFields"][v]["value"]["login"])
                            assignee_link = f'[[⇗]({url}/users/' + data["customFields"][v]["value"]["ringId"] + ')]'

                user_update = ('#' + issue_list_author[issue_list[i]][0])
                user_update = functions.rep_i(user_update)
                user_update_link = f'[[⇗]({url}/users/' + issue_list_author[issue_list[i]][1] + ')]'

                des = codecs.escape_decode(des)[0].decode('utf8')
                des = functions.rep_des(des)
                text = f'{status_is} {link} {summary}\n\nИсполнитель: {assignee}{assignee_link}\nАвтор: {user_update}{user_update_link}\n{des}'
                text = functions.rep_des(text)
                await bot.send_message(chat_id, text=text, parse_mode='Markdown') 
            except Exception as err:
                print(err)

async def boty():
    while True:
        all_activities = await functions.get_all_activities()
        args_from_loop = await loop_0(all_activities)
        await loop_1(*args_from_loop)
        print('boty func:',datetime.now())
        await asyncio.sleep(45)

async def check_deadline_async():
    target_time = "12:00:00"
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        if current_time == target_time:
            data = await functions.get_list_issues()
            await functions.check_deadline(data)
        await asyncio.sleep(1)

async def check_deadline_by_hours_async():
    target_time = ["10:00:00", "13:00:00", "16:00:00", "19:00:00"]
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        if current_time in target_time:
            data = await functions.get_list_issues()
            await functions.check_deadline_by_hours(data)
        await asyncio.sleep(1)

async def main_123():
    await asyncio.gather(boty(),  check_deadline_async(), check_deadline_by_hours_async())

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop) 
    loop.run_until_complete(main_123())

