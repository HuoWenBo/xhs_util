import asyncio
import json
from os import getenv
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

import emoji as emoji
import typer
from aiofile import async_open
from jsonpath import JSONPath
from loguru import logger
from pandas import DataFrame, read_excel
from playwright.async_api import (
    async_playwright,
    BrowserType,
    BrowserContext,
    Page,
    ViewportSize,
    TimeoutError,
    Error
)

# 读取系统变量
LOCALAPPDATA: str = getenv('LOCALAPPDATA')
GOOGLE_CHROM_USER_DATA_DIR = Path(LOCALAPPDATA) / 'Google/Chrome/User Data'

MAIN_TYPES: List[str] = [
    '时尚',
    '穿搭',
    '母婴',
    '宠物',
    '美食',
    # '好物',
    '美妆',
    '家居'
]

app = typer.Typer()


async def load_javascript_template(filepath: Union[str, Path]) -> str:
    async with async_open(filepath, 'r', encoding='utf-8') as f:
        javascript_template = await f.read()
    return javascript_template


def generate_javascript(template: str, user_type: str, user_tag: List[str], profession: str) -> str:
    js = template.replace('#select_value_default#', user_type)
    js = js.replace('[`#checkbox_options_default#`]', user_tag.__str__())
    js = js.replace('#user-profession-default#', profession)
    return js


async def main(
        df: DataFrame,
        start_row: int = 0,
        end_row: int = None,
) -> None:
    from lib.model import Model
    columns: List[str] = df.columns.tolist()
    datas: DataFrame = DataFrame(
        columns=columns + [
            '一级',
            '二级',
            '职业',
            '点赞总数',
            '平均点赞',
            '评论总数',
            '平均评论',
            '分享总数',
            '平均分享',
        ]
    )

    init_javascript = load_javascript_template('./lib/init.js')
    style_javascript = load_javascript_template('./lib/style.js')
    javascript_template = load_javascript_template('./lib/inject_script.js')

    model = Model()

    try:
        async with (
            async_playwright() as playwright,
            async_open('.cache/chat_data.jsonl', 'a', encoding='utf8') as chat_data
        ):
            chromium: BrowserType = playwright.chromium
            context: BrowserContext = await chromium.launch_persistent_context(
                # 用户 Google Chrome 用户数据目录路径
                user_data_dir=GOOGLE_CHROM_USER_DATA_DIR,
                headless=False,
                bypass_csp=True,
                viewport=ViewportSize(
                    width=1920,
                    height=1080
                )
            )
            page: Page = context.pages[-1]
            index: int = datas.shape[0]
            end_row = end_row or df.shape[0]

            init_javascript = await init_javascript
            style_javascript = await style_javascript
            javascript_template = await javascript_template

            for i in range(start_row, end_row):
                if (link := df['主页链接'][i].strip()) and not link.startswith(
                        'https://www.xiaohongshu.com/user/profile/'):
                    logger.error(f'不是小红书主页链接或链接有其他字符 {link}')
                    continue
                await page.goto(link)
                initial_state: Dict[str, Any] = json.loads(
                    (await page.locator('body > script:nth-child(4)').text_content())[25:]
                    .replace('undefined', 'null')
                )
                if not initial_state:
                    logger.warning(f'用户不存在或被禁言或无笔记')
                    continue

                notes: List[Dict[str, Union[str, List[Dict[str, str]]]]] = [note for note in JSONPath(
                    '$.user.notes[0].*.noteCard.(title,desc,tagList,'
                    'interactInfo.(sticky,collectedCount,commentCount,likedCount,shareCount))'
                ).parse(initial_state) if note.get('interactInfo', {}).get('sticky', False) is False][:20]

                if not notes:
                    logger.warning(f'笔记为空')
                    continue

                notes_title: List[str] = []
                notes_desc: List[str] = []
                notes_tags: List[List[str]] = []
                liked_count: int = 0
                comment_count: int = 0
                share_count: int = 0

                for note in notes:
                    notes_title.append(emoji.replace_emoji(note.get('title', ''), replace='').replace(' ', ''))
                    notes_desc.append(emoji.replace_emoji(note.get('desc', ''), replace='').replace(' ', ''))
                    notes_tags.append([tag['name'] for tag in note.get('tagList', []) if tag['type'] == 'topic'])

                    liked_count += int(note.get('interactInfo', {}).get('likedCount', 0))
                    comment_count += int(note.get('interactInfo', {}).get('commentCount', 0))
                    share_count += int(note.get('interactInfo', {}).get('shareCount', 0))

                avg_liked_count: float = liked_count / (notes_length := len(notes))
                avg_comment_count: float = comment_count / notes_length
                avg_share_count: float = share_count / notes_length

                try:
                    user_info = page.locator('div.info')
                    nickname = await user_info.locator(
                        'div.basic-info > div.user-basic > div.user-nickname > div'
                    ).text_content()
                    number = (await user_info.locator('span.user-redId').text_content())[5:]
                    try:
                        user_desc = await user_info.locator('div.user-desc').text_content(timeout=100)
                    except TimeoutError:
                        user_desc = ''
                except TimeoutError as e:
                    logger.error(e)
                    continue
                logger.info(f'Excel 行号: {i + 2}, 开始预测 {nickname} 博主类型')
                # 将note_tags(双层列表)中的标签加入prompt中
                text = user_desc or ''
                for _ in range(len(notes)):
                    text += notes_title[_] + notes_desc[_] + ''.join(notes_tags[_])
                tags, profession = model.get_all_tags(text, user_desc)
                user_type: str = ''
                for main_type in MAIN_TYPES:
                    if main_type in tags:
                        tags.remove(main_type)
                        user_type = main_type
                        break

                labels: Dict[str, Union[str, List[str]]] = {
                    '一级': user_type,
                    '二级': tags,
                    '职业': profession
                }

                logger.info(labels)
                # 等待用户确认标签
                while True:
                    if not await page.locator('#forecast-result-container').all():
                        await page.evaluate(init_javascript)
                        await page.evaluate(style_javascript)
                        await page.evaluate(
                            generate_javascript(
                                javascript_template,
                                labels['一级'],
                                labels['二级'],
                                labels['职业']
                            )
                        )
                    try:
                        await asyncio.sleep(0.1)
                        label = await page.locator('#user-tag-data').text_content(timeout=100)
                        break
                    except TimeoutError:
                        continue

                if label:
                    labels = json.loads(label)

                for column in columns:
                    datas.loc[index, column] = df[column][i]

                datas.loc[index, '昵称'] = nickname
                datas.loc[index, 'ID'] = number
                datas.loc[index, '一级'] = labels.get('一级')
                datas.loc[index, '二级'] = '、'.join(labels.get('二级'))
                datas.loc[index, '职业'] = labels.get('职业')

                datas.loc[index, '点赞总数'] = liked_count
                datas.loc[index, '平均点赞'] = avg_liked_count
                datas.loc[index, '评论总数'] = comment_count
                datas.loc[index, '平均评论'] = avg_comment_count
                datas.loc[index, '分享总数'] = share_count
                datas.loc[index, '平均分享'] = avg_share_count

                index += 1

                try:
                    datas.to_excel('./output/temp_file.xlsx', index=False)
                except IOError:
                    pass

                data = {
                    'nickname': nickname,
                    'link': link,
                    'desc': user_desc,
                    'note_desc': notes_desc,
                    'note_tags': notes_tags,
                    'labels': labels,
                    'titles': notes_title,
                }
                await chat_data.write(json.dumps(data, ensure_ascii=False))
                await chat_data.write('\n')
    except Exception as e:
        if not isinstance(e, (Error, TimeoutError, KeyboardInterrupt)):
            logger.error(e)
    finally:
        from datetime import datetime

        filename: str = datetime.now().strftime('%Y-%m-%d.%H-%M-%S')
        logger.warning(f'文件保存路径: ./output/{filename}.xlsx')
        datas.to_excel(f'./output/{filename}.xlsx', index=False)

    await asyncio.sleep(0.25)


@app.command(
    'xhs-util',
    hidden=True,
    help='执行 小红书博主类型预测 脚本'
)
def run(
        filepath: Path = typer.Option(
            None,
            '--filepath',
            '-f',
            prompt='请填写 Excel 文件路径 ',
            help='必填选项: Excel 文件路径(相对路径或绝对路径)',
        ),
        start_row: int = typer.Option(
            1,
            '--start-row',
            '-sr',
            help='开始行号 默认从第一行开始',
            min=1
        ),
        end_row: Optional[int] = typer.Option(
            None,
            '--end-row',
            '-er',
            help='结束行号 默认到最后一行',
            min=1
        ),
) -> None:
    """
    执行 小红书博主类型预测 脚本
    """

    if filepath.suffix != '.xlsx':
        logger.error(f'文件类型错误, 当前版本仅支持(.xlsx): {filepath}')
        raise typer.Exit(-1)
    if not filepath.is_file():
        logger.error(f'文件路径错误, 没有这个文件: {filepath}')
        raise typer.Exit(-1)

    df: DataFrame = read_excel(filepath)
    asyncio.run(main(
        df,
        start_row - 1,
        end_row,
    ))


if __name__ == '__main__':
    app()
