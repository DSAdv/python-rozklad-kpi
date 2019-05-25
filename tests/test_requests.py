import json
import unittest
import logging
import asyncio

from rozklad_kpi.core import Endpoint


def _run(*coroutines):
    return asyncio.get_event_loop().run_until_complete(asyncio.gather(*coroutines))


class TestRequests(unittest.TestCase):

    def test_response_type(self):
        group_id = 4344
        teacher_id = 3694

        group_endpoints = [
            Endpoint.group,
            Endpoint.group_by_id.format(group_id),
            Endpoint.group_by_id__schedule.format(group_id),
            Endpoint.group_by_id__lessons.format(group_id),
            Endpoint.group_by_id__teachers.format(group_id),
        ]

        teachers_endpoints = [
            Endpoint.teachers,
            Endpoint.teachers_by_id.format(teacher_id),
            Endpoint.teachers_by_id__can_vote.format(teacher_id),
            Endpoint.teachers_by_id__vote.format(teacher_id),
        ]

        try:
            _run(Endpoint.request(Endpoint.BASE_URL, Endpoint.prepare_filter_params()))
        except Exception as e:
            self.assertEqual(type(e), AssertionError, f"Unexpected value of response\n"
                                                                    f"Error message: {str(e)}")
        result = _run(*(
            Endpoint.request(path, Endpoint.prepare_filter_params())
            for path in group_endpoints + teachers_endpoints
        ))

        for data in result:

                self.assertEqual(type(data), dict)




if __name__ == '__main__':
    unittest.main()