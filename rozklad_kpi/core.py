import asyncio
import json
from aiohttp import ClientSession, ClientTimeout

__all__ = ["Endpoint", "KpiScheduleAPI"]


class KpiScheduleAPI:

    @staticmethod
    def _request(*request_args):
        tasks = asyncio.gather(*(
            Endpoint.request(*args) for args in request_args
        ))
        return asyncio.get_event_loop().run_until_complete(tasks)

    def group(self, group_id=None, offset: int = 0):

        if isinstance(group_id, int):
            data = self._request(
                (Endpoint.group_by_id.format(group_id), Endpoint.prepare_filter_params()),
                (Endpoint.group_by_id__schedule.format(group_id), Endpoint.prepare_filter_params()),
            )
        elif isinstance(group_id, str):
            data = self._request((Endpoint.group, Endpoint.prepare_search_query(group_id)))
        else:
            data = self._request((Endpoint.group, Endpoint.prepare_filter_params(offset=offset)))

        return data

    def group_lessons(self,
                      group_id: int,
                      day_number: int = None,
                      lesson_number: int = None,
                      lesson_week: int = None):
        kwargs = {}

        if day_number:
            kwargs["day_number"] = day_number
        if lesson_number:
            kwargs["lesson_number"] = lesson_number
        if lesson_week:
            kwargs["lesson_week"] = lesson_week

        return self._request((
            Endpoint.group_by_id__lessons.format(group_id),
            Endpoint.prepare_filter_params(**kwargs)
        ))

    def teacher(self, teacher_id=None, offset: int = 0):

        if isinstance(teacher_id, int):
            data = self._request(
                (Endpoint.teachers_by_id.format(teacher_id), Endpoint.prepare_filter_params()),
                (Endpoint.teachers_by_id__vote.format(teacher_id), Endpoint.prepare_filter_params()),
                (Endpoint.teachers_by_id__can_vote.format(teacher_id), Endpoint.prepare_filter_params()),
            )
        elif isinstance(teacher_id, str):
            data = self._request((Endpoint.teachers, Endpoint.prepare_search_query(teacher_id)))
        else:
            data = self._request((Endpoint.group, Endpoint.prepare_filter_params(offset=offset)))

        return data


class Endpoint:

    API_VERSION = "v2"
    BASE_URL = "https://api.rozklad.org.ua/{}/".format(API_VERSION)

    UA = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/72.0.3626.121 Safari/537.36"
    )

    group = BASE_URL + "groups"
    group_by_id = group + "/{}"

    group_by_id__lessons = group_by_id + "/lessons"
    group_by_id__teachers = group_by_id + "/teachers"
    group_by_id__schedule = group_by_id + "/timetable"

    teachers = BASE_URL + "teachers"
    teachers_by_id = teachers + "/{}"
    teachers_by_id__can_vote = teachers_by_id + "/canvote"
    teachers_by_id__vote = teachers_by_id + "/vote"

    @staticmethod
    async def request(path, params, headers=None):
        headers = headers or {}
        headers.update({
            "User-Agent": Endpoint.UA,
            "Content-Type": "application/json",
        })
        timeout = ClientTimeout(30)
        async with ClientSession(headers=headers, timeout=timeout) as session:
            response = await session.get(path, params=params)
            print(response.request_info.url, response.status, response.content_type)
            assert response.content_type == "application/json", f"Wrong response Content-Type, " \
                f"expected 'application/json', but received '{response.content_type}'"
            # print(await response.text())
            return await response.json(encoding="utf-8", content_type=None)

    @staticmethod
    def prepare_filter_params(**kwargs):
        print(kwargs.get("offset"))
        return {"filter": json.dumps(
            dict({"offset": kwargs.get("offset", 0), "limit": kwargs.get("offset", 100)}, **kwargs)
        )}

    @staticmethod
    def prepare_search_query(query):
        return {"search": json.dumps({"query": query})}