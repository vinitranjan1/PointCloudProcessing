from ._pallets import *
from ._settings import *
from ._buffer import *
from ._baydoor import *
from ._floorplan import *
from ._elevator import *
from ._level import *
from collections import defaultdict
from datetime import datetime

import csv
import pdb

import sys, os, shutil, logging, pickle, tqdm, datetime, pandas as pd, numpy as np
from configobj import ConfigObj

class Warehouse():

    """
    Warehouse

    The overarching container class for all vtk visuals.
    Initialized from a set of configuration files and logs to build system elements within the warehouse.
    """

    def __init__(self, renderer=None, interactor=None, playbackManager=None):
        # print('_warehouse.__init__')
        self._renderer = renderer
        self._renderer.AddObserver('EndEvent', self.update)
        self._interactor = interactor
        self._interactor.AddObserver('CharEvent', self.keyboardEvent)

        self._systems = {} # {'system name': actor}
        self._config = {}

        self.__pm = playbackManager
        self.__playbackUpdateID = self.__pm.AddObserver('PlaybackChange', self.reload)

    def keyboardEvent(self, obj, event):
        # print('_warehouse.keyboardEvent')
        """
        Bind some keyboard events to internal behaviors
        """
        if obj.GetKeyCode() is 'z': self.setColorRepresentation('sku')
        elif obj.GetKeyCode() is 'x': self.setColorRepresentation('action')
        elif obj.GetKeyCode() is 'c': self.setColorRepresentation('state')

    def reload(self):
        # print('_warehouse.reload')
        """
        Reloads all internal systems
        """
        self.__pm.pause()
        for system_id, system in self._systems.items():
            system.reload(self.__pm.time)
        self.__pm.resume()

    def update(self, obj, event):
        # print('_warehouse.update')
        """
        Updates all internal systems
        """
        # if self.__pm.time > datetime.datetime(2016, 1, 2, 6, 55):
        #     self.__pm.setTime(datetime.datetime(2016, 1, 2, 6, 25))
        for system_id, system in self._systems.items():
            system.update(obj, event, self.__pm.time)

    def setColorRepresentation(self, name):
        # print('_warehouse.setColorRepresentation')
        """
        Sets the color representation of the pallets mapper
        """
        self._systems['pallets'].setColorRepresentation(name)

    def _loadConfigDataSimDir(self, path, file_path):
        # print('_warehouse._loadConfigDataSimDir')
        """
        Returns a config object parsed from a file at path/file_path
        """
        return ConfigObj(os.path.join(path, file_path))
    def _loadConfigData(self, filename):
        # print('_warehouse._loadConfigData')
        """
        (Deprecated) Returns a config object parsed from a file at filename
        """
        return ConfigObj(filename)

    def _loadPalletInitializationSimDir(self, path, file_path):
        # print('_warehouse._loadPalletInitializationSimDir')
        """
        Loads a pallet initialization pickle file from path/file_path
        """
        # if os.path.isfile(os.path.join(path, file_path)):
        #
        #     with open('init.p', "rb") as f:
        #         pdb.set_trace()
        #         return pd.read_pickle(f)
        #         # return pickle.load(f)
        # else:
        logging.warning('[WAREHOUSE] Pallet initialization file does not exist in zip.\n  file: {}'.format(file_path))
        return {}

    def _loadPalletInitialization(self, filename):
        # print('_warehouse._loadPalletInitialization')
        """
        (Deprecated) Loads a pallet initialization pickle file from filename
        """
        if os.path.isfile(filename):
            with open(filename, "rb") as f: return pickle.load(f)
        else:
            logging.warning('[WAREHOUSE] Pallet initialization file does not exist.\n  file: {}'.format(filename))
            return {}

    def initializeFromSimDir(self, path, overwrite=False):
        # print('_warehouse.initializeFromSimDir')
        """
        Initialize all interal data from a .linsim simulation directory.
        """

        _data_path = os.path.join('simviz', 'systems_data.p')
        _data = None
        self.__pm.pause() # pause time

        # load _config
        self._config = self._loadConfigDataSimDir(path, os.path.join('design', 'warehouse.ini'))
        # ---Chris Addon vvv--------------------------------------------------------------------------------------------

        path1 = '/Users/eckman/Documents/LineageLogistics/simviz/vtk/Sunnyvale/Input_WarehouseMap.csv'
        input_warehousemap = open(path1, 'rt')
        read_warehousemap = csv.reader(input_warehousemap)
        reach_map = {}
        for row in read_warehousemap:
            FIX = row[-1].rstrip()
            name = row[0]
            what_is_it = row[1]
            x = row[2]
            y = row[3]
            z = row[4]
            connections = FIX.split("|")
            reach_map[name] = {'Component': what_is_it, 'x':  x, 'y':  y, 'z': z, 'Connected': connections}
        self._reach_map = reach_map

        #---Chris Addon ^^^---------------------------------------------------------------------------------------------

        # load vis data from file if provided and not explicitly told to overwrite
        if path is not None and os.path.isfile(os.path.join(path, _data_path)) and not overwrite:
            logging.info('[WAREHOUSE] Loading pallet data from file.')
            with open(os.path.join(path, _data_path), "rb") as f: _data = pickle.load(f)

        # ---Chris Addon vvv--------------------------------------------------------------------------------------------

        path2 = '/Users/eckman/Documents/LineageLogistics/simviz/vtk/Sunnyvale/Output_Movements.csv'
        output_movements = open(path2, 'rt')
        read_movements = csv.reader(output_movements)
        _output_data = {}
        # Start_pt, End_pt, Type, State, Date, PID
        for row in read_movements:
            start_pt = row[0]
            end_pt = row[1]
            component = row[2]
            state_type = row[3]
            datestamps = row[4]
            pallet_pid = row[5]

            _output_data[start_pt] = {'Start_pt': start_pt,
                                      'End_pt': end_pt,
                                      'Type': component,
                                      'State': state_type,
                                      'Date': datetime.datetime.strptime(datestamps, ' %Y-%d-%m %H:%M:%S'),
                                      'PID': pallet_pid}

        # ---Chris Addon ^^^--------------------------------------------------------------------------------------------

        # Otherwise, parse logs to produce pallet-indexed dataframe and build pallet objects from dataframe
        if not _data:
            # read in simulation.ini

            self.__sim_config = ConfigObj(os.path.join(path, 'simulation', 'simulation.ini'))

            # Load log data

            _data = self._dataFromLogsSimDir(path, os.path.join('simulation', 'logs'), overwrite)

            rackstores = self._loadPalletInitializationSimDir(path, os.path.join('simulation', 'init.p'))

            for id, system in tqdm.tqdm(rackstores.items(), desc='Appending Initial Rackstores', unit='racks'):
                # get system type by looping through system in ConfigObj object system type lists from .ini files

                system_type = [ k for k, v in self._config.items() if id in v.keys() ][0]

                for loc, rack in system.rackstore.items():
                    # get object by id in warehouse config
                    id_wh_config = self._config[system_type][id]
                    # warehouse config info about system_type
                    sys_loc = [float(i) for i in id_wh_config[SYSTEMS_LOOKUP[system_type]['loc']]]
                    for idx, pallet in enumerate(rack):
                        if pallet is not None and pallet.pid not in _data['pallets'].index:
                            # pdb.set_trace()
                            _data['pallets'].loc[pallet.pid] = {
                                'sku': pallet.sku,
                                'activity start': pd.Timestamp(self.__sim_config['global']['simulation_start_time']),
                                'activity end': pd.Timestamp(self.__sim_config['global']['simulation_end_time']),
                                'activity windows': [],
                                'keyframes': [{ \
                                    'time': pd.Timestamp(self.__sim_config['global']['simulation_start_time']), \
                                            # rack loc
                                    'loc_x': loc.x + \
                                            # offset by 1 pallet.x if it's in +x
                                            (loc.x > sys_loc[0]) * AISLE.x + \
                                            # offset by its position in the rack
                                            ((loc.x > sys_loc[0]) * 2 - 1) * PALLET_SLOT.x * idx, \
                                    'loc_y': loc.y, \
                                    'loc_z': loc.z }] }


            # Save _data to pickle file if specified
            # delete existing data if chosen to overwrite
            if overwrite and os.path.isdir(os.path.join(path, os.path.dirname(_data_path))):
                shutil.rmtree(os.path.join(path, os.path.dirname(_data_path)))
            # make a new directory and save to it
            os.makedirs(os.path.join(path, os.path.dirname(_data_path)))
            with open(os.path.join(path, _data_path), "wb") as f:
                pickle.dump(_data, f)

        # Create systems objects from config data
        #  ---Chris Addon vvv-------------------------------------------------------------------------------------------

        # for name in self._reach_map:
        #     actor = None
        #     start = [int(self._reach_map[name]['y']), int(self._reach_map[name]['x']), int(self._reach_map[name]['z'])]
        #     for conn in self._reach_map[name]['Connected']:
        #         end = [int(self._reach_map[conn]['y']), int(self._reach_map[conn]['x']), int(self._reach_map[conn]['z'])]
        #         # if self._reach_map[name]['Component'] == 'AsileCart':
        #         #     actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #         if self._reach_map[name]['Component'] == 'ConveyorBelt':
        #             actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #         elif self._reach_map[name]['Component'] == 'DockDoors':
        #             actor = BayDoorActor(**{'location': [start[0],start[1]]})
        #         # elif self._reach_map[name]['Component'] == 'Forklifts':
        #             # actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #         elif self._reach_map[name]['Component'] == 'FreezerDoors':
        #             actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #         # elif self._reach_map[name]['Component'] == 'Lifters':
        #         #     # actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #         #     actor = ElevatorActor(name=name, data=_output_data[name] if name in _output_data else None, playback_manager=self.__pm, **{'start': start, 'end': end})
        #         elif self._reach_map[name]['Component'] == 'PalletProfiler':
        #             actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #         elif self._reach_map[name]['Component'] == 'RowCart':
        #             # actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #             actor = LevelActor(name=name, data=_output_data[name] if name in _output_data else None, playback_manager=self._Warehouse__pm, **{'base_location': start, 'width': '57', 'stack_depths': ['8', '8']})
        #         elif self._reach_map[name]['Component'] == 'TurnTable':
        #             actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})
        #
        #         if actor and actor.initialized:
        #             self._systems[name] = actor
        #             self._renderer.AddActor(actor)

        # ---Chris Addon ^^^--------------------------------------------------------------------------------------------


        for system_type in self._config:
            for name, system in self._config[system_type].items():
                actor = None

                if system_type == 'buffers':
                    start = [float(i) for i in system['in_location']]
                    end   = [float(i) for i in system['out_location']]
                    if len(start) < 3: start += [0.0]*(3-len(start))
                    if len(end) < 3: end += [0.0]*(3-len(end))
                    actor = BufferActor(**{'start': start, 'end': end, 'arrow': False, 'name': False})

                elif system_type == 'doors':
                    actor = BayDoorActor(**{'location': [float(i) for i in system['location']]})

                elif system_type == 'elevators':
                    start = [float(i) for i in
                             (self._config['buffers'][system['inbound_buffer']]['out_location'] if 'inbound_buffer' in system else \
                              self._config['buffers'][system['outbound_buffer']]['in_location'])]
                    end   = start[0:2] + [float(self._config['levels'][system['levels'][-1]]['storage_location'][2])]
                    if len(start) < 3: start += [0.0]*(3-len(start))
                    if len(end) < 3: end += [0.0]*(3-len(end))
                    actor = ElevatorActor(name=name,
                                          data=_data[name] if name in _data else None,
                                          playback_manager=self.__pm,
                                          **{'start': start, 'end': end})
                    # pdb.set_trace()
                elif system_type == 'levels':
                    # pdb.set_trace()
                    actor = LevelActor(name=name,
                                       data=_data[name] if name in _data else None,
                                       playback_manager=self.__pm,
                                       **{'base_location': system['storage_location'],
                                          'width': system['width'],
                                          'stack_depths': system['stack_depth']})
                elif system_type == 'floorplan':
                    actor = WallActor(name=name, **system)


                if actor and actor.initialized:
                    self._systems[name] = actor
                    self._renderer.AddActor(actor)

        # create pallet actor, add to warehouse systems and renderer
        self._systems['pallets'] = PalletsActor(self.__pm, _data['pallets'])
        self._renderer.AddActor(self._systems['pallets'])
        self.reload()

    def initializeFromFiles(self, warehouse_ini, rackstore_pickle, logs_dir, savefile=None, overwrite=False):
        # print('_warehouse.initializeFromFiles')
        """
        (Deprecated) Initialize all internal systems and data from a set of files
        """
        self.__pm.pause() # pause time
        self._config = self._loadConfigData(warehouse_ini)

        # Load from file if provided and not explicitly told to overwrite
        if savefile is not None and os.path.isfile(savefile) and not overwrite:
            logging.info('[WAREHOUSE] Loading pallet data from file.')
            with open(savefile, "rb") as f:
                _data = pickle.load(f)

        # Otherwise, parse logs to produce pallet-indexed dataframe and build pallet objects from dataframe
        else:
            # Load log data
            _data = self._dataFromLogs(logs_dir, savefile, overwrite)
            rackstores = self._loadPalletInitialization(rackstore_pickle)

            for id, system in tqdm.tqdm(rackstores.items(), desc='Appending Initial Rackstores', unit='racks'):
                # get system type by looping through system in ConfigObj object system type lists from .ini files
                system_type = [ k for k, v in self._config.items() if id in v.keys() ][0]

                for loc, rack in system.rackstore.items():
                    # get object by id in warehouse config
                    id_wh_config = self._config[system_type][id]
                    # warehouse config info about system_type
                    sys_loc = [float(i) for i in id_wh_config[SYSTEMS_LOOKUP[system_type]['loc']]]
                    for idx, pallet in enumerate(rack):
                        if pallet is not None and pallet.pid not in _data['pallets'].index:
                            _data['pallets'].loc[pallet.pid] = {
                                'sku': 1, #pallet.sku,
                                'activity start': SIMULATION_START_TIME,
                                'activity end': SIMULATION_END_TIME,
                                'activity windows': [],
                                'keyframes': [{ \
                                    'time': SIMULATION_START_TIME, \
                                            # rack loc
                                    'loc_x': loc.x + \
                                            # offset by 1 pallet.x if it's in +x
                                            (loc.x > sys_loc[0]) * AISLE.x + \
                                            # offset by its position in the rack
                                            ((loc.x > sys_loc[0]) * 2 - 1) * PALLET_SLOT.x * idx, \
                                    'loc_y': loc.y, \
                                    'loc_z': loc.z }] }

            # Save pallet data to pickle file if specified
            if savefile is not None:
                with open(savefile, "wb") as f:
                    pickle.dump(_data, f)

        # Create systems objects from config data
        for system_type in self._config:
            for name, system in self._config[system_type].items():
                actor = None
                if system_type   == 'buffers':
                    start = [float(i) for i in system['in_location']]
                    end   = [float(i) for i in system['out_location']]
                    actor = BufferActor(self._renderer, **{'start': start, 'end': end})
                elif system_type == 'elevators':
                    start = self._config['buffers'][system['inbound_buffer']]['out_location'] if 'inbound_buffer' in system else self._config['buffers'][system['outbound_buffer']]['in_location']
                    start = [float(i) for i in start]
                    end   = start[0:2] + [float(self._config['levels'][system['levels'][-1]]['storage_location'][2])]
                    actor = ElevatorActor(name=name, data=_data[name] if name in _data else None, playback_manager=self.__pm, **{'start': start, 'end': end})
                    self._renderer.AddActor(actor)
                # elif system_type == 'levels':    actor = LevelActor(self._renderer, system)
                if actor and actor.initialized: self._systems[name] = actor

        # create pallet actor, add to warehouse systems and renderer
        self._systems['pallets'] = PalletsActor(self.__pm, _data['pallets'])
        self._renderer.AddActor(self._systems['pallets'])
        self.reload()

    def _dataFromLogsSimDir(self,
                            path=None,
                            logs_path=None,
                            overwrite=False,
                            names=['state', 'action', 'time', 'null', 'loc_x', 'loc_y', 'loc_z', 'depth', 'pid', 'sku'],
                            parse_dates=['time'],
                            dtype={'pid': str, 'sku': str, 'state': str, 'action': str}):
        # print('_warehouse._dataFromLogsSimDir')
        """
        Build data dataframes from logs within the .linsim simulation directory
        """

        names = names + ['temp1', 'temp2']

        # merge all log files into a single dataframe (and add a column for the system name the log entry came from)
        df = pd.concat([ pd.concat([pd.DataFrame({'system': [os.path.splitext(sys_name)[0]] * len(sys_df)}), sys_df], axis=1)
                        for sys_name, sys_df in { f: pd.read_csv(os.path.join(path, logs_path, f),
                                    names=names, dtype=dtype,
                                    parse_dates=parse_dates,
                                    infer_datetime_format=True)
                        for f in tqdm.tqdm(os.listdir(os.path.join(path, logs_path)),
                                           desc='Importing Logs',
                                           unit='files') }.items() ])

        return {'pallets': self._palletDataFromLogsDF(df), **self._systemsDataFromLogsDF(df)}
    def _dataFromLogs(self,
                      log_dir,
                      overwrite=False,
                      names=['state', 'action', 'time', 'null', 'loc_x', 'loc_y', 'loc_z', 'depth', 'pid', 'sku'],
                      parse_dates=['time'],
                      dtype={'pid': str, 'sku': str, 'state': str, 'action': str}):
        # print('_warehouse._dataFromLogs')
        """
        (Deprecated) Build data dataframes from a specified log directory
        """

        # merge all log files into a single dataframe (and add a column for the system name the log entry came from)
        df = pd.concat([ pd.concat([pd.DataFrame({'system': [os.path.splitext(sys_name)[0]] * len(sys_df)}), sys_df], axis=1)
                        for sys_name, sys_df in { f: pd.read_csv(os.path.join(log_dir, f),
                                    names=names, dtype=dtype,
                                    parse_dates=parse_dates,
                                    infer_datetime_format=True)
                        for f in tqdm.tqdm(os.listdir(log_dir),
                                           desc='Importing Logs',
                                           unit='files') }.items() ])

        return {'pallets': self._palletDataFromLogsDF(df), **self._systemsDataFromLogsDF(df)}

    def _systemsDataFromLogsDF(self, df):
        # print('_warehouse._systemsDataFromLogsDF')
        """
        From the dataframe compiled from all the logs, isolate the elevator data and reorganize the datastructure appropriately
        """

        systems = df[(pd.notnull(df['loc_x'])) & (pd.notnull(df['loc_y'])) & (pd.notnull(df['loc_z'])) & (pd.notnull(df['time']))] \
                    .drop_duplicates(subset=['system', 'state', 'action', 'time'], keep='last') \
                    .sort_values(['time']) \
                    .groupby('system')

        return { sys_name: sys_df.sort_values(['time'])[['state', 'action', 'time', 'loc_x', 'loc_y', 'loc_z']].reset_index(drop=True) \
                 for sys_name, sys_df in systems if \
                 'buffers' not in self._config or sys_name not in self._config['buffers'] }

    def _palletDataFromLogsDF(self, df):
        # print('_warehouse._palletDataFromLogsDF')
        """
        From the dataframe compiled from all the logs, isolate the pallet data and reorganize the datastructure appropriately
        """

        # group by pallet ID and start time, deduplicating events at the same time
        # first filter for the first action duplicated at a given time
        # then filter for only the last timestamp at any time (these two steps needed to get first CPDO action for pallet position)
        df = df[(pd.notnull(df['pid'])) & (df['pid'] != '-1')] \
                .sort_values(['pid', 'time']) \
                .drop_duplicates(subset=['pid', 'action', 'time'], keep='first') \
                .drop_duplicates(subset=['pid', 'time'], keep='last') \
                .astype({'pid': str, 'sku': str, 'state': str, 'action': str}) \
                .set_index('pid') \
                .set_index('sku', append=True)

        # restructure data around pallet ids
        pallets = df.reset_index()[['pid', 'sku']].drop_duplicates().reset_index(drop=True)
        pallets['keyframes'] = np.empty(pallets.shape[0], dtype=dict)
        pallets['activity windows'] = np.empty(pallets.shape[0], dtype=list)
        pallets['activity start'] = np.empty(pallets.shape[0], dtype=list)
        pallets['activity end'] = np.empty(pallets.shape[0], dtype=list)

        # loop through pid's and aggregate data
        count = 0
        for i, data in tqdm.tqdm(enumerate(pallets.iterrows()),
                                 total=pallets.shape[0],
                                 desc='Loading Pallets',
                                 unit='pallets'):
            _, data = data # (dataframe row index, dataframe row data)
            ki = [] # keyframes for pallet (row i)
            ai = []

                                     # pid    # sku
            for _, rowdata in df.loc[data[0], data[1]].drop_duplicates().iterrows():
                # map rowdata to a keyframe dictionary (comprehension is much
                # faster than slicing a single dataframe row)
                ki.append({ k: rowdata[k] for k in ['time', 'state', 'action', 'loc_x', 'loc_y', 'loc_z']})
                if not np.isnan(rowdata['depth']):
                    ki[-1]['loc_x'] = ki[-1]['loc_x'] + rowdata['depth']


                ## ADDED AS WORKAROUND FOR ADDING PALLET DEPTH TO AISLE OFFSET
                # get system type by looping through system in ConfigObj object system type lists from .ini files
                # system_type = [ k for k, v in self._config.items() if rowdata['system'] in v.keys() ][0]
                # if system_type == 'levels' and ki[-1]['loc_x'] > float(self._config[system_type][rowdata['system']][SYSTEMS_LOOKUP[system_type]['loc']][0]):
                #     ki[-1]['loc_x'] += PALLET_SLOT.x
                ## DONE WITH WORKAROUND


                if rowdata['action'] in ['CPPU']: # capture rackstore pick ups
                    if not ai or len(ai[-1]) > 1: ai.append({'start': ki[-1]['time']})
                    else: ai[-1]['start'] = ki[-1]['time']
                elif rowdata['action'] in ['CPDO']: # capture rackstore dropoffs
                    if not ai or len(ai[-1]) > 1: ai.append({'end': ki[-1]['time']})
                    else: ai[-1]['end'] = ki[-1]['time']

                # if rowdata['action'] == 'CMRP' and len(ki) >= 2:
                #     pallets.ix[i]['sku'] = 3
                #     ki[-1]['loc_x'] = ki[-2]['loc_x']
                #     ki[-1]['loc_y'] = ki[-2]['loc_y']
                #     ki[-1]['loc_z'] = ki[-2]['loc_z']

            if not ai: ai.append({})
            ai[0]['start'] = ki[0]['time']
            ai[-1]['end'] = ki[-1]['time']

            pallets.ix[i]['keyframes'] = ki
            pallets.ix[i]['activity windows'] = ai
            pallets.ix[i]['activity start'] = pd.Timestamp(self.__sim_config['global']['simulation_start_time']) if ki[0]['action'] in ['CPPU'] else ki[0]['time']
            pallets.ix[i]['activity end'] = pd.Timestamp(self.__sim_config['global']['simulation_end_time']) if ki[-1]['action'] in ['CPDO'] else ki[-1]['time']

            # #  SOME DEBUGGING CODE FOR CHECKING KEFYRAME ISSUES
            # print(pallets.ix[i]['pid'])
            # print( '\n'.join([ str(kf) for kf in pallets.ix[i]['keyframes']]))
            # count += 1
            # if count > 7:
            #     break

        # make pallet id the row index
        pallets.set_index('pid', inplace=True)

        # return pallet dataframe
        return pallets

    def _strFormatPalletRow(self, data, index):
        # print('_warehouse._strFormatPalletRow')
        """
        A helper function for neatly printing pallet information from a dataframe row
        """
        pallet = data['pallets'].loc[index]

        print('Pallet Data at index {}:'.format(index))
        print('  sku: {}'.format(pallet['sku']))
        print('  active: {} to {}'.format(pallet['activity start'], pallet['activity end']))
        print('  keyframes: \n{}'.format('    \n'.join(str(pd.DataFrame(pallet['keyframes'])).split('\n'))))
        print('  activity: \n{}'.format('    \n'.join(str(pd.DataFrame(pallet['activity windows'])).split('\n'))))
