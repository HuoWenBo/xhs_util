import asyncio
import json
from os import getenv
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

import emoji as emoji
import typer
from aiofile import async_open
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
        columns=columns + ['一级', '二级', '职业']
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
                if (link := df['主页链接'][i]) and not link.startswith('https://www.xiaohongshu.com/user/profile/'):
                    logger.error(f'不是小红书主页链接或链接有其他字符 {link}')
                    continue
                await page.goto(link)
                notes: List[Dict[str, Any]] = await page.evaluate(
                    '() => __INITIAL_STATE__.user.notes._rawValue[0]'
                )
                if not notes:
                    logger.warning(f'用户不存在或被禁言或无笔记')
                    continue
                titles: List[str] = list(map(
                    lambda _note: emoji.replace_emoji(_note.get('noteCard').get('title'), replace='').replace(' ', ''),
                    notes
                ))
                note_desc: List[str] = list(map(
                    lambda _note: emoji.replace_emoji(_note.get('noteCard').get('desc'), replace='').replace(' ', ''),
                    notes
                ))
                note_tags: List[List[str]] = list(map(
                    lambda _note: [tag['name'] for tag in _note.get('noteCard').get('tagList')
                                   if tag['type'] == 'topic'],
                    notes
                ))
                try:
                    user_info = page.locator('div.info')
                    nickname = await user_info.locator(
                        'div.basic-info > div.user-basic > div.user-nickname > div'
                    ).text_content()
                    number = (await user_info.locator('span.user-redId').text_content())[5:]
                    try:
                        desc = await user_info.locator('div.user-desc').text_content(timeout=100)
                    except TimeoutError:
                        desc = ''
                except TimeoutError as e:
                    logger.error(e)
                    continue
                logger.info(f'开始预测 {nickname} 博主类型')
                # 将note_tags(双层列表)中的标签加入prompt中
                text = desc if desc else ''
                for _ in range(len(notes)):
                    text += titles[_] + note_desc[_] + ''.join(note_tags[_])
                tags, profession = model.get_all_tags(text, desc)
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
                        label = await page.locator('#user-tag-data').text_content(timeout=1000)
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
                datas.loc[index, '二级'] = labels.get('职业')

                index += 1

                data = {
                    'nickname': nickname,
                    'link': link,
                    'desc': desc,
                    'note_desc': note_desc,
                    'note_tags': note_tags,
                    'labels': labels,
                    'titles': titles,
                }
                datas.to_excel('./output/temp_file.xlsx', index=False)

                await chat_data.write(json.dumps(data, ensure_ascii=False))
                await chat_data.write('\n')
    except Exception as e:
        from datetime import datetime
        if not isinstance(e, (Error, TimeoutError, KeyboardInterrupt)):
            logger.error(e)
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
