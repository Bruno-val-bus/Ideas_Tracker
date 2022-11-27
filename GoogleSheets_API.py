import gspread
from gspread.exceptions import APIError
from gspread_formatting import *
import time as time
from gspread.worksheet import Worksheet

class GoogleSheets_API:
    client = gspread.service_account()
    # might be useful: fetch_sheet_metadata() from gspread
    folder_id_personal_development = "1IW5d8UkYEq2FWXgHHEGFPNoGjIM7Gyrl"
    gworkbook_name = ""

class Concepts_API(GoogleSheets_API):
    # TODO set freq for concepts
    #   set hour reminder for mantras
    #   solve req frequency problem
    gworkbook_name = "Concepts"
    initial_concepts_sheet_name = "Concepts"
    mantras_sheet_name = "Mantras"
    trivia_sheet_name = "Trivia"
    anger_sheet_name = "Anger"
    idea_col = 1
    idea_usage_counter_col = 2
    min_usage_count = 0
    initial_concepts = {}
    mantras = []
    requests_limit_per_minute = 300  # 300 or 60? (s. https://console.cloud.google.com/apis/api/sheets.googleapis.com/quotas?project=personal-projects-360115)
    sleep_time_sec = 1
    req_per_minute_one_between_requests = 0

    def __init__(self):
        self.__workbook = self.client.open(self.gworkbook_name, folder_id=self.folder_id_personal_development)
        self.__initial_concepts_sheet = self.__workbook.get_worksheet_by_id(0)
        try:
            self.__build_initial_concepts_list()
        except APIError as api_err:
            print("Requests per minute limit exceeded.")
        self.__mantras_sheet = self.__workbook.get_worksheet_by_id(1086834586)
        #
        #
        #self.__trivia_sheet = self.__workbook.get_worksheet_by_id(1874023175)
        #self.__anger_sheet = self.__workbook.get_worksheet_by_id(1368565175)

    def __build_initial_concepts_list(self):
        """
        Creates self.initial_concepts and determines self.min_usage_count
        :return:
        """
        usage_count_list = []
        empty_rows_count = 0
        # TODO manage request limit (s. https://console.cloud.google.com/apis/api/sheets.googleapis.com/quotas?project=personal-projects-360115)
        start_req = 1.0
        no_of_requests = 2
        row_count = self.__initial_concepts_sheet.row_count + 1
        for row_index in range(1, row_count):
            elapsed_loop_sec = time.perf_counter() - start_req
            self.req_per_minute_one_loop = (no_of_requests / elapsed_loop_sec) * 60
            if max(self.req_per_minute_one_loop, self.req_per_minute_one_between_requests) >= self.requests_limit_per_minute:
                print("Request limit exceeded.")
                time.sleep(self.sleep_time_sec)
            start_req = time.perf_counter()
            # fetch concept
            concept = self.__initial_concepts_sheet.cell(row_index, self.idea_col).value
            # fetch usage count of concept
            usage_count = self.__initial_concepts_sheet.cell(row_index, self.idea_usage_counter_col).value
            end_req = time.perf_counter()
            elapsed_req_sec = end_req - start_req
            self.req_per_minute_one_between_requests = (no_of_requests / elapsed_req_sec) * 60
            if usage_count is None:
                # if count cell is empty, current count is zero
                usage_count = 0
            else:
                # else cast cell value to save count
                usage_count = int(usage_count)
            if concept is None:
                empty_rows_count += 1
                if empty_rows_count == 5:
                    # break condition to determine end_req of list
                    break
                else:
                    continue
            usage_count_list.append(usage_count)
            self.initial_concepts.update({concept: usage_count})
        self.min_usage_count = min(usage_count_list)

    def _make_req(self, row_idx: int, col_idx: int, ws: Worksheet, sleep_time=0.0) -> str:
        start_req = time.perf_counter()
        try:
            time.sleep(sleep_time)
            return ws.cell(row_idx, col_idx).value
        except APIError:
            end_req = time.perf_counter()
            elapsed_time = end_req - start_req
            self._make_req(row_idx=row_idx, col_idx=col_idx, ws=ws, sleep_time=elapsed_time*1.1)

    def __build_mantras_list(self):
        """
        TODO write method analogous to __build_initial_concepts_list
        :return:
        """
        empty_rows_count = 0
        for row_index in range(1, self.__mantras_sheet.row_count + 1):
            mantra = self.__mantras_sheet.cell(row_index, self.idea_col).value
            if mantra is None:
                empty_rows_count += 1
                if empty_rows_count == 10:
                    # break condition to determine end of list
                    break
                else:
                    continue
            self.mantras.append(mantra)


    def increase_concept_usage(self, concept):
        # TODO solve here also request limit problem. Maybe solvable with recursive method
        # updating database usage counter for specific concept in  self.initial_concepts
        concept_idx = list(self.initial_concepts.keys()).index(concept)
        sheet_idx = concept_idx + 1
        current_value = self.__initial_concepts_sheet.cell(sheet_idx, self.idea_usage_counter_col).value
        if current_value is None:
            # if cell is empty count has to be increased to 1
            new_value = 1
            self.__initial_concepts_sheet.update_cell(sheet_idx, self.idea_usage_counter_col, new_value)
        else:
            # if cell is contains count already it has to be increased by 1
            new_value = int(current_value) + 1
            self.__initial_concepts_sheet.update_cell(sheet_idx, self.idea_usage_counter_col, new_value)


class Books_API(GoogleSheets_API):
    gworkbook_name = "Books_1"

    def __init__(self):
        self.workbook = self.client.open(self.gworkbook_name, folder_id=self.folder_id_personal_development)
        # todo self.workbook.add_worksheet()

#concepts_TEST = Concepts_API()
