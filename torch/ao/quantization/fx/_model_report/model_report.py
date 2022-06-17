from typing import Any, Dict, Set, Tuple

import torch
from torch.ao.quantization.fx._model_report.detector import DetectorBase
from torch.ao.quantization.fx.graph_module import GraphModule
from torch.ao.quantization.observer import ObserverBase


DEFAULT_MODEL_REPORT_OBSERVER_PRE_EXTENSION = ".model_report_pre_observer"
DEFAULT_MODEL_REPORT_OBSERVER_POST_EXTENSION = ".model_report_post_observer"


class ModelReport:
    r"""
    Generates report and collects statistics
        Used to provide users suggestions on possible model configuration improvements

    Currently supports generating reports on:
    - Suggestions for dynamic vs static quantization for linear layers (Graph Modules)

    * :attr:`desired_report_detectors` The set of Detectors representing desired reports from the ModelReport class
        Make sure that these are all unique types of detectors [do not have more than 1 of the same class]

    Proper Use:
    1.) Initialize ModelReport object with reports of interest by passing in initialized detector objects
    2.) Prepare your model with prepare_fx
    3.) Call model_report.prepare_detailed_calibration on your model to add relavent observers
    4.) Callibrate your model with data
    5.) Call model_report.generate_report on your model to generate report and optionally remove added observers

    """

    def __init__(self, desired_report_detectors: Set[DetectorBase]):

        if len(desired_report_detectors) == 0:
            raise ValueError("Should include at least 1 desired report")

        # keep the reports private so they can't be modified
        self.__desired_report_detectors = desired_report_detectors
        self.__desired_reports = set([detector.get_detector_name() for detector in desired_report_detectors])

        # keep a mapping of desired reports to observers of interest
        # this is to get the readings, and to remove them, can create a large set
        # this set can then be used to traverse the graph and remove added observers
        self.__report_to_observers_of_interest: Dict[str, Set[str]] = {}

        # initialize each report to have empty set of observers of interest
        for desired_report in self.__desired_reports:
            self.__report_to_observers_of_interest[desired_report] = set([])

        # flags to ensure that we can only prepare once
        self.__prepared_flag = False

    def get_desired_reports(self) -> Set[str]:
        """ Returns a copy of the desired reports for viewing """
        return self.__desired_reports.copy()

    def get_observers_of_interest(self) -> Dict[str, Set[str]]:
        """ Returns a copy of the observers of interest for viewing """
        return self.__report_to_observers_of_interest.copy()

    def prepare_detailed_calibration(self, prepared_fx_model: GraphModule) -> GraphModule:
        r"""
        Takes in a prepared fx graph model and inserts the following observers:
        - ModelReportObserver

        Each observer is inserted based on the desired_reports into the relavent locations

        Right now, each report in self.__desired_reports has independent insertions
            However, if a module already has a Observer of the same type, the insertion will not occur
            This is because all of the same type of Observer collect same information, so redundant

        Args:
            prepared_fx_model (GraphModule):  The prepared Fx GraphModule

        Returns the same GraphModule with the observers inserted
        """

        # if already prepared once, cannot prepare again
        if self.__prepared_flag:
            raise ValueError("Already ran preparing detailed callibration. Run the report generation next after callibration.")

        # loop through each detector, find where placements should be, and keep track
        insert_observers_fqns: Dict[str, Any] = {}

        for detector in self.__desired_report_detectors:
            # determine observer points for each detector
            obs_fqn_to_info = detector.determine_observer_insert_points(prepared_fx_model)
            # map each insert point to the observer to use
            insert_observers_fqns.update(obs_fqn_to_info)
            # update the set of observers this report cares about
            self.__report_to_observers_of_interest[detector.get_detector_name()] = set(obs_fqn_to_info.keys())

        # now insert all the observers at their desired locations
        for observer_fqn in insert_observers_fqns:
            target_node = insert_observers_fqns[observer_fqn]["target_node"]
            insert_obs = insert_observers_fqns[observer_fqn]["insert_observer"]
            insert_post = insert_observers_fqns[observer_fqn]["insert_post"]
            observer_args = insert_observers_fqns[observer_fqn]["observer_args"]
            self.__insert_observer_around_module(
                prepared_fx_model, observer_fqn, target_node, insert_obs, observer_args, insert_post
            )

        self.__prepared_flag = True

        return prepared_fx_model

    def __insert_observer_around_module(
        self,
        prepared_fx_model: GraphModule,
        obs_fqn: str,
        target_node: torch.fx.node.Node,
        obs_to_insert: ObserverBase,
        observer_args: Tuple,
        insert_post: bool
    ):
        r"""
        Helper function that inserts the observer into both the graph structure and the module of the model

        Args
            prepared_fx_model (GraphModule):  The prepared Fx GraphModule
            node_fqn (str): The fully qualified name of the observer we want to insert
            target_node (torch.fx.node.Node): The node in prepared_fx_module we are inserting observers around
            obs_to_insert (ObserverBase): The observer we are inserting around target_node
            observer_args (Tuple): The arguments we want to pass into the observer
            insert_post (bool): whether this is meant to be a post observer for this node
        """
        # if we are inserting post, then our target node is the next node
        if insert_post:
            target_node = target_node.next

        with prepared_fx_model.graph.inserting_before(target_node):
            obs_to_insert = obs_to_insert()
            prepared_fx_model.add_submodule(obs_fqn, obs_to_insert)
            prepared_fx_model.graph.create_node(op="call_module", target=obs_fqn, args=observer_args)

        # recompile model after inserts are made
        prepared_fx_model.recompile()

    def __get_node_from_fqn(self, fx_model: GraphModule, node_fqn: str) -> torch.fx.node.Node:
        r"""
        Takes in a graph model and returns the node based on the fqn

        Args
            fx_model (GraphModule): The Fx GraphModule that already contains the node with fqn node_fqn
            node_fqn (str): The fully qualified name of the node we want to find in fx_model

        Returns the Node object of the given node_fqn otherwise returns None
        """
        pass

    def generate_model_report(
        self, calibrated_fx_model: GraphModule, remove_inserted_observers: bool
    ) -> Dict[str, Tuple[str, Dict]]:
        r"""
        Takes in a callibrated fx graph model and generates all the requested reports.
        The reports generated are specified by the desired_reports specified in desired_reports

        Can optionally remove all the observers inserted by the ModelReport instance

        Args:
            calibrated_fx_model (GraphModule): The Fx GraphModule that has already been callibrated by the user
            remove_inserted_observers (bool): True to remove the observers inserted by this ModelReport instance

        Returns a mapping of each desired report name to a tuple with:
            The textual summary of that report information
            A dictionary containing relavent statistics or information for that report
        """
        pass
