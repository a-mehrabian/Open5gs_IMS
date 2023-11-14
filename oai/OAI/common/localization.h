#define MAX_LOCALIZATION_UE 12
#define NFAPI_CC_MAX_L 1
#define MAX_NUM_RU_PER_eNB_L 1
#define NUMBER_OF_SRS_MAX_L 16
#define NUMBER_OF_ULSCH_MAX_L 8
#define MAXIMUM_NEIGHBOR_CELL_L 2
#define MAXIMUM_ANNTENA_L 1
#define MAXIMUM_OFDM_SYMBOL_SIZE_L 10


/**
   * "CQI" stands for "Channel Quality Indicator." It's a metric used by the User Equipment (UE) to report back to the base station (eNodeB or gNodeB) a
   * bout the perceived quality of the downlink channel. 
   * The base station uses this feedback to adapt the modulation and coding scheme (MCS) for the downlink data transmission to the UE, 
   * ensuring efficient use of the available spectrum and maintaining a target block error rate.
      The CQI value is an integer in the range of 0 to 15, with higher values indicating better channel quality. 
      The mapping of CQI values to modulation and coding schemes is defined in the LTE standards.
  */
typedef struct {
  int pucch2_snr[NFAPI_CC_MAX_L];
  int pusch_snr[NFAPI_CC_MAX_L];
  int pusch_snr_avg[NFAPI_CC_MAX_L];
  
  int ul_cqi;
  int dl_cqi;

  /** the timing_advance_r9 (as well as the standard timing_advance) can be used to estimate the distance between the UE (User Equipment) and the eNodeB
  Each unit of the TA value corresponds to a specific distance. In LTE, one TA unit is equivalent to 
16xTs seconds, where Tsis the sampling time, which is approximately 32 * 10^-8 seconds
  **/
  int timing_advance;
  int timing_advance_r9;
} localization_csi_t;

typedef struct {
  
  int ul_cqi;
  int dl_cqi;

  int timing_advance;

  int pusch_snr[NFAPI_CC_MAX_L];
  int pusch_snr_avg[NFAPI_CC_MAX_L];

  // It essentially indicates how much more power the UE can use for transmission if required
  int ue_power_headroom;
  // ue trx powert
  int estimated_ue_power;

} localization_ul_sdu_t;

typedef struct {
  /// preassigned mcs after rate adaptation
  int ulsch_mcs1[NFAPI_CC_MAX_L];
  /// adjusted mcs
  int ulsch_mcs2[NFAPI_CC_MAX_L];
  /// Uplink measured RSSI
  int UL_rssi[NFAPI_CC_MAX_L];

  /// PUCCH1a/b power (dBm)
  int Po_PUCCH_dBm[NFAPI_CC_MAX_L];
  /// Indicator that Po_PUCCH has been updated by PHY
  int Po_PUCCH_update[NFAPI_CC_MAX_L];

  /// snr
  int snr[NFAPI_CC_MAX_L];
  /// target snr
  int target_snr[NFAPI_CC_MAX_L];

} localization_ueStat_t;

typedef struct { 
  
  int timing_advance;

  /// (UL) HARQ RTT timers, especially used for CDRX operations, one timer per cell per harq process (and per user)
  // This represents the Round Trip Time (RTT) timers for each HARQ process on each carrier component (CC)
  int harq_rtt_timer[NFAPI_CC_MAX_L][8];
  int ul_harq_rtt_timer[NFAPI_CC_MAX_L][8]; // Note: UL HARQ RTT timers are only for asynchronous HARQ processes
  int ul_synchronous_harq_timer[NFAPI_CC_MAX_L][8];  // These timers are used for UL synchronous HARQ processes  

  // It essentially indicates how much more power the UE can use for transmission if required
  int ue_power_headroom[NFAPI_CC_MAX_L];

  int dl_cqi[NFAPI_CC_MAX_L];
  int ul_cqi[NFAPI_CC_MAX_L];

  int pusch_snr[NFAPI_CC_MAX_L];
  int pucch1_snr[NFAPI_CC_MAX_L];

  //block error rate  
  int total_BLER;  
  
  localization_csi_t CSI; 

  localization_ul_sdu_t ULSDU;

  localization_ueStat_t UESTAT;
  
  
} localization_mac_t;

typedef struct {
  /// \brief Hold the channel estimates in frequency domain based on SRS.
  /// - first index: rx antenna id [0..nb_antennas_rx[
  /// - second index: ? [0..ofdm_symbol_size[
  int srs_ch_estimates[MAXIMUM_ANNTENA_L][MAXIMUM_OFDM_SYMBOL_SIZE_L];
  /// \brief Hold the channel estimates in time domain based on SRS.
  /// - first index: rx antenna id [0..nb_antennas_rx[
  /// - second index: ? [0..2*ofdm_symbol_size[
  int srs_ch_estimates_time[MAXIMUM_ANNTENA_L][MAXIMUM_OFDM_SYMBOL_SIZE_L];
  /// \brief Holds the SRS for channel estimation at the RX.
  /// - first index: rx antenna id [0..nb_antennas_rx[
  /// - second index: ? [0..ofdm_symbol_size[
  int srs[MAXIMUM_ANNTENA_L];
} localization_srs_t;

typedef struct {
  //! total estimated noise power (linear)
  unsigned int   n0_power_tot;
  //! estimated avg noise power (dB)
  unsigned short n0_power_tot_dB;
  //! etimated avg noise power over all RB (dB)
  short n0_subband_power_avg_dB;
  // eNB measurements (per user)
  //! estimated received spatial signal power (linear)
  unsigned int   rx_spatial_power[NUMBER_OF_SRS_MAX_L][2][2];
  //! estimated received spatial signal power (dB)
  unsigned short rx_spatial_power_dB[NUMBER_OF_SRS_MAX_L][2][2];
  //! estimated rssi (dBm)
  short          rx_rssi_dBm[NUMBER_OF_SRS_MAX_L];  
}localization_L1Measurments_t;

typedef struct {
  int ulsch_power[4]; //NUMBER_OF_ULSCH_MAX
  int ulsch_noise_power[4]; //NUMBER_OF_ULSCH_MAX
  int current_Qm;
  int current_mcs;
  int timing_offset;
} localization_L1USCH_t;

// statis for UCI (PUCCH) measurement
typedef struct {
  // Represents the phase information of the received PUCCH format 1 signal. Phase information can be crucial for certain operations like beamforming.
  int pucch1_phase;

  //represent some statistics related to low and high values (possibly SNR or power levels) for PUCCH format 1
  // pure power, no db
  int pucch1_low_power_stat[4]; //NUMBER_OF_SCH_STATS_MAX
  int pucch1_high_power_stat[4]; //NUMBER_OF_SCH_STATS_MAX

  /// PUCCH background noise level
  int n0_pucch_dB;
} localization_UCI_t;

typedef struct {
  localization_L1Measurments_t L1Measurments;
  localization_L1USCH_t USHCH;
  localization_UCI_t UCI;
  localization_srs_t SRS;
} localization_physical_t;

typedef struct {
  long rsrp_serving_cell;
  long rsrq_serving_cell;
  long rsrp_neighbor_cell[MAXIMUM_NEIGHBOR_CELL_L];
  long rsrq_neighbor_cell[MAXIMUM_NEIGHBOR_CELL_L]; 

} localization_rrc_t;

typedef struct {
  int rnti;
  char imsi[16];
  localization_mac_t MAC;
  localization_physical_t L1; 
  localization_rrc_t RRC; 
} Localization_t;