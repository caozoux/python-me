
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo 0 > /sys/kernel/debug/tracing/events/enable
echo "" > /sys/kernel/debug/tracing/trace
echo "vec == 2 || vec ==3" > /sys/kernel/debug/tracing/events/irq/softirq_raise/filter
echo "vec == 2 || vec ==3" > /sys/kernel/debug/tracing/events/irq/softirq_entry/filter
echo "vec == 2 || vec ==3" > /sys/kernel/debug/tracing/events/irq/softirq_exit/filter
echo 1 > /sys/kernel/debug/tracing/events/irq/enable
echo 1 > /sys/kernel/debug/tracing/events/net/enable
echo 1 > /sys/kernel/debug/tracing/events/napi/enable
echo 1 > /sys/kernel/debug/tracing/events/skb/enable
echo 1 > /sys/kernel/debug/tracing/tracing_on
netperf TCP_RR  -l 1&
sleep 1
./netdev-scirpt.py
#sleep 4
echo 0 > /sys/kernel/debug/tracing/tracing_on
