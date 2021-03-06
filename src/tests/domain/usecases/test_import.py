# coding: utf-8

from unittest import TestCase, mock

from domain.constants import LinkSourceEnum
from domain.requests import ImportLinksRequest
from domain.usecases.import_links import ImportLinksUseCase
from tests.utils.factories import ImportStatisticsFactory, LinkFactory


class ImportTestCase(TestCase):

    def setUp(self):

        self.links_source_mock = mock.Mock()
        self.statistics_dao_mock = mock.Mock()
        self.user_notification_service_mock = mock.Mock()
        self.links_dao_mock = mock.Mock()

        self.usecase = ImportLinksUseCase(
            links_dao=self.links_dao_mock,
            link_source=self.links_source_mock,
            statistics_dao=self.statistics_dao_mock,
            user_notification_service=self.user_notification_service_mock,
        )

    def prepare__all_mocks(self, last_statistics, links):
        self.links_source_mock.get_source.return_value = LinkSourceEnum.POCKET
        self.statistics_dao_mock.get_last_by_source.return_value = last_statistics

        self.links_source_mock.get_links.return_value = links

    def prepare__statistics(self):
        return ImportStatisticsFactory()

    def prepare_links(self):
        link = LinkFactory()
        return [link]

    def test__execute__last_statistics_loaded(self):
        last_statistics = self.prepare__statistics()
        links = self.prepare_links()
        self.prepare__all_mocks(last_statistics, links)

        source = LinkSourceEnum.CUSTOM
        self.links_source_mock.get_source.return_value = source

        req = ImportLinksRequest()
        self.usecase.execute(req=req)

        self.statistics_dao_mock.get_last_by_source.assert_called_once_with(source)

    def test__execute__last_import_stat_exists__links_service_get_links_called(self):
        last_statistics = self.prepare__statistics()
        links = self.prepare_links()
        self.prepare__all_mocks(last_statistics, links)

        req = ImportLinksRequest()
        self.usecase.execute(req=req)

        self.links_source_mock.get_links.assert_called_once_with(last_statistics.dt)

    def test__execute__last_import_stat_not_exists__links_service_get_links_called(self):
        last_statistics = self.prepare__statistics()
        links = self.prepare_links()
        self.prepare__all_mocks(last_statistics, links)
        self.statistics_dao_mock.get_last_by_source.return_value = None

        req = ImportLinksRequest()
        self.usecase.execute(req=req)

        self.links_source_mock.get_links.assert_called_once_with(None)

    def test__execute__new_statistics_stored(self):
        last_statistics = self.prepare__statistics()
        links = self.prepare_links()
        self.prepare__all_mocks(last_statistics, links)
        current_statistics = ImportStatisticsFactory()
        self.usecase.prepare_statistics = mock.Mock()
        self.usecase.prepare_statistics.return_value = current_statistics

        req = ImportLinksRequest()
        self.usecase.execute(req)

        self.statistics_dao_mock.insert.assert_called_once_with(current_statistics)

    def test__execute__send_results__notification_sended(self):
        last_statistics = self.prepare__statistics()
        links = self.prepare_links()
        self.prepare__all_mocks(last_statistics, links)
        current_statistics = ImportStatisticsFactory()
        self.usecase.prepare_statistics = mock.Mock()
        self.usecase.prepare_statistics.return_value = current_statistics

        req = ImportLinksRequest(send_results=True)
        self.usecase.execute(req=req)

        self.user_notification_service_mock.send_import_result_notification.assert_called_once_with(current_statistics)
