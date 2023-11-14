/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the OAI Public License, Version 1.1  (the "License"); you may not use this file
 * except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.openairinterface.org/?page_id=698
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the OpenAirInterface (OAI) Software Alliance:
 *      contact@openairinterface.org
 */

/*! \file main.c
 * \brief top init of Layer 2
 * \author  Navid Nikaein and Raymond Knopp
 * \date 2010 - 2014
 * \version 1.0
 * \email: navid.nikaein@eurecom.fr
 * @ingroup _mac

 */

#include <dlfcn.h>
#include "mac.h"
#include "mac_proto.h"
#include "mac_extern.h"
#include "assertions.h"
#include "LAYER2/PDCP_v10.1.0/pdcp.h"
#include "RRC/LTE/rrc_defs.h"
#include "common/utils/LOG/log.h"
#include "RRC/L2_INTERFACE/openair_rrc_L2_interface.h"
#include "common/ran_context.h"
#include "intertask_interface.h"
#include <pthread.h>

extern RAN_CONTEXT_t RC;
extern int oai_exit;

void lte_dump_mac_stats(eNB_MAC_INST *mac, FILE *fd)
{
  UE_info_t *UE_info = &(mac->UE_info);

  for (int UE_id = 0; UE_id < MAX_MOBILES_PER_ENB; UE_id++) {
    if (UE_id < MAX_LOCALIZATION_UE) {
      RC.HL[UE_id].rnti = 0;
    }
    if (UE_info->active[UE_id]) {
      int rnti = UE_RNTI(mac->Mod_id, UE_id);
      int CC_id = UE_PCCID(mac->Mod_id, UE_id);
      UE_sched_ctrl_t *UE_scheduling_control = &(UE_info->UE_sched_ctrl[UE_id]);

      double total_bler;
      if (UE_scheduling_control->pusch_rx_num[CC_id] == 0 && UE_scheduling_control->pusch_rx_error_num[CC_id] == 0) {
        total_bler = 0;
      } else {
        total_bler = (double)UE_scheduling_control->pusch_rx_error_num[CC_id] / (double)(UE_scheduling_control->pusch_rx_error_num[CC_id] + UE_scheduling_control->pusch_rx_num[CC_id]) * 100;
      }

      if (UE_id < MAX_LOCALIZATION_UE) {
        RC.HL[UE_id].rnti = rnti;
        if (UE_scheduling_control->timing_advance) RC.HL[UE_id].MAC.timing_advance = UE_scheduling_control->timing_advance;
        if (UE_info->UE_template[CC_id][UE_id].phr_info) RC.HL[UE_id].MAC.ue_power_headroom[CC_id] = UE_info->UE_template[CC_id][UE_id].phr_info;
        if (UE_scheduling_control->dl_cqi[CC_id]) RC.HL[UE_id].MAC.dl_cqi[CC_id] =  UE_scheduling_control->dl_cqi[CC_id];
        if (UE_scheduling_control->pusch_snr[CC_id]) RC.HL[UE_id].MAC.pusch_snr[CC_id] = UE_scheduling_control->pusch_snr[CC_id];
        if (UE_scheduling_control->pucch1_snr[CC_id]) RC.HL[UE_id].MAC.pucch1_snr[CC_id] = UE_scheduling_control->pucch1_snr[CC_id];
        if (total_bler) RC.HL[UE_id].MAC.total_BLER = total_bler;

        for (int i = 0; i < 8; i++) {
          RC.HL[UE_id].MAC.harq_rtt_timer[CC_id][i] = UE_scheduling_control->harq_rtt_timer[CC_id][i];
          RC.HL[UE_id].MAC.ul_harq_rtt_timer[CC_id][i] = UE_scheduling_control->ul_harq_rtt_timer[CC_id][i];
          RC.HL[UE_id].MAC.ul_synchronous_harq_timer[CC_id][i] = UE_scheduling_control->ul_synchronous_harq_timer[CC_id][i];
        }

        if (UE_info->eNB_UE_stats[CC_id][UE_id].UL_rssi) RC.HL[UE_id].MAC.UESTAT.UL_rssi[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].UL_rssi;
        if (UE_info->eNB_UE_stats[CC_id][UE_id].ulsch_mcs1) RC.HL[UE_id].MAC.UESTAT.ulsch_mcs1[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].ulsch_mcs1;
        if (UE_info->eNB_UE_stats[CC_id][UE_id].ulsch_mcs2) RC.HL[UE_id].MAC.UESTAT.ulsch_mcs2[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].ulsch_mcs2;
        if (UE_info->eNB_UE_stats[CC_id][UE_id].Po_PUCCH_dBm) RC.HL[UE_id].MAC.UESTAT.Po_PUCCH_dBm[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].Po_PUCCH_dBm;
        if (UE_info->eNB_UE_stats[CC_id][UE_id].Po_PUCCH_update) RC.HL[UE_id].MAC.UESTAT.Po_PUCCH_update[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].Po_PUCCH_update;
        if (UE_info->eNB_UE_stats[CC_id][UE_id].snr) RC.HL[UE_id].MAC.UESTAT.snr[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].snr;
        if (UE_info->eNB_UE_stats[CC_id][UE_id].target_snr) RC.HL[UE_id].MAC.UESTAT.target_snr[CC_id] = UE_info->eNB_UE_stats[CC_id][UE_id].target_snr;

      }     

    }
  }
  fflush(fd);
  return;
}

void *mac_stats_thread(void *param)
{
  eNB_MAC_INST *mac = (eNB_MAC_INST *)param;
  FILE *fd;

  while (!oai_exit) {
    sleep(1);
    fd = fopen("MAC_stats.log", "w+");
    AssertFatal(fd != NULL, "Cannot open MAC_stats.log\n");
    lte_dump_mac_stats(mac, fd);
    fclose(fd);
  }
  return NULL;
}

void init_UE_info(UE_info_t *UE_info)
{
  UE_info->num_UEs = 0;
  init_ue_list(&UE_info->list);
  memset(UE_info->DLSCH_pdu, 0, sizeof(UE_info->DLSCH_pdu));
  memset(UE_info->UE_template, 0, sizeof(UE_info->UE_template));
  memset(UE_info->eNB_UE_stats, 0, sizeof(UE_info->eNB_UE_stats));
  memset(UE_info->UE_sched_ctrl, 0, sizeof(UE_info->UE_sched_ctrl));
  memset(UE_info->active, 0, sizeof(UE_info->active));
}

void mac_top_init_eNB(void)
{
  module_id_t i, j;
  eNB_MAC_INST **mac;

  LOG_I(MAC, "[MAIN] Init function start:nb_macrlc_inst=%d\n",
        RC.nb_macrlc_inst);

  if (RC.nb_macrlc_inst <= 0) {
    RC.mac = NULL;
    return;
  }

  mac = malloc16(RC.nb_macrlc_inst * sizeof(eNB_MAC_INST *));
  AssertFatal(mac != NULL,
              "can't ALLOCATE %zu Bytes for %d eNB_MAC_INST with size %zu \n",
              RC.nb_macrlc_inst * sizeof(eNB_MAC_INST *),
              RC.nb_macrlc_inst, sizeof(eNB_MAC_INST));
  for (i = 0; i < RC.nb_macrlc_inst; i++) {
    mac[i] = malloc16(sizeof(eNB_MAC_INST));
    AssertFatal(mac[i] != NULL,
                "can't ALLOCATE %zu Bytes for %d eNB_MAC_INST with size %zu \n",
                RC.nb_macrlc_inst * sizeof(eNB_MAC_INST *),
                RC.nb_macrlc_inst, sizeof(eNB_MAC_INST));
    LOG_D(MAC,
          "[MAIN] ALLOCATE %zu Bytes for %d eNB_MAC_INST @ %p\n",
          sizeof(eNB_MAC_INST), RC.nb_macrlc_inst, mac);
    bzero(mac[i], sizeof(eNB_MAC_INST));
    mac[i]->Mod_id = i;
    for (j = 0; j < MAX_NUM_CCs; j++) {
      mac[i]->DL_req[j].dl_config_request_body.dl_config_pdu_list =
          mac[i]->dl_config_pdu_list[j];
      mac[i]->UL_req[j].ul_config_request_body.ul_config_pdu_list =
          mac[i]->ul_config_pdu_list[j];
      for (int k = 0; k < 10; k++)
        mac[i]->UL_req_tmp[j][k].ul_config_request_body.ul_config_pdu_list =
            mac[i]->ul_config_pdu_list_tmp[j][k];
      for(int sf=0;sf<10;sf++)
        mac[i]->HI_DCI0_req[j][sf].hi_dci0_request_body.hi_dci0_pdu_list =
            mac[i]->hi_dci0_pdu_list[j][sf];
      mac[i]->TX_req[j].tx_request_body.tx_pdu_list = mac[i]->tx_request_pdu[j];
      mac[i]->ul_handle = 0;
    }

    mac[i]->if_inst = IF_Module_init(i);

    mac[i]->pre_processor_dl.algorithm = 0;
    mac[i]->pre_processor_dl.dl = dlsch_scheduler_pre_processor;
    char *s = "round_robin_dl";
    void *d = dlsym(NULL, s);
    AssertFatal(d, "%s(): no scheduler algo '%s' found\n", __func__, s);
    mac[i]->pre_processor_dl.dl_algo = *(default_sched_dl_algo_t *) d;
    mac[i]->pre_processor_dl.dl_algo.data = mac[i]->pre_processor_dl.dl_algo.setup();

    mac[i]->pre_processor_ul.algorithm = 0;
    mac[i]->pre_processor_ul.ul = ulsch_scheduler_pre_processor;
    s = "round_robin_ul";
    d = dlsym(NULL, s);
    AssertFatal(d, "%s(): no scheduler algo '%s' found\n", __func__, s);
    mac[i]->pre_processor_ul.ul_algo = *(default_sched_ul_algo_t *) d;
    mac[i]->pre_processor_ul.ul_algo.data = mac[i]->pre_processor_ul.ul_algo.setup();

    init_UE_info(&mac[i]->UE_info);
  }

  RC.mac = mac;

  AssertFatal(rlc_module_init(1) == 0,
      "Could not initialize RLC layer\n");

  // These should be out of here later
  pdcp_layer_init();

  rrc_init_global_param();

  for (i = 0; i < RC.nb_macrlc_inst; i++)
    threadCreate(&mac[i]->mac_stats_thread, mac_stats_thread, (void *)mac[i], "mac stats", -1, sched_get_priority_min(SCHED_OAI));
}

void mac_init_cell_params(int Mod_idP, int CC_idP)
{

    int j;
    UE_TEMPLATE *UE_template;

    //COMMON_channels_t *cc = &RC.mac[Mod_idP]->common_channels[CC_idP];

    memset(&RC.mac[Mod_idP]->eNB_stats, 0, sizeof(eNB_STATS));
    UE_template =
	(UE_TEMPLATE *) & RC.mac[Mod_idP]->UE_info.UE_template[CC_idP][0];

    for (j = 0; j < MAX_MOBILES_PER_ENB; j++) {
	UE_template[j].rnti = 0;
	// initiallize the eNB to UE statistics
	memset(&RC.mac[Mod_idP]->UE_info.eNB_UE_stats[CC_idP][j], 0,
	       sizeof(eNB_UE_STATS));
    }

}


int rlcmac_init_global_param(void)
{


    LOG_I(MAC, "[MAIN] CALLING RLC_MODULE_INIT...\n");

    if (rlc_module_init(1) != 0) {
	return (-1);
    }

    pdcp_layer_init();

    LOG_I(MAC, "[MAIN] Init Global Param Done\n");

    return 0;
}

int l2_init_eNB(void)
{



    LOG_I(MAC, "[MAIN] MAC_INIT_GLOBAL_PARAM IN...\n");

    rlcmac_init_global_param();

    LOG_D(MAC, "[MAIN] ALL INIT OK\n");


    return (1);
}
