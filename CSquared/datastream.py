
import os
from collections import OrderedDict

import pandas as pd

from css.release import utilities as u
from css.release.current import post


class DataStream(object):
    """
    The abstract approach to the data streaming process.
    input, investigate (optional), cache in records_cache
    drafting (optional), staging (optional)
    apply rulings (optional), process (optional), cache in
        decisions_cache (optional)
    render
    """

    @property
    def to_execute(self):
        """
        Accessed to see if input should be obtained for this source right now.
        """
        return True

    def input(self):
        """
        Returns list of records to either to enter into the data stream
        """
        pass

    to_investigate = False

    def investigate(self, inputs):
        """
        Given records straight from input, returns more detailed records.
        """
        # Optional behavior
        return inputs

    #
    # HANDLE RULINGS
    #
    to_rule = False
    # Ruling assumes that we are dealing with a list of records.

    def id(self, record):
        """
        Identifies what makes this record unique. Used to resolve rulings
        to the record to which it applies.

        Must return a string in order to be staged properly
        """
        return record

    def apply_ruling(self, ruling, record):
        """
        Given a single ruling and the corresponding record,
        produces a resolution. Defines how rulings act upon the record.
        """
        record.update(ruling)
        return record

    #
    # PROCESS RESOLUTIONS
    #
    to_process = False

    def process(self, resolutions):
        """
        Given resolutions (after rulings applied), executes intended
        commands.
        """
        # This is optional behavior
        return resolutions

    #
    # RENDER OUTPUT
    #
    def render(self, records=None, render_path=None):
        """
        Transforms stored decisions/records into final spreadsheet
        render_columns attribute existing is assumed
        """
        assert self.render_columns

        if not render_path:
            render_path = self.render_path
        if records is None:
            records = self.retrieve_final_items()

        if self.to_rule:
            records = self.apply_rulings(records)

        records = u.apply_aggregators(
            map(lambda rc: (rc[0], rc[2]), self.render_columns),
            records
        )

        u.write_excel(
            records,
            render_path,
            OrderedDict(map(lambda rc: (rc[0], rc[1]), self.render_columns)),
        )

    #
    # SUMMARIZE
    #
    to_summarize = True
    """Set to false if summarizing functions should not be called
    after running .query or .decide.

    Useful if .query or .decide print summarizing information at runtime.
    """

    def summarize_decisions(self):
        """
        Returns string summarizing current state of decisions.
        """
        cache = self.retrieve_decisions_cache()
        return "{} decisions".format(
            len(cache["results"])
        )

    def summarize_records(self):
        """
        Returns string summarizing current state of the cache.
        """
        cache = self.retrieve_records_cache()
        return "{} records".format(
            len(cache["results"])
        )



    #
    # Paths
    #
    @property
    def staged_ruling_path(self):
        """
        Returns path to the active ruling path
        """
        return os.path.join(
            post.paths["RULINGS_CACHE_PATH"],
            "{}_rulings.json".format(self.name)
        )

    @property
    def draft_ruling_path(self):
        """
        Returns path to the editable ruling path
        """
        return os.path.join(
            post.paths["UNSTAGED_RULINGS_PATH"],
            "{}_rulings.xlsx".format(self.name)
        )

    @property
    def records_cache_path(self):
        return os.path.join(
            post.paths["RECORDS_CACHE_PATH"],
            "{}.json".format(self.name)
        )

    @property
    def decisions_cache_path(self):
        return os.path.join(
            post.paths["DECISION_CACHE_PATH"],
            "{}.json".format(self.name)
        )

    @property
    def render_path(self):
        return os.path.join(
            post.paths["SPREADSHEET_PATH"],
            "{}.xlsx".format(self.name)
        )

    @property
    def final_path(self):
        return (
            self.decisions_cache_path if
            self.to_process else self.records_cache_path
        )

    #
    # Rulings Logic
    #
    @property
    def rulings(self):
        """
        Returns id: ruling dict of staged rulings to be applied.
        """
        try:
            rulings = u.load_cached_data(self.staged_ruling_path)
        except IOError:
            rulings = {}
        return rulings

    def apply_rulings(self, records):
        """
        Returns resolutions
        """
        def resolve_ruling(record, rulings):
            r_id = self.id(record)
            ruling = rulings.get(r_id, None)
            if ruling is None:
                # print r_id
                return record
            return self.apply_ruling(ruling, record)

        current_rulings = self.rulings
        resolutions = map(
            lambda r: resolve_ruling(r, current_rulings),
            records
        )
        return resolutions

    def prepare_draft_rulings(self):
        """
        Takes resolutions (intervened and not) and prepares a ruling doc
        """
        records = self.retrieve_cached_records()
        if records:
            records = self.apply_rulings(records)
            records = u.apply_aggregators(
                map(lambda rc: (rc[0], rc[2]), self.ruling_columns),
                records
            )
        else:
            records = []  # might be None

        u.write_excel(
            records,
            self.draft_ruling_path,
            OrderedDict(map(lambda rc: (rc[0], rc[1]), self.ruling_columns)),
        )

    def stage_draft_rulings(self):
        """
        Takes current draft ruling doc and makes them the new resolution.
        """
        rulings = pd.read_excel(self.draft_ruling_path)
        for k in rulings.keys():
            rulings[k].fillna(value="", inplace=True)
        rulings = rulings.to_dict("records")
        id_to_ruling = dict(
            map(lambda r: (self.id(r), r), rulings)
        )
        u.cache_results(id_to_ruling, self.staged_ruling_path)

    #
    # Caching Logic
    #
    def cache_records(self, records):
        """
        Dumps records into file specified by class
        """
        return u.cache_results(
            records,
            self.records_cache_path
        )

    def retrieve_cached_records(self):
        """
        Retrives records cached by self.cache_records
        """
        return u.load_cached_data(self.records_cache_path)

    def retrieve_records_cache(self):
        """
        Returns cache dict, including records and metadata
        """
        return u.load_cache(self.records_cache_path)

    def cache_decisions(self, decisions):
        """
        Dumps decisions into file specified by class
        """
        return u.cache_results(
            decisions,
            self.decisions_cache_path
        )

    def retrieve_cached_decisions(self):
        """
        Retrives decisions cached by self.cache_decisions
        """
        return u.load_cached_data(self.decisions_cache_path)

    def retrieve_decisions_cache(self):
        """
        Returns cache dict, including records and metadata
        """
        return u.load_cache(self.decisions_cache_path)

    def retrieve_final_items(self):
        return (
            self.retrieve_cached_decisions() if self.to_process else
            self.retrieve_cached_records()
        )

    def retrieve_final_cache(self):
        return (
            self.retrieve_decisions_cache() if self.to_process else
            self.retrieve_records_cache()
        )

    #
    # Execution logic
    #
    def query(self):
        """
        Puts together records pre-ruling
        """
        records = self.input()
        if self.to_investigate:
            records = self.investigate(records)
        post.log.info("Caching {} records for {}".format(len(records), self.name))
        self.cache_records(records)

    def decide(self, records):
        if self.to_rule:
            records = self.apply_rulings(records)
        records = self.process(records)
        self.cache_decisions(records)
