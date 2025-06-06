import aiohttp
import asyncio

from lxml import html


async def get_document(url, session):
    async with session.get(url, allow_redirects=False) as response:
        resp = await response.text()
        doc = html.fromstring(resp) if resp else None
        return url, doc


async def get_documents(urls):
    session = get_session()
    ret = await asyncio.gather(*[get_document(url, session) for url in urls])
    await session.close()
    return ret


async def get_jsons(courses):
    session = get_session()
    ret = await asyncio.gather(*[get_json(course, session) for course in courses])
    await session.close()
    return ret


async def get_json(course, session):
    async with session.get(course[1]) as response:
        resp = await response.text()
        return course[0], resp


def get_session():
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50), headers={'User-Agent': 'Mozilla/5.0'})
    return session
