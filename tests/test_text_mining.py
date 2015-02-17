from seqbot.runstatus import RunStatus
from seqbot.config import CONFIG, MSGS, DEFAULTS, THRESHOLDS

from seqbot.runstatus import RU__UNKNOWN, PROGRESS_UNKNOWN, INDEXING_DONE, INDEXING_NOT_DONE, NA_

import unittest

# "fixtures"

NONSENSE = { 'runID': 'nonsense_run_id',
             'RU_':   'RU_blah',
           }

FAKE_ARGS = ['8535937', 'RU_1234']
FAKE_KWARGS = { 'datadir': '/locus/data/fake',
                'site': 'fake_site',
                'group': 'fake_output',
              }

FAKE_QSCORES = { '1': '92.5', '2': '91', '3': '90.4' }
FAKE_TILESCORES = {"cluster_density": 1091800.0625, "mean_phasing": [0.00043796843965537846, 0.00382057240598702, 0.001232744086986973, 0.00067072979124662064], "mean_prephasing": [0.00061436897487423961, 0.0011075610195153526, -0.00029753600754085189, 0.00059090331723425714], "cluster_density_pf": 985240.07142857148, "num_clusters": 20725126.0, "num_clusters_pf": 18702375.0}
FAKE_TILESCORES_CHANGED = {"cluster_density": 850580.1, "mean_phasing": [0.00043796843965537846, 0.00382057240598702, 0.001232744086986973, 0.00067072979124662064], "mean_prephasing": [0.00061436897487423961, 0.0011075610195153526, -0.00029753600754085189, 0.00059090331723425714], "cluster_density_pf": 985240.07142857148, "num_clusters": 20725126.0, "num_clusters_pf": 18702375.0}
FAKE_TILESCORES_TOO_LOW = {"cluster_density": 555121.2, "mean_phasing": [0.00043796843965537846, 0.00382057240598702, 0.001232744086986973, 0.00067072979124662064], "mean_prephasing": [0.00061436897487423961, 0.0011075610195153526, -0.00029753600754085189, 0.00059090331723425714], "cluster_density_pf": 985240.07142857148, "num_clusters": 20725126.0, "num_clusters_pf": 18702375.0}
FAKE_TILESCORES_TOO_HIGH = {"cluster_density": 1231234.2, "mean_phasing": [0.00043796843965537846, 0.00382057240598702, 0.001232744086986973, 0.00067072979124662064], "mean_prephasing": [0.00061436897487423961, 0.0011075610195153526, -0.00029753600754085189, 0.00059090331723425714], "cluster_density_pf": 985240.07142857148, "num_clusters": 20725126.0, "num_clusters_pf": 18702375.0}

FAKE_INDEXING = { "CTGAAGCT-GGCTCTGA": { 'clusters': 1482542, 'name': 'SAMPLE NAME 1', 'project': 'PROJECT NAME' },   
                  "CGGCTATG-ATAGAGGC": { 'clusters': 1594654, 'name': 'SAMPLE NAME 2', 'project': 'PROJECT NAME' }, 
                  "CTGAAGCT-CCTATCCT": { 'clusters': 2305170, 'name': 'SAMPLE NAME 3', 'project': 'PROJECT NAME' },   
                }
FAKE_PF_READS = 99999999

FAKE_PROGRESS = { 'tile': 2114, 'lane': 1, 'cycle': 318 }

EMPTY_TILESCORES = { 'cluster_density': 0, 'mean_phasing': [0,0,0], 'mean_prephasing': [0,0,0], 'cluster_density_pf': 0, 'num_clusters': 0, 'num_clusters_pf': 0 }

# change from GOINGBAD_ to BAD_ should result in ONE message. 
GOINGBAD_QSCORES = { '1': 86.5, '2': 88.1, '3': 0 }
BAD_QSCORES = { '1': 86.5, '2': 88.1, '3': 77.3 }

# change from BAD_ to EVENWORSE_ should NOT result in a message.
EVENWORSE_QSCORES = { '1': 86.5, '2': 88.1, '3': 69.2 }

# change from HALF_QSCORES to GOOD_QSCORES should result in NO messages.
HALF_QSCORES = { '1': 98.0, '2': 96.4, '3': 0 }
GOOD_QSCORES = { '1': 97.1, '2': 95.2, '3': 93.3 }


FAKE_RESULTS = { 'complete': False,
                 'tilescores': RunStatus.DEFAULT_TILE_DICT,
                 'progress': RunStatus.DEFAULT_PROGRESS_DICT,
                 'indexing': None,
                 'qscores': None,
                 'rundir': '/locus/data/fake/fake_site/fake_output/' + FAKE_ARGS[0],
               }

# TODO: generate solid sample data 
SAMPLE = { 'runID': 'blah',
           'RU_': 'RS_Sample',
           'datadir': './sampledata',
           'site': 'local',
           'group': 'samples',
         }
           
SAMPLE_ARGS = ['1','2']
SAMPLE_KWARGS = {}
SAMPLE_OLD_STATE = RunStatus(SAMPLE['runID'], SAMPLE['RU_'])


class TestRunStatus(unittest.TestCase):

    def setUp(self):
        self.fakeRS = RunStatus(*FAKE_ARGS, **FAKE_KWARGS)
        self.nonsenseRS = RunStatus(NONSENSE['runID'])
        self.sampleRS = RunStatus(*SAMPLE_ARGS, **SAMPLE_KWARGS)
        
        # this is bizarre to me, but the next 2 lines are required to reset this variable between tests.
        global EMPTY_TILESCORES
        EMPTY_TILESCORES = { 'cluster_density': 0, 'mean_phasing': [0,0,0], 'mean_prephasing': [0,0,0], 'cluster_density_pf': 0, 'num_clusters': 0, 'num_clusters_pf': 0 }

    def tearDown(self):
        pass
        
    def test_skeleton_RunStatus_constructor(self):
        #test that it's ok to construct a RunStatus object from only a runID
        assert self.nonsenseRS.runID == NONSENSE['runID']
        assert self.nonsenseRS.old_state.runID == NONSENSE['runID']
        assert self.nonsenseRS.RU_ == RU__UNKNOWN
        
    def test_old_state_NA__is_NA_(self):
        assert self.nonsenseRS.old_state.old_state == NA_
        
    def test_init_no_kwargs_matches_config_DEFAULTS(self):
        assert self.nonsenseRS.site == DEFAULTS['site']
        assert self.nonsenseRS.group == DEFAULTS['group']
        assert self.nonsenseRS.datadir == DEFAULTS['datadir']

    def test_construct_rundir_matches_expected(self):
        # (covers testing of group, site, datadir)
        assert self.fakeRS.rundir == FAKE_RESULTS['rundir']

    def test_init_tilescores_no_kwargs_matches_defaults(self):
        assert self.fakeRS.tilescores == RunStatus.DEFAULT_TILE_DICT
    
    def test_init_progress_no_kwargs_matches_defaults(self):
        assert self.fakeRS.progress == RunStatus.DEFAULT_PROGRESS_DICT

    def test_init_qscores_no_kwargs_matches_empty_dict(self):
        assert self.fakeRS.qscores == {}
    
    def test_init_indexing_no_kwargs_matches_empty_dict(self):
        assert self.fakeRS.indexing == {}

    def test_init_qscores_no_kwargs_matches_empty_dict(self):
        assert self.fakeRS.qscores == {}
    
    def test_init_complete_is_boolean(self):
        self.assertFalse(self.fakeRS.complete)
    
    def test_init_old_state_no_kwargs_is_instance_RunStatus(self):
        assert isinstance(self.fakeRS.old_state, RunStatus)
    
    def test_init_old_state_from_kwargs_is_instance_RunStatus(self):
        assert isinstance(self.sampleRS.old_state, RunStatus)
        
    def test_qscores_keys_are_all_ints(self):
        self.fakeRS.qscores = FAKE_QSCORES
        for key in list(self.fakeRS._qscores.keys()):
            assert isinstance(key, int)
            
    def test_qscores_values_are_all_floats(self):
        self.fakeRS.qscores = FAKE_QSCORES
        for value in list(self.fakeRS._qscores.values()):
            assert isinstance(value, float)
            
    def test_qscores_empty_dict_sets__qscores_eq_empty_dict(self):
        self.fakeRS.qscores = {}
        assert self.fakeRS._qscores == {}

    def test_str_qscores_empty_returns_NA_(self):
        self.fakeRS.qscores = {}
        assert self.fakeRS.str_qscores() == NA_

    def test_str_qscores_nonempty_returns_string_containing_qscore_values(self):
        self.fakeRS.qscores = FAKE_QSCORES
        result = self.fakeRS.str_qscores()
        for value in list(self.fakeRS._qscores.values()):
            assert result.find('%s' % value) > -1
    
    def test_str_index_nonempty_returns_list_of_indices(self):
        self.fakeRS.indexing = FAKE_INDEXING
        self.fakeRS.total_ix_reads_pf = FAKE_PF_READS
        assert self.fakeRS.str_index() != MSGS['indexing_not_done']
        assert self.fakeRS.str_index() != ''

    def test_str_index_empty_returns_INDEXING_NOT_DONE(self):
        self.fakeRS.indexing = {}
        assert self.fakeRS.str_index() == MSGS['indexing_not_done']

    def test_get_pct_pf_zeroCD_returns_NA_(self):
        self.nonsenseRS.tilescores = EMPTY_TILESCORES
        self.nonsenseRS.tilescores['cluster_density_pf'] = 87654
        assert self.nonsenseRS.get_pct_pf() == 0.0
    
    def test_get_pct_pf_zeroCDpf_returns_NA_(self):
        self.fakeRS.tilescores = EMPTY_TILESCORES
        self.fakeRS.tilescores['cluster_density'] = 92550
        assert self.fakeRS.get_pct_pf() == 0.0

    def test_get_pct_pf_nonzeroCD_and_nonzeroCDpf_returns_float_between_0_and_100(self):
        self.fakeRS.tilescores = EMPTY_TILESCORES
        self.fakeRS.tilescores['cluster_density'] = 92550
        self.fakeRS.tilescores['cluster_density_pf'] = 87654
        assert isinstance(self.fakeRS.get_pct_pf(), float)

    def test_str_run_progress_returns_matching_strings(self):
        self.nonsenseRS.progress = FAKE_PROGRESS
        #'Cycle: {cycle}   Lane: {lane}    Tile: {tile}'.format(**self.progress)
        result = self.nonsenseRS.str_run_progress()
        assert result.find(str(FAKE_PROGRESS['tile'])) > -1
        assert result.find(str(FAKE_PROGRESS['cycle'])) > -1
        assert result.find(str(FAKE_PROGRESS['lane'])) > -1
    
    def test_str_run_progress_default_returns_nonempty_string(self):
        self.assertFalse( self.nonsenseRS.str_run_progress() == '' )
    
    def test_to_dict_contains_required_keys(self):
        required_keys = [ 'RU_', 'runID', 'tile', 'progress', 'quality', 'index', 'complete', 'site', 'group' ]
        self.assertTrue( all(k in self.fakeRS.to_dict() for k in required_keys) )

    def test_report_progress_incomplete_with_qscores_returns_match_str_run_progress(self):
        self.fakeRS.qscores = FAKE_QSCORES
        self.fakeRS.progress = FAKE_PROGRESS
        result = self.fakeRS.report_progress()
        assert result.find(str(FAKE_PROGRESS['tile'])) > -1
        assert result.find(str(FAKE_PROGRESS['cycle'])) > -1
        assert result.find(str(FAKE_PROGRESS['lane'])) > -1
    
    def test_report_tile_empty_returns_empty_string(self):
        self.fakeRS.tilescores = RunStatus.DEFAULT_TILE_DICT
        result = self.fakeRS.report_tile()
        assert result == ''
    
    def test_report_tile_unchanged_returns_empty_string(self):
        self.fakeRS.tilescores = EMPTY_TILESCORES
        self.fakeRS.old_state.tilescores = EMPTY_TILESCORES
        self.assertTrue( self.fakeRS.report_tile() == '' )
        
    def test_report_tile_NEW_returns_nonempty_string(self):
        self.fakeRS.old_state.tilescores = EMPTY_TILESCORES
        self.fakeRS.tilescores = FAKE_TILESCORES
        self.assertFalse( self.fakeRS.report_tile() == '' )
    
    def test_report_tile_nonzero_unchanged_returns_empty_string(self):
        self.fakeRS.old_state.tilescores = FAKE_TILESCORES
        self.fakeRS.tilescores = FAKE_TILESCORES    
        self.assertTrue( self.fakeRS.report_tile() == '' )

    def test_report_tile_CHANGED_returns_nonempty_string(self):
        self.fakeRS.old_state.tilescores = FAKE_TILESCORES
        self.fakeRS.tilescores = FAKE_TILESCORES_CHANGED
        self.assertFalse( self.fakeRS.report_tile() == '' )

    def test_report_tile_NEW_BELOW_THRESHOLD_returns_nonempty_string(self):
        self.fakeRS.old_state.tilescores = FAKE_TILESCORES
        self.fakeRS.tilescores = FAKE_TILESCORES_TOO_LOW
        self.assertFalse( self.fakeRS.report_tile() == '' )
        
    def test_report_tile_NEW_ABOVE_THRESHOLD_returns_nonempty_string(self):
        self.fakeRS.old_state.tilescores = EMPTY_TILESCORES
        self.fakeRS.tilescores = FAKE_TILESCORES_TOO_HIGH
        self.assertFalse( self.fakeRS.report_tile() == '' )
        
    def test_report_tile_UNCHANGED_BELOW_THRESHOLD_returns_nonempty_string(self):
        self.fakeRS.old_state.tilescores = FAKE_TILESCORES_TOO_LOW
        self.fakeRS.tilescores = FAKE_TILESCORES_TOO_LOW
        self.assertTrue( self.fakeRS.report_tile() == '' )
    
    def test_report_indexing_empty_returns_empty_string(self):
        self.fakeRS.old_state.indexing = {}
        self.fakeRS.indexing = {}
        self.assertTrue( self.fakeRS.report_indexing() == '')
    
    def test_report_indexing_old_state_empty_new_state_nonempty_returns_nonempty_string(self):
        self.fakeRS.indexing = FAKE_INDEXING
        self.fakeRS.total_ix_reads_pf = FAKE_PF_READS
        self.fakeRS.old_state.indexing = {}
        self.assertFalse( self.fakeRS.report_indexing() == '')
    
    def test_report_indexing_old_state_nonempty_returns_empty_string(self):
        self.fakeRS.indexing = FAKE_INDEXING
        self.fakeRS.total_ix_reads_pf = FAKE_PF_READS
        self.fakeRS.old_state.indexing = FAKE_INDEXING
        self.assertTrue( self.fakeRS.report_indexing() == '' )
    
    def test_report_quality_empty_returns_empty_list(self):
        assert self.nonsenseRS.report_quality() == []
    
    def test_report_quality_nonempty_scores_above_threshold_returns_empty_list(self):
        self.nonsenseRS.qscores = HALF_QSCORES
        assert self.nonsenseRS.report_quality() == []
        
    def test_report_quality_nonempty_with_failed_threshold_returns_nonempty_list(self):
        # change from GOINGBAD_ to BAD_ should result in ONE message. 
        self.nonsenseRS.qscores = BAD_QSCORES
        self.nonsenseRS.old_state.qscores = GOINGBAD_QSCORES
        assert len(self.nonsenseRS.report_quality()) == 1

    def test_report_quality_change_above_threshold_returns_empty_list(self):
        self.nonsenseRS.qscores = GOOD_QSCORES
        self.nonsenseRS.old_state.qscores = GOINGBAD_QSCORES
        assert self.nonsenseRS.report_quality() == []

    def test_report_quality_nonempty_with_failed_threshold_eq_old_state_returns_empty_list(self):
        self.nonsenseRS.qscores = BAD_QSCORES
        self.nonsenseRS.old_state.qscores = BAD_QSCORES
        assert self.nonsenseRS.report_quality() == []

    def test_report_quality_nonempty_with_failed_threshold_below_old_state_returns_empty_list(self):
        # TODO: Decide whether this is correct behavior (see "TODO: even_worse" in runstatus.py)
        self.nonsenseRS.old_state.qscores = BAD_QSCORES
        self.nonsenseRS.qscores = EVENWORSE_QSCORES
        assert self.nonsenseRS.report_quality() == []


    #TODO: set up real directories for these tests
    #def test_is_complete_missing_completion_marker_returns_False(self):
    #def test_is_complete_has_completion_marker_returns_True(self):
    #def test_report_progress_complete_returns_COMPLETE(self):
    #def test_report_complete_old_state_incomplete_new_state_complete_returns_nonempty_string(self):
    #def test_report_complete_incomplete_returns_empty_string(self):
    #def test_report_complete_old_state_complete_returns_empty_string(self):
