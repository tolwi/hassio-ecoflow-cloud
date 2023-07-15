# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: powerstream.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11powerstream.proto\"\xf3\x14\n\x11InverterHeartbeat\x12\x19\n\x0cinv_err_code\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x1a\n\rinv_warn_code\x18\x03 \x01(\rH\x01\x88\x01\x01\x12\x19\n\x0cpv1_err_code\x18\x02 \x01(\rH\x02\x88\x01\x01\x12\x1a\n\rpv1_warn_code\x18\x04 \x01(\rH\x03\x88\x01\x01\x12\x19\n\x0cpv2_err_code\x18\x05 \x01(\rH\x04\x88\x01\x01\x12\x1d\n\x10pv2_warning_code\x18\x06 \x01(\rH\x05\x88\x01\x01\x12\x19\n\x0c\x62\x61t_err_code\x18\x07 \x01(\rH\x06\x88\x01\x01\x12\x1d\n\x10\x62\x61t_warning_code\x18\x08 \x01(\rH\x07\x88\x01\x01\x12\x19\n\x0cllc_err_code\x18\t \x01(\rH\x08\x88\x01\x01\x12\x1d\n\x10llc_warning_code\x18\n \x01(\rH\t\x88\x01\x01\x12\x17\n\npv1_statue\x18\x0b \x01(\rH\n\x88\x01\x01\x12\x17\n\npv2_statue\x18\x0c \x01(\rH\x0b\x88\x01\x01\x12\x17\n\nbat_statue\x18\r \x01(\rH\x0c\x88\x01\x01\x12\x17\n\nllc_statue\x18\x0e \x01(\rH\r\x88\x01\x01\x12\x17\n\ninv_statue\x18\x0f \x01(\rH\x0e\x88\x01\x01\x12\x1b\n\x0epv1_input_volt\x18\x10 \x01(\x05H\x0f\x88\x01\x01\x12\x18\n\x0bpv1_op_volt\x18\x11 \x01(\x05H\x10\x88\x01\x01\x12\x1a\n\rpv1_input_cur\x18\x12 \x01(\x05H\x11\x88\x01\x01\x12\x1c\n\x0fpv1_input_watts\x18\x13 \x01(\x05H\x12\x88\x01\x01\x12\x15\n\x08pv1_temp\x18\x14 \x01(\x05H\x13\x88\x01\x01\x12\x1b\n\x0epv2_input_volt\x18\x15 \x01(\x05H\x14\x88\x01\x01\x12\x18\n\x0bpv2_op_volt\x18\x16 \x01(\x05H\x15\x88\x01\x01\x12\x1a\n\rpv2_input_cur\x18\x17 \x01(\x05H\x16\x88\x01\x01\x12\x1c\n\x0fpv2_input_watts\x18\x18 \x01(\x05H\x17\x88\x01\x01\x12\x15\n\x08pv2_temp\x18\x19 \x01(\x05H\x18\x88\x01\x01\x12\x1b\n\x0e\x62\x61t_input_volt\x18\x1a \x01(\x05H\x19\x88\x01\x01\x12\x18\n\x0b\x62\x61t_op_volt\x18\x1b \x01(\x05H\x1a\x88\x01\x01\x12\x1a\n\rbat_input_cur\x18\x1c \x01(\x05H\x1b\x88\x01\x01\x12\x1c\n\x0f\x62\x61t_input_watts\x18\x1d \x01(\x05H\x1c\x88\x01\x01\x12\x15\n\x08\x62\x61t_temp\x18\x1e \x01(\x05H\x1d\x88\x01\x01\x12\x14\n\x07\x62\x61t_soc\x18\x1f \x01(\rH\x1e\x88\x01\x01\x12\x1b\n\x0ellc_input_volt\x18  \x01(\x05H\x1f\x88\x01\x01\x12\x18\n\x0bllc_op_volt\x18! \x01(\x05H \x88\x01\x01\x12\x15\n\x08llc_temp\x18\" \x01(\x05H!\x88\x01\x01\x12\x1b\n\x0einv_input_volt\x18# \x01(\x05H\"\x88\x01\x01\x12\x18\n\x0binv_op_volt\x18$ \x01(\x05H#\x88\x01\x01\x12\x1b\n\x0einv_output_cur\x18% \x01(\x05H$\x88\x01\x01\x12\x1d\n\x10inv_output_watts\x18& \x01(\x05H%\x88\x01\x01\x12\x15\n\x08inv_temp\x18\' \x01(\x05H&\x88\x01\x01\x12\x15\n\x08inv_freq\x18( \x01(\x05H\'\x88\x01\x01\x12\x17\n\ninv_dc_cur\x18) \x01(\x05H(\x88\x01\x01\x12\x14\n\x07\x62p_type\x18* \x01(\x05H)\x88\x01\x01\x12\x1d\n\x10inv_relay_status\x18+ \x01(\x05H*\x88\x01\x01\x12\x1d\n\x10pv1_relay_status\x18, \x01(\x05H+\x88\x01\x01\x12\x1d\n\x10pv2_relay_status\x18- \x01(\x05H,\x88\x01\x01\x12\x1c\n\x0finstall_country\x18. \x01(\rH-\x88\x01\x01\x12\x19\n\x0cinstall_town\x18/ \x01(\rH.\x88\x01\x01\x12\x1c\n\x0fpermanent_watts\x18\x30 \x01(\rH/\x88\x01\x01\x12\x1a\n\rdynamic_watts\x18\x31 \x01(\rH0\x88\x01\x01\x12\x1c\n\x0fsupply_priority\x18\x32 \x01(\rH1\x88\x01\x01\x12\x18\n\x0blower_limit\x18\x33 \x01(\rH2\x88\x01\x01\x12\x18\n\x0bupper_limit\x18\x34 \x01(\rH3\x88\x01\x01\x12\x17\n\ninv_on_off\x18\x35 \x01(\rH4\x88\x01\x01\x12\x1e\n\x11wireless_err_code\x18\x36 \x01(\rH5\x88\x01\x01\x12\x1f\n\x12wireless_warn_code\x18\x37 \x01(\rH6\x88\x01\x01\x12\x1b\n\x0einv_brightness\x18\x38 \x01(\rH7\x88\x01\x01\x12 \n\x13heartbeat_frequency\x18\x39 \x01(\rH8\x88\x01\x01\x12\x18\n\x0brated_power\x18: \x01(\rH9\x88\x01\x01\x12\x1b\n\x0e\x62\x61ttery_remain\x18< \x01(\rH:\x88\x01\x01\x42\x0f\n\r_inv_err_codeB\x10\n\x0e_inv_warn_codeB\x0f\n\r_pv1_err_codeB\x10\n\x0e_pv1_warn_codeB\x0f\n\r_pv2_err_codeB\x13\n\x11_pv2_warning_codeB\x0f\n\r_bat_err_codeB\x13\n\x11_bat_warning_codeB\x0f\n\r_llc_err_codeB\x13\n\x11_llc_warning_codeB\r\n\x0b_pv1_statueB\r\n\x0b_pv2_statueB\r\n\x0b_bat_statueB\r\n\x0b_llc_statueB\r\n\x0b_inv_statueB\x11\n\x0f_pv1_input_voltB\x0e\n\x0c_pv1_op_voltB\x10\n\x0e_pv1_input_curB\x12\n\x10_pv1_input_wattsB\x0b\n\t_pv1_tempB\x11\n\x0f_pv2_input_voltB\x0e\n\x0c_pv2_op_voltB\x10\n\x0e_pv2_input_curB\x12\n\x10_pv2_input_wattsB\x0b\n\t_pv2_tempB\x11\n\x0f_bat_input_voltB\x0e\n\x0c_bat_op_voltB\x10\n\x0e_bat_input_curB\x12\n\x10_bat_input_wattsB\x0b\n\t_bat_tempB\n\n\x08_bat_socB\x11\n\x0f_llc_input_voltB\x0e\n\x0c_llc_op_voltB\x0b\n\t_llc_tempB\x11\n\x0f_inv_input_voltB\x0e\n\x0c_inv_op_voltB\x11\n\x0f_inv_output_curB\x13\n\x11_inv_output_wattsB\x0b\n\t_inv_tempB\x0b\n\t_inv_freqB\r\n\x0b_inv_dc_curB\n\n\x08_bp_typeB\x13\n\x11_inv_relay_statusB\x13\n\x11_pv1_relay_statusB\x13\n\x11_pv2_relay_statusB\x12\n\x10_install_countryB\x0f\n\r_install_townB\x12\n\x10_permanent_wattsB\x10\n\x0e_dynamic_wattsB\x12\n\x10_supply_priorityB\x0e\n\x0c_lower_limitB\x0e\n\x0c_upper_limitB\r\n\x0b_inv_on_offB\x14\n\x12_wireless_err_codeB\x15\n\x13_wireless_warn_codeB\x11\n\x0f_inv_brightnessB\x16\n\x14_heartbeat_frequencyB\x0e\n\x0c_rated_powerB\x11\n\x0f_battery_remain\"F\n\x12PermanentWattsPack\x12\x1c\n\x0fpermanent_watts\x18\x01 \x01(\rH\x00\x88\x01\x01\x42\x12\n\x10_permanent_watts\"F\n\x12SupplyPriorityPack\x12\x1c\n\x0fsupply_priority\x18\x01 \x01(\rH\x00\x88\x01\x01\x42\x12\n\x10_supply_priority\"8\n\x0c\x42\x61tLowerPack\x12\x18\n\x0blower_limit\x18\x01 \x01(\x05H\x00\x88\x01\x01\x42\x0e\n\x0c_lower_limit\"8\n\x0c\x42\x61tUpperPack\x12\x18\n\x0bupper_limit\x18\x01 \x01(\x05H\x00\x88\x01\x01\x42\x0e\n\x0c_upper_limit\"8\n\x0e\x42rightnessPack\x12\x17\n\nbrightness\x18\x01 \x01(\x05H\x00\x88\x01\x01\x42\r\n\x0b_brightness\"\xd7\x02\n\tPowerItem\x12\x16\n\ttimestamp\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x15\n\x08timezone\x18\x02 \x01(\x11H\x01\x88\x01\x01\x12\x1e\n\x11inv_to_grid_power\x18\x03 \x01(\rH\x02\x88\x01\x01\x12\x1e\n\x11inv_to_plug_power\x18\x04 \x01(\rH\x03\x88\x01\x01\x12\x1a\n\rbattery_power\x18\x05 \x01(\x05H\x04\x88\x01\x01\x12\x1d\n\x10pv1_output_power\x18\x06 \x01(\rH\x05\x88\x01\x01\x12\x1d\n\x10pv2_output_power\x18\x07 \x01(\rH\x06\x88\x01\x01\x42\x0c\n\n_timestampB\x0b\n\t_timezoneB\x14\n\x12_inv_to_grid_powerB\x14\n\x12_inv_to_plug_powerB\x10\n\x0e_battery_powerB\x13\n\x11_pv1_output_powerB\x13\n\x11_pv2_output_power\"S\n\tPowerPack\x12\x14\n\x07sys_seq\x18\x01 \x01(\rH\x00\x88\x01\x01\x12$\n\x10sys_power_stream\x18\x02 \x03(\x0b\x32\n.PowerItemB\n\n\x08_sys_seq\"0\n\x0cPowerAckPack\x12\x14\n\x07sys_seq\x18\x01 \x01(\rH\x00\x88\x01\x01\x42\n\n\x08_sys_seq\"?\n\x0bNodeMassage\x12\x0f\n\x02sn\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x10\n\x03mac\x18\x02 \x01(\x0cH\x01\x88\x01\x01\x42\x05\n\x03_snB\x06\n\x04_mac\"\x9e\x02\n\x11MeshChildNodeInfo\x12\x1a\n\rtopology_type\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x1a\n\rmesh_protocol\x18\x02 \x01(\rH\x01\x88\x01\x01\x12\x1f\n\x12max_sub_device_num\x18\x03 \x01(\rH\x02\x88\x01\x01\x12\x1a\n\rparent_mac_id\x18\x04 \x01(\x0cH\x03\x88\x01\x01\x12\x14\n\x07mesh_id\x18\x05 \x01(\x0cH\x04\x88\x01\x01\x12%\n\x0fsub_device_list\x18\x06 \x03(\x0b\x32\x0c.NodeMassageB\x10\n\x0e_topology_typeB\x10\n\x0e_mesh_protocolB\x15\n\x13_max_sub_device_numB\x10\n\x0e_parent_mac_idB\n\n\x08_mesh_idb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'powerstream_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_INVERTERHEARTBEAT']._serialized_start=22
  _globals['_INVERTERHEARTBEAT']._serialized_end=2697
  _globals['_PERMANENTWATTSPACK']._serialized_start=2699
  _globals['_PERMANENTWATTSPACK']._serialized_end=2769
  _globals['_SUPPLYPRIORITYPACK']._serialized_start=2771
  _globals['_SUPPLYPRIORITYPACK']._serialized_end=2841
  _globals['_BATLOWERPACK']._serialized_start=2843
  _globals['_BATLOWERPACK']._serialized_end=2899
  _globals['_BATUPPERPACK']._serialized_start=2901
  _globals['_BATUPPERPACK']._serialized_end=2957
  _globals['_BRIGHTNESSPACK']._serialized_start=2959
  _globals['_BRIGHTNESSPACK']._serialized_end=3015
  _globals['_POWERITEM']._serialized_start=3018
  _globals['_POWERITEM']._serialized_end=3361
  _globals['_POWERPACK']._serialized_start=3363
  _globals['_POWERPACK']._serialized_end=3446
  _globals['_POWERACKPACK']._serialized_start=3448
  _globals['_POWERACKPACK']._serialized_end=3496
  _globals['_NODEMASSAGE']._serialized_start=3498
  _globals['_NODEMASSAGE']._serialized_end=3561
  _globals['_MESHCHILDNODEINFO']._serialized_start=3564
  _globals['_MESHCHILDNODEINFO']._serialized_end=3850
# @@protoc_insertion_point(module_scope)