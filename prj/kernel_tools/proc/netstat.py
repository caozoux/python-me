#!/bin/python3

import time
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interval", type="int", dest="interval", default="1",
                  help="--interval interval ")
parser.add_option("-m", "--mode", type="string", dest="mode",
                  help="--mode netstat/snmp")

(options, args) = parser.parse_args()

#SyncookiesSent,SyncookiesRecv,SyncookiesFailed,EmbryonicRsts,PruneCalled,RcvPruned,OfoPruned,OutOfWindowIcmps,LockDroppedIcmps,ArpFilter,TW,TWRecycled,TWKilled,PAWSActive,PAWSEstab,DelayedACKs,DelayedACKLocked,DelayedACKLost,ListenOverflows,ListenDrops,TCPHPHits,TCPPureAcks,TCPHPAcks,TCPRenoRecovery,TCPSackRecovery,TCPSACKReneging,TCPSACKReorder,TCPRenoReorder,TCPTSReorder,TCPFullUndo,TCPPartialUndo,TCPDSACKUndo,TCPLossUndo,TCPLostRetransmit,TCPRenoFailures,TCPSackFailures,TCPLossFailures,TCPFastRetrans,TCPSlowStartRetrans,TCPTimeouts,TCPLossProbes,TCPLossProbeRecovery,TCPRenoRecoveryFail,TCPSackRecoveryFail,TCPRcvCollapsed,TCPBacklogCoalesce,TCPDSACKOldSent,TCPDSACKOfoSent,TCPDSACKRecv,TCPDSACKOfoRecv,TCPAbortOnData,TCPAbortOnClose,TCPAbortOnMemory,TCPAbortOnTimeout,TCPAbortOnLinger,TCPAbortFailed,TCPMemoryPressures,TCPMemoryPressuresChrono,TCPSACKDiscard,TCPDSACKIgnoredOld,TCPDSACKIgnoredNoUndo,TCPSpuriousRTOs,TCPMD5NotFound,TCPMD5Unexpected,TCPMD5Failure,TCPSackShifted,TCPSackMerged,TCPSackShiftFallback,TCPBacklogDrop,PFMemallocDrop,TCPMinTTLDrop,TCPDeferAcceptDrop,IPReversePathFilter,TCPTimeWaitOverflow,TCPReqQFullDoCookies,TCPReqQFullDrop,TCPRetransFail,TCPRcvCoalesce,TCPOFOQueue,TCPOFODrop,TCPOFOMerge,TCPChallengeACK,TCPSYNChallenge,TCPFastOpenActive,TCPFastOpenActiveFail,TCPFastOpenPassive,TCPFastOpenPassiveFail,TCPFastOpenListenOverflow,TCPFastOpenCookieReqd,TCPFastOpenBlackhole,TCPSpuriousRtxHostQueues,BusyPollRxPackets,TCPAutoCorking,TCPFromZeroWindowAdv,TCPToZeroWindowAdv,TCPWantZeroWindowAdv,TCPSynRetrans,TCPOrigDataSent,TCPHystartTrainDetect,TCPHystartTrainCwnd,TCPHystartDelayDetect,TCPHystartDelayCwnd,TCPACKSkippedSynRecv,TCPACKSkippedPAWS,TCPACKSkippedSeq,TCPACKSkippedFinWait2,TCPACKSkippedTimeWait,TCPACKSkippedChallenge,TCPWinProbe,TCPKeepAlive,TCPMTUPFail,TCPMTUPSuccess,TCPDelivered,TCPDeliveredCE,TCPAckCompressed,TCPZeroWindowDrop,TCPRcvQDrop,TCPWqueueTooBig,TCPFastOpenPassiveAltKey,TcpTimeoutRehash,TcpDuplicateDataRehash,TCPDSACKRecvSegs,TCPDSACKIgnoredDubious,TCPMigrateReqSuccess,TCPMigrateReqFailure =  map(int, netstat_data[1:])
netstat_name=["SyncookiesSent","SyncookiesRecv","SyncookiesFailed","EmbryonicRsts","PruneCalled","RcvPruned","OfoPruned","OutOfWindowIcmps","LockDroppedIcmps","ArpFilter","TW","TWRecycled","TWKilled","PAWSActive","PAWSEstab","DelayedACKs","DelayedACKLocked","DelayedACKLost","ListenOverflows","ListenDrops","TCPHPHits","TCPPureAcks","TCPHPAcks","TCPRenoRecovery","TCPSackRecovery","TCPSACKReneging","TCPSACKReorder","TCPRenoReorder","TCPTSReorder","TCPFullUndo","TCPPartialUndo","TCPDSACKUndo","TCPLossUndo","TCPLostRetransmit","TCPRenoFailures","TCPSackFailures","TCPLossFailures","TCPFastRetrans","TCPSlowStartRetrans","TCPTimeouts","TCPLossProbes","TCPLossProbeRecovery","TCPRenoRecoveryFail","TCPSackRecoveryFail","TCPRcvCollapsed","TCPBacklogCoalesce","TCPDSACKOldSent","TCPDSACKOfoSent","TCPDSACKRecv","TCPDSACKOfoRecv","TCPAbortOnData","TCPAbortOnClose","TCPAbortOnMemory","TCPAbortOnTimeout","TCPAbortOnLinger","TCPAbortFailed","TCPMemoryPressures","TCPMemoryPressuresChrono","TCPSACKDiscard","TCPDSACKIgnoredOld","TCPDSACKIgnoredNoUndo","TCPSpuriousRTOs","TCPMD5NotFound","TCPMD5Unexpected","TCPMD5Failure","TCPSackShifted","TCPSackMerged","TCPSackShiftFallback","TCPBacklogDrop","PFMemallocDrop","TCPMinTTLDrop","TCPDeferAcceptDrop","IPReversePathFilter","TCPTimeWaitOverflow","TCPReqQFullDoCookies","TCPReqQFullDrop","TCPRetransFail","TCPRcvCoalesce","TCPOFOQueue","TCPOFODrop","TCPOFOMerge","TCPChallengeACK","TCPSYNChallenge","TCPFastOpenActive","TCPFastOpenActiveFail","TCPFastOpenPassive","TCPFastOpenPassiveFail","TCPFastOpenListenOverflow","TCPFastOpenCookieReqd","TCPFastOpenBlackhole","TCPSpuriousRtxHostQueues","BusyPollRxPackets","TCPAutoCorking","TCPFromZeroWindowAdv","TCPToZeroWindowAdv","TCPWantZeroWindowAdv","TCPSynRetrans","TCPOrigDataSent","TCPHystartTrainDetect","TCPHystartTrainCwnd","TCPHystartDelayDetect","TCPHystartDelayCwnd","TCPACKSkippedSynRecv","TCPACKSkippedPAWS","TCPACKSkippedSeq","TCPACKSkippedFinWait2","TCPACKSkippedTimeWait","TCPACKSkippedChallenge","TCPWinProbe","TCPKeepAlive","TCPMTUPFail","TCPMTUPSuccess","TCPDelivered","TCPDeliveredCE","TCPAckCompressed","TCPZeroWindowDrop","TCPRcvQDrop","TCPWqueueTooBig","TCPFastOpenPassiveAltKey","TcpTimeoutRehash","TcpDuplicateDataRehash","TCPDSACKRecvSegs","TCPDSACKIgnoredDubious","TCPMigrateReqSuccess","TCPMigrateReqFailure"]

snmp_ip_name=["Forwarding","DefaultTTL","InReceives","InHdrErrors","InAddrErrors","ForwDatagrams","InUnknownProtos","InDiscards","InDelivers","OutRequests","OutDiscards","OutNoRoutes","ReasmTimeout","ReasmReqds","ReasmOKs","ReasmFails","FragOKs","FragFails","FragCreates"]

def get_snmp_ip():
    with open('/proc/net/snmp', 'r') as file:
        lines = file.readlines()

    snmp_ip_list = lines[1][:-1].split(" ")
    return snmp_ip_list

def get_netstat():
    with open('/proc/net/netstat', 'r') as file:
        lines = file.readlines()

    netstat_list = lines[1][:-1].split(" ")

    return netstat_list

def netstat_report():
    netstat_old = get_netstat()
    while True:
        time.sleep(options.interval)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("============",current_time,"==============")
        netstat_new = get_netstat()
        for i in range(1, len(netstat_new)-1):
            diff=int(netstat_new[i]) - int(netstat_old[i])
            if diff > 0:
                print("%-25s: %d"%(netstat_name[i], diff))
        netstat_old = netstat_new

def snmp_report(mode):
    if mode == "ip":
        data_old = get_snmp_ip()
        while True:
            time.sleep(options.interval)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("============",current_time,"==============")
            data_new = get_snmp_ip()
            for i in range(1, len(data_new)-1):
                diff=int(data_new[i]) - int(data_old[i])
                if diff > 0:
                    print("%-25s: %d"%(snmp_ip_name[i], diff))
            data_old = data_new

if options.mode == "netstat":
    netstat_report()
elif options.mode == "snmp":
    snmp_report("ip")

